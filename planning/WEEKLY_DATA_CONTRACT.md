# Weekly Intelligence calculation scaffold — staging only

This stage adds src/weekly.py and tests/test_weekly.py. The engine only processes sanitized, already-published completed matches and returns inert JSON-compatible candidate data. It has no WARCON request, disk writer, scheduler, Discord delivery, or published page.

- Weekly window is Sunday noon to Sunday noon America/New_York, including daylight saving changes.
- Weekly views crossing an official season transition split into separate seasonal summaries; Season 2 starts 2026-10-15T16:00:00Z. Season 3 requires verified official start metadata before publishing.
- Records are limited to 1ADAAR's most recent 120 matches. The module explicitly marks week completeness unproven and must never send a winner as if the entire weekly history were known.
- Faction appearances are distinct player-match appearances, not join events. Recorded participation seconds are assigned to the final match faction and do not establish exact time after faction switches.
- Headshot and longest-shot awards are suppressed when the kill feed isn't confirmed for the analyzed matches. Season-wide best K/D (more than 20 matches in that season), character levels and true join counts remain unavailable.
- Stored awards contain re-sanitized player display names but no hashed key, raw SteamID, private roster, join code, RCON details or Discord secrets. Conflicting payloads with the same match ID are excluded entirely, with a count exposed for review; byte-identical duplicates count only once.
- publicationEnabled remains false. Sunday Discord posting and the permanent reports page are not yet implemented, pending first live-match validation and coverage design.
- `planning/weekly-preview.html` is a staging-only responsive visual concept with unmistakably fictional values; it is not a report renderer or a deployable Pages artifact.
- The desired UI and acceptance gates are in planning/V1.0.1.md.
