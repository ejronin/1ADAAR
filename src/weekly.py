"""Weekly results derived only from archived, sanitized WARCON match records.

No network calls or posting happen here. The saved match window is incomplete;
no award is a claim about all WARDOGS matches or career progression.
"""
from collections import Counter
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
import re
from src.player_index import safe_name

EASTERN = ZoneInfo("America/New_York")
UTC = timezone.utc
SOURCE = "1ADAAR captured completed matches (most recent 120; coverage unverified)"
OFFICIAL_SEASONS = (
    {"key": "wardogs-1", "name": "Season 1", "startsAt": "2026-09-10T00:00:00Z"},
    {"key": "wardogs-2", "name": "Season 2", "startsAt": "2026-10-15T16:00:00Z"},
)
KEY = re.compile(r"^[a-f0-9]{64}$")


def parse_utc(value):
    if not isinstance(value, str):
        raise ValueError("Missing timestamp")
    moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if moment.tzinfo is None:
        raise ValueError("Naive timestamp")
    return moment.astimezone(UTC)


def iso(moment):
    return moment.astimezone(UTC).isoformat().replace("+00:00", "Z")


def sunday_window(day):
    """Sunday 12 PM Eastern to Sunday 12 PM Eastern (not 168 fixed hours)."""
    day = date.fromisoformat(day) if isinstance(day, str) else day
    if not isinstance(day, date) or day.weekday() != 6:
        raise ValueError("Ending day must be Sunday")
    start = datetime.combine(day - timedelta(days=7), time(12), tzinfo=EASTERN)
    end = datetime.combine(day, time(12), tzinfo=EASTERN)
    return start.astimezone(UTC), end.astimezone(UTC)


def _season_list(values):
    rows = [(s["key"], s["name"], parse_utc(s["startsAt"])) for s in values]
    if len(set(s[0] for s in rows)) != len(rows):
        raise ValueError("Duplicate season keys")
    if any(not re.fullmatch(r"[a-z0-9-]{1,64}", s[0]) for s in rows):
        raise ValueError("Invalid season key")
    if any(a[2] >= b[2] for a, b in zip(rows, rows[1:])):
        raise ValueError("Season starts are not strictly increasing")
    return rows


def _nonnegative(value):
    return value if type(value) is int and value >= 0 else None


def _award(players, metric, unit):
    values = [(row[metric], row["name"], key) for key, row in players.items()
              if row.get(metric) is not None and row[metric] > 0]
    if not values:
        return None
    value, name, _ = min(values, key=lambda x: (-x[0], x[1].casefold(), x[2]))
    return {"name": name, "value": value, "unit": unit}


def _winner_is_verified(match):
    """Count victory awards only when WARCON explicitly confirmed a unique winner."""
    if match.get("winnerVerified") is not True:
        return False
    winner = match.get("winner")
    scores = match.get("scores")
    if not isinstance(winner, str) or not winner.strip() or not isinstance(scores, list):
        return False
    valid = [s for s in scores if isinstance(s, dict)
             and isinstance(s.get("name"), str)
             and type(s.get("score")) in (int, float)]
    if not valid or len(valid) != len(scores):
        return False
    top = max(row["score"] for row in valid)
    leaders = [row for row in valid if row["score"] == top]
    return len(leaders) == 1 and leaders[0]["name"].strip().casefold() == winner.strip().casefold()


