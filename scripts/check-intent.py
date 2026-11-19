#!/usr/bin/env python3
"""Static structural validator for Video Intent V1 (campaigns/<slug>/intent.md)."""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import json
import re
from pathlib import Path
from typing import Any

REQUIRED_SECTIONS = (
    "Purpose & viewer effect",
    "Subject & visual truth",
    "Format, audio & delivery",
    "Constraints & boundaries",
    "Success signal",
)

VALID_STATUSES = frozenset({"draft", "ready"})
VALID_AUTONOMY_MODES = frozenset({"autonomous-draft", "checkpointed"})
VALID_BINDINGS = frozenset({"hard", "default"})

REQUESTER_OWNER_RE = re.compile(
    r"\b(?:user|human|requester|client|founder|owner|pm|me)\b",
    re.IGNORECASE,
)

VAGUE_QUALIFIER_PATTERNS = (
    ("cinematic", re.compile(r"\bcinematic\b", re.IGNORECASE)),
    ("premium", re.compile(r"\bpremium\b", re.IGNORECASE)),
    ("dynamic", re.compile(r"\bdynamic\b", re.IGNORECASE)),
    ("high quality", re.compile(r"\bhigh[\s-]+quality\b", re.IGNORECASE)),
    ("красиво", re.compile(r"\bкрасиво\b", re.IGNORECASE)),
    ("качественно", re.compile(r"\bкачественно\b", re.IGNORECASE)),
)

PLACEHOLDER_EXACT_RE = re.compile(
    r"^(?:tbd|todo|tba|n/a|na|\.\.\.|…|\?\?\?)$",
    re.IGNORECASE,
)
PLACEHOLDER_TOKEN_CI_RE = re.compile(r"\b(?:TBD|TODO|TBA|N/A)\b", re.IGNORECASE)
PLACEHOLDER_NA_UPPER_RE = re.compile(r"(?<![A-Za-z0-9_])NA(?![A-Za-z0-9_])")
PLACEHOLDER_ELLIPSIS_RE = re.compile(r"(?:^|[\s:(\[])\.\.\.(?:$|[\s.)\]])")
PLACEHOLDER_ANGLE_RE = re.compile(r"<(?!https?://|mailto:)[A-Za-z_][^<>\n]*>")

FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")


def _strip_md_wrapper(text: str) -> str:
    """Strip outer whitespace, markdown bold/italic wrappers, and backticks."""
    val = text.strip()
    while len(val) >= 2 and (
        (val.startswith("**") and val.endswith("**"))
        or (val.startswith("__") and val.endswith("__"))
        or (val.startswith("`") and val.endswith("`"))
    ):
        if val.startswith(("**", "__")):
            val = val[2:-2].strip()
        else:
            val = val[1:-1].strip()
    if len(val) >= 2 and val.startswith("*") and val.endswith("*"):
        val = val[1:-1].strip()
    return val


def _strip_fenced_blocks(text: str) -> str:
    """Return text with fenced code blocks blanked out (preserving line count)."""
    out: list[str] = []
    in_fence = False
    fence_char = ""
    fence_len = 0
    for line in text.splitlines():
        m = FENCE_RE.match(line)
        if not in_fence:
            if m:
                in_fence = True
                fence_char = m.group(1)[0]
                fence_len = len(m.group(1))
                out.append("")
                continue
            out.append(line)
        else:
            stripped = line.lstrip()
            if (
                stripped.startswith(fence_char * fence_len)
                and stripped.strip(fence_char).strip() == ""
            ):
                in_fence = False
            out.append("")
    return "\n".join(out)


def is_placeholder(value: str | None) -> bool:
    """Return True if value is empty or contains unresolved placeholder markers."""
    if value is None:
        return True
    cleaned = _strip_md_wrapper(value)
    if not cleaned:
        return True
    if PLACEHOLDER_EXACT_RE.match(cleaned.rstrip(".")):
        return True
    if PLACEHOLDER_TOKEN_CI_RE.search(cleaned):
        return True
    # Strip inline backticked code spans so documented path templates like
    # `campaigns/<slug>/intent.md` or `NA` identifiers in code don't false-positive.
    prose_only = re.sub(r"`[^`\n]+`", " ", cleaned)
    if PLACEHOLDER_NA_UPPER_RE.search(prose_only):
        return True
    if PLACEHOLDER_ELLIPSIS_RE.search(prose_only):
        return True
    return bool(PLACEHOLDER_ANGLE_RE.search(prose_only))


