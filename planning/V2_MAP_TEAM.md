# Map and faction performance — v1.1.0 plan

This is the design direction for the map/faction page, developed in [staging PR #22](https://github.com/ejronin/1ADAAR/pull/22). It isn't production approval; v1.0.1 stays live until the finished staging build is reviewed.

## Branding and navigation

- Retain the exact official 1AD emblem and official WARDOGS branding, not recreated words or lookalike logos.
- Main site and player pages: charcoal, black, white and green; faction identity uses the authentic source-derived emblems and faction colors.
- Weekly Roundup uses amber/gold with gold/silver/bronze podium recognition.
- V2 build order: (1) redesigned player profile, (2) Map & Team Performance drill-down, (3) top-three weekly community spotlight, (4) verified Discord membership/consented profile picture, (5) real season-specific public ranking, (6) completed permanent history and player comparison staging features.
- Community spotlight **must not** rank a player as Discord-eligible based on name similarity, public Steam ID lookup or a guessed avatar. Eligibility needs opt-in verified Discord association and membership at the cutoff; nonmembers remain in ordinary public server statistics.

## Page layout

**Main player profile** (`players.html#player-<64-char-hash>`):
- Header and all-time WARCON career cards, recent captured match performance, radial data visualizations only for supported measures.
- Two small preview panels: results by map and by faction, each labeled 'Saved matches only'; link to **See full map & team results**. Never use an all-time leaderboard result to fill a captured-match gap.
- Share links contain the existing pseudonymous hash, not raw Steam IDs.

**Secondary page** (`map-team.html?player=<hash>&season=all|wardogs-2`):
1. Player name and source, clear scope explanation; back to their player profile.
2. Summary metrics: saved matches with recorded player results, unique maps, eligible recorded win rate, best map *only if the sample qualifies*.
3. Radial progress: win rate from recorded outcomes and three known faction appearances as shares of recognized faction appearances, with numerals/labels for assistive tech. Never invent a 'skill', accuracy or reflex score.
4. **Map performance**, Image 2-inspired rows: map, match appearances, outcomes, recorded wins percentage, kills/deaths (K/D only if deaths > 0), recorded time, and a visual bar whose value is printed in text.
5. **Faction performance** with official emblems: participation counts, recorded outcomes, K/D, time, and win percentages. Faction **appearances** are not unique join events.
6. **Map + faction** cross-tab for drill-down on a specific location and team.
7. Filters for season and sorting (matches, recorded win rate, kills, playtime). Only official, locally documented season boundaries; do not mix seasons, label unknown outcomes 'Not recorded'.
8. Empty state: 'No saved completed matches for this player yet' if no captured match includes the player. Never use sample/demo figures on this page.

## Statistics and source

Source: only completed, sanitized `schemaVersion:2` WARCON match records preserved by `src/season_archive.py`.
Season is assigned by official match end timestamp. One match counts once for a player, whether or not the team result is present.

- **Matches played (saved)**: count of completed captured match rows containing this player's pseudonymous key.
- **Wins/losses/draws**: count only known `player.result` values; missing outcome tracked separately and excluded from recorded win-rate denominator.
- **Win rate**: `wins / (wins + losses + draws)`. Show '—' when there are zero matches with a recorded result, and disclose the denominator.
- **K/D**: `sum(kills) / sum(deaths)`. Show '—' when recorded deaths are zero; never label a no-death sample '0 K/D'.
- **Time played**: sum of this player's `seconds` on captured match rows; not automatically the full match duration.
- **Headshots, accuracy, and longest shot**: excluded until complete and verified kill-feed coverage is established.
- **Best recorded map**: eligible maps need at least **5 matches with known player outcomes**. Sort by win rate, then wins, then count; equal top results are labeled tied, not arbitrarily crowned. Without 5 valid outcomes show 'Not enough matches yet'.
- **Faction distribution**: percentages of matches with *known faction names*. An unassigned team should not quietly lower known-team shares.
- **Unknowns**: no disguised 0 values. Keep unknown outcome counts visible; unassigned maps/teams show neutral labels.
- The old top-120 match window is **not** the full source: v2 uses the immutable captured season/month archive. The archive can still miss matches that WARCON did not return or GitHub Actions failed to fetch.

## Build and privacy rules

- A single GitHub Actions full collector pass precomputes privacy-safe summaries; no new WARCON fetch, server, Discord webhook, hosting bill or browser-side heavy archive reads.
- Static shard files by first hex character of the existing pseudonymous player key under `docs/data/map-team/`. A player's browser request fetches one shard, not entire month/history.
- Read-only HTML/CSS/JS; DOM text must use `textContent` rather than injecting player names as markup. No profile PFP until avatar permissions and verified identity rules exist.
- Add unit tests for multi-season splits, duplicate match IDs, missing outcomes, thresholded best-map rankings, all-time/season scope separation, privacy and empty states; JavaScript syntax and navigation tests.
- Visual QA on narrow phones and desktop; ensure bars do not require color to convey win/loss outcomes.

## Before release

A successful CI test suite is necessary but not sufficient for real-data validation. Keep staging draft until design and browser checks and the first real captured match can confirm formulas. No merge to production without explicit approval.
