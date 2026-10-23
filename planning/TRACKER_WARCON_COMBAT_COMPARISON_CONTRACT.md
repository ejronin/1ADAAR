# WARDOGS Tracker × WARCON — player intelligence comparison contract

Status: staging design and implementation guardrails (2026-10-22). **No cross-server daily figures are currently available in 1ADAAR.** Do not publish imaginary shares or mock combat as actual history.

## Source audit (confirmed)

**WARDOGS Tracker** public API, [documented endpoints](https://wardogstracker.gg/developers), OpenAPI `https://wardogstracker.gg/api/v1/openapi.json`:

- `GET /players/{steamId}`: **current synchronized game-account snapshot**, including overall level, career XP, six roles (each level/XP), unlocked-item count, leaderboard rank/count, optional Steam avatar URL and privacy-filtered economy. **Not combat totals; not daily samples.**
- `GET /players/{steamId}/unlocks`: inventory of unlocked items; private fields may be withheld. Not implemented into this narrow owner-test PR; no loadout builder requested.
- `GET /servers/{slug|serverId}/leaderboard?range=24h|7d|30d|all`: **one claimed community server with a connected kill feed**. Aggregated kills/deaths/headshots, longest kill and top weapon. Not a per-day series; not a global per-player across-all-servers feed.
- The Tracker page shows community-server combat in the **Combat** tab. Its own message says kills on official and disconnected community servers are NOT counted. Thus “all WARDOGS kills” would be false.

**1ADAAR / public WARCON**:

- `docs/data/players.json`: server-specific career counters from current WARCON leaderboard API. They are *not* a daily combat history.
- `docs/data/matches.json`: archived completed match data. As verified today, `matches: []`. No completed-match evidence for a per-day player series yet.
- `docs/data/history/*.json`: retained server career leaderboard snapshots (180-day scheme); snapshot differences are not equivalent to daily kills when coverage, resets, faction changes or corrections are unknown.
- WARCON's private kill feed may capture timestamped server combat, but cannot be exported as game-wide. Any authenticated server source requires owner permission and privacy-sanitized transfer.

## Chart choices

1. **Role radar** — six source-qualified role levels, scale /100; retain exact XP table. A zero level / zero XP is measured zero, not missing.
2. **Role specialization dot/lollipop plot** — same verified role levels, easier visual comparison and accessible labels. No duplicate progress-bar collection.
3. **Unlocks, leaderboard rank** — separate compact numeric cards; null/private/unranked display `—`, not zero. Ranking needs denominator and Tracker's eligible-synced-player scope.
4. **1AD daily combat vs other connected community servers:** when two *comparable complete* per-player daily kill-feed datasets exist, use **stacked day columns**: 1AD share (green) and *other Tracker-covered server events* (neutral) on a common daily UTC or America/New_York boundary (declare which). For kills and deaths use separate series / tabs; never stack one against the other as parts of one total.
5. **If cross-source subset membership or coverage cannot be verified**, instead use **two adjacent dot/line series** under clearly separated source headings, not an additive chart or a percent-share. Always display actual capture windows, participating servers and caveats.
6. **Box-and-whisker** is useful for the *distribution of per-completed-match K/D or kills* after enough observations (e.g. 10 independent matches) and coverage checks. It is NOT a good chart for two daily counts. Avoid undefined K/D when deaths are zero; display counts and annotate the zero-death handling. If too few matches, use individual-match dot points rather than an invented distribution.
7. **Season/milestone bars** require verified game-season ID, threshold schedule and series. The current public `/players/{steamId}` response does not document milestone target/next-up fields. Do not derive “75 XP to next Recon level” from cumulative XP without a verified progression curve.
8. **Steam profile avatar**: use Tracker's allowlisted `player.avatarUrl` after server authorization, not a guessed URL from a visible name. For anonymous search/compare, a separate approved public-avatar lookup must match the player's one-way WARCON key without publishing raw SteamID.

## Eligibility gates for a daily proportional chart

- Same authenticated and verified player identity (Steam account proof), same calendar date + timezone + season, compatible kill/death event definitions.
- Verified *Tracker-covered* total events containing 1AD, not “all game servers.” Account for missing or duplicated events, match resets and possible kill-feed overlap.
- Coverage fraction known: do not treat a missing event/day as 0 or assume 1AD kills are a subset unless the same event universe is established.
- Report `1AD recorded kills`, `other Tracker-covered kills`, `total matched recorded kills`, `1AD share = 1AD/total` **only if every inclusion check passes**. If Tracker coverage doesn't include 1AD, no subtraction is allowed.
- A public `servers/{server}/leaderboard?range=30d` summary cannot be divided into days just because a daily axis exists.
- On 2026-10-22, `docs/data/matches.json` has 0 archived completed matches. The page therefore shows an explicit no-data comparison viewport, not fake daily columns.

## Rollout

- **Now (staged)**: game-wide radar, exact role XP, six-role dot plot, unlock count, eligible rank, optionally shown Steam PFP, and clearly labeled empty combat comparison.
- **After real matches/feeds**: WARCON per-match distribution, player/day 1AD kills and deaths using consistent time boundaries and capture integrity.
- **Only with new supported Tracker daily API or approved cross-server feed integration**: verified 1AD subset share of Tracker-covered matches; if unavailable, keep separate measurements and sources.
- No 1AD publication from an unmerged PR without owner approval. The narrow owner-test page is optional and does not change production WARCON, Discord or player pages.
