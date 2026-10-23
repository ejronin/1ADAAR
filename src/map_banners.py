"""Explicitly approved, local-only WARDOGS map art for the Discord report.

Missing, unapproved or invalid artwork falls back to the existing official
community hero. No remote requests, user supplied paths or datamined files.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "docs" / "assets" / "map-banners"
MANIFEST = FOLDER / "manifest.json"
EXPECTED = {"Bakurani": "bakurani.webp", "Ozeti": "ozeti.webp",
            "Zestafona": "zestafona.webp"}


def banner_for_map(name: object) -> Path | None:
    if not isinstance(name, str):
        return None
    match = next((n for n in EXPECTED if n.casefold() == name.strip().casefold()), None)
    if match is None:
        return None
    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(manifest, dict) or manifest.get("schemaVersion") != 1:
        return None
    files = manifest.get("images")
    if not isinstance(files, dict) or files.get(match) != EXPECTED[match]:
        return None
    candidate = FOLDER / EXPECTED[match]
    if not candidate.is_file() or candidate.stat().st_size > 8_000_000:
        return None
    return candidate
