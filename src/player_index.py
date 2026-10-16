"""WARCON public leaderboard -> least-information player lookup index.

A one-way stable SHA256 lookup key links public leaderboard entries and recent-match
lines. It hides the literal SteamID from UI and HTML/JSON, but is pseudonymization,
NOT cryptographic anonymity against enumeration of plausible SteamIDs.
"""
from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone

LOOKUP_PREFIX = b"1ADAAR:v1:"
BOARD_PAGE_LIMIT = 20  # WARCON public endpoint permits 20 * 50 = 1,000 entries


def player_key(steam_id: object) -> str:
    if not isinstance(steam_id, str) or not re.fullmatch(r"\d{17}", steam_id):
        return ""
    return hashlib.sha256(LOOKUP_PREFIX + steam_id.encode("ascii")).hexdigest()


def safe_name(value: object) -> str:
    if not isinstance(value, str):
        return ""
    out = "".join(ch for ch in value if ch.isprintable() and ch not in "@`<>{}\\").strip()[:64]
    # WARCON uses SteamID as a fallback name; never display it.
    return "" if re.fullmatch(r"\d{17}", out) else out


def nonnegative_integer(value: object) -> int:
    return max(0, value) if isinstance(value, int) and not isinstance(value, bool) else 0


def sanitize_board_row(row: object, *, has_feed: bool) -> dict | None:
    if not isinstance(row, dict):
        return None
    key, name = player_key(row.get("steamId")), safe_name(row.get("name"))
    if not key or not name:
        return None
    out = {"key": key, "name": name, "hasFeed": bool(has_feed)}
    for field in ("rank", "minutes", "seedMinutes", "kills", "deaths", "matches", "wins",
                  "losses", "draws", "cash"):
        out[field] = nonnegative_integer(row.get(field))
    for field in ("headshots", "teamKills", "vehicleKills", "killStreak"):
        # These columns have no meaning without the verified server kill feed.
        out[field] = nonnegative_integer(row.get(field)) if has_feed else None
    stamp = row.get("lastSeen")
    try:
        out["lastSeen"] = datetime.fromisoformat(stamp.replace("Z", "+00:00")).astimezone(timezone.utc).isoformat() if stamp else None
    except (ValueError, AttributeError, TypeError):
        out["lastSeen"] = None
    return out


def collect_players(fetch_json_fn, base_url: str) -> dict:
    """Bounded all-time leaderboard snapshot. No privileged API endpoints or secrets."""
    players, first_feed, pages_seen = {}, False, 0
    for page in range(1, BOARD_PAGE_LIMIT + 1):
        doc = fetch_json_fn(f"{base_url}?scope=server&range=all&sort=kills&minMinutes=0&page={page}")
        rows = doc.get("rows")
        if not isinstance(rows, list):
            raise ValueError("WARCON public leaderboard response does not contain rows")
        if page == 1:
            first_feed = bool(doc.get("hasFeed"))
        for row in rows:
            entry = sanitize_board_row(row, has_feed=first_feed)
            if entry:
                players[entry["key"]] = entry
        pages_seen += 1
        if not rows or len(rows) < 50 or page * 50 >= nonnegative_integer(doc.get("total")):
            break
    return {"schemaVersion": 2, "source": "WARCON public leaderboard API (all time, server)",
            "limit": BOARD_PAGE_LIMIT * 50, "capped": pages_seen == BOARD_PAGE_LIMIT and len(players) >= BOARD_PAGE_LIMIT * 50,
            "hasFeed": first_feed, "players": sorted(players.values(), key=lambda x: (x["rank"],x["name"].casefold()))}
