# Weekly report data rules

`src/weekly.py` calculates results from matches 1ADAAR has saved. `src/weekly_publish.py` creates the Sunday archive and Discord post, using the approved navy card in `src/weekly_card.py`. Nothing here fetches WARCON directly or guesses the winner of a match.

- A reporting week runs **Sunday noon to Sunday noon Eastern**, including daylight-saving changes.
- A week that crosses a season boundary is split by season. Season 2 starts `2026-10-15T16:00:00Z`; don't assign Season 3 until its official start is known.
- The input is limited to the most recent 120 saved matches. That cannot prove a whole week's coverage, so the report must say when its history is incomplete.
- **Faction appearances** count recorded player–match appearances, not the number of times someone joined or switched teams. Participation time is assigned to the recorded final faction; it isn't proof of time spent in each faction.
- Headshots and longest-shot awards need confirmed kill-feed data. Don't publish them when feed coverage is unknown. Character levels, true join counts and season-wide K/D rankings beyond the saved sample are also unavailable.
- Re-sanitize display names before saving awards. Never store SteamIDs, player hashes, join codes, private rosters, RCON details or Discord secrets in award output.
- Identical duplicate match records count once. If two records share a match ID but disagree, exclude both and record the conflict for review.
- A verified WARCON winner is required before a match counts toward a player's win award or a faction's match wins. Pending and disputed winners are never inferred from player results.
- Podium kills are the total recorded per player for the featured season that week. Map leaders are per-map recorded kill totals, not career totals or a single-match record. A 20-match weekly K/D award requires 20 saved matches with valid kills/deaths and at least one death.
- Sunday publication is eligible after noon Eastern. The first eligible window ends October 25, 2026. GitHub Actions may run a few minutes late. Discord is not contacted when the archive is empty.
- The approved navy artwork is used for real weekly results. The separate preview renderer is test-only and contains fictional examples.

The reporting requirements and release checks are in [`V1.0.1.md`](V1.0.1.md).
