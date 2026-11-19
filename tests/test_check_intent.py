"""Unit and CLI tests for scripts/check-intent.py."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "check-intent.py"
EXAMPLE_CAMPAIGN = REPO_ROOT / "campaigns" / "example-product-spot"


def make_valid_intent(
    *,
    status: str = "ready",
    autonomy_mode: str = "autonomous-draft",
    include_scenarios: bool = True,
    purpose_extra: str = "",
    extra_sections: str = "",
    include_budget: bool = True,
    omit_section: str | None = None,
    open_questions_body: str | None = None,
) -> str:
    budget_block = ""
    if include_budget:
        budget_block = (
            "- **Authority & budget envelope:**\n"
            f"  - Autonomy mode: {autonomy_mode}\n"
            "  - Draft cap: 120 credits\n"
            "  - Final cap: 240 credits\n"
            "  - Max auto-retries/shot: 2\n"
        )

    sections: list[tuple[str, str]] = [
        (
            "Purpose & viewer effect",
            f"Show a ceramic pour-over kettle pouring boiling water cleanly into a carafe.{purpose_extra}",
        ),
        (
            "Subject & visual truth",
            "Matte stoneware kettle in charcoal glaze with walnut handle, filmed on oak counter.",
        ),
        (
            "Format, audio & delivery",
            "15s 16:9 24fps spot, H.264/AAC master at -14 LUFS with native kettle pouring foley.",
        ),
        (
            "Constraints & boundaries",
            (
                "- **Must not:** Show plastic packaging, logos, or glossy studio sweeps.\n"
                f"{budget_block}"
                "- **Scope & non-goals:** Single 15s hero cut only; no 9:16 social variants."
            ),
        ),
        (
            "Success signal",
            "Pass qa_media.py clip and render checks at 24fps with natural liquid physics.",
        ),
    ]

    if include_scenarios:
        sections.append(
            (
                "Concrete viewer scenarios",
                "- **Muted autoplay:** Steam rises clearly from the spout against morning backlight within 2 seconds.",
            )
        )

    sections.append(
        (
            "Settled decisions",
            (
                "### I1 — Natural daylight kitchen setting\n"
                "- **Binding:** hard\n"
                "- **Decision:** Shoot on a sunlit oak countertop with morning window key.\n"
                "- **Rejected:** Dark studio sweep.\n"
                "- **Why:** Warm domestic light matches the handmade ceramic brand truth."
            ),
        )
    )

    sections.append(
        (
            "Assumptions & reopen triggers",
            (
                "- **A1 — Reference photo supplied:** Clean side-profile kettle photo exists — "
                "**Reopen if:** the photo lacks spout geometry detail."
            ),
        )
    )

    if open_questions_body is not None:
        sections.append(("Open questions", open_questions_body))

    lines = ["# Intent: Stoneware Kettle — Morning Pour 15s Spot", "", f"status: {status}", ""]
    for heading, body in sections:
        if omit_section and heading.lower() == omit_section.lower():
            continue
        lines.append(f"## {heading}")
        lines.append("")
        lines.append(body)
        lines.append("")
    if extra_sections:
        lines.append(extra_sections.strip())
        lines.append("")
    return "\n".join(lines)


class TestCheckIntent(unittest.TestCase):
    def _run(self, target: Path, *extra_args: str) -> tuple[int, dict]:
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), str(target), "--json", *extra_args],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertTrue(
            proc.stdout.strip(),
            f"Expected JSON on stdout, got stderr={proc.stderr!r}",
        )
        return proc.returncode, json.loads(proc.stdout)

    def test_example_campaign_intent_passes(self) -> None:
        code, data = self._run(EXAMPLE_CAMPAIGN)
        self.assertEqual(code, 0, msg=f"Unexpected errors: {data.get('errors')}")
        self.assertTrue(data["ok"])
        self.assertEqual(data["status"], "ready")
        env = data["budget_envelope"]
        self.assertEqual(env["autonomy_mode"], "autonomous-draft")
        self.assertEqual(env["draft_cap"], 140)
        self.assertEqual(env["final_cap"], 260)
        self.assertEqual(env["max_auto_retries"], 2)

    def test_valid_ready_and_draft_intents_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ready_path = Path(tmp) / "ready_intent.md"
            ready_path.write_text(make_valid_intent(status="ready"), encoding="utf-8")
            code, data = self._run(ready_path)
            self.assertEqual(code, 0, msg=data)
            self.assertTrue(data["ok"])
            self.assertEqual(data["status"], "ready")

            draft_path = Path(tmp) / "draft_intent.md"
            draft_path.write_text(
                make_valid_intent(
                    status="draft",
                    autonomy_mode="checkpointed",
                    extra_sections="## Remaining frontier\n\n- Confirm whether closing tagline appears on card.",
                    open_questions_body=(
                        "- **Q1 — Closing tagline:** Owner: requester | "
                        "Fallback: omit closing card | Reopen if: brand wants URL overlay."
                    ),
                ),
                encoding="utf-8",
            )
            code_d, data_d = self._run(draft_path)
            self.assertEqual(code_d, 0, msg=data_d)
            self.assertTrue(data_d["ok"])
            self.assertEqual(data_d["status"], "draft")
            self.assertEqual(data_d["budget_envelope"]["autonomy_mode"], "checkpointed")

    def test_rejects_missing_required_section(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "intent.md"
            path.write_text(
                make_valid_intent(omit_section="Success signal"),
                encoding="utf-8",
            )
            code, data = self._run(path)
            self.assertEqual(code, 1)
            self.assertFalse(data["ok"])
            self.assertTrue(
                any("Success signal" in err for err in data["errors"]),
                msg=data["errors"],
            )

    def test_rejects_placeholder_tbd(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "intent.md"
            path.write_text(
                make_valid_intent(purpose_extra=" Lighting details TBD."),
                encoding="utf-8",
            )
            code, data = self._run(path)
            self.assertEqual(code, 1)
            self.assertFalse(data["ok"])
            self.assertTrue(
                any("placeholder" in err.lower() for err in data["errors"]),
                msg=data["errors"],
            )

    def test_rejects_remaining_frontier_at_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "intent.md"
            path.write_text(
                make_valid_intent(
                    status="ready",
                    extra_sections="## Remaining frontier\n\n- Decide exact kettle color.",
                ),
                encoding="utf-8",
            )
            code, data = self._run(path)
            self.assertEqual(code, 1)
            self.assertFalse(data["ok"])
            self.assertTrue(
                any("Remaining frontier" in err for err in data["errors"]),
                msg=data["errors"],
            )

    def test_rejects_requester_owned_open_question_at_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "intent.md"
            path.write_text(
                make_valid_intent(
                    status="ready",
                    open_questions_body=(
                        "- **Q1 — Final color palette:** Owner: requester | "
                        "Fallback: matte charcoal | Reopen if: packaging changes."
                    ),
                ),
                encoding="utf-8",
            )
            code, data = self._run(path)
            self.assertEqual(code, 1)
            self.assertFalse(data["ok"])
            self.assertTrue(
                any("requester" in err.lower() for err in data["errors"]),
                msg=data["errors"],
            )

    def test_rejects_missing_budget_envelope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "intent.md"
            path.write_text(
                make_valid_intent(include_budget=False),
                encoding="utf-8",
            )
            code, data = self._run(path)
            self.assertEqual(code, 1)
            self.assertFalse(data["ok"])
            self.assertTrue(
                any(
                    "budget" in err.lower() or "autonomy" in err.lower() or "cap" in err.lower()
                    for err in data["errors"]
                ),
                msg=data["errors"],
            )

    def test_rejects_invalid_autonomy_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "intent.md"
            path.write_text(
                make_valid_intent(autonomy_mode="yolo-unlimited"),
                encoding="utf-8",
            )
            code, data = self._run(path)
            self.assertEqual(code, 1)
            self.assertFalse(data["ok"])
            self.assertTrue(
                any("autonomy" in err.lower() for err in data["errors"]),
                msg=data["errors"],
            )

    def test_warns_on_unbound_qualifier_when_scenarios_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "intent.md"
            path.write_text(
                make_valid_intent(
                    include_scenarios=False,
                    purpose_extra=" Deliver a cinematic premium look.",
                ),
                encoding="utf-8",
            )
            code, data = self._run(path)
            self.assertEqual(code, 0, msg=data)
            self.assertTrue(data["ok"])
            self.assertTrue(
                any(
                    "cinematic" in w.lower() or "premium" in w.lower() or "qualifier" in w.lower()
                    for w in data["warnings"]
                ),
                msg=f"Expected unbound qualifier warning, got warnings={data['warnings']!r}",
            )

    def test_missing_file_returns_exit_code_2(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "does-not-exist" / "intent.md"
            code, data = self._run(missing)
            self.assertEqual(code, 2)
            self.assertFalse(data["ok"])


if __name__ == "__main__":
    unittest.main()