def _norm_heading(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip()).lower()


def _parse_document(text: str) -> tuple[str | None, str, dict[str, tuple[str, str]]]:
    """Parse title, header block before first H2, and H2 sections."""
    lines = text.splitlines()
    title: str | None = None
    header_lines: list[str] = []
    sections: dict[str, tuple[str, str]] = {}

    current_key: str | None = None
    current_raw_heading: str = ""
    current_lines: list[str] = []

    in_fence = False
    fence_char = ""
    fence_len = 0

    for line in lines:
        fm = FENCE_RE.match(line)
        if not in_fence and fm:
            in_fence = True
            fence_char = fm.group(1)[0]
            fence_len = len(fm.group(1))
            if current_key is None:
                header_lines.append(line)
            else:
                current_lines.append(line)
            continue
        if in_fence:
            stripped = line.lstrip()
            if (
                stripped.startswith(fence_char * fence_len)
                and stripped.strip(fence_char).strip() == ""
            ):
                in_fence = False
            if current_key is None:
                header_lines.append(line)
            else:
                current_lines.append(line)
            continue

        if current_key is None and title is None:
            tm = re.match(r"^#\s+Intent:\s*(.+?)\s*$", line)
            if tm:
                title = tm.group(1).strip()
                continue

        h2 = re.match(r"^##\s+(.+?)\s*$", line)
        if h2:
            if current_key is not None:
                sections[current_key] = (current_raw_heading, "\n".join(current_lines))
            current_raw_heading = h2.group(1).strip()
            current_key = _norm_heading(current_raw_heading)
            current_lines = []
            continue

        if current_key is None:
            header_lines.append(line)
        else:
            current_lines.append(line)

    if current_key is not None:
        sections[current_key] = (current_raw_heading, "\n".join(current_lines))

    return title, "\n".join(header_lines), sections


def _extract_status(header_text: str) -> str | None:
    for line in header_text.splitlines():
        m = re.match(
            r"^\s*(?:[-*]\s+)?(?:\*\*|__)?status(?:\*\*|__)?\s*:\s*(.+?)\s*$",
            line,
            re.IGNORECASE,
        )
        if m:
            val = _strip_md_wrapper(m.group(1)).lower()
            # Drop optional trailing inline note like "(approved)"? No, keep strict token
            return val
    return None


def _extract_field_block(section_text: str, field_name: str) -> str | None:
    """Extract inline or sub-bullet/H3 block for a named field in a section."""
    escaped = re.escape(field_name)
    # Match either:
    # - **Field name:** value (optional indented continuation lines)
    # - Field name: value
    # ### Field name (followed by lines until next ###)
    lines = section_text.splitlines()
    inline_re = re.compile(
        rf"^(\s*)(?:[-*]\s+)?(?:\*\*|__)?{escaped}(?:\*\*|__)?\s*:\s*(?:\*\*|__)?\s*(.*)$",
        re.IGNORECASE,
    )
    h3_re = re.compile(rf"^###\s+{escaped}\s*:?\s*$", re.IGNORECASE)

    for idx, line in enumerate(lines):
        m = inline_re.match(line)
        if m:
            base_indent = len(m.group(1))
            first_val = m.group(2).strip()
            collected: list[str] = []
            if first_val:
                collected.append(first_val)
            is_bullet = line.lstrip().startswith(("-", "*"))
            # Gather indented continuation / sub-bullet lines
            for next_line in lines[idx + 1 :]:
                if not next_line.strip():
                    if collected:
                        # Stop at blank line only if next non-empty line is not indented deeper
                        continue
                    continue
                if next_line.lstrip().startswith("###"):
                    break
                next_indent = len(next_line) - len(next_line.lstrip(" "))
                if next_indent > base_indent:
                    collected.append(next_line.strip())
                elif not is_bullet and next_line.lstrip().startswith(("-", "*")):
                    # Unindented bullets directly under `Field:` header when first_val was empty
                    if not first_val:
                        collected.append(next_line.strip())
                    else:
                        break
                else:
                    break
            return "\n".join(collected).strip()

        if h3_re.match(line):
            collected = []
            for next_line in lines[idx + 1 :]:
                if re.match(r"^#{1,3}\s+", next_line):
                    break
                if next_line.strip():
                    collected.append(next_line.strip())
            return "\n".join(collected).strip()

    return None


