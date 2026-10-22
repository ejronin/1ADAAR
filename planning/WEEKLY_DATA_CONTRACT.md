# Weekly report data rules

`src/weekly.py` calculates proposed weekly results from already-saved, sanitized matches. `tests/test_weekly.py` checks the math and filtering. This part of the project does **not** fetch WARCON, write a published file, schedule a Discord post or choose a winner automatically.

- A reporting week runs **Sunday noon to Sunday noon Eastern**, including daylight-saving changes.
- A week that crosses a season boundary is split by season. Season 2 starts `2026-10-15T16:00:00Z`; don't assign Season 3 until its official start is known.
- The input is limited to the most recent 120 saved matches. That cannot prove a whole week's coverage, so the report must say when its history is incomplete.
- **Faction appearances** count recorded player–match appearances, not the number of times someone joined or switched teams. Participation time is assigned to the recorded final faction; it isn't proof of time spent in each faction.
- Headshots and longest-shot awards need confirmed kill-feed data. Don't publish them when feed coverage is unknown. Character levels, true join counts and season-wide K/D rankings beyond the saved sample are also unavailable.
- Re-sanitize display names before saving awards. Never store SteamIDs, player hashes, join codes, private rosters, RCON details or Discord secrets in award output.
- Identical duplicate match records count once. If two records share a match ID but disagree, exclude both and record the conflict for review.
- `publicationEnabled` remains `false`. Sunday publishing and a permanent weekly archive still require first-match checks and coverage approval.
- `planning/weekly-preview.html` is an example layout with fictional numbers, not a production report generator.

The reporting requirements and release checks are in [`V1.0.1.md`](V1.0.1.md).
