"""Verify the newly started round from public WARCON server status.

Never announce a predicted map. Only report a DIFFERENT, observed current map
after a specific completed match, with a recognized condition and fresh time.
"""
from __future__ import annotations
import datetime as dt

MAPS = {"NorthAmerica": "Zestafona", "Europe": "Ozeti", "Kavkazi": "Bakurani",
        "Zestafona": "Zestafona", "Ozeti": "Ozeti", "Bakurani": "Bakurani"}
CONDITIONS = {
    "DayStartClear": "Early morning • Clear",
    "DayEarlyClear": "Morning • Clear",
    "DayEarlyFog": "Morning • Fog",
    "DayClear": "Day • Clear",
    "DayLateClear": "Late day • Clear",
    "DayLateGray": "Late day • Overcast",
    "DayLateGrayFog": "Late day • Fog",
    "DayEndClear": "Evening • Clear",
}
POST_WINDOW = dt.timedelta(hours=3)
CLOCK_LEEWAY = dt.timedelta(seconds=30)


def confirmed_next_round(status: dict | None, match: dict,
                         *, now: dt.datetime | None = None) -> dict | None:
    """Only a genuinely observed next map+lighting pair is publishable.

    Some WARCON anonymous status feeds omit lighting. We then skip posting
    rather than claim conditions the public API cannot verify.
    """
    if not isinstance(status, dict) or status.get("ok") is not True:
        return None
    if not isinstance(match, dict):
        return None
    old = MAPS.get(match.get("map"))
    new = MAPS.get(status.get("map"))
    conditions = CONDITIONS.get(status.get("lighting"))
    if not old or not new or new == old or not conditions:
        return None
    try:
        end = dt.datetime.fromisoformat(match["endedAt"].replace("Z", "+00:00"))
        observed = dt.datetime.fromisoformat(status["observedAt"].replace("Z", "+00:00"))
        at = (now or dt.datetime.now(dt.timezone.utc)).astimezone(dt.timezone.utc)
        if end.tzinfo is None or observed.tzinfo is None:
            return None
        end, observed = end.astimezone(dt.timezone.utc), observed.astimezone(dt.timezone.utc)
    except (KeyError, ValueError, TypeError, AttributeError, OverflowError):
        return None
    # Real observed data must follow match end and be recent at message time.
    if observed < end - CLOCK_LEEWAY or observed > at + CLOCK_LEEWAY:
        return None
    if at - observed > dt.timedelta(minutes=15):
        return None
    if at - end > POST_WINDOW or at < end - CLOCK_LEEWAY:
        return None
    return {"map": new, "conditions": conditions, "observedAt": observed.isoformat(),
            "source": "WARCON public observed server status"}
