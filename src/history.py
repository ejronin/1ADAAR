"""Bounded, privacy-preserving career snapshots of the public WARCON leaderboard.

No raw SteamIDs, names, tokens or live server credentials are stored. Histories
are sharded by the first character of the existing public SHA256 player key so
a phone loads only the selected player's shard, not the entire leaderboard.
"""
from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path

KEY = re.compile(r"^[a-f0-9]{64}$")
HEX = "0123456789abcdef"
FIELDS = ("kills", "deaths", "matches", "wins", "losses", "draws", "minutes")
MAX_SNAPSHOTS = 60
KEEP_DAYS = 180
MAX_KEYS_PER_SHARD = 125


def _count(value: object) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError("Unexpected leaderboard statistic")
    return value


def record_snapshots(directory: Path, leaderboard: dict, *, now: dt.datetime | None = None) -> int:
    """Write at most one changed leaderboard snapshot per player per UTC date.

    Returns number of changed shard files. The collector only calls this after
    a successfully validated WARCON leaderboard fetch, never for demo records.
    """
    if not isinstance(leaderboard, dict) or not isinstance(leaderboard.get("players"), list):
        raise ValueError("Invalid WARCON leaderboard index")
    timestamp = now or dt.datetime.now(dt.timezone.utc)
    day = timestamp.astimezone(dt.timezone.utc).date()
    cutoff = (day - dt.timedelta(days=KEEP_DAYS)).isoformat()
    today = day.isoformat()
    today_updates: dict[str, dict] = {}
    for player in leaderboard["players"][:1000]:
        if not isinstance(player, dict) or not KEY.fullmatch(str(player.get("key", ""))):
            raise ValueError("Invalid pseudonymous player key")
        point = {"date": today, **{field: _count(player.get(field)) for field in FIELDS}}
        # Empty/idle profiles are not historical match performance.
        if point["matches"] == 0 and point["kills"] == 0 and point["deaths"] == 0:
            continue
        today_updates[player["key"]] = point
    changed = 0
    for shard in HEX:
        file = directory / f"{shard}.json"
        if file.exists():
            doc = json.loads(file.read_text(encoding="utf-8"))
            if doc.get("schemaVersion") != 1 or not isinstance(doc.get("players"), dict):
                raise ValueError(f"Invalid history shard: {shard}")
            tracks = doc["players"]
        else:
            tracks = {}
        old_serialized = json.dumps(tracks, sort_keys=True)
        for key in list(tracks):
            if not KEY.fullmatch(key) or key[0] != shard:
                raise ValueError("History shard contains invalid player key")
            samples = tracks[key]
            if not isinstance(samples, list) or any(
                not isinstance(point, dict) or not isinstance(point.get("date"), str)
                or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", point["date"])
                or any(not isinstance(point.get(field), int) or point[field] < 0 for field in FIELDS)
                for point in samples
            ):
                raise ValueError("History shard contains invalid snapshot")
            samples = [p for p in samples if cutoff <= p["date"] <= today]
            if samples:
                tracks[key] = samples[-MAX_SNAPSHOTS:]
            else:
                del tracks[key]
        for key, point in today_updates.items():
            if key[0] != shard:
                continue
            samples = tracks.get(key, [])
            # Refresh today's point when another match ends, never emit two
            # samples on one day. Skip unchanged career totals entirely.
            if samples and all(samples[-1][field] == point[field] for field in FIELDS):
                continue
            if samples and samples[-1]["date"] == today:
                samples[-1] = point
            else:
                samples.append(point)
            tracks[key] = samples[-MAX_SNAPSHOTS:]
        if len(tracks) > MAX_KEYS_PER_SHARD:
            # Keep players with the most recent real activity.
            newest = sorted(tracks, key=lambda key: (tracks[key][-1]["date"], key), reverse=True)
            keep = set(newest[:MAX_KEYS_PER_SHARD])
            tracks = {key: tracks[key] for key in tracks if key in keep}
        if json.dumps(tracks, sort_keys=True) != old_serialized:
            directory.mkdir(parents=True, exist_ok=True)
            output = {"schemaVersion": 1, "source": "WARCON public leaderboard snapshots",
                      "retentionDays": KEEP_DAYS, "players": tracks}
            tmp = file.with_suffix(".tmp")
            tmp.write_text(json.dumps(output, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
            tmp.replace(file)
            changed += 1
    return changed
