"""Repository-level checks: instructions, docs links, campaign scaffolding, and example campaign."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
EXAMPLE_CAMPAIGN = REPO_ROOT / "campaigns" / "example-product-spot"
EXAMPLE_BRAND = REPO_ROOT / "brands" / "example-brand" / "brand.md"

FORBIDDEN_BINARY_EXTS = frozenset({".png", ".jpg", ".jpeg", ".mp4", ".mov", ".webm", ".wav", ".mp3"})
REQUIRED_NO_MUSIC_LINE = "NO MUSIC. NO BACKGROUND SCORE. Native diegetic sound only."


class TestRepoChecks(unittest.TestCase):
    def _run_py(self, script_name: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / script_name), *args],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_check_instructions_passes(self) -> None:
        proc = self._run_py("check-instructions.py", str(REPO_ROOT))
        self.assertEqual(
            proc.returncode,
            0,
            msg=f"check-instructions.py failed:\nstdout={proc.stdout}\nstderr={proc.stderr}",
        )
        self.assertIn("skills=11", proc.stdout)

    def test_all_eleven_skills_and_ad_craft_glossary_exist(self) -> None:
        expected_skills = (
            "idea-refine",
            "grilling",
            "ad-references",
            "ad-concepts",
            "ad-script",
            "ad-storyboard",
            "higgsfield-cli",
            "video-direction",
            "video-consistency",
            "video-qa",
            "video-assembly",
        )
        skills_root = REPO_ROOT / ".agents" / "skills"
        for name in expected_skills:
            skill_md = skills_root / name / "SKILL.md"
            self.assertTrue(skill_md.is_file(), msg=f"Missing skill: {skill_md}")

        glossary = REPO_ROOT / "docs" / "ad-craft-glossary.md"
        self.assertTrue(glossary.is_file(), "Missing docs/ad-craft-glossary.md")
        self.assertGreater(len(glossary.read_text(encoding="utf-8").strip()), 100)

    def test_check_docs_passes(self) -> None:
        proc = self._run_py("check-docs.py", str(REPO_ROOT))
        self.assertEqual(
            proc.returncode,
            0,
            msg=f"check-docs.py failed:\nstdout={proc.stdout}\nstderr={proc.stderr}",
        )

    def test_campaign_init_scaffolds_structure_and_guards_duplicates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            proc = self._run_py(
                "campaign_init.py",
                "--slug",
                "nordic-launch",
                "--brand",
                "example-brand",
                "--root",
                str(tmp),
            )
            self.assertEqual(
                proc.returncode,
                0,
                msg=f"campaign_init.py failed:\nstdout={proc.stdout}\nstderr={proc.stderr}",
            )

            created_dirs = list((tmp / "campaigns").glob("*-nordic-launch"))
            self.assertEqual(len(created_dirs), 1, msg=f"Unexpected dirs: {created_dirs}")
            camp_dir = created_dirs[0]

            for rel in (
                "prompts",
                "tasks",
                "qc",
                "media/references",
                "media/stills",
                "media/shots",
                "media/audio",
                "media/exports",
            ):
                self.assertTrue((camp_dir / rel).is_dir(), msg=f"Missing scaffold subdir: {rel}")

            intent_path = camp_dir / "intent.md"
            self.assertTrue(intent_path.is_file())
            intent_text = intent_path.read_text(encoding="utf-8")
            self.assertIn("status: draft", intent_text)
            self.assertIn("brands/example-brand/brand.md", intent_text)

            # Second invocation with identical slug/day must refuse overwrite
            dup_proc = self._run_py(
                "campaign_init.py",
                "--slug",
                "nordic-launch",
                "--root",
                str(tmp),
            )
            self.assertNotEqual(dup_proc.returncode, 0)

            # Invalid slug must return exit 2
            bad_proc = self._run_py(
                "campaign_init.py",
                "--slug",
                "../escape",
                "--root",
                str(tmp),
            )
            self.assertEqual(bad_proc.returncode, 2)

    def test_example_product_spot_end_to_end(self) -> None:
        self.assertTrue(EXAMPLE_BRAND.is_file(), "Missing brands/example-brand/brand.md")

        for rel in (
            "intent.md",
            "treatment.md",
            "script.md",
            "storyboard.md",
            "style-bible.md",
            "shotlist.json",
            "tasks.md",
            "prompts/s01_still_v1.txt",
            "prompts/s01_video_v1.txt",
            "prompts/s02_still_v1.txt",
            "prompts/s02_video_v1.txt",
            "prompts/s03_still_v1.txt",
            "prompts/s03_video_v1.txt",
            "tasks/T01-upload-references.md",
            "tasks/T02-generate-stills.md",
            "tasks/T03-pilot-s02-draft.md",
            "tasks/T04a-draft-s01.md",
            "tasks/T04b-draft-s03.md",
            "tasks/T05-music-and-assemble-draft.md",
            "tasks/T06-final-1080p-renders.md",
            "tasks/T07-assemble-master-and-delivery.md",
        ):
            self.assertTrue(
                (EXAMPLE_CAMPAIGN / rel).is_file(),
                msg=f"Missing example campaign file: {rel}",
            )

        # Verify workflow schema, style bible, and treatment contracts
        shotlist = json.loads((EXAMPLE_CAMPAIGN / "shotlist.json").read_text(encoding="utf-8"))
        for shot in shotlist["shots"]:
            self.assertTrue(shot["video"]["is_workflow"], msg=f"{shot['id']} must set is_workflow: true")
            self.assertEqual(shot["video"]["mode"], "omni_reference", msg=f"{shot['id']} must use omni_reference")

        style_text = (EXAMPLE_CAMPAIGN / "style-bible.md").read_text(encoding="utf-8")
        self.assertIn("status: ready", style_text)
        self.assertIn("## Negative Constraints & Anti-IP Phrasing", style_text)

        treatment_text = (EXAMPLE_CAMPAIGN / "treatment.md").read_text(encoding="utf-8")
        self.assertIn("## Audio & Music Architecture", treatment_text)

        # Verify canonical three-column script and continuity-locked storyboard sections
        script_text = (EXAMPLE_CAMPAIGN / "script.md").read_text(encoding="utf-8")
        for token in (
            "| Time | Video | Audio |",
            "## Read-aloud budget",
            "## Mute test",
            "Verdict: PASS",
            "[PAUSE ",
        ):
            self.assertIn(token, script_text, msg=f"Missing '{token}' in script.md")

        storyboard_text = (EXAMPLE_CAMPAIGN / "storyboard.md").read_text(encoding="utf-8")
        for token in (
            "## Continuity Lock",
            "### S01 |",
            "### S02 |",
            "### S03 |",
            "**Test-take check:**",
            "## Cut-by-cut continuity audit",
        ):
            self.assertIn(token, storyboard_text, msg=f"Missing '{token}' in storyboard.md")

        # Every video prompt must enforce native diegetic sound only
        for shot_id in ("s01", "s02", "s03"):
            lines = [
                ln.strip()
                for ln in (EXAMPLE_CAMPAIGN / "prompts" / f"{shot_id}_video_v1.txt")
                .read_text(encoding="utf-8")
                .splitlines()
                if ln.strip()
            ]
            self.assertEqual(
                lines[-1],
                REQUIRED_NO_MUSIC_LINE,
                msg=f"{shot_id}_video_v1.txt must end with diegetic-only directive",
            )

        # Zero committed binary media files in reference campaign
        binaries = [
            p
            for p in EXAMPLE_CAMPAIGN.rglob("*")
            if p.is_file() and p.suffix.lower() in FORBIDDEN_BINARY_EXTS
        ]
        self.assertEqual(binaries, [], msg=f"Unexpected binary files in example campaign: {binaries}")

        # Validators & budget status pass cleanly
        intent_proc = self._run_py("check-intent.py", str(EXAMPLE_CAMPAIGN), "--json")
        self.assertEqual(intent_proc.returncode, 0, msg=intent_proc.stdout + intent_proc.stderr)
        self.assertTrue(json.loads(intent_proc.stdout)["ok"])

        ledger_proc = self._run_py("check-ledger.py", str(EXAMPLE_CAMPAIGN), "--json")
        self.assertEqual(ledger_proc.returncode, 0, msg=ledger_proc.stdout + ledger_proc.stderr)
        self.assertTrue(json.loads(ledger_proc.stdout)["ok"])

        status_proc = self._run_py(
            "hf_guard.py", "status", "--campaign", str(EXAMPLE_CAMPAIGN), "--json"
        )
        self.assertEqual(status_proc.returncode, 0, msg=status_proc.stdout + status_proc.stderr)
        st = json.loads(status_proc.stdout)
        self.assertTrue(st["ok"])
        self.assertEqual(st["phases"]["draft"]["cap"], 140)
        self.assertEqual(st["phases"]["final"]["cap"], 260)


if __name__ == "__main__":
    unittest.main()
