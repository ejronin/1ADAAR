"""Safe read-only projection of public WARCON server status for GitHub Pages.

No RCON access, join code, roster, SteamID or private credentials are retained.
Yellow means a *recent loss of reachability*, not a confirmed game restart:
WARCON's public endpoint has no explicit restart-state field.
"""
from __future__ import annotations

import datetime as dt
from typing import Any

MAX_OBSERVATION_AGE = dt.timedelta(minutes=15)
VALID_STATES = frozenset({"online", "offline", "reconnecting", "unknown"})
MAP_NAMES = {"NorthAmerica": "Zestafona", "Europe": "Ozeti", "Kavkazi": "Bakurani"}
UTC = dt.timezone.utc


def _time(value: Any) -> dt.datetime | None:
    if not isinstance(value, str):
        return None
    try:
        result = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        return result.astimezone(UTC) if result.tzinfo is not None else None
    except (ValueError, OverflowError):
        return None


def unknown(when: dt.datetime | None = None) -> dict:
    now = (when or dt.datetime.now(UTC)).astimezone(UTC)
    return {"schemaVersion": 1, "state": "unknown", "checkedAt": now.isoformat(),
            "observedAt": None, "players": None, "maxPlayers": None,
            "map": None, "source": "WARCON public server status"}


def project(server: dict, previous: str = "unknown",
            *, now: dt.datetime | None = None) -> dict:
    """Pure status projection. Restart is never asserted without a public signal."""
    when = (now or dt.datetime.now(UTC)).astimezone(UTC)
    if not isinstance(server, dict):
        raise ValueError("Malformed public server status")
    observed = _time(server.get("observedAt"))
    # 'ok' from old poll is not a current reachability claim.
    if (observed is None or when - observed > MAX_OBSERVATION_AGE
            or observed - when > dt.timedelta(minutes=2)
            or not isinstance(server.get("ok"), bool)):
        return unknown(when)
    good = server["ok"]
    state = "online" if good else ("reconnecting" if previous == "online" else "offline")
    players = server.get("players")
    max_players = server.get("maxPlayers")
    if not isinstance(players, int) or isinstance(players, bool) or players < 0:
        players = None
    if not isinstance(max_players, int) or isinstance(max_players, bool) or max_players <= 0:
        max_players = None
    map_name = server.get("map")
    if not isinstance(map_name, str) or not map_name.strip():
        map_name = None
    elif good:
        map_name = MAP_NAMES.get(map_name, map_name)[:55]
    else:
        map_name = None  # previous-session map is NOT the current map
    return {"schemaVersion": 1, "state": state, "checkedAt": when.isoformat(),
            "observedAt": observed.isoformat(),
            "players": players if good else None,
            "maxPlayers": max_players if good else None,
            "map": map_name if good else None,
            "source": "WARCON public server status"}
