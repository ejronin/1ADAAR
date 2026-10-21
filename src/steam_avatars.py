"""Optional Steam avatar enrichment for public 1ADAAR player cards.

Only run in GitHub Actions. SteamIDs and the Steam API key are transient and
must never enter public JSON, rendered HTML, logs, or Git commit history.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import urllib.parse
import urllib.request
from typing import Callable

STEAM_API = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
STEAM_IDS = re.compile(r"^\d{17}$")
KEYS = re.compile(r"^[0-9a-f]{64}$")
LEGACY_CDN = re.compile(r"^/steamcommunity/public/images/avatars/[0-9a-f]{2}/[0-9a-f]{40}_full\.jpg$")
NEW_CDN = re.compile(r"^/[0-9a-f]{40}_full\.jpg$")
LEGACY_HOSTS = frozenset(("steamcdn-a.akamaihd.net", "steamcommunity-a.akamaihd.net"))
NEW_HOSTS = frozenset(("avatars.steamstatic.com", "avatars.akamai.steamstatic.com"))
MAX_BATCHES = 2
BATCH_SIZE = 100
REFRESH_AFTER = dt.timedelta(hours=24)
MAX_RESPONSE_BYTES = 1_000_000


def valid_avatar_url(value: object) -> str | None:
    if not isinstance(value, str) or len(value) > 350:
        return None
    try:
        url = urllib.parse.urlsplit(value)
        if (url.scheme != "https" or url.username or url.password or
                url.port is not None or url.query or url.fragment):
            return None
        host = (url.hostname or "").lower()
        valid = ((host in LEGACY_HOSTS and LEGACY_CDN.fullmatch(url.path)) or
                 (host in NEW_HOSTS and NEW_CDN.fullmatch(url.path)))
        return value if valid else None
    except ValueError:
        return None


def steam_summaries(steam_ids: list[str], key: str) -> dict:
    """Use only the documented Steam endpoint; never include the key in errors."""
    if not steam_ids or len(steam_ids) > BATCH_SIZE or not all(STEAM_IDS.fullmatch(x) for x in steam_ids):
        raise ValueError("Invalid Steam avatar batch")
    if not key or len(key) > 256:
        raise ValueError("Steam avatar key not configured")
    query = urllib.parse.urlencode({"key": key, "steamids": ",".join(steam_ids)})
    request = urllib.request.Request(STEAM_API + "?" + query, headers={
        "Accept": "application/json", "User-Agent": "1ADAAR-static-avatar-snapshot/1.0"
    })
    # The key appears in a query string: disable redirects before any cross-host
    # request could occur. Never log Steam exception strings containing URLs.
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None
    opener = urllib.request.build_opener(NoRedirect)
    with opener.open(request, timeout=15) as response:
        final = urllib.parse.urlsplit(response.geturl())
        if final.scheme != "https" or final.hostname != "api.steampowered.com":
            raise ValueError("Unexpected Steam API redirect")
        data = response.read(MAX_RESPONSE_BYTES + 1)
        if len(data) > MAX_RESPONSE_BYTES:
            raise ValueError("Oversized Steam API response")
        return json.loads(data)


def _fresh(row: dict, now: dt.datetime) -> bool:
    stamp = row.get("avatarCheckedAt")
    if not isinstance(stamp, str):
        return False
    try:
        then = dt.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        return then.tzinfo is not None and dt.timedelta(0) <= now - then < REFRESH_AFTER
    except ValueError:
        return False


def resolve_avatars(
    ids_by_key: dict[str, str],
    old_players: list[dict],
    api_key: str,
    *,
    now: dt.datetime | None = None,
    fetch: Callable[[list[str], str], dict] = steam_summaries,
    max_batches: int = MAX_BATCHES,
) -> dict[str, dict]:
    """Return only public avatar URLs/check timestamps, keyed by existing public digests.

    Negative results are cached for 24h too; failures retain any last good image.
    At most 200 uncached/expired players are queried per ten-minute collection.
    """
    now = now or dt.datetime.now(dt.timezone.utc)
    if now.tzinfo is None:
        raise ValueError("Avatar refresh requires timezone-aware UTC datetime")
    now = now.astimezone(dt.timezone.utc)
    cached = {
        p["key"]: p for p in old_players
        if isinstance(p, dict) and isinstance(p.get("key"), str) and KEYS.fullmatch(p["key"])
    }
    result = {}
    due = []
    for key, steam_id in ids_by_key.items():
        if not KEYS.fullmatch(key) or not STEAM_IDS.fullmatch(steam_id):
            continue
        old = cached.get(key, {})
        data = {}
        image = valid_avatar_url(old.get("avatar"))
        if image:
            data["avatar"] = image
        if isinstance(old.get("avatarCheckedAt"), str) and _fresh(old, now):
            data["avatarCheckedAt"] = old["avatarCheckedAt"]
        elif api_key:
            due.append((key, steam_id))
        result[key] = data

    if not api_key:
        return result

    for offset in range(0, min(len(due), max_batches * BATCH_SIZE), BATCH_SIZE):
        batch = due[offset:offset + BATCH_SIZE]
        requested = {steam_id: key for key, steam_id in batch}
        try:
            response = fetch([steam_id for _, steam_id in batch], api_key)
            players = response.get("response", {}).get("players")
            if not isinstance(players, list):
                raise ValueError("Malformed Steam summaries")
        except Exception:
            # Keep cached images on API timeout, disabled key or transient failure.
            # Never print an exception: HTTP failures may include the secret URL.
            break

        returned = {
            p["steamid"]: p for p in players
            if isinstance(p, dict) and p.get("steamid") in requested
        }
        checked_at = now.isoformat().replace("+00:00", "Z")
        for key, steam_id in batch:
            image = valid_avatar_url(returned.get(steam_id, {}).get("avatarfull"))
            data = {"avatarCheckedAt": checked_at}
            if image:
                data["avatar"] = image
            result[key] = data
    return result
