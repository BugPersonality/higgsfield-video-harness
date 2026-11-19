"""Unit and integration tests for scripts/hf_guard.py using a mock higgsfield CLI."""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "hf_guard.py"


MOCK_HF_SCRIPT = textwrap.dedent(
    """\
    #!/usr/bin/env python3
    import json
    import os
    import sys
    from pathlib import Path

    args = sys.argv[1:]
    log_path = Path(os.environ["MOCK_HF_LOG"])
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"argv": args}) + "\\n")

    cost = int(os.environ.get("MOCK_HF_COST", "15"))
    balance = int(os.environ.get("MOCK_HF_BALANCE", "500"))
    media_file = Path(os.environ["MOCK_HF_MEDIA"])
    counter_path = Path(os.environ["MOCK_HF_COUNTER"])
    list_path = Path(os.environ["MOCK_HF_LIST"])

    if args[:2] == ["account", "status"]:
        print(json.dumps({"balance": balance, "currency": "credits"}))
        sys.exit(0)

    if args[:2] == ["upload", "create"]:
        count = int(counter_path.read_text(encoding="utf-8").strip()) if counter_path.is_file() else 0
        count += 1
        counter_path.write_text(str(count), encoding="utf-8")
        upload_id = f"upl-mock-{count:03d}"
        print(json.dumps({"upload_id": upload_id, "url": f"https://cdn.example/uploads/{upload_id}"}))
        sys.exit(0)

    if len(args) >= 2 and args[1] == "cost":
        print(json.dumps({"estimated_credits": cost}))
        sys.exit(0)

    if args[:2] == ["generate", "list"]:
        if list_path.is_file():
            print(list_path.read_text(encoding="utf-8"))
        else:
            print(json.dumps({"jobs": []}))
        sys.exit(0)

    if args[:2] in (
        ["generate", "create"],
        ["generate", "workflow"],
        ["product-photoshoot", "create"],
        ["soul-id", "create"],
    ):
        if os.environ.get("MOCK_HF_REJECT") == "1":
            print(json.dumps({"error": "HTTP 429 rate limited"}), file=sys.stderr)
            sys.exit(1)

        count = int(counter_path.read_text(encoding="utf-8").strip()) if counter_path.is_file() else 0
        count += 1
        counter_path.write_text(str(count), encoding="utf-8")
        job_id = f"mock-job-{count:03d}"

        custom_url = os.environ.get("MOCK_HF_URL_OVERRIDE")
        if custom_url:
            out_url = custom_url
        else:
            media_file.write_bytes(f"MOCK-MEDIA-{job_id}".encode("utf-8"))
            out_url = str(media_file)

        status = os.environ.get("MOCK_HF_CREATE_STATUS", "completed")
        print(
            json.dumps(
                {
                    "job_id": job_id,
                    "status": status,
                    "credits": 0 if status == "in_progress" else cost,
                    "url": out_url,
                }
            )
        )
        sys.exit(0)

    if args[:2] == ["generate", "wait"]:
        job_id = args[2]
        media_file.write_bytes(f"MOCK-RESUMED-{job_id}".encode("utf-8"))
        print(
            json.dumps(
                {
                    "job_id": job_id,
                    "status": "completed",
                    "credits": cost,
                    "url": str(media_file),
                }
            )
        )
        sys.exit(0)

    print(json.dumps({"error": f"unhandled mock command: {args}"}), file=sys.stderr)
    sys.exit(1)
    """
)


def _write_intent(
    campaign_dir: Path,
    *,
    status: str = "ready",
    draft_cap: int = 50,
    final_cap: int = 100,
    max_retries: int = 1,
) -> None:
    campaign_dir.mkdir(parents=True, exist_ok=True)
    (campaign_dir / "intent.md").write_text(
        f"# Intent: Mock Guard Campaign\n\n"
        f"status: {status}\n\n"
        "## Purpose & viewer effect\n\n"
        "Verify credit cap enforcement and idempotent retries.\n\n"
        "## Subject & visual truth\n\n"
        "Matte ceramic mug on pale limestone table in daylight.\n\n"
        "## Format, audio & delivery\n\n"
        "5s 16:9 24fps clip.\n\n"
        "## Constraints & boundaries\n\n"
        "- **Must not:** Exceed credit envelope or double-charge timeouts.\n"
        "- **Authority & budget envelope:**\n"
        "  - Autonomy mode: autonomous-draft\n"
        f"  - Draft cap: {draft_cap} credits\n"
        f"  - Final cap: {final_cap} credits\n"
        f"  - Max auto-retries/shot: {max_retries}\n"
        "- **Scope & non-goals:** Guardrail test campaign only.\n\n"
        "## Success signal\n\n"
        "Receipts reflect exact credit spend and attempt limits.\n",
        encoding="utf-8",
    )


