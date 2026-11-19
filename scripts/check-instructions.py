#!/usr/bin/env python3
"""Validate AGENTS.md, Codex config sync, typed roles, and skill contracts."""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import importlib.util
import json
import re
import tomllib
import urllib.parse
from pathlib import Path
from typing import Any

REQUIRED_ROLE_KEYS = ("name", "description", "class", "output_schema", "instructions")
DECISION_SKILL_MAX_LINES = 300


def _load_check_docs():
    mod_path = Path(__file__).resolve().with_name("check-docs.py")
    spec = importlib.util.spec_from_file_location("check_docs", mod_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load sibling module: {mod_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_CHECK_DOCS = _load_check_docs()


def _strip_inline_comment(raw: str) -> str:
    """Remove unquoted trailing `# comment` from a YAML scalar."""
    in_single = False
    in_double = False
    escaped = False
    for idx, ch in enumerate(raw):
        if escaped:
            escaped = False
            continue
        if ch == "\\" and in_double:
            escaped = True
            continue
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double and (idx == 0 or raw[idx - 1].isspace()):
            return raw[:idx].rstrip()
    return raw.rstrip()


def _parse_yaml_scalar(raw: str) -> Any:
    val = _strip_inline_comment(raw.strip())
    if not val:
        return ""
    if (val.startswith('"') and val.endswith('"') and len(val) >= 2) or (
        val.startswith("'") and val.endswith("'") and len(val) >= 2
    ):
        quote = val[0]
        inner = val[1:-1]
        if quote == '"':
            return (
                inner.replace('\\"', '"')
                .replace("\\n", "\n")
                .replace("\\t", "\t")
                .replace("\\\\", "\\")
            )
        return inner.replace("''", "'")
    low = val.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    if low in ("null", "~"):
        return None
    if re.match(r"^-?\d+$", val):
        return int(val)
    if re.match(r"^-?\d+\.\d+$", val):
        return float(val)
    return val


def parse_simple_yaml(text: str) -> dict[str, Any]:
    """Parse a clean subset of YAML (nested dicts, lists, block scalars) using stdlib only."""
    lines = text.splitlines()
    root: dict[str, Any] = {}
    # Stack of (indent, container_dict)
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]

    idx = 0
    n = len(lines)
    while idx < n:
        line = lines[idx]
        if not line.strip() or line.lstrip().startswith("#"):
            idx += 1
            continue

        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()

        # Skip YAML list entries belonging to the parent key (handled below if preceded by key:)
        if stripped.startswith("- "):
            idx += 1
            continue

        if ":" not in stripped:
            raise ValueError(f"invalid YAML line {idx + 1}: {stripped!r}")

        key_part, _, rest_part = stripped.partition(":")
        key = key_part.strip().strip("\"'")
        if not key:
            raise ValueError(f"empty YAML key on line {idx + 1}")
        rest = rest_part.strip()

        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()
        target = stack[-1][1]

        # Block scalar (|, >)
        if rest in ("|", "|-", "|+", ">", ">-", ">+"):
            fold = rest.startswith(">")
            block_lines: list[str] = []
            idx += 1
            block_indent: int | None = None
            while idx < n:
                bline = lines[idx]
                if not bline.strip():
                    block_lines.append("")
                    idx += 1
                    continue
                bindent = len(bline) - len(bline.lstrip(" "))
                if bindent <= indent:
                    break
                if block_indent is None:
                    block_indent = bindent
                block_lines.append(bline[min(block_indent, bindent) :])
                idx += 1
            if fold:
                target[key] = " ".join(s.strip() for s in block_lines if s.strip()).strip()
            else:
                target[key] = "\n".join(block_lines).strip()
            continue

        # Empty value -> either nested mapping or YAML list on indented lines
        if rest == "" or rest.startswith("#"):
            # Look ahead to next non-blank, non-comment line
            look = idx + 1
            while look < n and (not lines[look].strip() or lines[look].lstrip().startswith("#")):
                look += 1
            if look < n:
                next_indent = len(lines[look]) - len(lines[look].lstrip(" "))
                next_stripped = lines[look].strip()
                if next_indent > indent and next_stripped.startswith("- "):
                    items: list[Any] = []
                    idx = look
                    while idx < n:
                        lline = lines[idx]
                        if not lline.strip() or lline.lstrip().startswith("#"):
                            idx += 1
                            continue
                        lindent = len(lline) - len(lline.lstrip(" "))
                        lstripped = lline.strip()
                        if lindent < next_indent or not lstripped.startswith("- "):
                            break
                        items.append(_parse_yaml_scalar(lstripped[2:]))
                        idx += 1
                    target[key] = items
                    continue
                if next_indent > indent:
                    child: dict[str, Any] = {}
                    target[key] = child
                    stack.append((indent, child))
                    idx += 1
                    continue
            target[key] = ""
            idx += 1
            continue

        # Multi-line unquoted continuation (e.g., description folded across indented lines)
        val_lines = [rest]
        next_idx = idx + 1
        while next_idx < n:
            nline = lines[next_idx]
            if not nline.strip() or nline.lstrip().startswith("#"):
                break
            nindent = len(nline) - len(nline.lstrip(" "))
            nstripped = nline.strip()
            if nindent > indent and ":" not in nstripped and not nstripped.startswith("- "):
                val_lines.append(nstripped)
                next_idx += 1
            else:
                break
        if len(val_lines) > 1:
            target[key] = _parse_yaml_scalar(" ".join(val_lines))
            idx = next_idx
        else:
            target[key] = _parse_yaml_scalar(rest)
            idx += 1

    return root


def _extract_frontmatter(text: str) -> tuple[dict[str, Any] | None, str | None]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, "missing opening '---' YAML frontmatter delimiter"
    end_idx: int | None = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break
    if end_idx is None:
        return None, "missing closing '---' YAML frontmatter delimiter"
    fm_text = "\n".join(lines[1:end_idx])
    try:
        parsed = parse_simple_yaml(fm_text)
    except ValueError as exc:
        return None, f"malformed YAML frontmatter: {exc}"
    return parsed, None


def _find_nested_key(data: dict[str, Any], target_key: str) -> tuple[bool, Any]:
    if target_key in data:
        return True, data[target_key]
    for v in data.values():
        if isinstance(v, dict):
            found, val = _find_nested_key(v, target_key)
            if found:
                return True, val
    return False, None


def _load_toml(path: Path, label: str, errors: list[str]) -> dict[str, Any] | None:
    if not path.is_file():
        errors.append(f"missing required file: {label}")
        return None
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        errors.append(f"{label}: failed to parse TOML: {exc}")
        return None
    if not isinstance(data, dict):
        errors.append(f"{label}: TOML root must be a table")
        return None
    return data


def validate_instructions(repo_root: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checked = {
        "roles": 0,
        "skills": 0,
        "workflow_skills": 0,
        "decision_skills": 0,
    }

    # 1. Core files
    agents_md = repo_root / "AGENTS.md"
    if not agents_md.is_file() or not agents_md.read_text(encoding="utf-8").strip():
        errors.append("missing or empty required file: AGENTS.md")

    proj_toml = _load_toml(
        repo_root / ".agents" / "codex-project.toml",
        ".agents/codex-project.toml",
        errors,
    )
    codex_toml = _load_toml(
        repo_root / ".codex" / "config.toml",
        ".codex/config.toml",
        errors,
    )

    # 2. Config sync checks
    if proj_toml is not None and codex_toml is not None:
        p_ma = (proj_toml.get("features") or {}).get("multi_agent_v2")
        c_ma = (codex_toml.get("features") or {}).get("multi_agent_v2")
        if c_ma is None:
            errors.append(".codex/config.toml: missing 'features.multi_agent_v2'")
        elif c_ma != p_ma:
            errors.append(
                f"config mismatch: features.multi_agent_v2 is {c_ma!r} in .codex/config.toml "
                f"vs {p_ma!r} in .agents/codex-project.toml"
            )

        p_agents = proj_toml.get("agents") or {}
        c_agents = codex_toml.get("agents") or {}

        for key in ("enabled", "max_concurrent_threads_per_session"):
            pv = p_agents.get(key)
            cv = c_agents.get(key)
            if cv is None:
                errors.append(f".codex/config.toml: missing 'agents.{key}'")
            elif cv != pv:
                errors.append(
                    f"config mismatch: agents.{key} is {cv!r} in .codex/config.toml "
                    f"vs {pv!r} in .agents/codex-project.toml"
                )

        p_dev = proj_toml.get("developer_instructions")
        c_dev = codex_toml.get("developer_instructions")
        if isinstance(p_dev, str) and p_dev.strip():
            if not isinstance(c_dev, str) or c_dev.strip() != p_dev.strip():
                errors.append(
                    "config mismatch: 'developer_instructions' in .codex/config.toml "
                    "does not match .agents/codex-project.toml"
                )
        elif isinstance(c_dev, str) and c_dev.strip():
            errors.append(
                "config mismatch: 'developer_instructions' present in .codex/config.toml "
                "but missing in .agents/codex-project.toml"
            )

        mcp_hf = ((codex_toml.get("mcp_servers") or {}).get("higgsfield")) or {}
        mcp_url = mcp_hf.get("url") if isinstance(mcp_hf, dict) else None
        if not isinstance(mcp_url, str) or not mcp_url.strip():
            errors.append(".codex/config.toml: missing non-empty '[mcp_servers.higgsfield].url'")

    # 3. Validate .agents/roles/*.toml
    roles_dir = repo_root / ".agents" / "roles"
    role_classes_dir = repo_root / ".agents" / "role-classes"
    schema_anchor_cache: dict[Path, set[str]] = {}
    if not roles_dir.is_dir():
        errors.append("missing directory: .agents/roles")
    else:
        role_files = sorted(roles_dir.glob("*.toml"))
        if not role_files:
            errors.append(".agents/roles: no *.toml role definitions found")
        for rpath in role_files:
            checked["roles"] += 1
            rel = str(rpath.relative_to(repo_root))
            rdata = _load_toml(rpath, rel, errors)
            if rdata is None:
                continue
            for key in REQUIRED_ROLE_KEYS:
                val = rdata.get(key)
                if not isinstance(val, str) or not val.strip():
                    errors.append(f"{rel}: missing or empty required string key '{key}'")
            rname = rdata.get("name")
            if isinstance(rname, str) and rname.strip() != rpath.stem:
                errors.append(
                    f"{rel}: role name '{rname}' does not match filename stem '{rpath.stem}'"
                )
            rclass = rdata.get("class")
            if isinstance(rclass, str) and rclass.strip():
                class_doc = role_classes_dir / f"{rclass.strip()}.md"
                if not class_doc.is_file():
                    errors.append(
                        f"{rel}: role class '{rclass}' has no matching file "
                        f"'.agents/role-classes/{rclass}.md'"
                    )
            rschema = rdata.get("output_schema")
            if isinstance(rschema, str) and rschema.strip():
                raw_schema = rschema.strip()
                if "#" in raw_schema:
                    schema_file, schema_frag = raw_schema.split("#", 1)
                else:
                    schema_file, schema_frag = raw_schema, ""
                schema_file = schema_file.strip()
                if schema_file.endswith(".md"):
                    schema_path = (repo_root / schema_file).resolve()
                    if not schema_path.is_file():
                        errors.append(
                            f"{rel}: output_schema references missing file '{schema_file}'"
                        )
                    elif schema_frag.strip():
                        if schema_path not in schema_anchor_cache:
                            schema_anchor_cache[schema_path] = _CHECK_DOCS.extract_anchors(
                                schema_path
                            )
                        frag_norm = urllib.parse.unquote(schema_frag).strip().lower()
                        if frag_norm not in schema_anchor_cache[schema_path]:
                            errors.append(
                                f"{rel}: output_schema anchor '#{schema_frag}' not found in '{schema_file}'"
                            )

    # 4. Validate .agents/skills/<dir>/SKILL.md
    skills_dir = repo_root / ".agents" / "skills"
    if skills_dir.is_dir():
        skill_dirs = sorted(
            p for p in skills_dir.iterdir() if p.is_dir() and not p.name.startswith(".")
        )
        for sdir in skill_dirs:
            checked["skills"] += 1
            skill_md = sdir / "SKILL.md"
            rel_dir = str(sdir.relative_to(repo_root))
            if not skill_md.is_file():
                errors.append(f"{rel_dir}: missing required SKILL.md")
                continue

            text = skill_md.read_text(encoding="utf-8")
            rel_skill = str(skill_md.relative_to(repo_root))
            fm, fm_err = _extract_frontmatter(text)
            if fm_err is not None or fm is None:
                errors.append(f"{rel_skill}: {fm_err}")
                continue

            sname = fm.get("name")
            if not isinstance(sname, str) or sname.strip() != sdir.name:
                errors.append(
                    f"{rel_skill}: frontmatter 'name' ({sname!r}) must match directory name '{sdir.name}'"
                )

            sdesc = fm.get("description")
            if not isinstance(sdesc, str) or not sdesc.strip():
                errors.append(f"{rel_skill}: frontmatter 'description' must be non-empty")

            # Resolve kind (top-level or nested under metadata)
            raw_kind = fm.get("kind")
            if not raw_kind and isinstance(fm.get("metadata"), dict):
                raw_kind = fm["metadata"].get("kind")
            kind = str(raw_kind).strip().lower() if raw_kind else "decision"

            # Resolve disable-model-invocation flag
            raw_dmi = fm.get("disable-model-invocation")
            if raw_dmi is None and isinstance(fm.get("metadata"), dict):
                raw_dmi = fm["metadata"].get("disable-model-invocation")
            disable_model_invocation = raw_dmi is True

            openai_yaml = sdir / "agents" / "openai.yaml"
            oy_data: dict[str, Any] | None = None
            oy_exists = openai_yaml.is_file()
            if oy_exists:
                try:
                    oy_data = parse_simple_yaml(openai_yaml.read_text(encoding="utf-8"))
                except ValueError as exc:
                    errors.append(
                        f"{rel_dir}/agents/openai.yaml: failed to parse YAML: {exc}"
                    )

            allow_implicit_false = False
            if oy_data is not None:
                found_flag, flag_val = _find_nested_key(
                    oy_data, "allow_implicit_invocation"
                )
                allow_implicit_false = found_flag and flag_val is False

            if kind == "workflow":
                checked["workflow_skills"] += 1
                if not oy_exists:
                    errors.append(
                        f"{rel_skill}: workflow skill must have '{rel_dir}/agents/openai.yaml'"
                    )
                elif oy_data is not None and not allow_implicit_false:
                    _, flag_val = _find_nested_key(oy_data, "allow_implicit_invocation")
                    errors.append(
                        f"{rel_dir}/agents/openai.yaml: workflow skill must set "
                        f"'allow_implicit_invocation: false' (found {flag_val!r})"
                    )
            else:
                checked["decision_skills"] += 1
                line_count = len(text.splitlines())
                if line_count >= DECISION_SKILL_MAX_LINES:
                    errors.append(
                        f"{rel_skill}: decision skill has {line_count} lines "
                        f"(must be under {DECISION_SKILL_MAX_LINES} lines)"
                    )

            # Invocation-mode symmetry between SKILL.md and agents/openai.yaml
            if disable_model_invocation:
                if not oy_exists and kind != "workflow":
                    errors.append(
                        f"{rel_skill}: 'disable-model-invocation: true' requires "
                        f"'{rel_dir}/agents/openai.yaml' with 'allow_implicit_invocation: false'"
                    )
                elif oy_data is not None and not allow_implicit_false and kind != "workflow":
                    _, flag_val = _find_nested_key(oy_data, "allow_implicit_invocation")
                    errors.append(
                        f"{rel_dir}/agents/openai.yaml: 'disable-model-invocation: true' in SKILL.md "
                        f"requires 'allow_implicit_invocation: false' (found {flag_val!r})"
                    )
            elif allow_implicit_false:
                errors.append(
                    f"{rel_skill}: '{rel_dir}/agents/openai.yaml' sets "
                    "'allow_implicit_invocation: false' but SKILL.md omits "
                    "'disable-model-invocation: true'"
                )

            if oy_data is not None and not allow_implicit_false:
                for req_meta in ("display_name", "short_description"):
                    found_m, m_val = _find_nested_key(oy_data, req_meta)
                    if not found_m or not isinstance(m_val, str) or not m_val.strip():
                        errors.append(
                            f"{rel_dir}/agents/openai.yaml: model-invoked skill requires non-empty '{req_meta}'"
                        )

    return {
        "ok": len(errors) == 0,
        "repo_root": str(repo_root),
        "checked": checked,
        "warnings": warnings,
        "errors": errors,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate AGENTS.md, .codex/config.toml sync, .agents/roles, and .agents/skills."
    )
    parser.add_argument(
        "repo_root",
        nargs="?",
        default=".",
        help="Path to repository root (default: current directory).",
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
    root = Path(args.repo_root).resolve()
    if not root.is_dir():
        msg = f"repository root directory not found: {root}"
        if args.as_json:
            print(json.dumps({"ok": False, "error": msg}, indent=2))
        else:
            print(f"ERROR: {msg}", file=sys.stderr)
        return 2

    report = validate_instructions(root)
    if args.as_json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        state = "OK" if report["ok"] else "FAIL"
        chk = report["checked"]
        print(
            f"[{state}] instructions check ({root}): "
            f"roles={chk['roles']}, skills={chk['skills']} "
            f"(workflow={chk['workflow_skills']}, decision={chk['decision_skills']})"
        )
        for w in report["warnings"]:
            print(f"  WARN: {w}")
        for e in report["errors"]:
            print(f"  ERROR: {e}")

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
