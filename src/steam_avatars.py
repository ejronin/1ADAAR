"""Optional Steam profile portraits resolved privately at collection time.

STEAM_WEB_API_KEY is a GitHub Actions secret. The public artifact contains
only an HTTPS Steam CDN avatar URL keyed by an existing pseudonymous hash,
NEVER a SteamID64, API key or direct Steam profile link.
"""
from __future__ import annotations
import json
import re
import urllib.parse
import urllib.request

STEAM_SUMMARIES = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
MAX_BATCH = 100
MAX_BYTES = 2_000_000
URL_PATTERN = re.compile(
    r"https://(?:avatars\d*\.steamstatic\.com|steamcommunity-a\.akamaihd\.net|"
    r"community\.cloudflare\.steamstatic\.com)/[A-Za-z0-9/_.-]+\.(?:jpg|jpeg|png)"
    r"(?:\?[A-Za-z0-9=&_-]+)?$", re.IGNORECASE
)
STEAM_ID = re.compile(r"\d{17}\Z")


def safe_avatar(url: object) -> str | None:
    """Accept only vetted public Steam CDN images, no external player links."""
    return url if isinstance(url, str) and len(url) <= 350 and URL_PATTERN.fullmatch(url) else None


def fetch_steam_avatars(keyed_steam_ids: dict[str, str], api_key: str) -> dict[str, str]:
    """Resolve exact SteamID matches in small batches; fail closed on bad data."""
    if not api_key or not re.fullmatch(r"[a-fA-F0-9]{32}", api_key):
        raise ValueError("Valid private STEAM_WEB_API_KEY is required")
    from src.player_index import player_key
    ids = sorted({steam_id for steam_id in keyed_steam_ids.values() if
                  isinstance(steam_id, str) and STEAM_ID.fullmatch(steam_id)})
    results: dict[str, str] = {}
    for start in range(0, len(ids), MAX_BATCH):
        batch = ids[start:start + MAX_BATCH]
        query = urllib.parse.urlencode({"key": api_key, "steamids": ",".join(batch)})
        url = STEAM_SUMMARIES + "?" + query
        request = urllib.request.Request(url, headers={"Accept": "application/json",
                                    "User-Agent": "1ADAAR profile portraits/1.1"})
        # No URL/key is ever included in failure output.
        with urllib.request.urlopen(request, timeout=14) as response:
            if urllib.parse.urlparse(response.geturl()).netloc != "api.steampowered.com":
                raise ValueError("Unexpected Steam API redirect")
            raw = response.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                raise ValueError("Steam response exceeded safe limit")
        document = json.loads(raw)
        players = document.get("response", {}).get("players", [])
        if not isinstance(players, list):
            raise ValueError("Steam summaries are invalid")
        requested = set(batch)
        for row in players:
            if not isinstance(row, dict):
                continue
            steam_id = row.get("steamid")
            if steam_id not in requested:
                continue
            lookup = player_key(steam_id)
            if keyed_steam_ids.get(lookup) != steam_id:
                continue
            image = safe_avatar(row.get("avatarfull"))
            if image:
                results[lookup] = image
    return results
