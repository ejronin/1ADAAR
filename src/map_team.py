"""Static map/team summaries from actual saved WARDOGS completed-match records.

No WARCON fetch, private identity or client-side full-archive analysis.
Each file contains only players whose public pseudonymous key begins with its
hex shard; all-time here means *all captured matches*, NOT WARCON career totals.
"""
from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path

from src.player_index import safe_name
from src.recap import atomic_write_json, read_json
from src.season_archive import HEX_KEY, MONTH, SEASON_KEY, _public_copy, _season_for
from src.weekly import OFFICIAL_SEASONS, _season_list, parse_utc

HEX = "0123456789abcdef"
MIN_BEST_MAP_MATCHES = 5
UNKNOWN_TEAM = "Unknown team"
UNKNOWN_MAP = "Unknown map"
RESULTS = {"win": "wins", "loss": "losses", "draw": "draws"}


def _stat():
    return {"matches": 0, "wins": 0, "losses": 0, "draws": 0,
            "unknownOutcomes": 0, "kills": 0, "deaths": 0, "seconds": 0}


def _add(stats: dict, player: dict):
    stats["matches"] += 1
    outcome = RESULTS.get(player.get("result"))
    stats[outcome if outcome else "unknownOutcomes"] += 1
    for key in ("kills", "deaths", "seconds"):
        value = player.get(key)
        if type(value) is not int or value < 0:
            raise ValueError("Invalid captured player totals")
        stats[key] += value


def _scope():
    return {"total": _stat(), "maps": defaultdict(_stat),
            "factions": defaultdict(_stat), "combinations": defaultdict(_stat)}


def _number(value):
    return round(value, 4)


def _render(stats: dict):
    result = dict(stats)
    known = stats["wins"] + stats["losses"] + stats["draws"]
    result["knownOutcomes"] = known
    result["winRate"] = _number(stats["wins"] / known) if known else None
    result["kd"] = _number(stats["kills"] / stats["deaths"]) if stats["deaths"] else None
    return result


def _best_map(rows: list[dict]):
    valid = [r for r in rows if r["name"] != UNKNOWN_MAP and
             r["knownOutcomes"] >= MIN_BEST_MAP_MATCHES]
    if not valid:
        return None
    high = max((r["winRate"], r["wins"], r["knownOutcomes"]) for r in valid)
    ties = [r for r in valid if (r["winRate"], r["wins"], r["knownOutcomes"]) == high]
    # Never arbitrarily promote one map if several share identical numbers.
    return {"name": ties[0]["name"] if len(ties) == 1 else None,
            "tied": len(ties) > 1,
            "names": sorted(r["name"] for r in ties),
            "winRate": high[0], "knownOutcomes": high[2]}


def _final_scope(scope: dict):
    maps = [{"name": name, **_render(stats)} for name, stats in scope["maps"].items()]
    maps.sort(key=lambda row: (-row["matches"], row["name"]))
    factions = [{"name": name, **_render(stats)} for name, stats in scope["factions"].items()]
    factions.sort(key=lambda row: (-row["matches"], row["name"]))
    combination = [
        {"map": key[0], "faction": key[1], **_render(stats)}
        for key, stats in scope["combinations"].items()
    ]
    combination.sort(key=lambda row: (-row["matches"], row["map"], row["faction"]))
    return {"total": _render(scope["total"]),
            "uniqueMaps": len([r for r in maps if r["name"] != UNKNOWN_MAP]),
            "maps": maps, "factions": factions, "combinations": combination,
            "bestMap": _best_map(maps)}


def build_map_team(archive_directory: Path, output_directory: Path) -> dict:
    """Recompute shard snapshots only when captured-match content changes.

    One match ID counts once across all archive files. Fail closed if an
    archive is malformed or if results conflict; no published guesswork.
    """
    seasons = _season_list(OFFICIAL_SEASONS)
    seen_match_ids = set()
    people = {}
    count = 0

    for path in sorted(archive_directory.glob("*/*.json")):
        season_key = path.parent.name
        month = path.stem
        if not SEASON_KEY.fullmatch(season_key) or not MONTH.fullmatch(month):
            raise ValueError("Invalid captured season path")
        doc = json.loads(path.read_text(encoding="utf-8"))
        if (not isinstance(doc, dict) or doc.get("schemaVersion") != 1
            or doc.get("seasonKey") != season_key or doc.get("month") != month
            or not isinstance(doc.get("matches"), list)):
            raise ValueError("Invalid captured season match file")
        captured = sorted(doc["matches"], key=lambda m: (m["endedAt"], m["id"]))
        for original in captured:
            match = _public_copy(original)
            ident = match["id"]
            ended = parse_utc(match["endedAt"])
            if ident in seen_match_ids:
                raise ValueError("Duplicate captured match ID across archive")
            if _season_for(ended, seasons) != season_key or ended.strftime("%Y-%m") != month:
                raise ValueError("Match is stored under the wrong official season or month")
            seen_match_ids.add(ident)
            count += 1
            in_match = set()
            for player in match["players"]:
                key = player["key"]
                if not HEX_KEY.fullmatch(key) or key in in_match:
                    raise ValueError("Invalid or duplicated player identity in one match")
                in_match.add(key)
                name = safe_name(player.get("name"))
                if not name:
                    continue
                person = people.setdefault(key, {"name": name, "scopes": {}})
                person["name"] = name
                map_name = match.get("map") or UNKNOWN_MAP
                faction = player.get("faction") or UNKNOWN_TEAM
                for scope_key in ("all", season_key):
                    scope = person["scopes"].setdefault(scope_key, _scope())
                    _add(scope["total"], player)
                    _add(scope["maps"][map_name], player)
                    _add(scope["factions"][faction], player)
                    _add(scope["combinations"][(map_name, faction)], player)

    shards: dict[str, dict] = defaultdict(dict)
    for key, person in people.items():
        shards[key[0]][key] = {
            "name": person["name"],
            "scopes": {scope_name: _final_scope(scope)
                       for scope_name, scope in sorted(person["scopes"].items())},
        }
    changed = 0
    for letter in HEX:
        path = output_directory / f"{letter}.json"
        doc = {"schemaVersion": 1,
               "source": "Completed matches saved by 1ADAAR from public WARCON",
               "coverage": "captured-only", "players": dict(sorted(shards[letter].items()))}
        if read_json(path, {}) != doc:
            atomic_write_json(path, doc)
            changed += 1

    index = {"schemaVersion": 1, "coverage": "captured-only",
             "source": "Completed matches captured by 1ADAAR from public WARCON",
             "capturedMatches": count, "playersWithCapturedMatches": len(people),
             "officialSeasons": [{"key": key, "name": name}
                                 for key, name, _ in seasons]}
    if read_json(output_directory / "index.json", {}) != index:
        atomic_write_json(output_directory / "index.json", index)
        changed += 1
    return {"capturedMatches": count, "players": len(people), "changedFiles": changed}