def _segment(matches, start, end):
    stats, factions, durations, wins, maps = {}, Counter(), Counter(), Counter(), Counter()
    map_kills = {}
    feed_complete = bool(matches) and all(m.get("hasFeed") is True for m in matches)
    for m in matches:
        map_name = m["map"].strip()[:55] if isinstance(m.get("map"), str) else ""
        if map_name:
            maps[map_name] += 1
        winner_confirmed = _winner_is_verified(m)
        if winner_confirmed:
            wins[m["winner"].strip()[:40]] += 1
        seen = set()
        for p in m["players"]:
            if not isinstance(p, dict) or not isinstance(p.get("key"), str) or not KEY.fullmatch(p["key"]):
                continue
            name = safe_name(p.get("name"))
            if p["key"] in seen or not name:
                continue
            seen.add(p["key"])
            v = stats.setdefault(p["key"], {"name": "", "matches": 0, "kills": 0,
                "deaths": 0, "wins": 0, "seconds": 0, "headshots": 0,
                "longestM": 0, "kdEligible": True})
            v["name"] = name
            v["matches"] += 1
            if (winner_confirmed and p.get("result") == "win"
                    and str(p.get("faction", "")).strip().casefold()
                    == m["winner"].strip().casefold()):
                v["wins"] += 1
            for f in ("kills", "deaths", "seconds"):
                amount = _nonnegative(p.get(f))
                if amount is not None:
                    v[f] += amount
                elif f in ("kills", "deaths"):
                    v["kdEligible"] = False
            recorded_kills = _nonnegative(p.get("kills"))
            if map_name and recorded_kills is not None:
                by_map = map_kills.setdefault(map_name, {})
                mark = by_map.setdefault(p["key"], {"name": name, "kills": 0})
                mark["name"] = name
                mark["kills"] += recorded_kills
            if feed_complete:
                for f in ("headshots", "longestM"):
                    amount = _nonnegative(p.get(f))
                    if amount is None:
                        feed_complete = False
                        break
                    if f == "longestM":
                        v[f] = max(v[f], amount)
                    else:
                        v[f] += amount
            faction = p.get("faction")
            if isinstance(faction, str) and faction.strip():
                faction = faction.strip()[:40]
                factions[faction] += 1  # Appearance, not an actual join event.
                duration = _nonnegative(p.get("seconds"))
                if duration is not None:
                    durations[faction] += duration
    if not feed_complete:
        for p in stats.values():
            p["headshots"] = p["longestM"] = None
    killers = sorted(stats.items(), key=lambda item: (
        -item[1]["kills"], item[1]["name"].casefold(), item[0]))
    top_killers = [
        {"name": row["name"], "kills": row["kills"], "matches": row["matches"]}
        for _, row in killers if row["kills"] > 0
    ][:3]
    map_leaders = []
    for map_name, matches_count in sorted(maps.items(),
                                          key=lambda item: (-item[1], item[0])):
        ranked = sorted(map_kills.get(map_name, {}).items(),
                        key=lambda item: (-item[1]["kills"],
                                          item[1]["name"].casefold(), item[0]))
        best = ranked[0][1] if ranked and ranked[0][1]["kills"] > 0 else None
        map_leaders.append({
            "name": map_name, "matches": matches_count,
            "leader": {"name": best["name"], "kills": best["kills"]} if best else None,
        })
    kd_players = [(row["kills"] / row["deaths"], row["name"], key)
                  for key, row in stats.items()
                  if row["matches"] >= 20 and row["kdEligible"] and row["deaths"] > 0]
    kd_players.sort(key=lambda item: (-item[0], item[1].casefold(), item[2]))
    best_kd = ({"name": kd_players[0][1], "value": round(kd_players[0][0], 2),
                "unit": "K/D"} if kd_players else None)
    awards = {
        "mostMatches": _award(stats, "matches", "matches"),
        "mostKills": _award(stats, "kills", "kills"),
        "mostWins": _award(stats, "wins", "wins"),
        "mostPlaytime": _award(stats, "seconds", "seconds"),
        "mostHeadshots": _award(stats, "headshots", "headshots") if feed_complete else None,
        "longestShot": _award(stats, "longestM", "meters") if feed_complete else None,
        "bestWeeklyKd20": best_kd,
    }
    return {
        "fromUtc": iso(start), "toUtc": iso(end),
        "completedMatchesInArchive": len(matches), "uniqueRecordedPlayers": len(stats),
        "factions": [{"name": f, "appearances": c, "recordedPlayerSeconds": durations[f],
                      "matchesWon": wins[f]}
                     for f, c in sorted(factions.items(), key=lambda row: (-row[1], row[0]))],
        "maps": [{"name": name, "matches": n}
                 for name, n in sorted(maps.items(), key=lambda row: (-row[1], row[0]))],
        "topKillers": top_killers, "mapLeaders": map_leaders,
        "awards": awards, "combatFeedCoverage": "complete" if feed_complete else "unverified",
        "coverage": "archive-limited", "completeWeekProven": False,
    }


def summarize_week(matches, ending_sunday, *, seasons=OFFICIAL_SEASONS):
    """Return staged summary of verifiable captured matches; never publish."""
    start, end = sunday_window(ending_sunday)
    seasons = _season_list(seasons)
    if not seasons:
        raise ValueError("Official season metadata required")
    picked, conflicted = {}, set()
    for m in matches:
        if not isinstance(m, dict) or m.get("schemaVersion") != 2 or type(m.get("id")) is not int:
            continue
        if m["id"] <= 0 or not isinstance(m.get("players"), list) or not isinstance(m.get("scores"), list) or not m["scores"]:
            continue
        try:
            ended, begun = parse_utc(m["endedAt"]), parse_utc(m["startedAt"])
        except (KeyError, ValueError, TypeError, OverflowError):
            continue
        if start <= ended < end and begun <= ended and m["id"] not in conflicted:
            entry = (ended, m)
            if m["id"] in picked and picked[m["id"]] != entry:
                # A conflicting duplicate makes the match unverifiable. Exclude
                # the ID entirely rather than rewarding whichever record came last.
                del picked[m["id"]]
                conflicted.add(m["id"])
            else:
                picked[m["id"]] = entry
    rows = sorted(picked.values(), key=lambda item: (item[0], item[1]["id"]))
    segments = []
    for i, (key, name, begins) in enumerate(seasons):
        next_start = seasons[i+1][2] if i+1 < len(seasons) else end
        lower, upper = max(start, begins), min(end, next_start)
        if lower >= upper:
            continue
        relevant = [m for timestamp, m in rows if lower <= timestamp < upper]
        segments.append({"seasonKey": key, "seasonName": name,
                         **_segment(relevant, lower, upper)})
    if not segments:
        raise ValueError("Window has no official season metadata")
    return {
        "schemaVersion": 1, "kind": "staged-weekly-candidate",
        "publicationEnabled": False, "source": SOURCE,
        "weekEndingEastern": str(ending_sunday), "fromUtc": iso(start),
        "toUtc": iso(end), "segments": segments,
        "conflictingMatchIdsExcluded": len(conflicted),
        "qualifier": "Captured completed matches only; incomplete archives possible.",
        "seasonKdOver20": None, "characterLevelAwards": None,
        "actualFactionJoinCounts": None,
    }