def _parse_int_field(raw: str | None, allowed_units: tuple[str, ...]) -> int | None:
    if raw is None or is_placeholder(raw):
        return None
    cleaned = _strip_md_wrapper(raw).strip()
    # Reject decimals such as 12.5
    if re.match(r"^-?\d+\.\d+", cleaned):
        return None
    units_pat = "|".join(re.escape(u) for u in allowed_units)
    m = re.match(
        rf"^(-?\d+)(?:\s*(?:{units_pat}))?(?:\s*[\(\[—–-].*)?$",
        cleaned,
        re.IGNORECASE,
    )
    if not m:
        return None
    return int(m.group(1))


def resolve_intent_path(target: str | Path) -> Path:
    """Resolve a campaign directory or direct path to intent.md."""
    p = Path(target)
    if p.is_dir():
        return p / "intent.md"
    return p


def find_repo_root(start: Path) -> Path:
    """Locate repository root by walking up for AGENTS.md, Makefile, or .git."""
    cur = start.resolve()
    if cur.is_file():
        cur = cur.parent
    for parent in (cur, *cur.parents):
        if (parent / "AGENTS.md").is_file() or (parent / ".git").exists():
            return parent
    return cur


def parse_budget_envelope(intent_path: str | Path) -> dict[str, Any]:
    """Parse status and Authority & budget envelope fields from intent.md.

    Reusable by check-ledger.py and hf_guard.py.
    """
    path = resolve_intent_path(intent_path)
    errors: list[str] = []
    result: dict[str, Any] = {
        "status": None,
        "autonomy_mode": None,
        "draft_cap": None,
        "final_cap": None,
        "max_auto_retries": None,
        "errors": errors,
    }

    if not path.is_file():
        errors.append(f"intent file not found: {path}")
        return result

    text = path.read_text(encoding="utf-8")
    _, header_text, sections = _parse_document(text)
    result["status"] = _extract_status(header_text)

    constraints_entry = sections.get(_norm_heading("Constraints & boundaries"))
    if constraints_entry is None:
        errors.append("missing required section '## Constraints & boundaries'")
        return result

    constraints_body = constraints_entry[1]
    envelope_block = _extract_field_block(
        constraints_body, "Authority & budget envelope"
    )
    if envelope_block is None or not envelope_block.strip():
        errors.append(
            "Constraints & boundaries: missing 'Authority & budget envelope:' block"
        )
        return result

    # Parse individual envelope fields from the envelope block
    raw_mode = _extract_field_block(envelope_block, "Autonomy mode")
    if raw_mode is None or is_placeholder(raw_mode):
        errors.append("Authority & budget envelope: missing or placeholder 'Autonomy mode:'")
    else:
        # Take first token before optional explanatory parenthetical
        mode_val = _strip_md_wrapper(raw_mode.splitlines()[0]).split("(")[0].strip()
        mode_val = _strip_md_wrapper(mode_val)
        if mode_val not in VALID_AUTONOMY_MODES:
            errors.append(
                f"Authority & budget envelope: invalid Autonomy mode '{mode_val}' "
                f"(expected one of {sorted(VALID_AUTONOMY_MODES)})"
            )
        else:
            result["autonomy_mode"] = mode_val

    raw_draft = _extract_field_block(envelope_block, "Draft cap")
    draft_cap = _parse_int_field(raw_draft, ("credits", "credit", "cr", "cr."))
    if draft_cap is None:
        errors.append(
            "Authority & budget envelope: missing or unparseable integer 'Draft cap:'"
        )
    elif draft_cap <= 0:
        errors.append(
            f"Authority & budget envelope: 'Draft cap' must be a positive integer (> 0), got {draft_cap}"
        )
    else:
        result["draft_cap"] = draft_cap

    raw_final = _extract_field_block(envelope_block, "Final cap")
    final_cap = _parse_int_field(raw_final, ("credits", "credit", "cr", "cr."))
    if final_cap is None:
        errors.append(
            "Authority & budget envelope: missing or unparseable integer 'Final cap:'"
        )
    elif final_cap < 0:
        errors.append(
            f"Authority & budget envelope: 'Final cap' must be non-negative (>= 0), got {final_cap}"
        )
    else:
        result["final_cap"] = final_cap

    raw_retries = _extract_field_block(envelope_block, "Max auto-retries/shot")
    max_retries = _parse_int_field(
        raw_retries, ("retries/shot", "retries", "retry", "attempts", "attempt")
    )
    if max_retries is None:
        errors.append(
            "Authority & budget envelope: missing or unparseable integer 'Max auto-retries/shot:'"
        )
    elif max_retries < 0:
        errors.append(
            f"Authority & budget envelope: 'Max auto-retries/shot' must be >= 0, got {max_retries}"
        )
    else:
        result["max_auto_retries"] = max_retries

    return result


