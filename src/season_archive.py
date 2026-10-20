"""Append-only, public, season-organized history from captured completed matches.

Preserves older records when the dashboard's 120-match window rolls over.
This is an archive of matches 1ADAAR *captured*, NOT a complete census of
every played match. Never persist raw WARCON payloads or literal SteamIDs.
"""
from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path
import re

from src.player_index import safe_name
from src.weekly import OFFICIAL_SEASONS, parse_utc, _season_list

HEX_KEY = re.compile(r"^[a-f0-9]{64}$")
MONTH = re.compile(r"^\d{4}-\d{2}$")
SEASON_KEY = re.compile(r"^[a-z0-9-]{1,64}$")
TOP_LIMIT = 120
MAX_PLAYERS = 120
MAX_AWARDS = 5
ALLOW_AWARD_KEYS = {"kills", "kd", "longest", "streak", "cash"}


def _count(value: object) -> int:
    if type(value) is not int or value < 0:
        raise ValueError("Invalid recorded count")
    return value


def _text(value: object, maximum: int = 70) -> str:
    if not isinstance(value, str):
        return ""
    return "".join(c for c in value if c.isprintable() and c not in "@`<>{}\\").strip()[:maximum]


def _public_copy(match: dict) -> dict:
    """Whitelist the already sanitized public schema; discard everything else."""
    if not isinstance(match, dict) or match.get("schemaVersion") != 2:
        raise ValueError("Archive only accepts version 2 public match records")
    ident = _count(match.get("id"))
    if ident == 0:
        raise ValueError("Invalid match number")
    started, ended = parse_utc(match["startedAt"]), parse_utc(match["endedAt"])
    if started > ended:
        raise ValueError("Match ends before it starts")
    scores = []
    for row in match.get("scores", [])[:6]:
        name = _text(row.get("name"), 40) if isinstance(row, dict) else ""
        score = row.get("score") if isinstance(row, dict) else None
        if not name or type(score) not in (int, float) or not (0 <= score < 1_000_000):
            raise ValueError("Invalid faction score")
        scores.append({"name": name, "score": score})
    if not scores or max(r["score"] for r in scores) <= 0:
        raise ValueError("Unfinished or abandoned match")
    players = []
    for row in match.get("players", [])[:MAX_PLAYERS]:
        if not isinstance(row, dict) or not HEX_KEY.fullmatch(str(row.get("key", ""))):
            raise ValueError("Player identity must be pseudonymous")
        name = safe_name(row.get("name"))
        if not name:
            continue
        item = {"key": row["key"], "name": name,
                "faction": _text(row.get("faction"), 30),
                "result": row.get("result") if row.get("result") in ("win", "loss", "draw") else ""}
        for key in ("kills", "deaths", "seconds", "cashDelta", "headshots", "longestM", "killStreak"):
            value = row.get(key)
            if key == "cashDelta" and type(value) is int:
                item[key] = value
            elif value is None and key in ("headshots", "longestM", "killStreak"):
                item[key] = None
            else:
                item[key] = _count(value)
        players.append(item)
    awards = []
    for row in match.get("awards", [])[:MAX_AWARDS]:
        if not isinstance(row, dict) or row.get("key") not in ALLOW_AWARD_KEYS:
            continue
        name = safe_name(row.get("name"))
        if name:
            awards.append({"key": row["key"], "label": _text(row.get("label"), 30),
                           "name": name, "value": _text(row.get("value"), 25)})
    out = {
        "schemaVersion": 2, "id": ident,
        "startedAt": started.isoformat().replace("+00:00", "Z"),
        "endedAt": ended.isoformat().replace("+00:00", "Z"),
        "durationSeconds": _count(match.get("durationSeconds")),
        "map": _text(match.get("map"), 55),
        "mode": _text(match.get("mode"), 90),
        "lighting": _text(match.get("lighting"), 50),
        "winner": _text(match.get("winner"), 35),
        "scores": scores, "peakPlayers": _count(match.get("peakPlayers")),
        "players": players, "awards": awards,
        "hasFeed": match.get("hasFeed") is True,
        "warconUrl": "",
    }
    # Strict source URL; no upstream arbitrary links or credentials.
    url = match.get("warconUrl")
    expected = f"https://console.warcon.app/s/e30a7ee9-7ea5-4633-882e-98d2e0c03342/matches/{ident}"
    if url and url != expected:
        raise ValueError("Unexpected WARCON match link")
    out["warconUrl"] = expected
    return out


def _season_for(ended, seasons):
    applicable = [s for s in seasons if s[2] <= ended]
    return applicable[-1][0] if applicable else None


def archive_captured_matches(directory: Path, matches: list[dict],
                             *, seasons=OFFICIAL_SEASONS) -> dict:
    """Safely add captures to per-season/month JSON files, without changing old matches.

    Returns count of records newly preserved. Existing data is never truncated
    to the 120-match website window. Exact duplicates are ignored; conflicting
    matches raise an error and never replace an earlier verified record.
    """
    if not isinstance(matches, list):
        raise ValueError("Expected match list")
    season_rows = _season_list(seasons)
    if not season_rows:
        raise ValueError("Official season boundaries missing")
    incoming = defaultdict(dict)
    for m in matches:
        cleaned = _public_copy(m)
        ended = parse_utc(cleaned["endedAt"])
        season = _season_for(ended, season_rows)
        if season is None:
            continue  # Earlier than the first known official season: do not guess
        key = (season, ended.strftime("%Y-%m"))
        previous = incoming[key].get(cleaned["id"])
        if previous is not None and previous != cleaned:
            raise ValueError("Conflicting duplicate match in incoming capture")
        incoming[key][cleaned["id"]] = cleaned

    to_write = {}
    changed = 0
    for (season, month), additions in incoming.items():
        if not SEASON_KEY.fullmatch(season) or not MONTH.fullmatch(month):
            raise ValueError("Invalid season or month")
        target = directory / season / f"{month}.json"
        if target.is_file():
            doc = json.loads(target.read_text(encoding="utf-8"))
            if doc.get("schemaVersion") != 1 or doc.get("seasonKey") != season or doc.get("month") != month:
                raise ValueError("Malformed existing archive shard")
            entries = doc.get("matches")
            if not isinstance(entries, list):
                raise ValueError("Malformed existing match list")
        else:
            entries = []
        by_id = {}
        for item in entries:
            clean_existing = _public_copy(item)
            if clean_existing["id"] in by_id:
                raise ValueError("Duplicate existing match ID")
            by_id[clean_existing["id"]] = clean_existing
        for ident, match in additions.items():
            if ident in by_id and by_id[ident] != match:
                raise ValueError("Existing saved match conflicts with new capture")
            if ident not in by_id:
                by_id[ident] = match
                changed += 1
        if len(by_id) != len(entries):
            to_write[target] = {
                "schemaVersion": 1, "source": "Completed matches captured by 1ADAAR from public WARCON data",
                "coverage": "captured-only", "seasonKey": season, "month": month,
                "matches": sorted(by_id.values(), key=lambda x: (x["endedAt"], x["id"]), reverse=True),
            }

    # Validate all before writing. Atomic per-file replacements; a later CI
    # failure can retry without duplicating or deleting archived matches.
    if to_write:
        from src.recap import atomic_write_json
        for path, doc in to_write.items():
            atomic_write_json(path, doc)
    return {"newMatches": changed, "changedFiles": len(to_write)}
