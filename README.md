# 1ADAAR — OneAverageDan After-Action Report

[Open 1ADAAR](https://ejronin.github.io/1ADAAR/) · [WARCON match records](https://console.warcon.app/s/e30a7ee9-7ea5-4633-882e-98d2e0c03342/matches)

1ADAAR is the match-report and player-stats site for the **OneAverageDan WARDOGS Community Server**. It shows results saved through WARCON, career statistics, trends, map and faction breakdowns, and community reports. This is a community project, not an official developer-run server.

The site runs on GitHub Pages. GitHub Actions pulls approved public data from WARCON and prepares Discord match recaps. The pages themselves are static: opening a player profile does not start a server job or query WARCON directly.

**Data isn't live.** GitHub schedules can run late or be skipped. Server status is based on the latest successful reading and becomes **Status unknown** when stale. Check [WARCON](https://console.warcon.app/s/e30a7ee9-7ea5-4633-882e-98d2e0c03342/matches) for a fresher server reading. Public status may also be disabled even when a logged-in WARCON admin can see the server.

## How it works

| Part | What it does |
|---|---|
| WARCON | Supplies public server, leaderboard and completed-match records |
| GitHub Actions | Collects the public data, saves the approved fields and builds recap images |
| GitHub Pages | Serves the dashboard, JSON data and browser-rendered charts |
| Discord webhook | Posts the recap after a new, verified completed match |

No personal computer, always-on bot or paid website server is required for the existing public dashboard. GitHub Actions and Pages still have usage limits and scheduled jobs are not a real-time service.

### Main pages

- **Match reports:** completed matches, final faction scores, map and report links. An unfinished match is not published as a result.
- **Player lookup:** searches the available public WARCON player index by in-game name or supplied SteamID64. The entered ID isn't displayed in the resulting page.
- **Player dossier:** career totals from WARCON, saved-match summaries and historical snapshots. These cover different time periods and should not be treated as interchangeable.
- **Map and faction breakdown:** comparisons based on matches that 1ADAAR has actually saved. It does not claim to include every match ever played.
- **Activity and weekly reports:** recorded match starts and eligible community results. Missing source data stays missing; sample PlayerOne figures are always fictional.

The public leaderboard import is capped by WARCON's available pages: up to 20 pages of 50 entries, or 1,000 players. Being outside that index does not mean a player has never visited the server.

## For maintainers

### First-time setup

1. In WARCON, enable public leaderboards and careers for this server. A disabled public endpoint cannot be worked around by the website.
2. Create a dedicated Discord webhook in `#match-recap`, named something like **1ADAAR Match Reports**.
3. Add its URL as the GitHub Actions repository secret `DISCORD_MATCH_WEBHOOK`. Never place it in a source file, issue or chat.
4. Set GitHub Pages to deploy through **GitHub Actions** in repository settings.
5. Manually run **Collect WARCON and publish 1ADAAR** from the Actions tab. The initial import establishes a baseline without reposting the older match history.
6. Check the published site, player lookup and new-match behavior. Run **Deploy dashboard to GitHub Pages** if the site needs its first deployment.
7. Protect `main` using repository rules, required checks and pull-request review. Confirm the collector still has the permissions it needs for routine data updates.

The official 1AD, WARDOGS and faction artwork is already in `docs/assets/`. Do not replace those files with recreated logos.

### Routine updates

The main collector aims to run about every ten minutes. It checks WARCON match pages and fetches details for newly completed matches; work on a separate lighter status check is documented in [the v1.0.1 plan](planning/V1.0.1.md). GitHub timing is best-effort, so the timestamp shown on the website matters more than the schedule.

A match is posted only after WARCON reports an end time and usable final scores. The collector keeps a delivery checkpoint to avoid repeat posts in normal operation. A failure between Discord accepting a message and saving the checkpoint **can** still produce a duplicate on retry; this isn't an exactly-once delivery system.

The recent match list keeps up to 120 completed reports in the published view. Older recorded matches and season information may live in separate retained archives. Career history is also bounded: up to 60 changed daily observations over 180 days per player, stored across 16 JSON shards. A snapshot is taken only when a successful leaderboard read provides real data. Earlier history is never filled in afterward.

PlayerOne is a **fictional test profile** used for design and chart checks. It does not appear in the real leaderboard, match archive or ordinary Discord deliveries.

### Test locally

Run the checks from the repository root:

```sh
python -m unittest discover -s tests -v
python -m http.server 8000 --directory docs
```

Visit `http://localhost:8000/`. To inspect collection without writing data or posting to Discord, run:

```sh
python -m src.recap --dry-run
```

For one clearly marked test Discord delivery, use **Actions → Verify Discord match recap webhook → Run workflow**. This uses the existing webhook secret, does not add a real match to the archive, and must not be confused with a live result.

### When something goes wrong

- **Status looks stale:** compare the displayed observation time with WARCON, then check the most recent Actions run.
- **No new match report:** confirm that WARCON has an ended match with final scores, and check the collector logs and delivery checkpoint. Don't post a fictional result as a workaround.
- **Missing player:** check WARCON's public leaderboard settings and the 1,000-entry index limit.
- **Charts or a page fail:** use a local static server, inspect the data files and run the tests. Preserve working data while checking the cause.
- **Public WARCON API fails:** retain the last known good published data where possible; let the job report its failure rather than inventing new values.
- **WARCON stats look wrong:** do **not** use WARCON's **Purge Stats** control. It permanently removes recorded results.

## Statistics and their limits

The dashboard combines several sources, each with its own scope:

| Source | Safe use | Important limit |
|---|---|---|
| WARCON public leaderboard | Career kills, deaths, wins, matches, playtime and permitted combat totals | A bounded public index and snapshots, not private account history |
| Saved completed matches | Match-level kills/deaths, results, map and faction comparisons | Only matches actually captured by 1ADAAR |
| Saved career snapshots | Changes in career totals or career K/D over time | Starts when collection starts; no invented earlier points |
| Recorded match-start activity | Server-wide day/hour heatmap | Counts starts, **not** individual players' online hours |
| Optional kill feed | Specific cause, headshot or distance measurements when present | Coverage and identity matching must be verified before player-specific weapon claims |
| WARDOGS Tracker (separate service) | Optional synced account progression for consenting players | Not a WARCON/RCON feed or automatic Steam account connection |

Current design work also covers the six-role progression radar (Assault, Medic, Support, Recon, Driver and Pilot), overall WARDOG level, career XP, and separately hidden account cash/gold. These come from accessible, synced **WARDOGS Tracker** profiles, not the dedicated-server RCON player list. Nothing is connected merely by opening an external sync link. A durable, cross-device opt-in requires a separately approved secure identity and consent service; see [the integration plan](https://github.com/ejronin/1ADAAR/blob/design/v1.1.0-ia-handoff/design/v1.1.0/research/PLAYER_PROGRESSION_OPT_IN_IMPLEMENTATION.md) on the design branch.

No equipped loadout, player movement heatmap, aim accuracy, time-to-kill or six-role *combat-performance* score should be inferred from unrelated fields. Weapon kills-with/deaths-by comparisons remain out of scope until the kill feed supports reliable attribution.

### Privacy

The public site contains player names, approved performance totals and SHA-256-derived lookup keys. These keys are **pseudonymous, not anonymous**: they can be compared with candidate Steam IDs and cannot serve as authentication credentials.

Never publish raw SteamID64 values, RCON credentials, WARCON private API keys, Discord webhook URLs, staff notes, login tokens or private session data. Don't commit hidden account cash/gold to `docs/data/` or Git history. A `.gitignore` change does not remove anything already committed.

Sharing a player profile uses its public lookup key; sharing a match uses its recorded match link. The PlayerOne share option is visibly marked as fictional. Keep user mentions disabled in webhook posts.

## Branding and UI

Use the original community 1AD emblem, WARDOGS press artwork and the matching faction symbols. Lonestar is blue, Valkyra red and Manticore green. Ordinary dashboard screens use charcoal and restrained green; the weekly podium uses gold, silver and bronze. Design work should stay accessible on mobile, support reduced-motion preferences and avoid decorative graphics that imply unsupported numbers.

Python Pillow/CairoSVG produces the Discord artwork in GitHub Actions. Browser charts use published JSON and JavaScript/SVG. Don't add a framework just for the appearance of sophistication; any new tooling needs an implementation reason and working staging preview.

## Development and release notes

The release and design details are still being reviewed on their staging/design branches. Those links are marked by their branch and do not mean the work has shipped:

- [Release requirements and checks](https://github.com/ejronin/1ADAAR/blob/design/v1.1.0-ia-handoff/planning/V1.1.0_RELEASE_GATES.md)
- [Current design handoff and prototypes](https://github.com/ejronin/1ADAAR/blob/design/v1.1.0-ia-handoff/design/v1.1.0/README.md)
- [Technology assessment](https://github.com/ejronin/1ADAAR/blob/design/v1.1.0-ia-handoff/design/v1.1.0/research/FRONTEND_GRAPHICS_TECHNOLOGY_ASSESSMENT.md)
- [WARCON and RCON field notes](https://github.com/ejronin/1ADAAR/blob/design/v1.1.0-ia-handoff/design/v1.1.0/research/RCON_WARCON_FIELD_INVENTORY.md)
- [Player progression opt-in setup](https://github.com/ejronin/1ADAAR/blob/design/v1.1.0-ia-handoff/design/v1.1.0/research/PLAYER_PROGRESSION_OPT_IN_IMPLEMENTATION.md)
- [v1.0.1 release and weekly reporting](planning/V1.0.1.md)
- [v2-named work that is planned for the v1.1.0 release](https://github.com/ejronin/1ADAAR/blob/design/v1.1.0-ia-handoff/planning/V2.0.md)

The current design handoff is in [PR #28](https://github.com/ejronin/1ADAAR/pull/28). It is a **design reference**, not something to merge straight into production. The implementation engineer builds on staging, provides the actual working preview and test results, and the owner approves the final appearance and behavior before any production deployment.