def _is_explicit_none(section_body: str) -> bool:
    lines = [ln.strip() for ln in section_body.splitlines() if ln.strip()]
    if not lines:
        return True
    if len(lines) == 1:
        cleaned = re.sub(r"^[-*]\s+", "", lines[0]).strip().rstrip(".").lower()
        return cleaned in {"none", "no open questions", "no settled decisions", "no assumptions"}
    return False


def _split_top_bullets(section_body: str) -> list[str]:
    """Split a section into top-level bullet items (keeping indented continuations)."""
    items: list[str] = []
    current: list[str] = []
    for line in section_body.splitlines():
        if re.match(r"^[-*]\s+", line):
            if current:
                items.append("\n".join(current))
            current = [line]
        elif current and (not line.strip() or line.startswith((" ", "\t"))):
            current.append(line)
        elif line.strip() and not current:
            # Non-bullet text; capture so caller can flag malformed lines
            current = [line]
    if current:
        items.append("\n".join(current))
    return items


def _validate_settled_decisions(body: str, errors: list[str]) -> None:
    if _is_explicit_none(body):
        return

    lines = body.splitlines()
    entries: list[tuple[str, list[str]]] = []
    current_heading: str | None = None
    current_lines: list[str] = []

    for line in lines:
        if re.match(r"^###\s+", line):
            if current_heading is not None:
                entries.append((current_heading, current_lines))
            current_heading = line.strip()
            current_lines = []
        elif current_heading is not None:
            current_lines.append(line)
        elif line.strip():
            errors.append(
                f"Settled decisions: unexpected content outside '### I<n> — <title>' heading: {line.strip()[:60]}"
            )

    if current_heading is not None:
        entries.append((current_heading, current_lines))

    if not entries:
        errors.append("Settled decisions: section is present but contains no '### I<n> — <title>' entries")
        return

    seen_ids: set[str] = set()
    heading_re = re.compile(r"^###\s+(I\d+)\s*(?:—|--|–|-|:)\s*(.+?)\s*$")
    superseded_re = re.compile(
        r"(?:\*\*|__)?Superseded\s+by(?:\*\*|__)?\s*:?\s*(?:\*\*|__|`)*\s*(I\d+)\b",
        re.IGNORECASE,
    )

    for heading, entry_lines in entries:
        m = heading_re.match(heading)
        if not m:
            errors.append(
                f"Settled decisions: heading '{heading}' does not match '### I<n> — <title>'"
            )
            continue
        did, dtitle = m.group(1), m.group(2)
        if is_placeholder(dtitle):
            errors.append(f"Settled decisions ({did}): title is empty or placeholder")
        if did in seen_ids:
            errors.append(f"Settled decisions: duplicate decision ID '{did}'")
        seen_ids.add(did)

        entry_text = "\n".join(entry_lines)

        binding_raw = _extract_field_block(entry_text, "Binding")
        if binding_raw is None or is_placeholder(binding_raw):
            errors.append(f"Settled decisions ({did}): missing or placeholder 'Binding: hard|default'")
        else:
            bval = _strip_md_wrapper(binding_raw.splitlines()[0]).split()[0].rstrip(".,;").lower()
            if bval not in VALID_BINDINGS:
                errors.append(
                    f"Settled decisions ({did}): invalid Binding '{bval}' (expected 'hard' or 'default')"
                )

        sup_m = superseded_re.search(entry_text)
        if sup_m:
            if sup_m.group(1) == did:
                errors.append(f"Settled decisions ({did}): cannot supersede itself")
            continue

        for req_field in ("Decision", "Rejected", "Why"):
            val = _extract_field_block(entry_text, req_field)
            if val is None or is_placeholder(val):
                errors.append(
                    f"Settled decisions ({did}): missing or placeholder '{req_field}:' "
                    f"(required unless 'Superseded by I<m>' is present)"
                )


