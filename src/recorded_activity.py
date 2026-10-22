"""Public, server-wide saved-match activity with honest coverage.

Counts when each *completed captured match* began in US Eastern local time.
This is NEVER personal activity, session playtime, or total server utilization.
No private identifiers, user-specific schedules, SteamIDs, or role XP are used.
"""
from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from src.recap import atomic_write_json, read_json
from src.season_archive import MONTH, SEASON_KEY, _public_copy, _season_for
from src.weekly import OFFICIAL_SEASONS, _season_list, parse_utc

EASTERN = ZoneInfo("America/New_York")
TIMEZONE = "America/New_York"
METER = "Captured completed-match starts"


def _empty():
    return {"count": 0, "byWeekdayAndHour": [[0 for _ in range(24)] for _ in range(7)],
            "firstMatchStartedAt": None, "lastMatchStartedAt": None}


def _add(stats: dict, started: datetime) -> None:
    local = started.astimezone(EASTERN)
    stats["count"] += 1
    stats["byWeekdayAndHour"][local.weekday()][local.hour] += 1
    timestamp = started.isoformat().replace("+00:00", "Z")
    if stats["firstMatchStartedAt"] is None or timestamp < stats["firstMatchStartedAt"]:
        stats["firstMatchStartedAt"] = timestamp
    if stats["lastMatchStartedAt"] is None or timestamp > stats["lastMatchStartedAt"]:
        stats["lastMatchStartedAt"] = timestamp


def build_recorded_activity(archive: Path, output: Path) -> dict:
    """Rebuild solely from the sanitized completed-match archive; no API calls."""
    seasons = _season_list(OFFICIAL_SEASONS)
    totals = {"all": _empty()}
    names = {"all": "All saved seasons"}
    for key, name, _ in seasons:
        totals[key] = _empty()
        names[key] = name
    seen = set()
    for file in sorted(archive.glob("*/*.json")):
        season_key, month = file.parent.name, file.stem
        if not SEASON_KEY.fullmatch(season_key) or not MONTH.fullmatch(month):
            raise ValueError("Invalid archive season/month")
        doc = json.loads(file.read_text(encoding="utf-8"))
        if (not isinstance(doc, dict) or doc.get("schemaVersion") != 1 or
            doc.get("seasonKey") != season_key or doc.get("month") != month or
            not isinstance(doc.get("matches"), list)):
            raise ValueError("Invalid archived match shard")
        if season_key not in totals:
            raise ValueError("Unknown official season")
        for raw in doc["matches"]:
            item = _public_copy(raw)
            ident = item["id"]
            if ident in seen:
                raise ValueError("Duplicate match ID in archive")
            seen.add(ident)
            ended = parse_utc(item["endedAt"])
            started = parse_utc(item["startedAt"])
            if (_season_for(ended, seasons) != season_key or
                    ended.strftime("%Y-%m") != month):
                raise ValueError("Match in wrong season/month shard")
            for scope in ("all", season_key):
                _add(totals[scope], started)
    document = {
        "schemaVersion": 1,
        "source": "1ADAAR captured completed WARCON matches",
        "scope": "server",
        "coverage": "captured-only",
        "measurement": METER,
        "timestampField": "startedAt",
        "timezone": TIMEZONE,
        "dataLimitations": (
            "Counts only completed matches actually saved by 1ADAAR. "
            "A zero cell means no captured match start in that slot; "
            "it does not prove the server was inactive. "
            "This is not player session data or time spent playing."
        ),
        "seasons": [
            {"key": key, "name": names[key], **totals[key]}
            for key in ("all", *(season[0] for season in seasons))
        ],
    }
    if read_json(output, {}) != document:
        atomic_write_json(output, document)
        changed = 1
    else:
        changed = 0
    return {"capturedMatches": len(seen), "changedFiles": changed}
