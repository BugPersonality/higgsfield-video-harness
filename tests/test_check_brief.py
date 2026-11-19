"""Unit and CLI tests for scripts/check-brief.py."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "check-brief.py"
EXAMPLE_CAMPAIGN = REPO_ROOT / "campaigns" / "example-product-spot"


def make_valid_brief(
    *,
    status: str = "active",
    campaign_cap: str = "400 credits",
    lookbook_variants: str = "3",
    max_retries: str = "2",
    auto_open_dailies: str = "true",
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
            "- **Budget & round policy:**\n"
            f"  - Campaign cap: {campaign_cap}\n"
            f"  - Lookbook variants: {lookbook_variants}\n"
            f"  - Max auto-retries/asset: {max_retries}\n"
            f"  - Auto-open dailies: {auto_open_dailies}\n"
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
            "Settled meaning",
            (
                "### M1 — Natural daylight kitchen setting\n"
                "- **Binding:** hard\n"
                "- **Decision:** Shoot on a sunlit oak countertop with morning window key.\n"
                "- **Rejected:** Dark studio sweep.\n"
                "- **Why:** Warm domestic light matches the handmade ceramic brand truth."
            ),
        )
    )

    sections.append(
        (
            "Assumptions",
            (
                "- **A1 — Reference photo supplied:** Clean side-profile kettle photo exists — "
                "**Reopen if:** the photo lacks spout geometry detail."
            ),
        )
    )

    if open_questions_body is not None:
        sections.append(("Open questions", open_questions_body))

    lines = ["# Brief: Stoneware Kettle — Morning Pour 15s Spot", "", f"status: {status}", ""]
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


class TestCheckBrief(unittest.TestCase):
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

    def test_example_campaign_brief_passes(self) -> None:
        code, data = self._run(EXAMPLE_CAMPAIGN)
        self.assertEqual(code, 0, msg=f"Unexpected errors: {data.get('errors')}")
        self.assertTrue(data["ok"])
        self.assertEqual(data["status"], "active")
        env = data["budget_envelope"]
        self.assertEqual(env["campaign_cap"], 400)
        self.assertEqual(env["lookbook_variants"], 3)
        self.assertEqual(env["max_retries"], 2)
        self.assertIs(env["auto_open_dailies"], True)

    def test_valid_active_draft_and_done_briefs_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            active_path = Path(tmp) / "active_brief.md"
            active_path.write_text(make_valid_brief(status="active"), encoding="utf-8")
            code, data = self._run(active_path)
            self.assertEqual(code, 0, msg=data)
            self.assertTrue(data["ok"])
            self.assertEqual(data["status"], "active")

            draft_path = Path(tmp) / "draft_brief.md"
            draft_path.write_text(
                make_valid_brief(
                    status="draft",
                    auto_open_dailies="false",
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
            self.assertIs(data_d["budget_envelope"]["auto_open_dailies"], False)

            done_path = Path(tmp) / "done_brief.md"
            done_path.write_text(make_valid_brief(status="done"), encoding="utf-8")
            code_done, data_done = self._run(done_path)
            self.assertEqual(code_done, 0, msg=data_done)
            self.assertTrue(data_done["ok"])
            self.assertEqual(data_done["status"], "done")

    def test_rejects_missing_required_section(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "brief.md"
            path.write_text(
                make_valid_brief(omit_section="Success signal"),
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
            path = Path(tmp) / "brief.md"
            path.write_text(
                make_valid_brief(purpose_extra=" Lighting details TBD."),
                encoding="utf-8",
            )
            code, data = self._run(path)
            self.assertEqual(code, 1)
            self.assertFalse(data["ok"])
            self.assertTrue(
                any("placeholder" in err.lower() for err in data["errors"]),
                msg=data["errors"],
            )

    def test_rejects_requester_owned_open_question_at_active(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "brief.md"
            path.write_text(
                make_valid_brief(
                    status="active",
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

    def test_rejects_missing_budget_and_round_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "brief.md"
            path.write_text(
                make_valid_brief(include_budget=False),
                encoding="utf-8",
            )
            code, data = self._run(path)
            self.assertEqual(code, 1)
            self.assertFalse(data["ok"])
            self.assertTrue(
                any(
                    "budget" in err.lower() or "policy" in err.lower() or "cap" in err.lower()
                    for err in data["errors"]
                ),
                msg=data["errors"],
            )

    def test_rejects_invalid_lookbook_variants_and_auto_open_dailies(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            for bad_variants in ("0", "9"):
                path = Path(tmp) / f"brief_v_{bad_variants}.md"
                path.write_text(
                    make_valid_brief(lookbook_variants=bad_variants),
                    encoding="utf-8",
                )
                code, data = self._run(path)
                self.assertEqual(code, 1, msg=f"Expected failure for variants={bad_variants}: {data}")
                self.assertFalse(data["ok"])
                self.assertTrue(
                    any("lookbook" in err.lower() or "variant" in err.lower() for err in data["errors"]),
                    msg=data["errors"],
                )

            bad_bool_path = Path(tmp) / "brief_bad_auto_open.md"
            bad_bool_path.write_text(
                make_valid_brief(auto_open_dailies="maybe"),
                encoding="utf-8",
            )
            code_b, data_b = self._run(bad_bool_path)
            self.assertEqual(code_b, 1, msg=data_b)
            self.assertFalse(data_b["ok"])
            self.assertTrue(
                any("auto-open" in err.lower() or "dailies" in err.lower() for err in data_b["errors"]),
                msg=data_b["errors"],
            )

    def test_warns_on_unbound_qualifier_when_scenarios_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "brief.md"
            path.write_text(
                make_valid_brief(
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

    def test_ignores_backticked_slug_and_na_inside_code_spans(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "brief.md"
            path.write_text(
                make_valid_brief(
                    purpose_extra=(
                        " Output lives under `campaigns/<slug>/media/exports/master.mp4` "
                        "and uses `NA` as the brand code."
                    ),
                ),
                encoding="utf-8",
            )
            code, data = self._run(path)
            self.assertEqual(code, 0, msg=f"Backticked tokens should be ignored: {data}")
            self.assertTrue(data["ok"])
            self.assertEqual(data["errors"], [])

    def test_missing_file_returns_exit_code_2(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "does-not-exist" / "brief.md"
            code, data = self._run(missing)
            self.assertEqual(code, 2)
            self.assertFalse(data["ok"])

    def test_draft_brief_with_placeholders_passes_with_warnings_while_active_rejects(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            # 1) Freshly scaffolded draft brief from campaign_init.py contains <...> templates
            init_proc = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts" / "campaign_init.py"),
                    "--slug",
                    "draft-seed",
                    "--root",
                    str(tmp_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(
                init_proc.returncode,
                0,
                msg=f"campaign_init.py failed: {init_proc.stdout}\n{init_proc.stderr}",
            )
            created = list((tmp_path / "campaigns").glob("*-draft-seed"))
            self.assertEqual(len(created), 1)
            scaffold_brief = created[0] / "brief.md"

            code_sc, data_sc = self._run(scaffold_brief)
            self.assertEqual(
                code_sc,
                0,
                msg=f"Fresh scaffolded draft brief must pass with warnings: {data_sc}",
            )
            self.assertTrue(data_sc["ok"], msg=data_sc)
            self.assertEqual(data_sc["status"], "draft")
            self.assertEqual(data_sc["errors"], [])
            self.assertTrue(
                len(data_sc.get("warnings", [])) > 0,
                msg=f"Expected placeholder warnings on scaffolded draft brief: {data_sc}",
            )

            # 2) Explicit draft brief with <...> and TBD passes with warnings; active rejects it
            draft_tbd = tmp_path / "draft_tbd.md"
            draft_text = make_valid_brief(
                status="draft",
                purpose_extra=" Confirm <hero angle> and lighting details TBD.",
            )
            draft_tbd.write_text(draft_text, encoding="utf-8")
            code_d, data_d = self._run(draft_tbd)
            self.assertEqual(code_d, 0, msg=f"Draft brief with TBD/<...> should pass: {data_d}")
            self.assertTrue(data_d["ok"], msg=data_d)
            self.assertEqual(data_d["errors"], [])
            self.assertTrue(
                any("placeholder" in w.lower() for w in data_d.get("warnings", [])),
                msg=f"Expected placeholder warning on draft brief, got: {data_d}",
            )

            active_tbd = tmp_path / "active_tbd.md"
            active_tbd.write_text(
                draft_text.replace("status: draft", "status: active", 1),
                encoding="utf-8",
            )
            code_a, data_a = self._run(active_tbd)
            self.assertEqual(code_a, 1, msg=f"Active brief with TBD/<...> must fail: {data_a}")
            self.assertFalse(data_a["ok"], msg=data_a)
            self.assertTrue(
                any("placeholder" in e.lower() for e in data_a.get("errors", [])),
                msg=f"Expected placeholder error on active brief, got: {data_a}",
            )


if __name__ == "__main__":
    unittest.main()