def _validate_assumptions(body: str, errors: list[str]) -> None:
    if _is_explicit_none(body):
        return

    items = _split_top_bullets(body)
    seen_ids: set[str] = set()
    item_re = re.compile(r"^[-*]\s+(?:\*\*|__)?(A\d+)\b", re.IGNORECASE)
    reopen_re = re.compile(r"(?:\*\*|__)?Reopen\s+if(?:\*\*|__)?\s*:\s*(.+)", re.IGNORECASE | re.DOTALL)

    for item in items:
        first_line = item.splitlines()[0].strip()
        m = item_re.match(first_line)
        if not m:
            errors.append(
                f"Assumptions & reopen triggers: item must start with '- **A<n> ...**': {first_line[:60]}"
            )
            continue
        aid = m.group(1).upper()
        if aid in seen_ids:
            errors.append(f"Assumptions & reopen triggers: duplicate assumption ID '{aid}'")
        seen_ids.add(aid)

        rm = reopen_re.search(item)
        if not rm:
            errors.append(
                f"Assumptions & reopen triggers ({aid}): missing 'Reopen if:' trigger"
            )
        else:
            cond = rm.group(1).strip()
            if is_placeholder(cond):
                errors.append(
                    f"Assumptions & reopen triggers ({aid}): 'Reopen if:' condition is empty or placeholder"
                )


def _extract_inline_subkey(item_text: str, key: str) -> str | None:
    """Extract subkey value from either inline '; Key: val' or sub-bullet '- Key: val'."""
    val = _extract_field_block(item_text, key)
    if val is not None:
        return val

    escaped = re.escape(key)
    pattern = re.compile(
        rf"(?:\*\*|__)?{escaped}(?:\*\*|__)?\s*:\s*(?:\*\*|__)?\s*(.+?)"
        rf"(?=(?:\s*[;|.]?\s+|\n\s*(?:[-*]\s+)?)(?:\*\*|__)?(?:Owner|Fallback|Reopen\s+if)(?:\*\*|__)?\s*:|$)",
        re.IGNORECASE | re.DOTALL,
    )
    m = pattern.search(item_text)
    if m:
        return m.group(1).strip().rstrip(";|.").strip()
    return None


