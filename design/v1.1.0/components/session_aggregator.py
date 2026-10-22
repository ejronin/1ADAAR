"""Pure, privacy-gated activity aggregation for future authorized WARCON sessions.

Prototype component only; NOT a collector and NEVER reads remote credentials.
No player identifiers are copied into the resulting public-safe aggregate.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from statistics import median
from zoneinfo import ZoneInfo

MAX_WINDOW_DAYS = 366
MINUTE = 60.0


def _instant(value: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError("Invalid timestamp")
    try:
        when = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError("Invalid timestamp") from error
    if when.tzinfo is None or when.utcoffset() is None:
        raise ValueError("Session timestamps must contain UTC offset")
    return when.astimezone(timezone.utc)


def aggregate_player_sessions(
    sessions: list[dict],
    *,
    window_start: str,
    window_end: str,
    zone: str = "America/New_York",
    capture_complete: bool = False,
    publication_approved: bool = False,
) -> dict:
    """Aggregate elapsed time by local calendar date and weekday/hour.

    NEVER call this for public Pages data unless access, player-specific
    publication and coverage disclosure have been explicitly authorized.
    Overlapping/repeated records are merged; open sessions are omitted rather
    than counted as zero duration. Under-covered days remain unknown.
    """
    if not publication_approved:
        raise PermissionError("Player session publishing needs explicit authorization")
    if not isinstance(sessions, list):
        raise ValueError("Session rows must be a list")
    tz = ZoneInfo(zone)
    start, end = _instant(window_start), _instant(window_end)
    if end <= start or end - start > timedelta(days=MAX_WINDOW_DAYS):
        raise ValueError("Invalid or excessive aggregation range")
    clipped = []
    skipped = 0
    for session in sessions:
        if not isinstance(session, dict):
            skipped += 1
            continue
        try:
            joined = _instant(session.get("joinedAt"))
            left = _instant(session.get("leftAt"))
        except (ValueError, TypeError):
            skipped += 1
            continue
        if left <= joined:
            skipped += 1
            continue
        a, b = max(start, joined), min(end, left)
        if b > a:
            clipped.append((a, b))
    clipped.sort()
    merged = []
    for a, b in clipped:
        if merged and a <= merged[-1][1]:
            previous_a, previous_b = merged[-1]
            merged[-1] = (previous_a, max(previous_b, b))
        else:
            merged.append((a, b))
    hourly = [[0.0] * 24 for _ in range(7)]  # Monday=0
    calendar = {}
    for joined, left in merged:
        time = joined
        while time < left:
            # Step on UTC hour boundaries. Conversion at each step correctly
            # counts 01:00 twice when Eastern time falls back during DST.
            next_utc_hour = time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            next_time = min(left, next_utc_hour)
            minutes = (next_time-time).total_seconds()/MINUTE
            local = time.astimezone(tz)
            key = local.date().isoformat()
            calendar[key] = calendar.get(key, 0) + minutes
            hourly[local.weekday()][local.hour] += minutes
            time = next_time
    total_minutes = sum(calendar.values())
    durations = [(b-a).total_seconds()/MINUTE for a, b in merged]
    return {
        "schemaVersion": 1,
        "source": "WARCON protected player session join/leave intervals",
        "metric": "observed elapsed session minutes (overlaps de-duplicated)",
        "timezone": tz.key,
        "windowStart": start.isoformat().replace("+00:00", "Z"),
        "windowEnd": end.isoformat().replace("+00:00", "Z"),
        "coverage": "complete" if capture_complete else "partial/unknown",
        "skippedIncompleteSessions": skipped,
        "sourceSessions": len(clipped),
        "mergedIntervals": len(merged),
        "observedActiveDays": len(calendar),
        "observedMinutes": round(total_minutes, 2),
        "medianObservedIntervalMinutes": round(median(durations), 2) if durations else None,
        "minutesByDay": {k: round(v, 2) for k, v in sorted(calendar.items())},
        "minutesByWeekdayHour": [[round(x, 2) for x in row] for row in hourly],
    }
