"""Unit and CLI tests for scripts/check-ledger.py."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "check-ledger.py"
EXAMPLE_CAMPAIGN = REPO_ROOT / "campaigns" / "example-product-spot"
EXAMPLE_BRAND = REPO_ROOT / "brands" / "example-brand"


def _copy_campaign_fixture(tmp_root: Path) -> Path:
    """Copy example campaign and brand into an isolated repo-shaped temp directory."""
    brand_dst = tmp_root / "brands" / "example-brand"
    brand_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(EXAMPLE_BRAND, brand_dst)

    camp_dst = tmp_root / "campaigns" / "example-product-spot"
    camp_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(EXAMPLE_CAMPAIGN, camp_dst)
    return camp_dst


def _write_packet(
    path: Path,
    task_id: str,
    title: str,
    depends_on: list[str],
    owners: list[str],
    locks: list[str] | None = None,
) -> None:
    dep_lines = "\n".join(f"- {item}" for item in depends_on)
    lock_lines = "\n".join(f"- {item}" for item in (locks or ["none"]))
    owner_lines = "\n".join(f"- `{item}`" for item in owners)
    path.write_text(
        f"# {task_id} — {title}\n\n"
        "## Outcome\n\n"
        f"Complete {title.lower()} within campaign quality and budget constraints.\n\n"
        "## Depends on\n\n"
        f"{dep_lines}\n\n"
        "## Sources\n\n"
        "- ../intent.md\n"
        "- ../shotlist.json\n\n"
        "## Provides\n\n"
        f"- Verified output for {task_id}.\n\n"
        "## Boundary\n\n"
        "Stay strictly within declared mutable owners and credit caps.\n\n"
        "## Mutable owners\n\n"
        f"{owner_lines}\n\n"
        "## Exclusive locks\n\n"
        f"{lock_lines}\n\n"
        "## Final validation\n\n"
        "- Confirm artifact passes deterministic QA and budget checks.\n\n"
        "## Reopen if\n\n"
        "Quality gate fails after bounded retries or budget cap is exceeded.\n",
        encoding="utf-8",
    )


class TestCheckLedger(unittest.TestCase):
    def _run(self, target: Path) -> tuple[int, dict, str]:
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), str(target), "--json"],
            capture_output=True,
            text=True,
            check=False,
        )
        combined = f"{proc.stdout}\n{proc.stderr}"
        parsed: dict = {}
        if proc.stdout.strip():
            try:
                parsed = json.loads(proc.stdout)
            except json.JSONDecodeError:
                parsed = {}
        return proc.returncode, parsed, combined

    def test_example_campaign_ledger_passes(self) -> None:
        code, data, combined = self._run(EXAMPLE_CAMPAIGN)
        self.assertEqual(code, 0, msg=f"Expected pass, got:\n{combined}")
        self.assertTrue(data["ok"], msg=data)
        self.assertEqual(data["errors"], [])
        self.assertEqual(data["task_count"], 8)
        self.assertEqual(data["budget"]["draft_estimated"], 85)
        self.assertEqual(data["budget"]["final_estimated"], 240)
        wave4 = next((w["tasks"] for w in data["waves"] if w["wave"] == 4), [])
        self.assertEqual(wave4, ["T04a", "T04b"])

    def test_example_shotlist_continuity_lock_and_test_take_check(self) -> None:
        shotlist = json.loads(
            (EXAMPLE_CAMPAIGN / "shotlist.json").read_text(encoding="utf-8")
        )
        lock = shotlist.get("continuity_lock")
        self.assertIsInstance(lock, dict)
        for key in ("product", "lighting_and_palette", "space_cast_axis"):
            self.assertIsInstance(lock.get(key), str)
            self.assertTrue(lock[key].strip(), msg=f"Empty continuity_lock.{key}")

        shots_by_id = {s["id"]: s for s in shotlist["shots"]}
        self.assertIsNone(shots_by_id["s01"]["test_take_check"])
        self.assertIsNone(shots_by_id["s03"]["test_take_check"])
        s02_check = shots_by_id["s02"]["test_take_check"]
        self.assertIsInstance(s02_check, dict)
        self.assertTrue(s02_check.get("risk", "").strip())
        self.assertTrue(s02_check.get("pass_check", "").strip())

    def test_accepts_ref_and_last_frame_anchors_and_ignores_disabled_audio_budget(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            camp = _copy_campaign_fixture(Path(tmp))
            shotlist_path = camp / "shotlist.json"
            shotlist = json.loads(shotlist_path.read_text(encoding="utf-8"))

            shotlist["shots"][0]["video"]["start_image_from"] = "ref_bag_front"
            shotlist["shots"][1]["video"]["end_image_from"] = "s01.last_frame"
            shotlist["audio"]["voiceover"]["enabled"] = False
            shotlist["audio"]["voiceover"]["estimated_credits"] = 999
            shotlist_path.write_text(json.dumps(shotlist, indent=2), encoding="utf-8")

            code, data, combined = self._run(camp)
            self.assertEqual(code, 0, msg=f"Expected pass for ref/last_frame & disabled audio:\n{combined}")
            self.assertTrue(data["ok"], msg=data)
            self.assertEqual(data["budget"]["draft_estimated"], 85)

    def test_detects_cycle_in_dag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            camp = _copy_campaign_fixture(Path(tmp))
            tasks_md = camp / "tasks.md"
            tasks_md.write_text(
                tasks_md.read_text(encoding="utf-8").replace(
                    "Depends on: none", "Depends on: T03", 1
                ),
                encoding="utf-8",
            )
            t01 = camp / "tasks" / "T01-upload-references.md"
            t01.write_text(
                t01.read_text(encoding="utf-8").replace(
                    "## Depends on\n\n- none", "## Depends on\n\n- T03", 1
                ),
                encoding="utf-8",
            )

            code, data, combined = self._run(camp)
            self.assertEqual(code, 1, msg=f"Expected failure on cycle:\n{combined}")
            errors_text = " ".join(data.get("errors", [])) if data else combined
            self.assertTrue(
                any(tok in errors_text.lower() for tok in ("cycle", "circular", "dag")),
                msg=f"Expected cycle diagnostic, got: {errors_text!r}",
            )

    def test_rejects_video_without_still_or_reference_prerequisite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            camp = _copy_campaign_fixture(Path(tmp))
            tasks_dir = camp / "tasks"
            for old in tasks_dir.glob("*.md"):
                old.unlink()

            (camp / "tasks.md").write_text(
                "# Tasks: Video Without Still Prereq\n\n"
                "status: ready\n"
                "Intent: intent.md\n"
                "Treatment: treatment.md\n"
                "Shotlist: shotlist.json\n"
                "Completion: Generate audio and video clip.\n"
                "Global constraints: Stay within Draft cap <= 140 credits.\n\n"
                "## Tasks\n\n"
                "- [ ] T01: Generate ambient music stem [audio]\n"
                "  Depends on: budget-envelope [effect:spend]\n"
                "  Packet: tasks/T01-audio.md\n\n"
                "- [ ] T02: Generate draft motion video for s01 [video]\n"
                "  Depends on: T01, budget-envelope [effect:spend]\n"
                "  Packet: tasks/T02-video.md\n",
                encoding="utf-8",
            )
            _write_packet(
                tasks_dir / "T01-audio.md",
                "T01",
                "Generate Ambient Music Stem",
                ["budget-envelope [effect:spend]"],
                ["media/audio/music-*"],
                ["`receipts.jsonl`"],
            )
            _write_packet(
                tasks_dir / "T02-video.md",
                "T02",
                "Generate Draft Video s01",
                ["T01", "budget-envelope [effect:spend]"],
                ["media/shots/s01-draft-*"],
                ["`receipts.jsonl`"],
            )

            code, data, combined = self._run(camp)
            self.assertEqual(
                code,
                1,
                msg=f"Expected failure when [video] lacks [still]/[reference]:\n{combined}",
            )
            errors_text = " ".join(data.get("errors", [])) if data else combined
            self.assertTrue(
                any(tok in errors_text.lower() for tok in ("still", "reference", "video", "depend")),
                msg=f"Expected video prerequisite diagnostic, got: {errors_text!r}",
            )

    def test_rejects_budget_sum_exceeding_draft_cap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            camp = _copy_campaign_fixture(Path(tmp))
            shotlist_path = camp / "shotlist.json"
            shotlist = json.loads(shotlist_path.read_text(encoding="utf-8"))
            # Push draft budget from 85 to 220 credits (> 140 Draft cap in intent.md)
            shotlist["shots"][0]["video"]["estimated_draft_credits"] = 150
            shotlist_path.write_text(json.dumps(shotlist, indent=2), encoding="utf-8")

            code, data, combined = self._run(camp)
            self.assertEqual(code, 1, msg=f"Expected budget cap failure:\n{combined}")
            errors_text = " ".join(data.get("errors", [])) if data else combined
            self.assertTrue(
                any(tok in errors_text.lower() for tok in ("draft", "cap", "budget", "credit")),
                msg=f"Expected budget diagnostic, got: {errors_text!r}",
            )

    def test_detects_packet_depends_on_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            camp = _copy_campaign_fixture(Path(tmp))
            t03 = camp / "tasks" / "T03-pilot-s02-draft.md"
            # tasks.md declares T02 [acceptance]; mutate packet to T01
            t03.write_text(
                t03.read_text(encoding="utf-8").replace(
                    "## Depends on\n\n- T02 [acceptance]", "## Depends on\n\n- T01", 1
                ),
                encoding="utf-8",
            )

            code, data, combined = self._run(camp)
            self.assertEqual(code, 1, msg=f"Expected packet mismatch failure:\n{combined}")
            errors_text = " ".join(data.get("errors", [])) if data else combined
            self.assertTrue(
                any(tok in errors_text.lower() for tok in ("depends", "mismatch", "t03")),
                msg=f"Expected Depends on mismatch diagnostic, got: {errors_text!r}",
            )

    def test_detects_overlapping_mutable_owners_in_same_wave(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            camp = _copy_campaign_fixture(Path(tmp))
            tasks_dir = camp / "tasks"
            for old in tasks_dir.glob("*.md"):
                old.unlink()

            (camp / "tasks.md").write_text(
                "# Tasks: Parallel Wave Overlap Test\n\n"
                "status: ready\n"
                "Intent: intent.md\n"
                "Treatment: treatment.md\n"
                "Shotlist: shotlist.json\n"
                "Completion: Generate reference uploads and parallel stills.\n"
                "Global constraints: Disjoint mutable owners in each wave.\n\n"
                "## Tasks\n\n"
                "- [ ] T01: Upload reference imagery [reference]\n"
                "  Depends on: none\n"
                "  Packet: tasks/T01-refs.md\n\n"
                "- [ ] T02: Generate still batch A [still]\n"
                "  Depends on: T01, budget-envelope [effect:spend]\n"
                "  Packet: tasks/T02-still-a.md\n\n"
                "- [ ] T03: Generate still batch B [still]\n"
                "  Depends on: T01, budget-envelope [effect:spend]\n"
                "  Packet: tasks/T03-still-b.md\n",
                encoding="utf-8",
            )
            _write_packet(
                tasks_dir / "T01-refs.md",
                "T01",
                "Upload Reference Imagery",
                ["none"],
                ["qc/T01-references.json"],
                ["`receipts.jsonl`"],
            )
            # Both T02 and T03 share Exclusive locks: receipts.jsonl; overlapping Mutable owners must STILL fail!
            _write_packet(
                tasks_dir / "T02-still-a.md",
                "T02",
                "Generate Still Batch A",
                ["T01", "budget-envelope [effect:spend]"],
                ["media/stills/s01-*", "qc/s01-still.json"],
                ["`receipts.jsonl`"],
            )
            _write_packet(
                tasks_dir / "T03-still-b.md",
                "T03",
                "Generate Still Batch B",
                ["T01", "budget-envelope [effect:spend]"],
                ["media/stills/s01-*", "qc/s02-still.json"],
                ["`receipts.jsonl`"],
            )

            code, data, combined = self._run(camp)
            self.assertEqual(
                code,
                1,
                msg=f"Expected overlapping mutable owner failure even with shared lock:\n{combined}",
            )
            errors_text = " ".join(data.get("errors", [])) if data else combined
            self.assertTrue(
                any(
                    tok in errors_text.lower()
                    for tok in ("owner", "overlap", "conflict", "disjoint", "wave")
                ),
                msg=f"Expected mutable owner overlap diagnostic, got: {errors_text!r}",
            )

    def test_rejects_malformed_continuity_lock_and_test_take_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            camp = _copy_campaign_fixture(Path(tmp))
            shotlist_path = camp / "shotlist.json"
            shotlist = json.loads(shotlist_path.read_text(encoding="utf-8"))
            shotlist["continuity_lock"] = {"product": "valid only"}
            shotlist["shots"][1]["test_take_check"] = {"risk": "TBD", "pass_check": ""}
            shotlist_path.write_text(json.dumps(shotlist, indent=2), encoding="utf-8")

            code, data, combined = self._run(camp)
            self.assertEqual(code, 1, msg=f"Expected continuity/test_take failure:\n{combined}")
            errors_text = " ".join(data.get("errors", [])) if data else combined
            self.assertIn("continuity_lock", errors_text)
            self.assertIn("test_take_check", errors_text)


if __name__ == "__main__":
    unittest.main()
