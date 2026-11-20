"""Unit and CLI tests for scripts/check-campaign.py."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "check-campaign.py"
EXAMPLE_CAMPAIGN = REPO_ROOT / "campaigns" / "example-product-spot"
EXAMPLE_BRAND = REPO_ROOT / "brands" / "example-brand"


def _copy_campaign_fixture(tmp_root: Path) -> Path:
    """Copy example campaign and brand into an isolated repo-shaped temp directory."""
    (tmp_root / "AGENTS.md").write_text("# Test Fixture Root\n", encoding="utf-8")
    brand_dst = tmp_root / "brands" / "example-brand"
    brand_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(EXAMPLE_BRAND, brand_dst)

    camp_dst = tmp_root / "campaigns" / "example-product-spot"
    camp_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(EXAMPLE_CAMPAIGN, camp_dst)
    return camp_dst


def _extract_total_estimated(data: dict) -> int | float | None:
    budget = data.get("budget") or {}
    if not isinstance(budget, dict):
        return None
    for key in (
        "total_estimated",
        "planned_total",
        "total_planned_credits",
        "estimated_total",
        "total",
    ):
        val = budget.get(key)
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            return val
    return None


class TestCheckCampaign(unittest.TestCase):
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

    def test_example_campaign_passes(self) -> None:
        code, data, combined = self._run(EXAMPLE_CAMPAIGN)
        self.assertEqual(code, 0, msg=f"Expected pass, got:\n{combined}")
        self.assertTrue(data["ok"], msg=data)
        self.assertEqual(data.get("errors", []), [])
        total = _extract_total_estimated(data)
        if total is not None:
            self.assertEqual(total, 355)

    def test_example_shotlist_lookbook_continuity_lock_and_test_take_check(self) -> None:
        shotlist = json.loads(
            (EXAMPLE_CAMPAIGN / "shotlist.json").read_text(encoding="utf-8")
        )
        lock = shotlist.get("continuity_lock")
        self.assertIsInstance(lock, dict)
        for key in ("product", "lighting_and_palette", "space_cast_axis"):
            self.assertIsInstance(lock.get(key), str)
            self.assertTrue(lock[key].strip(), msg=f"Empty continuity_lock.{key}")

        lookbook = shotlist.get("lookbook")
        self.assertIsInstance(lookbook, list)
        self.assertEqual(len(lookbook), 1)
        lb = lookbook[0]
        self.assertEqual(lb["id"], "lb_traveler_hand")
        self.assertEqual(lb["status"], "LOCKED")
        self.assertEqual(lb["approved_variant"], "B")
        self.assertIsNone(lb["approved_upload_id"])
        self.assertEqual(lb["estimated_credits"], 30)

        shots_by_id = {s["id"]: s for s in shotlist["shots"]}
        self.assertIsNone(shots_by_id["s01"]["test_take_check"])
        self.assertIsNone(shots_by_id["s03"]["test_take_check"])
        self.assertEqual(shots_by_id["s01"]["still"]["status"], "LOCKED")
        self.assertEqual(shots_by_id["s02"]["still"]["status"], "ITERATING")
        self.assertEqual(shots_by_id["s03"]["still"]["status"], "LOCKED")
        self.assertIn("selected_job_id", shotlist["audio"]["music"])
        self.assertIsNone(shotlist["audio"]["music"]["selected_job_id"])
        s02_check = shots_by_id["s02"]["test_take_check"]
        self.assertIsInstance(s02_check, dict)
        self.assertTrue(s02_check.get("risk", "").strip())
        self.assertTrue(s02_check.get("pass_check", "").strip())

    def test_detects_planned_spend_exceeding_campaign_cap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            camp = _copy_campaign_fixture(Path(tmp))
            shotlist_path = camp / "shotlist.json"
            shotlist = json.loads(shotlist_path.read_text(encoding="utf-8"))
            # Push planned spend from 355 to 475 (> 400 Campaign cap in brief.md)
            shotlist["shots"][0]["video"]["estimated_final_credits"] = 200
            shotlist_path.write_text(json.dumps(shotlist, indent=2), encoding="utf-8")

            code, data, combined = self._run(camp)
            self.assertEqual(code, 1, msg=f"Expected Campaign cap failure:\n{combined}")
            self.assertFalse(data.get("ok", True))
            errors_text = " ".join(data.get("errors", [])) if data else combined
            self.assertTrue(
                any(tok in errors_text.lower() for tok in ("cap", "budget", "credit", "400")),
                msg=f"Expected budget cap diagnostic, got: {errors_text!r}",
            )

    def test_disabled_audio_does_not_count_toward_campaign_cap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            camp = _copy_campaign_fixture(Path(tmp))
            shotlist_path = camp / "shotlist.json"
            shotlist = json.loads(shotlist_path.read_text(encoding="utf-8"))
            shotlist["audio"]["voiceover"]["enabled"] = False
            shotlist["audio"]["voiceover"]["estimated_credits"] = 999
            shotlist_path.write_text(json.dumps(shotlist, indent=2), encoding="utf-8")

            code, data, combined = self._run(camp)
            self.assertEqual(
                code,
                0,
                msg=f"Disabled audio should not count toward Campaign cap:\n{combined}",
            )
            self.assertTrue(data["ok"], msg=data)
            total = _extract_total_estimated(data)
            if total is not None:
                self.assertEqual(total, 355)

    def test_accepts_lookbook_ref_and_last_frame_anchors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            camp = _copy_campaign_fixture(Path(tmp))
            shotlist_path = camp / "shotlist.json"
            shotlist = json.loads(shotlist_path.read_text(encoding="utf-8"))
            shotlist["shots"][0]["video"]["start_image_from"] = "ref_bag_front"
            shotlist["shots"][1]["video"]["start_image_from"] = "lb_traveler_hand"
            shotlist["shots"][1]["video"]["end_image_from"] = "s01.last_frame"
            shotlist_path.write_text(json.dumps(shotlist, indent=2), encoding="utf-8")

            code, data, combined = self._run(camp)
            self.assertEqual(
                code,
                0,
                msg=f"Expected pass for lb_traveler_hand, ref_*, and s01.last_frame:\n{combined}",
            )
            self.assertTrue(data["ok"], msg=data)

            # Unknown anchor must fail
            shotlist["shots"][0]["video"]["start_image_from"] = "ref_does_not_exist"
            shotlist_path.write_text(json.dumps(shotlist, indent=2), encoding="utf-8")
            code_bad, data_bad, combined_bad = self._run(camp)
            self.assertEqual(
                code_bad,
                1,
                msg=f"Expected failure for unknown anchor:\n{combined_bad}",
            )
            self.assertFalse(data_bad.get("ok", True))

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

    def test_rejects_invalid_asset_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            camp = _copy_campaign_fixture(Path(tmp))
            shotlist_path = camp / "shotlist.json"
            shotlist = json.loads(shotlist_path.read_text(encoding="utf-8"))
            shotlist["shots"][0]["still"]["status"] = "BOGUS"
            shotlist_path.write_text(json.dumps(shotlist, indent=2), encoding="utf-8")

            code, data, combined = self._run(camp)
            self.assertEqual(code, 1, msg=f"Expected invalid status failure:\n{combined}")
            self.assertFalse(data.get("ok", True))
            errors_text = " ".join(data.get("errors", [])) if data else combined
            self.assertTrue(
                any(tok in errors_text.lower() for tok in ("bogus", "status")),
                msg=f"Expected invalid status diagnostic, got: {errors_text!r}",
            )

    def test_rejects_locked_lookbook_missing_approved_variant(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            camp = _copy_campaign_fixture(Path(tmp))
            shotlist_path = camp / "shotlist.json"
            shotlist = json.loads(shotlist_path.read_text(encoding="utf-8"))
            shotlist["lookbook"][0]["status"] = "LOCKED"
            shotlist["lookbook"][0]["approved_variant"] = None
            shotlist_path.write_text(json.dumps(shotlist, indent=2), encoding="utf-8")

            code, data, combined = self._run(camp)
            self.assertEqual(
                code,
                1,
                msg=f"Expected failure when LOCKED lookbook misses approved_variant:\n{combined}",
            )
            self.assertFalse(data.get("ok", True))
            errors_text = " ".join(data.get("errors", [])) if data else combined
            self.assertTrue(
                any(
                    tok in errors_text.lower()
                    for tok in ("approved_variant", "locked", "lookbook")
                ),
                msg=f"Expected approved_variant diagnostic, got: {errors_text!r}",
            )

    def test_rejects_malformed_taste_log_duplicate_and_empty_entry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            camp = _copy_campaign_fixture(Path(tmp))
            taste_path = camp / "taste-log.md"
            original = taste_path.read_text(encoding="utf-8")

            # Duplicate TL-01 entry
            taste_path.write_text(
                original
                + "\n### TL-01 (R2 — Duplicate Lookbook)\n\n"
                + "- **More of:** Cool morning daylight.\n",
                encoding="utf-8",
            )
            code_dup, data_dup, combined_dup = self._run(camp)
            self.assertEqual(
                code_dup,
                1,
                msg=f"Expected duplicate TL-01 failure:\n{combined_dup}",
            )
            self.assertFalse(data_dup.get("ok", True))
            err_dup = " ".join(data_dup.get("errors", [])) if data_dup else combined_dup
            self.assertTrue(
                any(tok in err_dup.lower() for tok in ("tl-01", "duplicate", "taste")),
                msg=f"Expected duplicate TL-01 diagnostic, got: {err_dup!r}",
            )

            # Empty TL-03 entry with no bullets
            taste_path.write_text(
                original + "\n### TL-03 (R4 — Draft Motion)\n\n",
                encoding="utf-8",
            )
            code_empty, data_empty, combined_empty = self._run(camp)
            self.assertEqual(
                code_empty,
                1,
                msg=f"Expected empty taste-log entry failure:\n{combined_empty}",
            )
            self.assertFalse(data_empty.get("ok", True))
            err_empty = (
                " ".join(data_empty.get("errors", [])) if data_empty else combined_empty
            )
            self.assertTrue(
                any(
                    tok in err_empty.lower()
                    for tok in ("tl-03", "empty", "bullet", "taste")
                ),
                msg=f"Expected empty taste-log diagnostic, got: {err_empty!r}",
            )

    def test_rejects_shots_duration_sum_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            camp = _copy_campaign_fixture(Path(tmp))
            shotlist_path = camp / "shotlist.json"
            shotlist = json.loads(shotlist_path.read_text(encoding="utf-8"))
            shotlist["target_duration_s"] = 30
            shotlist_path.write_text(json.dumps(shotlist, indent=2), encoding="utf-8")

            code, data, combined = self._run(camp)
            self.assertEqual(
                code,
                1,
                msg=f"Expected duration mismatch failure:\n{combined}",
            )
            self.assertFalse(data.get("ok", True))
            errors_text = " ".join(data.get("errors", [])) if data else combined
            self.assertTrue(
                any(tok in errors_text.lower() for tok in ("duration", "target_duration")),
                msg=f"Expected duration mismatch diagnostic, got: {errors_text!r}",
            )

    def test_rejects_cinematic_studio_video_4_0_non_workflow_or_i2v_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            camp = _copy_campaign_fixture(Path(tmp))
            shotlist_path = camp / "shotlist.json"
            base = json.loads(shotlist_path.read_text(encoding="utf-8"))

            # Case 1: is_workflow: false on cinematic_studio_video_4_0
            bad_wf = json.loads(json.dumps(base))
            bad_wf["shots"][0]["video"]["is_workflow"] = False
            shotlist_path.write_text(json.dumps(bad_wf, indent=2), encoding="utf-8")
            code1, data1, comb1 = self._run(camp)
            self.assertEqual(code1, 1, msg=f"Expected is_workflow=false failure:\n{comb1}")
            self.assertFalse(data1.get("ok", True))
            err1 = " ".join(data1.get("errors", [])) if data1 else comb1
            self.assertTrue(
                any(tok in err1.lower() for tok in ("is_workflow", "workflow", "cinematic_studio_video_4_0")),
                msg=f"Expected workflow diagnostic, got: {err1!r}",
            )

            # Case 2: mode: "i2v" on cinematic_studio_video_4_0
            bad_mode = json.loads(json.dumps(base))
            bad_mode["shots"][0]["video"]["is_workflow"] = True
            bad_mode["shots"][0]["video"]["mode"] = "i2v"
            shotlist_path.write_text(json.dumps(bad_mode, indent=2), encoding="utf-8")
            code2, data2, comb2 = self._run(camp)
            self.assertEqual(code2, 1, msg=f"Expected mode=i2v failure:\n{comb2}")
            self.assertFalse(data2.get("ok", True))
            err2 = " ".join(data2.get("errors", [])) if data2 else comb2
            self.assertTrue(
                any(tok in err2.lower() for tok in ("omni_reference", "i2v", "mode", "cinematic_studio_video_4_0")),
                msg=f"Expected mode diagnostic, got: {err2!r}",
            )

    def test_rejects_missing_or_null_credit_estimates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            camp = _copy_campaign_fixture(Path(tmp))
            shotlist_path = camp / "shotlist.json"
            base = json.loads(shotlist_path.read_text(encoding="utf-8"))

            mutations = [
                ("still.estimated_credits", lambda d: d["shots"][0]["still"].__setitem__("estimated_credits", None)),
                ("video.estimated_draft_credits", lambda d: d["shots"][0]["video"].pop("estimated_draft_credits")),
                ("video.estimated_final_credits", lambda d: d["shots"][0]["video"].__setitem__("estimated_final_credits", None)),
            ]
            for label, mutate in mutations:
                mutated = json.loads(json.dumps(base))
                mutate(mutated)
                shotlist_path.write_text(json.dumps(mutated, indent=2), encoding="utf-8")
                code, data, comb = self._run(camp)
                self.assertEqual(
                    code,
                    1,
                    msg=f"Expected missing/null {label} to fail (not default to 0):\n{comb}",
                )
                self.assertFalse(data.get("ok", True))
                err = " ".join(data.get("errors", [])) if data else comb
                self.assertTrue(
                    any(tok in err.lower() for tok in ("estimated", "credit", label.split(".")[-1])),
                    msg=f"Expected estimate diagnostic for {label}, got: {err!r}",
                )

    def test_rejects_enabled_audio_music_without_valid_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            camp = _copy_campaign_fixture(Path(tmp))
            shotlist_path = camp / "shotlist.json"
            base = json.loads(shotlist_path.read_text(encoding="utf-8"))

            # Missing status on enabled audio.music
            missing_st = json.loads(json.dumps(base))
            missing_st["audio"]["music"].pop("status", None)
            shotlist_path.write_text(json.dumps(missing_st, indent=2), encoding="utf-8")
            code1, data1, comb1 = self._run(camp)
            self.assertEqual(code1, 1, msg=f"Expected missing music.status failure:\n{comb1}")
            self.assertFalse(data1.get("ok", True))
            err1 = " ".join(data1.get("errors", [])) if data1 else comb1
            self.assertTrue(
                any(tok in err1.lower() for tok in ("status", "music", "audio")),
                msg=f"Expected audio.music status diagnostic, got: {err1!r}",
            )

            # Invalid status value on enabled audio.music
            bad_st = json.loads(json.dumps(base))
            bad_st["audio"]["music"]["status"] = "UNKNOWN"
            shotlist_path.write_text(json.dumps(bad_st, indent=2), encoding="utf-8")
            code2, data2, comb2 = self._run(camp)
            self.assertEqual(code2, 1, msg=f"Expected invalid music.status failure:\n{comb2}")
            self.assertFalse(data2.get("ok", True))
            err2 = " ".join(data2.get("errors", [])) if data2 else comb2
            self.assertTrue(
                any(tok in err2.lower() for tok in ("status", "unknown", "music")),
                msg=f"Expected invalid audio.music status diagnostic, got: {err2!r}",
            )


    def test_enforces_reference_budgets_cel_caps_and_photocopy_guard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            camp = _copy_campaign_fixture(Path(tmp))
            shotlist_path = camp / "shotlist.json"
            base = json.loads(shotlist_path.read_text(encoding="utf-8"))

            extra_refs = [
                {"id": f"ref_extra_{i}", "kind": "prop", "local_path": f"media/references/e{i}.png", "upload_id": None}
                for i in range(1, 11)
            ]
            base["references"].extend(extra_refs)
            extra_ids = [r["id"] for r in extra_refs]

            warn_mut = json.loads(json.dumps(base))
            warn_mut["shots"][0]["still"]["references"] = extra_ids[:7]
            warn_mut["shots"][0]["video"]["image_references"] = extra_ids[:5]
            warn_mut["shots"][1]["video"]["model"] = "wan3_0"
            warn_mut["shots"][1]["video"]["is_workflow"] = False
            warn_mut["shots"][1]["video"]["start_image_from"] = "s02.still"
            warn_mut["shots"][1]["video"]["image_references"] = ["ref_bag_front"]
            warn_mut["shots"][2]["video"]["start_image_from"] = "s02.last_frame"
            warn_mut["shots"][2]["video"]["image_references"] = []
            shotlist_path.write_text(json.dumps(warn_mut, indent=2), encoding="utf-8")

            code_w, data_w, comb_w = self._run(camp)
            self.assertEqual(code_w, 0, msg=f"Advisory spatial warnings must not fail exit code:\n{comb_w}")
            self.assertTrue(data_w.get("ok"), msg=data_w)
            warns_text = " ".join(data_w.get("warnings", []))
            self.assertIn("optimal R3 still budget", warns_text, msg=data_w)
            self.assertIn("optimal R4/R5 video budget", warns_text, msg=data_w)
            self.assertIn("wan3_0", warns_text, msg=data_w)
            self.assertIn("photocopy", warns_text, msg=data_w)

            err_mut = json.loads(json.dumps(base))
            err_mut["shots"][0]["still"]["model"] = "flux_kontext"
            err_mut["shots"][0]["still"]["references"] = extra_ids[:5]
            err_mut["shots"][1]["video"]["model"] = "kling4_0"
            err_mut["shots"][1]["video"]["is_workflow"] = False
            err_mut["shots"][1]["video"]["start_image_from"] = "s02.still"
            err_mut["shots"][1]["video"]["image_references"] = extra_ids[:10]
            shotlist_path.write_text(json.dumps(err_mut, indent=2), encoding="utf-8")

            code_e, data_e, comb_e = self._run(camp)
            self.assertEqual(code_e, 1, msg=f"Hard CEL cap violations must fail:\n{comb_e}")
            self.assertFalse(data_e.get("ok", True))
            err_text = " ".join(data_e.get("errors", []))
            self.assertIn("flux_kontext", err_text, msg=data_e)
            self.assertIn("kling4_0", err_text, msg=data_e)


if __name__ == "__main__":
    unittest.main()
