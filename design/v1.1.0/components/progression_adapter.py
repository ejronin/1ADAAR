"""Safe read-only adapter for already-public WARDOGS Tracker progression JSON.

Inputs are memory-only third-party GET /api/v1/players/{steamId} responses.
Integration must respect tracker privacy, rate limits and source attribution.
Never place raw SteamID, HTTP cookie/session or a profile URL containing raw
SteamID in GitHub Pages artifacts.

This module DOES NOT authenticate users, perform API requests, bypass privacy,
or pretend a private WDRCON/WARCON endpoint supplies role levels.
"""
from __future__ import annotations

from datetime import datetime
from math import isfinite

ROLES = ("Assault","Medic","Support","Recon","Driver","Pilot")
TRACKER = "WARDOGS Tracker (public opt-in synchronized progression)"
CREDIT = "https://wardogstracker.gg/developers"


def normalize_tracker_progression(
    payload: dict,
    *,
    requested_steam_id: str,
    public_display_approved: bool,
    max_level: int | None,
) -> dict | None:
    """Return no identifying fields, or None when any source gate fails.

    max_level must be verified for the current WARDOGS progression season.
    A valid JSON response alone is not permission to republish personal
    history or copy session credentials.
    """
    if not public_display_approved:
        return None
    if not (isinstance(requested_steam_id, str) and
            len(requested_steam_id)==17 and requested_steam_id.isascii() and
            requested_steam_id.isdigit()):
        return None
    if not (isinstance(max_level, int) and not isinstance(max_level, bool)
            and max_level>0):
        return None
    if not isinstance(payload, dict):
        return None
    player = payload.get("player")
    if not isinstance(player, dict) or player.get("steamId") != requested_steam_id:
        return None
    stats = player.get("stats")
    if not isinstance(stats, dict):
        return None
    roles=stats.get("roles")
    if not isinstance(roles, dict):
        return None
    checked={}
    checked_xp={}
    for role in ROLES:
        record=roles.get(role.lower())
        if not isinstance(record, dict):
            return None
        lv,xp=record.get("level"),record.get("xp")
        if not (isinstance(lv,(int,float)) and not isinstance(lv,bool) and
                isfinite(lv) and 0<=lv<=max_level and
                isinstance(xp,(int,float)) and not isinstance(xp,bool) and
                isfinite(xp) and xp>=0):
            return None
        checked[role]=float(lv)
        checked_xp[role]=int(xp)
    stamp=stats.get("syncedAt")
    if not isinstance(stamp,str):
        return None
    try:
        when=datetime.fromisoformat(stamp.replace("Z","+00:00"))
        if when.utcoffset() is None:
            return None
    except ValueError:
        return None
    # No SteamID, original public profile URL, or other identifying fields.
    return {
        "sourceStatus":"verified",
        "source":TRACKER,
        "sourceUrl":CREDIT,
        "capturedAt":when.isoformat(),
        "dataScope":"third-party, player-synced WARDOGS progression; NOT server match",
        "maxLevel":max_level,
        "levels":checked,
        "xp":checked_xp,
        "seasonStatus":"verify game season before mixing readings",
    }