class TestHfGuard(unittest.TestCase):
    def _setup_env(self, tmp: Path) -> tuple[Path, dict[str, str], Path, Path]:
        mock_bin = tmp / "mock_higgsfield"
        mock_bin.write_text(MOCK_HF_SCRIPT, encoding="utf-8")
        mock_bin.chmod(mock_bin.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        log_path = tmp / "mock_hf.log.jsonl"
        list_path = tmp / "mock_hf_list.json"
        counter_path = tmp / "mock_hf_counter.txt"
        media_path = tmp / "mock_source_media.bin"

        env = os.environ.copy()
        env["MOCK_HF_LOG"] = str(log_path)
        env["MOCK_HF_LIST"] = str(list_path)
        env["MOCK_HF_COUNTER"] = str(counter_path)
        env["MOCK_HF_MEDIA"] = str(media_path)
        env["MOCK_HF_COST"] = "15"
        env["MOCK_HF_BALANCE"] = "500"
        env.pop("MOCK_HF_REJECT", None)
        env.pop("MOCK_HF_URL_OVERRIDE", None)
        env.pop("MOCK_HF_CREATE_STATUS", None)
        return mock_bin, env, log_path, list_path

    def _run_guard(
        self, args: list[str], env: dict[str, str]
    ) -> tuple[int, dict, str]:
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        parsed = json.loads(proc.stdout) if proc.stdout.strip().startswith("{") else {}
        return proc.returncode, parsed, proc.stderr

    def _read_mock_calls(self, log_path: Path) -> list[list[str]]:
        if not log_path.is_file():
            return []
        return [
            json.loads(line)["argv"]
            for line in log_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def _read_receipts(self, camp: Path) -> list[dict]:
        path = camp / "receipts.jsonl"
        if not path.is_file():
            return []
        return [
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def test_preflight_succeeds_and_reports_exact_remaining_credits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            camp = tmp / "camp"
            _write_intent(camp, draft_cap=50, final_cap=120, max_retries=2)
            mock_bin, env, _, _ = self._setup_env(tmp)
            env["MOCK_HF_COST"] = "15"

            rc, data, err = self._run_guard(
                [
                    "preflight",
                    "--campaign",
                    str(camp),
                    "--shot",
                    "s01",
                    "--kind",
                    "video",
                    "--phase",
                    "draft",
                    "--model",
                    "cinematic_studio_video_4_0",
                    "--higgsfield-bin",
                    str(mock_bin),
                ],
                env,
            )
            self.assertEqual(rc, 0, msg=f"stderr={err}\ndata={data}")
            self.assertTrue(data["ok"])
            self.assertEqual(data["estimated_credits"], 15)
            self.assertEqual(data["spent_in_phase"], 0)
            self.assertEqual(data["phase_cap"], 50)
            self.assertEqual(data["remaining_after"], 35)

    def test_preflight_and_run_refuse_budget_exceeded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            camp = tmp / "camp"
            _write_intent(camp, draft_cap=20, final_cap=100, max_retries=2)
            mock_bin, env, log_path, _ = self._setup_env(tmp)
            env["MOCK_HF_COST"] = "25"

            base_args = [
                "--campaign",
                str(camp),
                "--shot",
                "s01",
                "--kind",
                "video",
                "--phase",
                "draft",
                "--model",
                "cinematic_studio_video_4_0",
                "--higgsfield-bin",
                str(mock_bin),
            ]

            rc_pf, data_pf, _ = self._run_guard(["preflight", *base_args], env)
            self.assertEqual(rc_pf, 2, msg=data_pf)
            self.assertFalse(data_pf["ok"])
            self.assertEqual(data_pf["error_code"], "budget_exceeded")

            out_file = camp / "media" / "shots" / "s01.mp4"
            rc_run, data_run, _ = self._run_guard(
                ["run", *base_args, "--out", str(out_file)], env
            )
            self.assertEqual(rc_run, 2, msg=data_run)
            self.assertFalse(data_run["ok"])
            self.assertEqual(data_run["error_code"], "budget_exceeded")
            self.assertFalse(out_file.exists())
            create_calls = [c for c in self._read_mock_calls(log_path) if c[:2] == ["generate", "create"]]
            self.assertEqual(create_calls, [])

    def test_run_writes_receipt_copies_output_and_enforces_retry_limit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            camp = tmp / "camp"
            # Max auto-retries/shot = 1 => at most 1 + 1 = 2 total attempts
            _write_intent(camp, draft_cap=100, final_cap=200, max_retries=1)
            mock_bin, env, log_path, _ = self._setup_env(tmp)
            env["MOCK_HF_COST"] = "15"

            prompt_file = camp / "prompt.txt"
            prompt_file.write_text("Sunlight across ceramic mug.", encoding="utf-8")

            out1 = camp / "media" / "shots" / "s01-take1.mp4"
            rc1, data1, err1 = self._run_guard(
                [
                    "run",
                    "--campaign",
                    str(camp),
                    "--shot",
                    "s01",
                    "--kind",
                    "video",
                    "--phase",
                    "draft",
                    "--model",
                    "cinematic_studio_video_4_0",
                    "--prompt-file",
                    str(prompt_file),
                    "--out",
                    str(out1),
                    "--higgsfield-bin",
                    str(mock_bin),
                ],
                env,
            )
            self.assertEqual(rc1, 0, msg=f"err={err1}\ndata={data1}")
            self.assertTrue(data1["ok"])
            self.assertEqual(data1["attempt"], 0)
            self.assertTrue(out1.is_file())
            self.assertEqual(out1.read_bytes(), b"MOCK-MEDIA-mock-job-001")

            out2 = camp / "media" / "shots" / "s01-take2.mp4"
            rc2, data2, _ = self._run_guard(
                [
                    "run",
                    "--campaign",
                    str(camp),
                    "--shot",
                    "s01",
                    "--kind",
                    "video",
                    "--phase",
                    "draft",
                    "--model",
                    "cinematic_studio_video_4_0",
                    "--prompt-file",
                    str(prompt_file),
                    "--out",
                    str(out2),
                    "--higgsfield-bin",
                    str(mock_bin),
                ],
                env,
            )
            self.assertEqual(rc2, 0, msg=data2)
            self.assertEqual(data2["attempt"], 1)
            self.assertTrue(out2.is_file())

            # Third attempt exceeds 1 + max_retries (= 2) and must exit 2
            out3 = camp / "media" / "shots" / "s01-take3.mp4"
            rc3, data3, _ = self._run_guard(
                [
                    "run",
                    "--campaign",
                    str(camp),
                    "--shot",
                    "s01",
                    "--kind",
                    "video",
                    "--phase",
                    "draft",
                    "--model",
                    "cinematic_studio_video_4_0",
                    "--prompt-file",
                    str(prompt_file),
                    "--out",
                    str(out3),
                    "--higgsfield-bin",
                    str(mock_bin),
                ],
                env,
            )
            self.assertEqual(rc3, 2, msg=data3)
            self.assertFalse(data3["ok"])
            self.assertEqual(data3["error_code"], "retry_limit_exceeded")
            self.assertFalse(out3.exists())

            completed_receipts = [
                r for r in self._read_receipts(camp) if r.get("status") == "completed"
            ]
            self.assertEqual(len(completed_receipts), 2)
            self.assertEqual([r["attempt"] for r in completed_receipts], [0, 1])

            rc_st, st_data, _ = self._run_guard(
                ["status", "--campaign", str(camp), "--json"], env
            )
            self.assertEqual(rc_st, 0, msg=st_data)
            self.assertEqual(st_data["phases"]["draft"]["spent"], 30)
            self.assertEqual(st_data["phases"]["draft"]["remaining"], 70)

            create_calls = [c for c in self._read_mock_calls(log_path) if c[:2] == ["generate", "create"]]
            self.assertEqual(len(create_calls), 2)

    def test_run_refuses_when_intent_is_draft(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            camp = tmp / "camp"
            _write_intent(camp, status="draft", draft_cap=100, final_cap=200, max_retries=2)
            mock_bin, env, log_path, _ = self._setup_env(tmp)

            rc, data, _ = self._run_guard(
                [
                    "run",
                    "--campaign",
                    str(camp),
                    "--shot",
                    "s01",
                    "--kind",
                    "still",
                    "--phase",
                    "draft",
                    "--model",
                    "gpt_image_2_6",
                    "--higgsfield-bin",
                    str(mock_bin),
                ],
                env,
            )
            self.assertEqual(rc, 2, msg=data)
            self.assertFalse(data["ok"])
            self.assertEqual(data["error_code"], "intent_not_ready")
            paid_calls = [
                c
                for c in self._read_mock_calls(log_path)
                if c[:2] in (["generate", "create"], ["generate", "workflow"], ["generate", "wait"])
            ]
            self.assertEqual(paid_calls, [])

    def test_duplicate_protection_resumes_in_flight_job_without_recreating(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            camp = tmp / "camp"
            _write_intent(camp, status="ready", draft_cap=100, final_cap=200, max_retries=2)
            mock_bin, env, log_path, list_path = self._setup_env(tmp)
            env["MOCK_HF_COST"] = "15"

            prompt_file = camp / "s01_video.txt"
            prompt_file.write_text("Slow push-in across matte leather clasp.", encoding="utf-8")

            rc_dry, dry_data, _ = self._run_guard(
                [
                    "run",
                    "--campaign",
                    str(camp),
                    "--shot",
                    "s01",
                    "--kind",
                    "video",
                    "--phase",
                    "draft",
                    "--model",
                    "cinematic_studio_video_4_0",
                    "--prompt-file",
                    str(prompt_file),
                    "--dry-run",
                    "--higgsfield-bin",
                    str(mock_bin),
                    "--",
                    "--resolution",
                    "480p",
                ],
                env,
            )
            self.assertEqual(rc_dry, 0, msg=dry_data)
            params_hash = dry_data["params_hash"]

            interrupted_job = "job-inflight-777"
            (camp / "receipts.jsonl").write_text(
                json.dumps(
                    {
                        "ts": "2026-11-19T20:00:00Z",
                        "reservation_id": "res-inflight-777",
                        "shot": "s01",
                        "kind": "video",
                        "phase": "draft",
                        "model": "cinematic_studio_video_4_0",
                        "is_workflow": False,
                        "params_hash": params_hash,
                        "job_id": interrupted_job,
                        "status": "in_progress",
                        "estimated_credits": 15,
                        "actual_credits": None,
                        "credits": 15,
                        "url": None,
                        "out": None,
                        "attempt": 0,
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            list_path.write_text(
                json.dumps({"jobs": [{"job_id": interrupted_job, "status": "in_progress"}]}),
                encoding="utf-8",
            )
            log_path.write_text("", encoding="utf-8")

            out_file = camp / "media" / "shots" / "s01-resumed.mp4"
            rc, data, err = self._run_guard(
                [
                    "run",
                    "--campaign",
                    str(camp),
                    "--shot",
                    "s01",
                    "--kind",
                    "video",
                    "--phase",
                    "draft",
                    "--model",
                    "cinematic_studio_video_4_0",
                    "--prompt-file",
                    str(prompt_file),
                    "--out",
                    str(out_file),
                    "--higgsfield-bin",
                    str(mock_bin),
                    "--",
                    "--resolution",
                    "480p",
                ],
                env,
            )
            self.assertEqual(rc, 0, msg=f"err={err}\ndata={data}")
            self.assertTrue(data["ok"])
            self.assertTrue(data["resumed"])
            self.assertEqual(data["job_id"], interrupted_job)
            self.assertTrue(out_file.is_file())
            self.assertEqual(out_file.read_bytes(), f"MOCK-RESUMED-{interrupted_job}".encode())

            calls = self._read_mock_calls(log_path)
            create_calls = [c for c in calls if c[:2] == ["generate", "create"]]
            wait_calls = [c for c in calls if c[:2] == ["generate", "wait"]]
            self.assertEqual(create_calls, [], msg=f"Unexpected duplicate create call: {calls}")
            self.assertEqual(len(wait_calls), 1, msg=f"Expected single wait call: {calls}")
            self.assertEqual(wait_calls[0][:3], ["generate", "wait", interrupted_job])
            self.assertIn("--json", wait_calls[0])

    def test_upload_records_upload_id_at_zero_credits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            camp = tmp / "camp"
            _write_intent(camp, draft_cap=50, final_cap=100, max_retries=2)
            mock_bin, env, log_path, _ = self._setup_env(tmp)

            ref_img = camp / "media" / "references" / "bag_hero_front.jpg"
            ref_img.parent.mkdir(parents=True, exist_ok=True)
            ref_img.write_bytes(b"\xff\xd8\xffMOCKJPEG")

            rc, data, err = self._run_guard(
                [
                    "upload",
                    "--campaign",
                    str(camp),
                    "--file",
                    str(ref_img),
                    "--ref-id",
                    "ref_bag_front",
                    "--higgsfield-bin",
                    str(mock_bin),
                ],
                env,
            )
            self.assertEqual(rc, 0, msg=f"err={err}\ndata={data}")
            self.assertTrue(data["ok"])
            self.assertEqual(data["upload_id"], "upl-mock-001")

            receipts = self._read_receipts(camp)
            self.assertEqual(len(receipts), 1)
            self.assertEqual(receipts[0]["upload_id"], "upl-mock-001")
            self.assertEqual(receipts[0]["kind"], "upload")
            self.assertEqual(float(receipts[0]["credits"]), 0.0)

            rc_st, st_data, _ = self._run_guard(
                ["status", "--campaign", str(camp), "--json"], env
            )
            self.assertEqual(rc_st, 0, msg=st_data)
            self.assertEqual(st_data["phases"]["draft"]["spent"], 0)

            upload_calls = [c for c in self._read_mock_calls(log_path) if c[:2] == ["upload", "create"]]
            self.assertEqual(len(upload_calls), 1)

    def test_run_product_photoshoot_command_succeeds(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            camp = tmp / "camp"
            _write_intent(camp, draft_cap=50, final_cap=100, max_retries=2)
            mock_bin, env, log_path, _ = self._setup_env(tmp)
            env["MOCK_HF_COST"] = "10"

            out_img = camp / "media" / "stills" / "s01-shoot.png"
            rc, data, err = self._run_guard(
                [
                    "run",
                    "--campaign",
                    str(camp),
                    "--shot",
                    "s01",
                    "--kind",
                    "still",
                    "--phase",
                    "draft",
                    "--command",
                    "product-photoshoot",
                    "--model",
                    "gpt_image_2",
                    "--out",
                    str(out_img),
                    "--higgsfield-bin",
                    str(mock_bin),
                    "--",
                    "--mode",
                    "lifestyle_scene",
                ],
                env,
            )
            self.assertEqual(rc, 0, msg=f"err={err}\ndata={data}")
            self.assertTrue(data["ok"])
            self.assertEqual(data["credits"], 10)
            self.assertTrue(out_img.is_file())

            calls = self._read_mock_calls(log_path)
            self.assertTrue(
                any(c[:2] == ["product-photoshoot", "create"] for c in calls),
                msg=f"Expected product-photoshoot create call, got: {calls}",
            )

    def test_rejected_cli_failure_without_job_id_does_not_consume_budget_or_retries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            camp = tmp / "camp"
            # Max auto-retries/shot = 0 => only 1 attempt allowed total
            _write_intent(camp, draft_cap=20, final_cap=100, max_retries=0)
            mock_bin, env, _, _ = self._setup_env(tmp)
            env["MOCK_HF_COST"] = "15"
            env["MOCK_HF_REJECT"] = "1"

            base_run = [
                "run",
                "--campaign",
                str(camp),
                "--shot",
                "s01",
                "--kind",
                "video",
                "--phase",
                "draft",
                "--model",
                "cinematic_studio_video_4_0",
                "--higgsfield-bin",
                str(mock_bin),
            ]
            rc_fail, data_fail, _ = self._run_guard(base_run, env)
            self.assertEqual(rc_fail, 1, msg=data_fail)
            self.assertFalse(data_fail["ok"])
            self.assertEqual(data_fail["status"], "rejected")
            self.assertEqual(float(data_fail["credits"]), 0.0)

            rc_st, st_data, _ = self._run_guard(
                ["status", "--campaign", str(camp), "--json"], env
            )
            self.assertEqual(rc_st, 0, msg=st_data)
            self.assertEqual(st_data["phases"]["draft"]["spent"], 0)
            self.assertEqual(st_data["phases"]["draft"]["remaining"], 20)

            # Clear rejection and verify retry + budget were NOT consumed
            env.pop("MOCK_HF_REJECT", None)
            out_file = camp / "media" / "shots" / "s01-ok.mp4"
            rc_ok, data_ok, err_ok = self._run_guard(
                [*base_run, "--out", str(out_file)], env
            )
            self.assertEqual(rc_ok, 0, msg=f"err={err_ok}\ndata={data_ok}")
            self.assertTrue(data_ok["ok"])
            self.assertEqual(data_ok["attempt"], 0)
            self.assertTrue(out_file.is_file())

    def test_download_failed_preserves_job_and_resumes_without_recreating(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            camp = tmp / "camp"
            _write_intent(camp, draft_cap=50, final_cap=100, max_retries=1)
            mock_bin, env, log_path, _ = self._setup_env(tmp)
            env["MOCK_HF_COST"] = "15"

            transient_src = tmp / "transient_download_source.mp4"
            env["MOCK_HF_URL_OVERRIDE"] = str(transient_src)

            out_file = camp / "media" / "shots" / "s01-dl.mp4"
            run_args = [
                "run",
                "--campaign",
                str(camp),
                "--shot",
                "s01",
                "--kind",
                "video",
                "--phase",
                "draft",
                "--model",
                "cinematic_studio_video_4_0",
                "--out",
                str(out_file),
                "--higgsfield-bin",
                str(mock_bin),
            ]

            # First run: remote job completes (charging 15 cr) but local download source is missing
            rc1, data1, _ = self._run_guard(run_args, env)
            self.assertEqual(rc1, 1, msg=data1)
            self.assertFalse(data1["ok"])
            self.assertEqual(data1["status"], "download_failed")
            self.assertEqual(data1["error_code"], "download_failed")
            self.assertEqual(data1["job_id"], "mock-job-001")
            self.assertEqual(data1["actual_credits"], 15)
            self.assertFalse(out_file.exists())

            # Source becomes available; clear mock log and re-run to verify zero duplicate create calls
            transient_src.write_bytes(b"RECOVERED-VIDEO-BYTES")
            log_path.write_text("", encoding="utf-8")

            rc2, data2, err2 = self._run_guard(run_args, env)
            self.assertEqual(rc2, 0, msg=f"err={err2}\ndata={data2}")
            self.assertTrue(data2["ok"])
            self.assertEqual(data2["job_id"], "mock-job-001")
            self.assertTrue(out_file.is_file())
            self.assertEqual(out_file.read_bytes(), b"RECOVERED-VIDEO-BYTES")

            calls_after = self._read_mock_calls(log_path)
            create_calls = [c for c in calls_after if c[:2] == ["generate", "create"]]
            self.assertEqual(create_calls, [], msg=f"Unexpected recreate on download retry: {calls_after}")

            rc_st, st_data, _ = self._run_guard(
                ["status", "--campaign", str(camp), "--json"], env
            )
            self.assertEqual(rc_st, 0, msg=st_data)
            self.assertEqual(st_data["phases"]["draft"]["spent"], 15)

    def test_unresolved_reserved_or_in_progress_receipt_blocks_concurrent_overspend(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            camp = tmp / "camp"
            _write_intent(camp, draft_cap=25, final_cap=100, max_retries=2)
            mock_bin, env, log_path, _ = self._setup_env(tmp)
            env["MOCK_HF_COST"] = "15"

            # Seed an unresolved active `reserved` receipt for s01 holding 15 credits
            (camp / "receipts.jsonl").write_text(
                json.dumps(
                    {
                        "ts": "2026-11-19T20:10:00Z",
                        "reservation_id": "res-active-s01",
                        "shot": "s01",
                        "kind": "video",
                        "phase": "draft",
                        "model": "cinematic_studio_video_4_0",
                        "is_workflow": False,
                        "params_hash": "hash-s01-in-flight",
                        "job_id": "",
                        "status": "reserved",
                        "estimated_credits": 15,
                        "actual_credits": None,
                        "credits": 15,
                        "url": None,
                        "out": None,
                        "attempt": 0,
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            # Concurrent call for s02 (15 cr) would push 15 + 15 = 30 > Draft cap 25
            rc, data, _ = self._run_guard(
                [
                    "run",
                    "--campaign",
                    str(camp),
                    "--shot",
                    "s02",
                    "--kind",
                    "video",
                    "--phase",
                    "draft",
                    "--model",
                    "cinematic_studio_video_4_0",
                    "--higgsfield-bin",
                    str(mock_bin),
                ],
                env,
            )
            self.assertEqual(rc, 2, msg=data)
            self.assertFalse(data["ok"])
            self.assertEqual(data["error_code"], "budget_exceeded")
            self.assertEqual(data["spent_in_phase"], 15)
            create_calls = [c for c in self._read_mock_calls(log_path) if c[:2] == ["generate", "create"]]
            self.assertEqual(create_calls, [])


if __name__ == "__main__":
    unittest.main()
