#!/usr/bin/env python3
"""Budget-enforcing, atomic-reservation, idempotent wrapper around the higgsfield CLI."""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import contextlib
import datetime
import fcntl
import hashlib
import http.client
import importlib.util
import json
import os
import shutil
import subprocess
import urllib.error
import urllib.parse
import urllib.request
import uuid
from collections.abc import Iterator
from pathlib import Path
from typing import Any

VALID_PHASES = ("draft", "final")
VALID_KINDS = ("still", "video", "audio", "analysis")
VALID_HF_COMMANDS = ("generate", "product-photoshoot", "soul-id")

IN_FLIGHT_STATUSES = frozenset(
    {
        "reserved",
        "in_progress",
        "running",
        "queued",
        "pending",
        "processing",
        "submitted",
        "starting",
    }
)
COMPLETED_STATUSES = frozenset({"completed", "succeeded", "success", "done", "finished"})
FAILED_STATUSES = frozenset(
    {"failed", "error", "cancelled", "canceled", "rejected", "ip_detected", "timeout"}
)


class CorruptReceiptsError(RuntimeError):
    """Raised when receipts.jsonl contains malformed JSONL data."""


def _load_check_intent():
    mod_path = Path(__file__).resolve().with_name("check-intent.py")
    spec = importlib.util.spec_from_file_location("check_intent", mod_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load sibling module: {mod_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_CHECK_INTENT = _load_check_intent()


def _utc_now_iso() -> str:
    return (
        datetime.datetime.now(datetime.UTC)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _is_number(val: Any) -> bool:
    return isinstance(val, (int, float)) and not isinstance(val, bool)


def _extract_numeric_field(payload: Any, keys: tuple[str, ...]) -> float | None:
    """Search payload (shallow then nested dicts) for the first numeric value matching keys."""
    if not isinstance(payload, dict):
        return None
    for k in keys:
        if k in payload:
            v = payload[k]
            if _is_number(v):
                return float(v)
            if isinstance(v, str):
                try:
                    return float(v.strip())
                except ValueError:
                    pass
    for nested_key in ("data", "estimate", "result", "account", "billing", "job", "cost"):
        nested = payload.get(nested_key)
        if isinstance(nested, dict):
            found = _extract_numeric_field(nested, keys)
            if found is not None:
                return found
    for v in payload.values():
        if isinstance(v, dict):
            found = _extract_numeric_field(v, keys)
            if found is not None:
                return found
    return None


def _extract_string_field(payload: Any, keys: tuple[str, ...]) -> str | None:
    if not isinstance(payload, dict):
        return None
    for k in keys:
        v = payload.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    for nested_key in ("data", "result", "job", "output", "asset", "upload"):
        nested = payload.get(nested_key)
        if isinstance(nested, dict):
            found = _extract_string_field(nested, keys)
            if found is not None:
                return found
    for list_key in ("outputs", "results", "assets", "files", "media", "items"):
        items = payload.get(list_key)
        if isinstance(items, list):
            for item in items:
                if isinstance(item, str) and item.strip():
                    if any(k in ("url", "output_url", "media_url") for k in keys):
                        return item.strip()
                elif isinstance(item, dict):
                    found = _extract_string_field(item, keys)
                    if found is not None:
                        return found
    return None


def _clean_num(val: float) -> int | float:
    return int(val) if float(val).is_integer() else round(val, 4)


def compute_params_hash(
    *,
    shot: str,
    kind: str,
    phase: str,
    model: str,
    is_workflow: bool,
    args: list[str],
    hf_command: str = "generate",
) -> str:
    """Compute deterministic SHA-256 over canonical generation parameters."""
    payload: dict[str, Any] = {
        "shot": shot,
        "kind": kind,
        "phase": phase,
        "model": model,
        "is_workflow": bool(is_workflow),
        "args": list(args),
    }
    if hf_command != "generate":
        payload["command"] = hf_command
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@contextlib.contextmanager
def _receipts_lock(campaign_dir: Path) -> Iterator[None]:
    campaign_dir.mkdir(parents=True, exist_ok=True)
    lock_path = campaign_dir / ".receipts.lock"
    with lock_path.open("a+", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def _read_receipts_raw(campaign_dir: Path) -> list[dict[str, Any]]:
    receipts_path = campaign_dir / "receipts.jsonl"
    if not receipts_path.is_file():
        return []
    records: list[dict[str, Any]] = []
    for lineno, raw_line in enumerate(
        receipts_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            raise CorruptReceiptsError(
                f"malformed JSON in {receipts_path}:{lineno}: {exc}"
            ) from exc
        if not isinstance(obj, dict):
            raise CorruptReceiptsError(
                f"expected JSON object in {receipts_path}:{lineno}, got {type(obj).__name__}"
            )
        records.append(obj)
    return records


def _collapse_receipts(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collapse append-only journal by reservation_id and job_id (latest record wins)."""
    by_res: dict[str, int] = {}
    by_job: dict[str, int] = {}
    output: list[dict[str, Any]] = []

    for rec in records:
        if rec.get("status") == "dry_run":
            continue
        rid = rec.get("reservation_id")
        rid_key = rid.strip() if isinstance(rid, str) and rid.strip() else ""
        jid = rec.get("job_id")
        jid_key = jid.strip() if isinstance(jid, str) and jid.strip() else ""

        target_idx: int | None = None
        if rid_key and rid_key in by_res:
            target_idx = by_res[rid_key]
        elif jid_key and jid_key in by_job:
            target_idx = by_job[jid_key]

        if target_idx is not None:
            output[target_idx] = rec
            if rid_key:
                by_res[rid_key] = target_idx
            if jid_key:
                by_job[jid_key] = target_idx
        else:
            idx = len(output)
            output.append(rec)
            if rid_key:
                by_res[rid_key] = idx
            if jid_key:
                by_job[jid_key] = idx
    return output


def _append_receipt(campaign_dir: Path, record: dict[str, Any]) -> None:
    receipts_path = campaign_dir / "receipts.jsonl"
    with receipts_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        fh.flush()
        os.fsync(fh.fileno())


def _effective_credits(rec: dict[str, Any]) -> float:
    """Compute effective spend for one collapsed receipt record."""
    status = str(rec.get("status") or "").lower()
    kind = str(rec.get("kind") or "video").lower()
    if kind == "upload":
        return 0.0
    if status == "rejected" and not str(rec.get("job_id") or "").strip():
        return 0.0
    if status in IN_FLIGHT_STATUSES:
        for key in ("credits", "estimated_credits"):
            v = rec.get(key)
            if _is_number(v) and float(v) > 0:
                return float(v)
        v = rec.get("credits")
        return float(v) if _is_number(v) else 0.0
    for key in ("actual_credits", "credits"):
        v = rec.get(key)
        if _is_number(v):
            return float(v)
    return 0.0


def _counts_as_attempt(rec: dict[str, Any]) -> bool:
    status = str(rec.get("status") or "").lower()
    kind = str(rec.get("kind") or "video").lower()
    if kind == "upload":
        return False
    return not (status == "rejected" and not str(rec.get("job_id") or "").strip())


def _summarize_receipts(
    records: list[dict[str, Any]],
) -> tuple[dict[str, float], dict[tuple[str, str, str], int]]:
    """Return (spent_by_phase, attempts_by_shot_kind_phase) from collapsed receipts."""
    collapsed = _collapse_receipts(records)
    spent: dict[str, float] = {"draft": 0.0, "final": 0.0}
    attempts: dict[tuple[str, str, str], int] = {}
    for rec in collapsed:
        phase = str(rec.get("phase") or "")
        shot = str(rec.get("shot") or "")
        kind = str(rec.get("kind") or "video")
        if phase in spent:
            spent[phase] += _effective_credits(rec)
        if shot and phase and _counts_as_attempt(rec):
            key = (shot, kind, phase)
            attempts[key] = attempts.get(key, 0) + 1
    return spent, attempts


def _run_cli(cmd: list[str]) -> tuple[int, str, str, Any]:
    """Execute higgsfield CLI command and attempt to parse stdout as JSON."""
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return 127, "", f"higgsfield binary not found: {cmd[0]}", None

    parsed: Any = None
    stdout = proc.stdout.strip()
    if stdout:
        try:
            parsed = json.loads(stdout)
        except json.JSONDecodeError:
            for line in reversed(stdout.splitlines()):
                line_s = line.strip()
                if line_s.startswith(("{", "[")):
                    try:
                        parsed = json.loads(line_s)
                        break
                    except json.JSONDecodeError:
                        pass
    return proc.returncode, proc.stdout, proc.stderr, parsed


def _resolve_hf_bin(cli_value: str | None) -> str:
    if cli_value:
        return cli_value
    return os.environ.get("HIGGSFIELD_BIN", "higgsfield")


def _load_envelope_or_error(
    campaign_dir: Path,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    intent_path = campaign_dir / "intent.md"
    if not intent_path.is_file():
        return None, {
            "ok": False,
            "error_code": "intent_not_ready",
            "message": f"intent.md not found in campaign directory: {campaign_dir}",
        }
    envelope = _CHECK_INTENT.parse_budget_envelope(intent_path)
    if envelope.get("status") != "ready":
        return None, {
            "ok": False,
            "error_code": "intent_not_ready",
            "status": envelope.get("status"),
            "message": (
                f"intent.md status is '{envelope.get('status')}' "
                "(paid generations and uploads require status: ready)"
            ),
        }
    if envelope.get("errors"):
        return None, {
            "ok": False,
            "error_code": "invalid_budget_envelope",
            "message": "; ".join(envelope["errors"]),
            "errors": envelope["errors"],
        }
    return envelope, None


def _build_cost_cmd(
    hf_bin: str,
    hf_command: str,
    model: str,
    is_workflow: bool,
    extra_args: list[str],
) -> list[str]:
    if hf_command == "generate":
        cmd = [hf_bin, "generate", "cost"]
        if is_workflow:
            cmd.append("workflow")
        cmd.extend([model, *extra_args, "--json"])
        return cmd
    return [hf_bin, hf_command, "cost", *extra_args, "--json"]


def _build_exec_cmd(
    hf_bin: str,
    hf_command: str,
    model: str,
    is_workflow: bool,
    cli_args: list[str],
    wait_timeout: str,
) -> list[str]:
    if hf_command == "generate":
        subcmd = "workflow" if is_workflow else "create"
        return [
            hf_bin,
            "generate",
            subcmd,
            model,
            *cli_args,
            "--wait",
            "--wait-timeout",
            wait_timeout,
            "--json",
        ]
    return [hf_bin, hf_command, "create", *cli_args, "--json"]


def _do_preflight(
    *,
    campaign_dir: Path,
    shot: str,
    kind: str,
    phase: str,
    model: str,
    is_workflow: bool,
    hf_command: str,
    hf_bin: str,
    extra_args: list[str],
    records: list[dict[str, Any]] | None = None,
) -> tuple[int, dict[str, Any]]:
    envelope, env_err = _load_envelope_or_error(campaign_dir)
    if env_err is not None or envelope is None:
        return 2, env_err or {"ok": False, "error_code": "intent_not_ready"}

    if records is None:
        try:
            records = _read_receipts_raw(campaign_dir)
        except CorruptReceiptsError as exc:
            return 2, {
                "ok": False,
                "error_code": "corrupt_receipts",
                "message": str(exc),
            }

    spent_map, attempts_map = _summarize_receipts(records)
    spent_in_phase = spent_map.get(phase, 0.0)
    phase_cap = int(envelope["draft_cap"] if phase == "draft" else envelope["final_cap"])
    max_retries = int(envelope["max_auto_retries"])
    max_attempts = 1 + max_retries
    attempts_used = attempts_map.get((shot, kind, phase), 0)

    if attempts_used >= max_attempts:
        return 2, {
            "ok": False,
            "error_code": "retry_limit_exceeded",
            "campaign": str(campaign_dir),
            "shot": shot,
            "kind": kind,
            "phase": phase,
            "attempts_used": attempts_used,
            "max_attempts": max_attempts,
            "max_auto_retries": max_retries,
            "message": (
                f"shot '{shot}' ({kind}/{phase}) has already used {attempts_used}/{max_attempts} "
                f"allowed attempts (max_auto_retries={max_retries})"
            ),
        }

    warnings: list[str] = []

    # Account status (non-fatal warning if unavailable)
    account_balance: float | None = None
    acc_rc, _, acc_err, acc_json = _run_cli([hf_bin, "account", "status", "--json"])
    if acc_rc == 0 and isinstance(acc_json, dict):
        account_balance = _extract_numeric_field(
            acc_json, ("balance", "credits", "available_credits", "remaining_credits")
        )
    else:
        detail = acc_err.strip() or f"exit code {acc_rc}"
        warnings.append(f"account status unavailable: {detail}")

    # Cost estimation (mandatory)
    cost_cmd = _build_cost_cmd(hf_bin, hf_command, model, is_workflow, extra_args)
    cost_rc, cost_out, cost_err, cost_json = _run_cli(cost_cmd)
    if (
        cost_rc not in (0, 127)
        and hf_command != "generate"
        and model
        and model != hf_command
    ):
        # Fallback to `generate cost <model>` if sub-namespace lacks a `cost` subcommand
        fallback_cmd = _build_cost_cmd(hf_bin, "generate", model, is_workflow, extra_args)
        fb_rc, fb_out, fb_err, fb_json = _run_cli(fallback_cmd)
        if fb_rc == 0:
            cost_cmd, cost_rc, cost_out, cost_err, cost_json = (
                fallback_cmd,
                fb_rc,
                fb_out,
                fb_err,
                fb_json,
            )
    if cost_rc == 127:
        return 1, {
            "ok": False,
            "error_code": "cli_not_found",
            "message": cost_err.strip(),
        }
    if cost_rc != 0:
        return 1, {
            "ok": False,
            "error_code": "cost_estimation_failed",
            "command": cost_cmd,
            "exit_code": cost_rc,
            "stderr": cost_err.strip(),
            "stdout": cost_out.strip(),
            "message": f"higgsfield cost estimation failed (exit {cost_rc})",
        }

    estimated_credits = _extract_numeric_field(
        cost_json, ("estimated_credits", "credits", "cost", "total_credits", "price")
    )
    if estimated_credits is None or estimated_credits < 0:
        return 1, {
            "ok": False,
            "error_code": "cost_parse_failed",
            "command": cost_cmd,
            "raw_output": cost_out.strip(),
            "message": "could not parse numeric credit estimate from higgsfield cost output",
        }

    if account_balance is not None and account_balance < estimated_credits:
        warnings.append(
            f"account balance ({_clean_num(account_balance)} credits) is lower than "
            f"estimated cost ({_clean_num(estimated_credits)} credits)"
        )

    projected_total = spent_in_phase + estimated_credits
    remaining_after = phase_cap - projected_total

    if projected_total > phase_cap:
        return 2, {
            "ok": False,
            "error_code": "budget_exceeded",
            "campaign": str(campaign_dir),
            "shot": shot,
            "kind": kind,
            "phase": phase,
            "model": model,
            "estimated_credits": _clean_num(estimated_credits),
            "spent_in_phase": _clean_num(spent_in_phase),
            "phase_cap": phase_cap,
            "remaining_before": _clean_num(phase_cap - spent_in_phase),
            "remaining_after": _clean_num(remaining_after),
            "attempts_used": attempts_used,
            "max_attempts": max_attempts,
            "account_balance": _clean_num(account_balance) if account_balance is not None else None,
            "warnings": warnings,
            "message": (
                f"{phase} budget cap exceeded: spent {_clean_num(spent_in_phase)} + "
                f"estimated {_clean_num(estimated_credits)} > cap {phase_cap} credits"
            ),
        }

    return 0, {
        "ok": True,
        "campaign": str(campaign_dir),
        "shot": shot,
        "kind": kind,
        "phase": phase,
        "command": hf_command,
        "model": model,
        "is_workflow": is_workflow,
        "estimated_credits": _clean_num(estimated_credits),
        "spent_in_phase": _clean_num(spent_in_phase),
        "phase_cap": phase_cap,
        "remaining_after": _clean_num(remaining_after),
        "attempts_used": attempts_used,
        "max_attempts": max_attempts,
        "account_balance": _clean_num(account_balance) if account_balance is not None else None,
        "warnings": warnings,
    }


def _extract_job_list(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for key in ("jobs", "items", "data", "generations", "results"):
            val = payload.get(key)
            if isinstance(val, list):
                return [item for item in val if isinstance(item, dict)]
    return []


def _find_download_failed_receipt(
    records: list[dict[str, Any]],
    params_hash: str,
) -> dict[str, Any] | None:
    collapsed = _collapse_receipts(records)
    for rec in reversed(collapsed):
        if (
            rec.get("params_hash") == params_hash
            and str(rec.get("status") or "").lower() == "download_failed"
            and isinstance(rec.get("url"), str)
            and rec["url"].strip()
        ):
            return rec
    return None


def _find_in_flight_job(
    records: list[dict[str, Any]],
    params_hash: str,
    hf_bin: str,
    hf_command: str,
) -> dict[str, Any]:
    """Inspect collapsed receipts, `generate list`, and `generate get` for in-flight work.

    Returns dict with keys:
      action: "none" | "wait" | "use_get_result" | "blocked_reservation"
      job_id: str | None
      reservation_id: str | None
      attempt: int | None
      estimated_credits: float | None
      get_payload: dict | None
      warnings: list[str]
    """
    warnings: list[str] = []
    collapsed = _collapse_receipts(records)

    unresolved_receipt: dict[str, Any] | None = None
    for rec in reversed(collapsed):
        rec_status = str(rec.get("status") or "").lower()
        if rec.get("params_hash") == params_hash and rec_status in IN_FLIGHT_STATUSES:
            unresolved_receipt = rec
            break

    remote_jobs: list[dict[str, Any]] = []
    list_ok = False
    if hf_command == "generate":
        list_rc, _, list_err, list_json = _run_cli([hf_bin, "generate", "list", "--json"])
        list_ok = list_rc == 0 and list_json is not None
        if list_ok:
            remote_jobs = _extract_job_list(list_json)
        else:
            detail = list_err.strip() or f"exit code {list_rc}"
            warnings.append(f"generate list unavailable during duplicate check: {detail}")

    remote_by_id: dict[str, dict[str, Any]] = {}
    for job in remote_jobs:
        jid = _extract_string_field(job, ("job_id", "id", "request_set_id", "request_id"))
        if jid:
            remote_by_id[jid] = job

    if unresolved_receipt is not None:
        rec_jid = str(unresolved_receipt.get("job_id") or "").strip()
        rec_rid = str(unresolved_receipt.get("reservation_id") or "").strip() or None
        rec_attempt = unresolved_receipt.get("attempt")
        attempt_int = int(rec_attempt) if isinstance(rec_attempt, int) else None
        est_raw = unresolved_receipt.get("estimated_credits")
        est_val = (
            float(est_raw)
            if _is_number(est_raw)
            else (
                float(unresolved_receipt["credits"])
                if _is_number(unresolved_receipt.get("credits"))
                else None
            )
        )

        if rec_jid:
            if hf_command != "generate":
                return {
                    "action": "blocked_reservation",
                    "job_id": rec_jid,
                    "reservation_id": rec_rid,
                    "attempt": attempt_int,
                    "estimated_credits": est_val,
                    "get_payload": None,
                    "warnings": warnings,
                }
            remote_job = remote_by_id.get(rec_jid)
            if remote_job is not None:
                rstatus = str(remote_job.get("status") or "").lower()
                if rstatus not in FAILED_STATUSES:
                    return {
                        "action": "wait",
                        "job_id": rec_jid,
                        "reservation_id": rec_rid,
                        "attempt": attempt_int,
                        "estimated_credits": est_val,
                        "get_payload": None,
                        "warnings": warnings,
                    }
            else:
                # Fallback to `generate get <job_id> --json` before ever submitting a new job
                get_rc, _, get_err, get_json = _run_cli(
                    [hf_bin, "generate", "get", rec_jid, "--json"]
                )
                if get_rc == 0 and isinstance(get_json, dict):
                    gstatus = str(
                        _extract_string_field(get_json, ("status", "state")) or ""
                    ).lower()
                    if gstatus in COMPLETED_STATUSES:
                        g_url = _extract_string_field(
                            get_json,
                            (
                                "url",
                                "output_url",
                                "media_url",
                                "video_url",
                                "image_url",
                                "audio_url",
                                "local_path",
                                "path",
                            ),
                        )
                        if g_url:
                            return {
                                "action": "use_get_result",
                                "job_id": rec_jid,
                                "reservation_id": rec_rid,
                                "attempt": attempt_int,
                                "estimated_credits": est_val,
                                "get_payload": get_json,
                                "warnings": warnings,
                            }
                        return {
                            "action": "wait",
                            "job_id": rec_jid,
                            "reservation_id": rec_rid,
                            "attempt": attempt_int,
                            "estimated_credits": est_val,
                            "get_payload": None,
                            "warnings": warnings,
                        }
                    if gstatus not in FAILED_STATUSES:
                        return {
                            "action": "wait",
                            "job_id": rec_jid,
                            "reservation_id": rec_rid,
                            "attempt": attempt_int,
                            "estimated_credits": est_val,
                            "get_payload": None,
                            "warnings": warnings,
                        }
                elif not list_ok:
                    detail = get_err.strip() or f"exit code {get_rc}"
                    warnings.append(
                        f"generate get fallback unavailable ({detail}); waiting on {rec_jid}"
                    )
                    return {
                        "action": "wait",
                        "job_id": rec_jid,
                        "reservation_id": rec_rid,
                        "attempt": attempt_int,
                        "estimated_credits": est_val,
                        "get_payload": None,
                        "warnings": warnings,
                    }
                else:
                    # Not in list AND get failed — fail safe by calling wait rather than double-spending
                    detail = get_err.strip() or f"exit code {get_rc}"
                    warnings.append(
                        f"job '{rec_jid}' absent from list and generate get failed ({detail}); "
                        "attempting wait before refusing"
                    )
                    return {
                        "action": "wait",
                        "job_id": rec_jid,
                        "reservation_id": rec_rid,
                        "attempt": attempt_int,
                        "estimated_credits": est_val,
                        "get_payload": None,
                        "warnings": warnings,
                    }
        else:
            # Active `reserved` record without a job_id yet: check remote list by params_hash first
            for job in remote_jobs:
                rstatus = str(job.get("status") or "").lower()
                if rstatus in IN_FLIGHT_STATUSES or rstatus in COMPLETED_STATUSES:
                    meta_hash = _extract_string_field(job, ("params_hash",))
                    if not meta_hash and isinstance(job.get("metadata"), dict):
                        meta_hash = _extract_string_field(job["metadata"], ("params_hash",))
                    if meta_hash == params_hash:
                        jid = _extract_string_field(
                            job, ("job_id", "id", "request_set_id", "request_id")
                        )
                        if jid:
                            return {
                                "action": "wait",
                                "job_id": jid,
                                "reservation_id": rec_rid,
                                "attempt": attempt_int,
                                "estimated_credits": est_val,
                                "get_payload": None,
                                "warnings": warnings,
                            }
            # Another worker holds an unresolved reservation for this exact params_hash
            return {
                "action": "blocked_reservation",
                "job_id": None,
                "reservation_id": rec_rid,
                "attempt": attempt_int,
                "estimated_credits": est_val,
                "get_payload": None,
                "warnings": warnings,
            }

    # Check generate list for any active job tagged with our params_hash
    for job in remote_jobs:
        rstatus = str(job.get("status") or "").lower()
        if rstatus in IN_FLIGHT_STATUSES:
            meta_hash = _extract_string_field(job, ("params_hash",))
            if not meta_hash and isinstance(job.get("metadata"), dict):
                meta_hash = _extract_string_field(job["metadata"], ("params_hash",))
            if meta_hash == params_hash:
                jid = _extract_string_field(
                    job, ("job_id", "id", "request_set_id", "request_id")
                )
                if jid:
                    return {
                        "action": "wait",
                        "job_id": jid,
                        "reservation_id": None,
                        "attempt": None,
                        "estimated_credits": None,
                        "get_payload": None,
                        "warnings": warnings,
                    }

    return {
        "action": "none",
        "job_id": None,
        "reservation_id": None,
        "attempt": None,
        "estimated_credits": None,
        "get_payload": None,
        "warnings": warnings,
    }


def _normalize_job_status(raw_status: str | None, exit_code: int) -> str:
    if raw_status:
        low = raw_status.strip().lower()
        if low in COMPLETED_STATUSES:
            return "completed"
        if low in IN_FLIGHT_STATUSES:
            return "in_progress"
        if low in FAILED_STATUSES:
            return low
        return low
    return "completed" if exit_code == 0 else "failed"


def _download_or_copy(url_or_path: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    parsed = urllib.parse.urlparse(url_or_path)
    if parsed.scheme in ("http", "https"):
        req = urllib.request.Request(
            url_or_path,
            headers={"User-Agent": "higgsfield-video-harness/1.0"},
        )
        with urllib.request.urlopen(req, timeout=120) as resp, dest.open("wb") as out_fh:
            shutil.copyfileobj(resp, out_fh)
    elif parsed.scheme == "file":
        src = Path(urllib.request.url2pathname(parsed.path))
        shutil.copyfile(src, dest)
    else:
        src = Path(url_or_path)
        if not src.is_file():
            raise FileNotFoundError(f"media source not found: {url_or_path}")
        shutil.copyfile(src, dest)


def _append_prompt_file(prompt_file: str | None, extra_args: list[str]) -> tuple[list[str] | None, dict[str, Any] | None]:
    cli_args = list(extra_args)
    if not prompt_file:
        return cli_args, None
    pf = Path(prompt_file)
    if not pf.is_file():
        return None, {
            "ok": False,
            "error_code": "prompt_file_not_found",
            "message": f"prompt file not found: {pf}",
        }
    prompt_text = pf.read_text(encoding="utf-8").strip()
    cli_args.extend(["--prompt", prompt_text])
    return cli_args, None


def _cmd_preflight(args: argparse.Namespace, extra_args: list[str]) -> int:
    campaign_dir = Path(args.campaign)
    hf_bin = _resolve_hf_bin(getattr(args, "higgsfield_bin", None))
    hf_command = args.hf_command
    model = args.model or (hf_command if hf_command != "generate" else None)
    if not model:
        print(
            json.dumps(
                {
                    "ok": False,
                    "error_code": "missing_model",
                    "message": "--model is required when --command is 'generate'",
                },
                indent=2,
            )
        )
        return 2

    cli_args, pf_err = _append_prompt_file(args.prompt_file, extra_args)
    if pf_err is not None or cli_args is None:
        print(json.dumps(pf_err, indent=2))
        return 2

    rc, payload = _do_preflight(
        campaign_dir=campaign_dir,
        shot=args.shot,
        kind=args.kind,
        phase=args.phase,
        model=model,
        is_workflow=args.workflow,
        hf_command=hf_command,
        hf_bin=hf_bin,
        extra_args=cli_args,
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return rc


def _cmd_upload(args: argparse.Namespace) -> int:
    campaign_dir = Path(args.campaign)
    file_path = Path(args.file)
    hf_bin = _resolve_hf_bin(getattr(args, "higgsfield_bin", None))

    if not campaign_dir.is_dir():
        print(
            json.dumps(
                {
                    "ok": False,
                    "error_code": "intent_not_ready",
                    "message": f"campaign directory not found: {campaign_dir}",
                },
                indent=2,
            )
        )
        return 2

    _, env_err = _load_envelope_or_error(campaign_dir)
    if env_err is not None:
        print(json.dumps(env_err, indent=2, ensure_ascii=False))
        return 2

    if not file_path.is_file():
        print(
            json.dumps(
                {
                    "ok": False,
                    "error_code": "file_not_found",
                    "message": f"upload source file not found: {file_path}",
                },
                indent=2,
            )
        )
        return 2

    upload_cmd = [hf_bin, "upload", "create", str(file_path), "--json"]
    rc, out, err, parsed = _run_cli(upload_cmd)
    if rc == 127:
        print(
            json.dumps(
                {
                    "ok": False,
                    "error_code": "cli_not_found",
                    "message": err.strip(),
                },
                indent=2,
            )
        )
        return 1
    if rc != 0:
        print(
            json.dumps(
                {
                    "ok": False,
                    "error_code": "upload_failed",
                    "exit_code": rc,
                    "stderr": err.strip(),
                    "stdout": out.strip(),
                    "message": f"higgsfield upload create failed (exit {rc})",
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 1

    upload_id = (
        _extract_string_field(parsed, ("upload_id", "id", "file_id", "asset_id"))
        if isinstance(parsed, dict)
        else None
    )
    if not upload_id:
        print(
            json.dumps(
                {
                    "ok": False,
                    "error_code": "upload_parse_failed",
                    "stdout": out.strip(),
                    "message": "upload succeeded but returned no upload_id",
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 1

    media_url = (
        _extract_string_field(parsed, ("url", "file_url", "asset_url"))
        if isinstance(parsed, dict)
        else None
    )
    ref_id = args.ref_id or file_path.stem
    params_hash = hashlib.sha256(
        json.dumps(
            {"kind": "upload", "ref_id": ref_id, "file": str(file_path)},
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()

    receipt = {
        "ts": _utc_now_iso(),
        "reservation_id": f"upl-{uuid.uuid4().hex[:12]}",
        "shot": ref_id,
        "ref_id": ref_id,
        "kind": "upload",
        "phase": "draft",
        "model": "upload",
        "is_workflow": False,
        "params_hash": params_hash,
        "job_id": upload_id,
        "upload_id": upload_id,
        "file": str(file_path),
        "status": "completed",
        "estimated_credits": 0.0,
        "actual_credits": 0.0,
        "credits": 0.0,
        "url": media_url,
        "out": None,
        "attempt": 0,
    }

    with _receipts_lock(campaign_dir):
        try:
            _read_receipts_raw(campaign_dir)
        except CorruptReceiptsError as exc:
            print(
                json.dumps(
                    {
                        "ok": False,
                        "error_code": "corrupt_receipts",
                        "message": str(exc),
                    },
                    indent=2,
                )
            )
            return 2
        _append_receipt(campaign_dir, receipt)

    print(
        json.dumps(
            {
                "ok": True,
                "upload_id": upload_id,
                "ref_id": ref_id,
                "file": str(file_path),
                "url": media_url,
                "credits": 0,
                "receipt": receipt,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


def _cmd_run(args: argparse.Namespace, extra_args: list[str]) -> int:
    campaign_dir = Path(args.campaign)
    hf_bin = _resolve_hf_bin(getattr(args, "higgsfield_bin", None))
    hf_command = args.hf_command
    model = args.model or (hf_command if hf_command != "generate" else None)
    if not model:
        print(
            json.dumps(
                {
                    "ok": False,
                    "error_code": "missing_model",
                    "message": "--model is required when --command is 'generate'",
                },
                indent=2,
            )
        )
        return 2

    cli_args, pf_err = _append_prompt_file(args.prompt_file, extra_args)
    if pf_err is not None or cli_args is None:
        print(json.dumps(pf_err, indent=2))
        return 2

    if not campaign_dir.is_dir():
        print(
            json.dumps(
                {
                    "ok": False,
                    "error_code": "intent_not_ready",
                    "message": f"campaign directory not found: {campaign_dir}",
                },
                indent=2,
            )
        )
        return 2

    # Verify intent envelope even for resumed/download-retried runs
    _, env_err = _load_envelope_or_error(campaign_dir)
    if env_err is not None:
        print(json.dumps(env_err, indent=2, ensure_ascii=False))
        return 2

    params_hash = compute_params_hash(
        shot=args.shot,
        kind=args.kind,
        phase=args.phase,
        model=model,
        is_workflow=args.workflow,
        args=cli_args,
        hf_command=hf_command,
    )

    reservation_id: str | None = None
    attempt_idx: int = 0
    estimated_credits: float = 0.0
    resumed_job_id: str | None = None
    resumed_get_payload: dict[str, Any] | None = None
    download_retry_rec: dict[str, Any] | None = None
    preflight_info: dict[str, Any] | None = None
    warnings: list[str] = []

    # Phase 1: locked duplicate check, download_failed check, preflight, and atomic reservation
    with _receipts_lock(campaign_dir):
        try:
            records = _read_receipts_raw(campaign_dir)
        except CorruptReceiptsError as exc:
            print(
                json.dumps(
                    {
                        "ok": False,
                        "error_code": "corrupt_receipts",
                        "message": str(exc),
                    },
                    indent=2,
                )
            )
            return 2

        # 1a. Check if a previous run completed remotely but failed locally on download
        download_retry_rec = _find_download_failed_receipt(records, params_hash)

        if download_retry_rec is not None:
            reservation_id = (
                str(download_retry_rec.get("reservation_id") or "").strip()
                or f"res-{uuid.uuid4().hex[:12]}"
            )
            resumed_job_id = str(download_retry_rec.get("job_id") or "")
            attempt_idx = int(download_retry_rec.get("attempt") or 0)
            est_r = download_retry_rec.get("estimated_credits")
            estimated_credits = float(est_r) if _is_number(est_r) else _effective_credits(download_retry_rec)
            if args.dry_run:
                print(
                    json.dumps(
                        {
                            "ok": True,
                            "dry_run": True,
                            "resumed": True,
                            "download_retry": True,
                            "job_id": resumed_job_id,
                            "url": download_retry_rec.get("url"),
                            "out": args.out,
                            "params_hash": params_hash,
                        },
                        indent=2,
                        ensure_ascii=False,
                    )
                )
                return 0
        else:
            # 1b. Check for in-flight remote job / active reservation
            dup_info = _find_in_flight_job(records, params_hash, hf_bin, hf_command)
            warnings.extend(dup_info["warnings"])
            action = dup_info["action"]

            if action == "blocked_reservation":
                print(
                    json.dumps(
                        {
                            "ok": False,
                            "error_code": "reservation_in_flight",
                            "reservation_id": dup_info["reservation_id"],
                            "job_id": dup_info["job_id"],
                            "params_hash": params_hash,
                            "message": (
                                "an unresolved reservation for this exact params_hash is already "
                                "active in receipts.jsonl; wait for completion or resolve manually "
                                "before retrying to prevent double-spend"
                            ),
                            "warnings": warnings,
                        },
                        indent=2,
                        ensure_ascii=False,
                    )
                )
                return 2

            if action in ("wait", "use_get_result"):
                resumed_job_id = dup_info["job_id"]
                reservation_id = dup_info["reservation_id"] or f"res-{uuid.uuid4().hex[:12]}"
                resumed_get_payload = dup_info["get_payload"]
                _, cur_attempts = _summarize_receipts(records)
                attempt_idx = (
                    dup_info["attempt"]
                    if dup_info["attempt"] is not None
                    else cur_attempts.get((args.shot, args.kind, args.phase), 0)
                )
                estimated_credits = (
                    float(dup_info["estimated_credits"])
                    if dup_info["estimated_credits"] is not None
                    else 0.0
                )
                if args.dry_run:
                    plan = {
                        "ok": True,
                        "dry_run": True,
                        "resumed": True,
                        "job_id": resumed_job_id,
                        "params_hash": params_hash,
                        "command": [
                            hf_bin,
                            "generate",
                            "wait",
                            resumed_job_id,
                            "--wait-timeout",
                            args.wait_timeout,
                            "--json",
                        ],
                        "out": args.out,
                        "warnings": warnings,
                    }
                    print(json.dumps(plan, indent=2, ensure_ascii=False))
                    return 0
            else:
                # 1c. Fresh submission: run preflight under lock so reservations count toward caps
                pf_rc, preflight_info = _do_preflight(
                    campaign_dir=campaign_dir,
                    shot=args.shot,
                    kind=args.kind,
                    phase=args.phase,
                    model=model,
                    is_workflow=args.workflow,
                    hf_command=hf_command,
                    hf_bin=hf_bin,
                    extra_args=cli_args,
                    records=records,
                )
                if pf_rc != 0:
                    print(json.dumps(preflight_info, indent=2, ensure_ascii=False))
                    return pf_rc

                warnings.extend(preflight_info.get("warnings") or [])
                estimated_credits = float(preflight_info["estimated_credits"])
                attempt_idx = int(preflight_info["attempts_used"])

                if args.dry_run:
                    planned_cmd = _build_exec_cmd(
                        hf_bin, hf_command, model, args.workflow, cli_args, args.wait_timeout
                    )
                    plan = {
                        "ok": True,
                        "dry_run": True,
                        "campaign": str(campaign_dir),
                        "shot": args.shot,
                        "kind": args.kind,
                        "phase": args.phase,
                        "command_type": hf_command,
                        "model": model,
                        "is_workflow": args.workflow,
                        "params_hash": params_hash,
                        "command": planned_cmd,
                        "out": args.out,
                        "preflight": preflight_info,
                        "warnings": warnings,
                    }
                    print(json.dumps(plan, indent=2, ensure_ascii=False))
                    return 0

                # Write atomic reservation BEFORE releasing lock and BEFORE remote CLI call
                reservation_id = f"res-{uuid.uuid4().hex[:12]}"
                reserved_rec = {
                    "ts": _utc_now_iso(),
                    "reservation_id": reservation_id,
                    "shot": args.shot,
                    "kind": args.kind,
                    "phase": args.phase,
                    "command": hf_command,
                    "model": model,
                    "is_workflow": bool(args.workflow),
                    "params_hash": params_hash,
                    "job_id": "",
                    "status": "reserved",
                    "estimated_credits": _clean_num(estimated_credits),
                    "actual_credits": None,
                    "credits": _clean_num(estimated_credits),
                    "url": None,
                    "out": None,
                    "attempt": attempt_idx,
                }
                _append_receipt(campaign_dir, reserved_rec)

    # Phase 1.5: Handle download-only retry (zero remote submission, zero extra spend)
    if download_retry_rec is not None:
        media_url = str(download_retry_rec["url"])
        prev_actual = _effective_credits(download_retry_rec)
        download_error: str | None = None
        out_recorded: str | None = None
        if args.out:
            try:
                _download_or_copy(media_url, Path(args.out))
                out_recorded = args.out
            except (OSError, urllib.error.URLError, http.client.HTTPException) as exc:
                download_error = f"retry download failed for '{args.out}': {exc}"

        final_status = "completed" if download_error is None else "download_failed"
        terminal_rec = {
            "ts": _utc_now_iso(),
            "reservation_id": reservation_id,
            "shot": args.shot,
            "kind": args.kind,
            "phase": args.phase,
            "command": hf_command,
            "model": model,
            "is_workflow": bool(args.workflow),
            "params_hash": params_hash,
            "job_id": resumed_job_id or "",
            "status": final_status,
            "estimated_credits": _clean_num(estimated_credits),
            "actual_credits": _clean_num(prev_actual),
            "credits": _clean_num(prev_actual),
            "url": media_url,
            "out": out_recorded,
            "attempt": attempt_idx,
        }
        with _receipts_lock(campaign_dir):
            _append_receipt(campaign_dir, terminal_rec)

        result: dict[str, Any] = {
            "ok": download_error is None,
            "resumed": True,
            "download_retried": True,
            "reservation_id": reservation_id,
            "job_id": terminal_rec["job_id"],
            "status": final_status,
            "estimated_credits": terminal_rec["estimated_credits"],
            "actual_credits": terminal_rec["actual_credits"],
            "credits": terminal_rec["credits"],
            "url": media_url,
            "out": out_recorded,
            "params_hash": params_hash,
            "attempt": attempt_idx,
            "receipt": terminal_rec,
            "warnings": warnings,
        }
        if download_error:
            result["error_code"] = "download_failed"
            result["error"] = download_error
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0 if download_error is None else 1

    # Phase 2: Execute remote CLI outside lock so parallel shots run concurrently
    if resumed_get_payload is not None:
        exec_rc = 0
        exec_out = json.dumps(resumed_get_payload)
        exec_err = ""
        exec_json: Any = resumed_get_payload
    elif resumed_job_id is not None:
        exec_cmd = [
            hf_bin,
            "generate",
            "wait",
            resumed_job_id,
            "--wait-timeout",
            args.wait_timeout,
            "--json",
        ]
        exec_rc, exec_out, exec_err, exec_json = _run_cli(exec_cmd)
    else:
        exec_cmd = _build_exec_cmd(
            hf_bin, hf_command, model, args.workflow, cli_args, args.wait_timeout
        )
        exec_rc, exec_out, exec_err, exec_json = _run_cli(exec_cmd)

    # Parse response
    job_id = (
        _extract_string_field(exec_json, ("job_id", "id", "request_set_id", "request_id"))
        if isinstance(exec_json, dict)
        else None
    ) or resumed_job_id or ""

    raw_status = (
        _extract_string_field(exec_json, ("status", "state"))
        if isinstance(exec_json, dict)
        else None
    )
    status = _normalize_job_status(raw_status, exec_rc)
    is_completed = exec_rc == 0 and status == "completed"

    media_url = (
        _extract_string_field(
            exec_json,
            (
                "url",
                "output_url",
                "media_url",
                "video_url",
                "image_url",
                "audio_url",
                "local_path",
                "path",
            ),
        )
        if isinstance(exec_json, dict)
        else None
    )

    reported_credits = (
        _extract_numeric_field(
            exec_json, ("credits", "credits_used", "actual_credits", "cost")
        )
        if isinstance(exec_json, dict)
        else None
    )

    # Classify terminal outcome and exact accounting
    download_error = None
    out_recorded = None
    actual_credits: float | None = None
    recorded_credits: float = 0.0

    if not job_id and not is_completed:
        # Immediate CLI error / HTTP 429 with NO remote job created: release reservation!
        status = "rejected"
        actual_credits = 0.0
        recorded_credits = 0.0
    elif status == "in_progress" or (
        resumed_job_id is not None and raw_status is None and exec_rc != 0
    ):
        # Timed out, still running remotely, or transient wait failure on known job_id:
        # keep status in_progress and retain estimated_credits reserved!
        status = "in_progress"
        actual_credits = None
        recorded_credits = (
            float(reported_credits)
            if reported_credits is not None and reported_credits > 0
            else estimated_credits
        )
    elif is_completed:
        actual_credits = (
            float(reported_credits) if reported_credits is not None else estimated_credits
        )
        recorded_credits = actual_credits
        if args.out:
            if not media_url:
                download_error = "generation completed but returned no media url or local_path"
                status = "download_failed"
                is_completed = False
            else:
                try:
                    _download_or_copy(media_url, Path(args.out))
                    out_recorded = args.out
                except (OSError, urllib.error.URLError, http.client.HTTPException) as exc:
                    download_error = f"failed to save output media to '{args.out}': {exc}"
                    status = "download_failed"
                    is_completed = False
    else:
        # Job created remotely (has job_id) and failed terminally
        actual_credits = float(reported_credits) if reported_credits is not None else 0.0
        recorded_credits = actual_credits

    # Phase 3: Re-acquire lock and append terminal receipt matching reservation_id
    terminal_rec = {
        "ts": _utc_now_iso(),
        "reservation_id": reservation_id,
        "shot": args.shot,
        "kind": args.kind,
        "phase": args.phase,
        "command": hf_command,
        "model": model,
        "is_workflow": bool(args.workflow),
        "params_hash": params_hash,
        "job_id": job_id,
        "status": status,
        "estimated_credits": _clean_num(estimated_credits),
        "actual_credits": _clean_num(actual_credits) if actual_credits is not None else None,
        "credits": _clean_num(recorded_credits),
        "url": media_url,
        "out": out_recorded,
        "attempt": attempt_idx,
    }
    with _receipts_lock(campaign_dir):
        _append_receipt(campaign_dir, terminal_rec)

    result = {
        "ok": is_completed,
        "resumed": resumed_job_id is not None,
        "reservation_id": reservation_id,
        "job_id": job_id,
        "status": status,
        "estimated_credits": terminal_rec["estimated_credits"],
        "actual_credits": terminal_rec["actual_credits"],
        "credits": terminal_rec["credits"],
        "url": media_url,
        "out": out_recorded,
        "params_hash": params_hash,
        "attempt": attempt_idx,
        "receipt": terminal_rec,
        "warnings": warnings,
    }
    if exec_rc == 127:
        result["error_code"] = "cli_not_found"
        result["message"] = exec_err.strip()
    elif download_error:
        result["error_code"] = "download_failed"
        result["error"] = download_error
    elif not is_completed:
        result["exit_code"] = exec_rc
        if exec_err.strip():
            result["stderr"] = exec_err.strip()
        if exec_out.strip() and exec_json is None:
            result["stdout"] = exec_out.strip()

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if is_completed else 1


def _cmd_status(args: argparse.Namespace) -> int:
    campaign_dir = Path(args.campaign)
    intent_path = campaign_dir / "intent.md"
    if not intent_path.is_file():
        err = {
            "ok": False,
            "error_code": "intent_not_found",
            "message": f"intent.md not found in {campaign_dir}",
        }
        if args.as_json:
            print(json.dumps(err, indent=2))
        else:
            print(f"ERROR: {err['message']}", file=sys.stderr)
        return 2

    envelope = _CHECK_INTENT.parse_budget_envelope(intent_path)
    try:
        records = _read_receipts_raw(campaign_dir)
    except CorruptReceiptsError as exc:
        err = {
            "ok": False,
            "error_code": "corrupt_receipts",
            "message": str(exc),
        }
        if args.as_json:
            print(json.dumps(err, indent=2))
        else:
            print(f"ERROR: {err['message']}", file=sys.stderr)
        return 2

    collapsed = _collapse_receipts(records)
    spent_map, attempts_map = _summarize_receipts(records)

    draft_cap = envelope.get("draft_cap")
    final_cap = envelope.get("final_cap")
    max_retries = envelope.get("max_auto_retries")

    shots_summary: dict[str, dict[str, Any]] = {}
    for rec in collapsed:
        if not _counts_as_attempt(rec):
            continue
        shot = str(rec.get("shot") or "unknown")
        kind = str(rec.get("kind") or "video")
        phase = str(rec.get("phase") or "draft")
        entry = shots_summary.setdefault(
            shot,
            {
                "attempts": {},
                "credits": 0.0,
                "latest_job_id": None,
                "latest_status": None,
            },
        )
        kp = f"{kind}/{phase}"
        entry["attempts"][kp] = attempts_map.get((shot, kind, phase), 0)
        entry["credits"] = _clean_num(float(entry["credits"]) + _effective_credits(rec))
        entry["latest_job_id"] = rec.get("job_id")
        entry["latest_status"] = rec.get("status")

    report = {
        "ok": True,
        "campaign": str(campaign_dir),
        "intent_status": envelope.get("status"),
        "autonomy_mode": envelope.get("autonomy_mode"),
        "max_auto_retries": max_retries,
        "phases": {
            "draft": {
                "spent": _clean_num(spent_map["draft"]),
                "cap": draft_cap,
                "remaining": (
                    _clean_num(draft_cap - spent_map["draft"])
                    if draft_cap is not None
                    else None
                ),
            },
            "final": {
                "spent": _clean_num(spent_map["final"]),
                "cap": final_cap,
                "remaining": (
                    _clean_num(final_cap - spent_map["final"])
                    if final_cap is not None
                    else None
                ),
            },
        },
        "receipt_count": len(records),
        "unique_job_count": len(collapsed),
        "shots": shots_summary,
    }

    if args.as_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        dp = report["phases"]["draft"]
        fp = report["phases"]["final"]
        print(
            f"Campaign: {campaign_dir} (intent={report['intent_status']}, "
            f"mode={report['autonomy_mode']}, max_retries={max_retries})"
        )
        print(
            f"  Draft phase: spent {dp['spent']} / {dp['cap']} credits "
            f"(remaining: {dp['remaining']})"
        )
        print(
            f"  Final phase: spent {fp['spent']} / {fp['cap']} credits "
            f"(remaining: {fp['remaining']})"
        )
        if shots_summary:
            print("  Shots:")
            for sid in sorted(shots_summary):
                s = shots_summary[sid]
                att_str = ", ".join(f"{k}={v}" for k, v in sorted(s["attempts"].items()))
                print(
                    f"    - {sid}: credits={s['credits']} attempts=({att_str}) "
                    f"latest_job={s['latest_job_id']} status={s['latest_status']}"
                )
        else:
            print("  Shots: (no receipts yet)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Budget-enforcing, atomic-reservation wrapper around the higgsfield CLI."
    )
    parser.add_argument(
        "--higgsfield-bin",
        default=None,
        help="Path to higgsfield executable (overrides HIGGSFIELD_BIN env var).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # preflight
    pf = sub.add_parser(
        "preflight",
        help="Check intent status, retry cap, and credit budget before generating.",
    )
    pf.add_argument("--campaign", required=True, help="Campaign directory containing intent.md.")
    pf.add_argument("--shot", required=True, help="Shot or asset identifier (e.g. s01).")
    pf.add_argument(
        "--kind",
        choices=VALID_KINDS,
        default="video",
        help="Generation kind for retry accounting (default: video).",
    )
    pf.add_argument("--phase", required=True, choices=VALID_PHASES, help="Budget phase.")
    pf.add_argument(
        "--command",
        dest="hf_command",
        choices=VALID_HF_COMMANDS,
        default="generate",
        help="Higgsfield CLI command namespace (default: generate).",
    )
    pf.add_argument(
        "--model",
        default=None,
        help="Higgsfield model or workflow identifier (required for --command generate).",
    )
    pf.add_argument("--workflow", action="store_true", help="Treat model as a Higgsfield workflow.")
    pf.add_argument("--prompt-file", default=None, help="Read prompt text from file and append --prompt.")
    pf.add_argument(
        "--higgsfield-bin",
        default=argparse.SUPPRESS,
        help="Path to higgsfield executable (overrides HIGGSFIELD_BIN env var).",
    )

    # run
    rn = sub.add_parser(
        "run",
        help="Run a guarded, deduplicated paid generation and record immutable receipts.",
    )
    rn.add_argument("--campaign", required=True, help="Campaign directory.")
    rn.add_argument("--shot", required=True, help="Shot or asset identifier (e.g. s01).")
    rn.add_argument("--kind", required=True, choices=VALID_KINDS, help="Generation kind.")
    rn.add_argument("--phase", required=True, choices=VALID_PHASES, help="Budget phase.")
    rn.add_argument(
        "--command",
        dest="hf_command",
        choices=VALID_HF_COMMANDS,
        default="generate",
        help="Higgsfield CLI command namespace (default: generate).",
    )
    rn.add_argument(
        "--model",
        default=None,
        help="Higgsfield model or workflow identifier (required for --command generate).",
    )
    rn.add_argument("--workflow", action="store_true", help="Invoke `generate workflow` instead of `create`.")
    rn.add_argument("--prompt-file", default=None, help="Read prompt text from file and append --prompt.")
    rn.add_argument("--out", default=None, help="Download or copy resulting media to this path.")
    rn.add_argument("--wait-timeout", default="20m", help="Timeout passed to --wait-timeout (default: 20m).")
    rn.add_argument(
        "--dry-run",
        action="store_true",
        help="Run preflight and print planned command without executing or writing a paid receipt.",
    )
    rn.add_argument(
        "--higgsfield-bin",
        default=argparse.SUPPRESS,
        help="Path to higgsfield executable (overrides HIGGSFIELD_BIN env var).",
    )

    # upload
    up = sub.add_parser(
        "upload",
        help="Upload a local reference asset via `higgsfield upload create` and record a 0-credit receipt.",
    )
    up.add_argument("--campaign", required=True, help="Campaign directory containing intent.md.")
    up.add_argument("--file", required=True, help="Local image/video/audio file to upload.")
    up.add_argument("--ref-id", default=None, help="Reference identifier (e.g. ref_bag_front).")
    up.add_argument(
        "--higgsfield-bin",
        default=argparse.SUPPRESS,
        help="Path to higgsfield executable (overrides HIGGSFIELD_BIN env var).",
    )

    # status
    st = sub.add_parser(
        "status",
        help="Show spent vs remaining credit envelope and per-shot attempts.",
    )
    st.add_argument("--campaign", required=True, help="Campaign directory.")
    st.add_argument("--json", action="store_true", dest="as_json", help="Emit JSON summary.")

    return parser


def main(argv: list[str] | None = None) -> int:
    raw_argv = list(sys.argv[1:] if argv is None else argv)
    if "--" in raw_argv:
        sep = raw_argv.index("--")
        own_argv = raw_argv[:sep]
        extra_args = raw_argv[sep + 1 :]
    else:
        own_argv = raw_argv
        extra_args = []

    parser = build_parser()
    args = parser.parse_args(own_argv)

    if args.command == "preflight":
        return _cmd_preflight(args, extra_args)
    if args.command == "run":
        return _cmd_run(args, extra_args)
    if args.command == "upload":
        return _cmd_upload(args)
    if args.command == "status":
        return _cmd_status(args)
    parser.error(f"unknown subcommand: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