def _validate_open_questions(body: str, status: str | None, errors: list[str]) -> None:
    if _is_explicit_none(body):
        return

    items = _split_top_bullets(body)
    for idx, item in enumerate(items, start=1):
        if not re.match(r"^[-*]\s+", item):
            errors.append(
                f"Open questions (item {idx}): expected bulleted item starting with '- ': {item.splitlines()[0][:60]}"
            )
            continue

        owner = _extract_inline_subkey(item, "Owner")
        fallback = _extract_inline_subkey(item, "Fallback")
        reopen_if = _extract_inline_subkey(item, "Reopen if")

        if owner is None or is_placeholder(owner):
            errors.append(f"Open questions (item {idx}): missing or placeholder 'Owner:'")
        elif status == "ready" and REQUESTER_OWNER_RE.search(_strip_md_wrapper(owner)):
            errors.append(
                f"Open questions (item {idx}): requester-owned question not allowed at status: ready "
                f"(Owner: '{_strip_md_wrapper(owner)}')"
            )

        if fallback is None or is_placeholder(fallback):
            errors.append(f"Open questions (item {idx}): missing or placeholder 'Fallback:'")

        if reopen_if is None or is_placeholder(reopen_if):
            errors.append(f"Open questions (item {idx}): missing or placeholder 'Reopen if:'")


def _check_backticked_paths(
    text: str,
    intent_path: Path,
    require_media: bool,
    errors: list[str],
    warnings: list[str],
) -> None:
    clean_text = _strip_fenced_blocks(text)
    repo_root = find_repo_root(intent_path)
    campaign_dir = intent_path.resolve().parent

    seen_checked: set[str] = set()
    for match in re.finditer(r"`([^`\n]+)`", clean_text):
        raw_span = match.group(1).strip()
        if not raw_span or raw_span in seen_checked:
            continue
        # Strip optional #anchor
        path_str = raw_span.split("#", 1)[0].strip()
        if not path_str or "<" in path_str or ">" in path_str:
            continue

        if path_str.startswith(("brands/", "docs/")):
            seen_checked.add(raw_span)
            if any(ch in path_str for ch in ("*", "?")):
                matches = list(repo_root.glob(path_str))
                if not matches:
                    errors.append(f"referenced repo path pattern not found: `{path_str}`")
            else:
                if not (repo_root / path_str).exists():
                    errors.append(f"referenced repo path does not exist: `{path_str}`")

        elif path_str.startswith("media/references/") or "/media/references/" in path_str:
            seen_checked.add(raw_span)
            is_glob = any(ch in path_str for ch in ("*", "?"))
            found = False
            if path_str.startswith("media/references/"):
                if is_glob:
                    found = bool(list(campaign_dir.glob(path_str)))
                else:
                    found = (campaign_dir / path_str).exists()
            else:
                if is_glob:
                    found = bool(list(repo_root.glob(path_str))) or bool(list(campaign_dir.glob(path_str)))
                else:
                    found = (repo_root / path_str).exists() or (campaign_dir / path_str).exists()

            if not found:
                msg = f"referenced media path not found on disk: `{path_str}`"
                if require_media:
                    errors.append(msg)
                else:
                    warnings.append(msg)


