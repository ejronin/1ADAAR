"""Conservative next-map projection from *public* WARCON status only.

WARCON's documented server rotation is not necessarily part of the anonymous
public status payload. Never guess a schedule or fetch private RCON endpoints.
When the current map has already changed, a rotation's 'next' is NOT next for
the just-ended match; return unknown instead.
"""
from __future__ import annotations
import datetime as dt

MAPS = {"NorthAmerica": "Zestafona", "Europe": "Ozeti", "Kavkazi": "Bakurani",
        "Zestafona": "Zestafona", "Ozeti": "Ozeti", "Bakurani": "Bakurani"}
LIGHTING = {
    "DayStartClear": "Morning • Clear",
    "DayEarlyClear": "Early day • Clear",
    "DayEarlyFog": "Early day • Fog",
    "DayClear": "Day • Clear",
    "DayLateClear": "Late day • Clear",
    "DayLateGray": "Late day • Overcast",
    "DayLateGrayFog": "Late day • Fog",
    "DayEndClear": "Evening • Clear",
}
MAX_AGE = dt.timedelta(minutes=3)


def clean_next_map(status: dict | None, ended_at: str, finished_map: str) -> dict | None:
    """Use only an explicit ordered next rotation entry, verified near match end."""
    if not isinstance(status, dict) or status.get("ok") is not True:
        return None
    observed = status.get("observedAt")
    try:
        ended = dt.datetime.fromisoformat(ended_at.replace("Z", "+00:00"))
        seen = dt.datetime.fromisoformat(observed.replace("Z", "+00:00"))
        if ended.tzinfo is None or seen.tzinfo is None:
            return None
        delta = seen - ended
        if delta < -dt.timedelta(seconds=30) or delta > MAX_AGE:
            return None
    except (TypeError, AttributeError, ValueError, OverflowError):
        return None
    rotation = status.get("rotation")
    if not isinstance(rotation, dict) or rotation.get("enabled") is not True:
        return None
    # Only an ordered, explicit next pointer can be displayed with confidence.
    if rotation.get("mode") != "ordered":
        return None
    current = status.get("map")
    if MAPS.get(current) is None or MAPS.get(current) != MAPS.get(finished_map):
        return None
    entries = rotation.get("entries")
    if not isinstance(entries, list) or not (1 <= len(entries) <= 100):
        return None
    idx = rotation.get("nextIndex")
    if type(idx) is not int or not (0 <= idx < len(entries)):
        return None
    next_entry = entries[idx]
    if not isinstance(next_entry, dict) or next_entry.get("denied") is True:
        return None
    target = MAPS.get(next_entry.get("map"))
    if not target:
        return None
    current_entry = next((row for row in entries if isinstance(row, dict)
                          and row.get("status") == "now"), None)
    if not current_entry or MAPS.get(current_entry.get("map")) != MAPS.get(current):
        return None
    # Refuse an entry that claims current status and next status at once.
    if next_entry.get("status") != "next":
        return None
    return {"map": target, "conditions": LIGHTING.get(next_entry.get("lighting")),
            "source": "WARCON ordered map rotation", "observedAt": observed}
