"""Integration tests for scripts/qa_media.py and scripts/assemble.sh using synthetic FFmpeg media."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
QA_SCRIPT = REPO_ROOT / "scripts" / "qa_media.py"
ASSEMBLE_SCRIPT = REPO_ROOT / "scripts" / "assemble.sh"

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def _ffmpeg(*args: str) -> None:
    proc = subprocess.run(
        ["ffmpeg", "-v", "error", "-y", *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed (rc={proc.returncode}): {proc.stderr}")


def _ffprobe_json(media_path: Path) -> dict:
    proc = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_format",
            "-show_streams",
            "-of",
            "json",
            str(media_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(proc.stdout)


@unittest.skipUnless(
    shutil.which("ffmpeg") and shutil.which("ffprobe"),
    "ffmpeg and ffprobe are required for media QA and assembly tests",
)
class TestQaAndAssemble(unittest.TestCase):
    def _run_qa(self, *args: str) -> tuple[int, dict, str]:
        proc = subprocess.run(
            [sys.executable, str(QA_SCRIPT), *args, "--json"],
            capture_output=True,
            text=True,
            check=False,
        )
        parsed = json.loads(proc.stdout) if proc.stdout.strip().startswith("{") else {}
        return proc.returncode, parsed, proc.stderr

    def test_good_clip_passes_and_writes_contact_sheet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            clip = tmp / "good.mp4"
            sheet = tmp / "good_sheet.png"

            _ffmpeg(
                "-f", "lavfi", "-i", "testsrc2=size=320x180:rate=24:duration=4",
                "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=4",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "ultrafast",
                "-c:a", "aac", "-b:a", "128k",
                str(clip),
            )

            rc, data, err = self._run_qa("clip", str(clip), "--sheet", str(sheet))
            self.assertEqual(rc, 0, msg=f"err={err}\ndata={data}")
            self.assertTrue(data["ok"])
            self.assertEqual(data["errors"], [])
            self.assertTrue(sheet.is_file())
            raw = sheet.read_bytes()
            self.assertGreater(len(raw), 100)
            self.assertTrue(raw.startswith(PNG_MAGIC))

    def test_black_gap_in_middle_fails_clip_qa(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            clip = tmp / "black_gap.mp4"

            _ffmpeg(
                "-f", "lavfi", "-i", "testsrc2=size=320x180:rate=24:duration=1.5",
                "-f", "lavfi", "-i", "color=c=black:s=320x180:r=24:d=1.0",
                "-f", "lavfi", "-i", "testsrc2=size=320x180:rate=24:duration=1.5",
                "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=4.0",
                "-filter_complex", "[0:v][1:v][2:v]concat=n=3:v=1:a=0[v]",
                "-map", "[v]", "-map", "3:a",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "ultrafast",
                "-c:a", "aac", "-b:a", "128k",
                str(clip),
            )

            rc, data, err = self._run_qa("clip", str(clip))
            self.assertEqual(rc, 1, msg=f"Expected black_gap failure, err={err}\ndata={data}")
            self.assertFalse(data["ok"])
            codes = {e["code"] for e in data.get("errors", [])}
            self.assertIn("black_gap", codes, msg=data)

    def test_frozen_tail_fails_clip_qa(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            clip = tmp / "frozen_tail.mp4"

            # 2.0s motion + 3.2s frozen tail exceeds default 3.0s frozen-tail ceiling
            _ffmpeg(
                "-f", "lavfi", "-i", "testsrc2=size=320x180:rate=24:duration=2.0",
                "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=5.2",
                "-vf", "tpad=stop_mode=clone:stop_duration=3.2",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "ultrafast",
                "-c:a", "aac", "-b:a", "128k",
                str(clip),
            )

            rc, data, err = self._run_qa("clip", str(clip))
            self.assertEqual(rc, 1, msg=f"Expected frozen_tail failure, err={err}\ndata={data}")
            self.assertFalse(data["ok"])
            codes = {e["code"] for e in data.get("errors", [])}
            self.assertIn("frozen_tail", codes, msg=data)

    def test_fully_static_clip_fails_clip_qa(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            clip = tmp / "fully_static.mp4"

            _ffmpeg(
                "-f", "lavfi", "-i", "color=c=0x446688:s=320x180:r=24:d=4.0",
                "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=4.0",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "ultrafast",
                "-c:a", "aac", "-b:a", "128k",
                str(clip),
            )

            rc, data, err = self._run_qa("clip", str(clip))
            self.assertEqual(rc, 1, msg=f"Expected fully_static_clip failure, err={err}\ndata={data}")
            self.assertFalse(data["ok"])
            codes = {e["code"] for e in data.get("errors", [])}
            self.assertIn("fully_static_clip", codes, msg=data)

    def test_two_second_hold_passes_clip_qa(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            clip = tmp / "closing_hold_2s.mp4"

            # 3.0s motion + 2.0s deliberate closing button hold stays under default 3.0s ceiling
            _ffmpeg(
                "-f", "lavfi", "-i", "testsrc2=size=320x180:rate=24:duration=3.0",
                "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=5.0",
                "-vf", "tpad=stop_mode=clone:stop_duration=2.0",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "ultrafast",
                "-c:a", "aac", "-b:a", "128k",
                str(clip),
            )

            rc, data, err = self._run_qa("clip", str(clip))
            self.assertEqual(rc, 0, msg=f"Expected 2.0s closing hold to pass, err={err}\ndata={data}")
            self.assertTrue(data["ok"])
            self.assertEqual(data["errors"], [])

    def test_voice_window_passes_for_4s_and_fails_for_4_95s(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            good_vo = tmp / "vo_4s.wav"
            long_vo = tmp / "vo_4_95s.wav"

            _ffmpeg(
                "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=4.0",
                str(good_vo),
            )
            _ffmpeg(
                "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=4.95",
                str(long_vo),
            )

            rc_ok, data_ok, err_ok = self._run_qa("voice", str(good_vo), "--window", "5")
            self.assertEqual(rc_ok, 0, msg=f"err={err_ok}\ndata={data_ok}")
            self.assertTrue(data_ok["ok"])

            rc_bad, data_bad, err_bad = self._run_qa("voice", str(long_vo), "--window", "5")
            self.assertEqual(rc_bad, 1, msg=f"err={err_bad}\ndata={data_bad}")
            self.assertFalse(data_bad["ok"])
            codes = {e["code"] for e in data_bad.get("errors", [])}
            self.assertIn("voice_too_long", codes, msg=data_bad)

    def test_assemble_end_to_end_and_render_qa(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            clip1 = tmp / "clip1.mp4"
            clip2 = tmp / "clip2.mp4"
            music = tmp / "music.wav"
            master = tmp / "exports" / "master.mp4"
            stems_dir = tmp / "exports" / "stems"
            sheet = tmp / "exports" / "master_sheet.png"

            _ffmpeg(
                "-f", "lavfi", "-i", "testsrc2=size=320x180:rate=24:duration=3",
                "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=3",
                "-af", "volume=-18dB",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "ultrafast",
                "-c:a", "aac", "-b:a", "128k",
                str(clip1),
            )
            _ffmpeg(
                "-f", "lavfi", "-i", "testsrc2=size=320x180:rate=24:duration=3",
                "-f", "lavfi", "-i", "sine=frequency=523:sample_rate=48000:duration=3",
                "-af", "volume=-18dB",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "ultrafast",
                "-c:a", "aac", "-b:a", "128k",
                str(clip2),
            )
            _ffmpeg(
                "-f", "lavfi", "-i", "sine=frequency=220:sample_rate=48000:duration=6",
                "-af", "volume=-14dB",
                str(music),
            )

            proc = subprocess.run(
                [
                    "bash",
                    str(ASSEMBLE_SCRIPT),
                    "--clips",
                    f"{clip1},{clip2}",
                    "--music",
                    str(music),
                    "--music-vol",
                    "0.14",
                    "--out",
                    str(master),
                    "--stems-dir",
                    str(stems_dir),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(
                proc.returncode,
                0,
                msg=f"assemble.sh failed:\nstdout={proc.stdout}\nstderr={proc.stderr}",
            )
            self.assertTrue(master.is_file(), "master.mp4 was not created")
            self.assertTrue(stems_dir.is_dir(), "stems directory was not created")
            stem_files = [p for p in stems_dir.iterdir() if p.is_file()]
            self.assertGreater(len(stem_files), 0, "stems directory is empty")

            probe = _ffprobe_json(master)
            streams = probe.get("streams") or []
            vstream = next((s for s in streams if s.get("codec_type") == "video"), None)
            astream = next((s for s in streams if s.get("codec_type") == "audio"), None)
            self.assertIsNotNone(vstream, msg=probe)
            self.assertIsNotNone(astream, msg=probe)
            self.assertEqual(vstream["codec_name"], "h264")
            self.assertEqual(astream["codec_name"], "aac")

            rc, data, err = self._run_qa("render", str(master), "--sheet", str(sheet))
            self.assertEqual(rc, 0, msg=f"render QA failed: err={err}\ndata={data}")
            self.assertTrue(data["ok"], msg=data)
            self.assertEqual(data["errors"], [])
            lufs = data["loudness"]["integrated_lufs"]
            self.assertIsNotNone(lufs)
            self.assertGreaterEqual(lufs, -16.0)
            self.assertLessEqual(lufs, -12.0)
            self.assertTrue(sheet.is_file())
            self.assertTrue(sheet.read_bytes().startswith(PNG_MAGIC))

    def test_assemble_manifest_autoloads_music_and_rejects_silent_audio(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            camp = tmp / "camp"
            shots_dir = camp / "media" / "shots"
            audio_dir = camp / "media" / "audio"
            shots_dir.mkdir(parents=True, exist_ok=True)
            audio_dir.mkdir(parents=True, exist_ok=True)

            clip1 = shots_dir / "s01.mp4"
            clip2 = shots_dir / "s02.mp4"
            music = audio_dir / "score.wav"
            silent_music = audio_dir / "silent_score.wav"

            # Video-only clips (-an) prove audible mix comes strictly from manifest music
            _ffmpeg(
                "-f", "lavfi", "-i", "testsrc2=size=320x180:rate=24:duration=3",
                "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "ultrafast",
                str(clip1),
            )
            _ffmpeg(
                "-f", "lavfi", "-i", "testsrc2=size=320x180:rate=24:duration=3",
                "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "ultrafast",
                str(clip2),
            )
            _ffmpeg(
                "-f", "lavfi", "-i", "sine=frequency=220:sample_rate=48000:duration=6",
                str(music),
            )
            _ffmpeg(
                "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000:d=6",
                str(silent_music),
            )

            manifest = camp / "shotlist.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "campaign": "autoload-test",
                        "shots": [
                            {"id": "s01", "duration_s": 3, "video": {"selected_take": "media/shots/s01.mp4"}},
                            {"id": "s02", "duration_s": 3, "video": {"selected_take": "media/shots/s02.mp4"}},
                        ],
                        "audio": {
                            "music": {
                                "enabled": True,
                                "selected_file": "media/audio/score.wav",
                            },
                            "voiceover": {
                                "enabled": False,
                                "tracks": [],
                            },
                        },
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

            master = camp / "media" / "exports" / "master.mp4"
            stems_dir = camp / "media" / "exports" / "stems"
            proc_ok = subprocess.run(
                [
                    "bash",
                    str(ASSEMBLE_SCRIPT),
                    "--campaign",
                    str(camp),
                    "--manifest",
                    str(manifest),
                    "--out",
                    str(master),
                    "--stems-dir",
                    str(stems_dir),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(
                proc_ok.returncode,
                0,
                msg=f"manifest autoload assemble failed:\nstdout={proc_ok.stdout}\nstderr={proc_ok.stderr}",
            )
            self.assertTrue(master.is_file())
            self.assertTrue((stems_dir / "music.wav").is_file(), "Expected autoloaded music.wav stem")

            rc_qa, qa_data, qa_err = self._run_qa("render", str(master))
            self.assertEqual(rc_qa, 0, msg=f"err={qa_err}\ndata={qa_data}")
            self.assertTrue(qa_data["ok"])
            self.assertIsNotNone(qa_data["loudness"]["integrated_lufs"])

            # Passing a completely silent --music track must fail loudly rather than injecting --allow-silent
            bad_master = camp / "media" / "exports" / "silent_fail.mp4"
            proc_bad = subprocess.run(
                [
                    "bash",
                    str(ASSEMBLE_SCRIPT),
                    "--clips",
                    f"{clip1},{clip2}",
                    "--music",
                    str(silent_music),
                    "--out",
                    str(bad_master),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(
                proc_bad.returncode,
                0,
                msg=f"Expected assemble.sh to fail loudly on silent --music track, got stdout={proc_bad.stdout}",
            )

    def test_assemble_animatic_from_stills_and_audio(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            tmp = Path(tmp_str)
            still1 = tmp / "s01.png"
            still2 = tmp / "s02.png"
            music = tmp / "music.wav"
            animatic_silent = tmp / "exports" / "animatic_silent.mp4"
            animatic_music = tmp / "exports" / "animatic_music.mp4"

            _ffmpeg(
                "-f", "lavfi", "-i", "color=c=0x8B5A2B:s=321x181:d=1",
                "-frames:v", "1", str(still1),
            )
            _ffmpeg(
                "-f", "lavfi", "-i", "color=c=0x5C6773:s=320x180:d=1",
                "-frames:v", "1", str(still2),
            )
            _ffmpeg(
                "-f", "lavfi", "-i", "sine=frequency=220:sample_rate=48000:duration=4",
                "-af", "volume=-14dB", str(music),
            )

            proc_silent = subprocess.run(
                [
                    "bash",
                    str(ASSEMBLE_SCRIPT),
                    "--animatic",
                    "--stills",
                    f"{still1}:2,{still2}:2",
                    "--out",
                    str(animatic_silent),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(
                proc_silent.returncode,
                0,
                msg=f"silent animatic failed:\nstdout={proc_silent.stdout}\nstderr={proc_silent.stderr}",
            )
            self.assertTrue(animatic_silent.is_file())

            proc_music = subprocess.run(
                [
                    "bash",
                    str(ASSEMBLE_SCRIPT),
                    "--animatic",
                    "--stills",
                    f"{still1}:2,{still2}:2",
                    "--music",
                    str(music),
                    "--out",
                    str(animatic_music),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(
                proc_music.returncode,
                0,
                msg=f"music animatic failed:\nstdout={proc_music.stdout}\nstderr={proc_music.stderr}",
            )
            self.assertTrue(animatic_music.is_file())
            probe = _ffprobe_json(animatic_music)
            dur = float(probe["format"]["duration"])
            self.assertGreaterEqual(dur, 3.5)
            self.assertLessEqual(dur, 4.5)

    def test_assemble_manifest_vo_only_does_not_swap_into_music(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_str:
            camp = Path(tmp_str)
            shots_dir = camp / "media" / "shots"
            audio_dir = camp / "media" / "audio"
            stems_dir = camp / "media" / "exports" / "stems"
            shots_dir.mkdir(parents=True)
            audio_dir.mkdir(parents=True)

            clip1 = shots_dir / "s01-t01.mp4"
            vo_file = audio_dir / "vo_full.wav"
            master = camp / "media" / "exports" / "master_vo.mp4"

            _ffmpeg(
                "-f", "lavfi", "-i", "testsrc2=size=320x180:rate=24:duration=4",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "ultrafast",
                str(clip1),
            )
            _ffmpeg(
                "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=4",
                "-af", "volume=-16dB", str(vo_file),
            )

            manifest = {
                "schema_version": 1,
                "campaign": "vo-only-manifest-test",
                "aspect_ratio": "16:9",
                "target_duration_s": 4,
                "fps_target": 24,
                "shots": [
                    {
                        "id": "s01",
                        "duration_s": 4,
                        "video": {"selected_take": "media/shots/s01-t01.mp4"},
                    }
                ],
                "audio": {
                    "music": {"enabled": False, "selected_file": None},
                    "voiceover": {"enabled": True, "selected_file": "media/audio/vo_full.wav"},
                },
            }
            manifest_path = camp / "shotlist.json"
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

            proc = subprocess.run(
                [
                    "bash",
                    str(ASSEMBLE_SCRIPT),
                    "--campaign",
                    str(camp),
                    "--manifest",
                    str(manifest_path),
                    "--out",
                    str(master),
                    "--stems-dir",
                    str(stems_dir),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(
                proc.returncode,
                0,
                msg=f"VO-only manifest assemble failed:\nstdout={proc.stdout}\nstderr={proc.stderr}",
            )
            self.assertTrue(master.is_file())
            self.assertTrue((stems_dir / "vo.wav").is_file(), "VO must be preserved in stems/vo.wav")
            self.assertFalse(
                (stems_dir / "music.wav").exists(),
                "VO-only manifest must NOT misassign VO into stems/music.wav",
            )


if __name__ == "__main__":
    unittest.main()
