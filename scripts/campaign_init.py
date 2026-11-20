#!/usr/bin/env python3
"""Scaffold a new campaign directory with Direction Brief V1 (brief.md) and taste-log.md."""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import datetime
import json
import re
from pathlib import Path

SLUG_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$")

SUBDIRS = (
    "prompts",
    "qc",
    "media/references",
    "media/lookbook",
    "media/lookbook/characters",
    "media/lookbook/locations",
    "media/lookbook/props",
    "media/stills",
    "media/shots",
    "media/audio",
    "media/exports",
)


def _render_brief_template(slug: str, brand: str | None, has_brand_taste: bool) -> str:
    title = slug.replace("-", " ").replace("_", " ").strip().title()
    if brand:
        brand_lines = f"- **Brand reference:** `brands/{brand}/brand.md`\n"
        if has_brand_taste:
            brand_lines += f"- **Brand taste seed:** `brands/{brand}/taste.md`\n"
    else:
        brand_lines = (
            "- **Brand reference:** <optional path to brands/<name>/brand.md or describe brand truth here>\n"
        )
    return (
        f"# Brief: {title}\n"
        "\n"
        "status: draft\n"
        "\n"
        "## Purpose & viewer effect\n"
        "\n"
        "- **Viewer takeaway:** <What should the viewer feel, remember, and do after watching?>\n"
        "- **Target audience & channel:** <Who is watching and on which platform?>\n"
        "\n"
        "## Subject & visual truth\n"
        "\n"
        f"{brand_lines}"
        "- **Hero subject & invariants:** <Product, character, logo/label, material, or color truths that must never drift.>\n"
        "- **Reference media:** Place source photos under `media/references/` and list exact filenames here.\n"
        "\n"
        "## Format, audio & delivery\n"
        "\n"
        "- **Aspect ratio & duration:** <e.g. 16:9 or 9:16, 15s (3 shots x 5s)>\n"
        "- **Audio & voiceover:** <Spoken language, pronunciation notes, voice tone, diegetic sound, music mood.>\n"
        "- **Deliverables:** `media/exports/master.mp4` + `media/exports/stems/`\n"
        "\n"
        "## Constraints & boundaries\n"
        "\n"
        "- **Must not:** <Visual taboos, forbidden tropes, competitor references, text/logo distortions.>\n"
        "- **Scope & non-goals:** <What is explicitly out of scope for this campaign?>\n"
        "- **Budget & round policy:**\n"
        "  - Campaign cap: 400 credits\n"
        "  - Lookbook variants: 3\n"
        "  - Max auto-retries/asset: 2\n"
        "  - Auto-open dailies: true\n"
        "\n"
        "## Success signal\n"
        "\n"
        "- <Concrete observable criteria proving the finished spot achieves the intended viewer effect.>\n"
    )


def _render_taste_log_template(slug: str, brand: str | None, has_brand_taste: bool) -> str:
    title = slug.replace("-", " ").replace("_", " ").strip().title()
    seed_line = (
        f"Brand taste seed: `brands/{brand}/taste.md`\n"
        if brand and has_brand_taste
        else "Brand taste seed: none\n"
    )
    return (
        f"# Taste Log: {title}\n"
        "\n"
        f"{seed_line}"
        "\n"
        "Cumulative Director taste memory for this campaign. Append a new `### TL-<NN>` entry\n"
        "after each round's Dailies review using `Approved / LOCKED`, `More of`, `Change / Steer`,\n"
        "and `Never` bullets. Never revert to a ruled-out aesthetic.\n"
    )


def scaffold_campaign(
    *,
    slug: str,
    brand: str | None = None,
    date_str: str | None = None,
    root: Path | None = None,
) -> Path:
    if not SLUG_RE.match(slug):
        raise ValueError(
            f"invalid slug '{slug}' (use alphanumeric characters, hyphens, and underscores only)"
        )

    if date_str is None:
        resolved_date = datetime.date.today().isoformat()
    else:
        try:
            resolved_date = datetime.date.fromisoformat(date_str).isoformat()
        except ValueError as exc:
            raise ValueError(
                f"invalid --date '{date_str}' (expected YYYY-MM-DD)"
            ) from exc

    repo_root = (
        Path(root).resolve()
        if root is not None
        else Path(__file__).resolve().parent.parent
    )
    campaign_dir = repo_root / "campaigns" / f"{resolved_date}-{slug}"

    if campaign_dir.exists():
        raise FileExistsError(f"campaign directory already exists: {campaign_dir}")

    has_brand_taste = bool(
        brand and (repo_root / "brands" / brand / "taste.md").is_file()
    )

    campaign_dir.mkdir(parents=True, exist_ok=False)
    for rel in SUBDIRS:
        (campaign_dir / rel).mkdir(parents=True, exist_ok=True)

    brief_path = campaign_dir / "brief.md"
    brief_path.write_text(
        _render_brief_template(slug, brand, has_brand_taste), encoding="utf-8"
    )

    taste_log_path = campaign_dir / "taste-log.md"
    taste_log_path.write_text(
        _render_taste_log_template(slug, brand, has_brand_taste), encoding="utf-8"
    )
    return campaign_dir


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Scaffold a new campaign directory under campaigns/<YYYY-MM-DD>-<slug>/."
    )
    parser.add_argument(
        "--slug",
        required=True,
        help="Short URL-safe campaign identifier (e.g. summer-launch).",
    )
    parser.add_argument(
        "--brand",
        default=None,
        help="Optional brand folder name under brands/<name>/.",
    )
    parser.add_argument(
        "--date",
        default=None,
        help="Campaign date prefix in YYYY-MM-DD format (default: today).",
    )
    parser.add_argument(
        "--root",
        default=None,
        help="Repository root directory (default: parent of scripts/).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Emit created campaign paths as JSON.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        created = scaffold_campaign(
            slug=args.slug,
            brand=args.brand,
            date_str=args.date,
            root=Path(args.root) if args.root else None,
        )
    except ValueError as exc:
        if args.as_json:
            print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except FileExistsError as exc:
        if args.as_json:
            print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.as_json:
        print(
            json.dumps(
                {
                    "ok": True,
                    "campaign_dir": str(created),
                    "brief_path": str(created / "brief.md"),
                    "taste_log_path": str(created / "taste-log.md"),
                },
                indent=2,
            )
        )
    else:
        print(f"Created campaign scaffold: {created}")
        print(f"  Brief template:  {created / 'brief.md'}")
        print(f"  Taste log:       {created / 'taste-log.md'}")
        print(f"  References dir:  {created / 'media' / 'references'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