def validate_intent(
    target: str | Path, *, require_media: bool = False
) -> dict[str, Any]:
    """Validate Video Intent V1 document and return structured report."""
    intent_path = resolve_intent_path(target)
    errors: list[str] = []
    warnings: list[str] = []

    if not intent_path.is_file():
        return {
            "ok": False,
            "file_found": False,
            "path": str(intent_path),
            "status": None,
            "title": None,
            "budget_envelope": None,
            "errors": [f"intent file not found: {intent_path}"],
            "warnings": [],
        }

    text = intent_path.read_text(encoding="utf-8")
    title, header_text, sections = _parse_document(text)

    if title is None or is_placeholder(title):
        errors.append("missing or placeholder H1 title matching '^# Intent: <title>'")

    status = _extract_status(header_text)
    if status is None:
        errors.append("missing 'status:' header line (expected 'draft' or 'ready')")
    elif status not in VALID_STATUSES:
        errors.append(
            f"invalid status '{status}' (expected one of {sorted(VALID_STATUSES)})"
        )

    # Required H2 sections
    for sec_name in REQUIRED_SECTIONS:
        sec_key = _norm_heading(sec_name)
        if sec_key not in sections:
            errors.append(f"missing required section '## {sec_name}'")
            continue
        sec_body = sections[sec_key][1].strip()
        if not sec_body or is_placeholder(sec_body):
            errors.append(f"section '## {sec_name}' is empty or contains placeholder text")

    # Remaining frontier allowed ONLY while status: draft
    if _norm_heading("Remaining frontier") in sections and status == "ready":
        errors.append(
            "section '## Remaining frontier' is only allowed while status: draft (remove before status: ready)"
        )

    # Constraints & boundaries specifics
    envelope = parse_budget_envelope(intent_path)
    constraints_entry = sections.get(_norm_heading("Constraints & boundaries"))
    if constraints_entry is not None:
        cbody = constraints_entry[1]
        for req_sub in ("Must not", "Scope & non-goals"):
            val = _extract_field_block(cbody, req_sub)
            if val is None or is_placeholder(val):
                errors.append(
                    f"Constraints & boundaries: missing or placeholder '{req_sub}:'"
                )
        errors.extend(envelope["errors"])

    # Settled decisions (optional)
    sd_entry = sections.get(_norm_heading("Settled decisions"))
    if sd_entry is not None:
        _validate_settled_decisions(sd_entry[1], errors)

    # Assumptions & reopen triggers (optional)
    assump_entry = sections.get(_norm_heading("Assumptions & reopen triggers"))
    if assump_entry is not None:
        _validate_assumptions(assump_entry[1], errors)

    # Open questions (optional)
    oq_entry = sections.get(_norm_heading("Open questions"))
    if oq_entry is not None:
        _validate_open_questions(oq_entry[1], status, errors)

    # Backticked repo & media paths
    _check_backticked_paths(text, intent_path, require_media, errors, warnings)

    # Vague unbound qualifiers check
    has_scenarios = (
        _norm_heading("Concrete viewer scenarios") in sections
        and bool(sections[_norm_heading("Concrete viewer scenarios")][1].strip())
    )
    if not has_scenarios:
        found_vague: list[str] = []
        for check_sec in ("Purpose & viewer effect", "Subject & visual truth"):
            entry = sections.get(_norm_heading(check_sec))
            if entry is None:
                continue
            body_clean = _strip_fenced_blocks(entry[1])
            for label, pat in VAGUE_QUALIFIER_PATTERNS:
                if pat.search(body_clean) and label not in found_vague:
                    found_vague.append(label)
        if found_vague:
            warnings.append(
                "vague unbound qualifier(s) in Purpose/Subject without "
                f"'## Concrete viewer scenarios': {', '.join(found_vague)}"
            )

    return {
        "ok": len(errors) == 0,
        "file_found": True,
        "path": str(intent_path),
        "status": status,
        "title": title,
        "budget_envelope": {
            "autonomy_mode": envelope["autonomy_mode"],
            "draft_cap": envelope["draft_cap"],
            "final_cap": envelope["final_cap"],
            "max_auto_retries": envelope["max_auto_retries"],
        },
        "errors": errors,
        "warnings": warnings,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a Video Intent V1 document (campaigns/<slug>/intent.md)."
    )
    parser.add_argument(
        "target",
        help="Path to campaign directory or intent.md file.",
    )
    parser.add_argument(
        "--require-media",
        action="store_true",
        help="Treat missing media/references/... paths as errors instead of warnings.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Emit validation report as JSON.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    report = validate_intent(args.target, require_media=args.require_media)

    if args.as_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        if not report["file_found"]:
            print(f"ERROR: {report['errors'][0]}", file=sys.stderr)
            return 2

        state = "OK" if report["ok"] else "FAIL"
        env = report["budget_envelope"] or {}
        print(
            f"[{state}] {report['path']} "
            f"(status={report['status']}, mode={env.get('autonomy_mode')}, "
            f"draft_cap={env.get('draft_cap')}, final_cap={env.get('final_cap')}, "
            f"max_retries={env.get('max_auto_retries')})"
        )
        for w in report["warnings"]:
            print(f"  WARN: {w}")
        for e in report["errors"]:
            print(f"  ERROR: {e}")

    if not report["file_found"]:
        return 2
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
