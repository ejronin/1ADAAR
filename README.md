# 1ADAAR — OneAverageDan After-Action Report

**What it is:** A public WARDOGS community dashboard showing finished matches, player stats, performance trends, and a link to the 1AD Discord.

**Where to use it:** https://ejronin.github.io/1ADAAR/

**How the data gets there:** WARCON records game activity. GitHub periodically copies approved public stats, makes the website available, and posts a Discord recap after a newly completed match. Opening a player profile **does not start a GitHub job or query WARCON**; the charts are calculated in your browser using the published data.

**Server-status accuracy:** WARCON's own page is the freshest place to check whether the server is running. The 1ADAAR indicator uses the last successful GitHub update and will show **Status unknown** when it has no recent reading. GitHub's schedule is not a real-time guarantee. You can use **Check status on WARCON** next to the indicator for an authoritative view. If the public server-status API is disabled by its administrator, 1ADAAR cannot read it, even if WARCON's logged-in panel shows the server as live.

**Privacy:** SteamID64 values, RCON passwords, Discord webhook URLs and administrative logs do not belong in the public website. Player names, totals and hashed lookup keys are intentionally public; hashed keys are pseudonymous, **not truly anonymous**. Anyone with access to GitHub can view files committed to this public repository, even if they aren't linked on the website.

**Want technical setup or maintainer details?** Everything below this section is documentation for administrators and contributors.

---

## Maintainer and deployment reference


**One match. One recap. One linked dossier. No paid backend.**

Production-oriented static dashboard and scheduled Discord recap workflow for the 1OF1-hosted OneAverageDan WARDOGS server. The WARCON public API supplies historical match results; GitHub Actions takes snapshots and posts to Discord; GitHub Pages presents the player-friendly dashboard.

- Dashboard: `https://ejronin.github.io/1ADAAR/` (GitHub Pages).
- Data source: `https://console.warcon.app/s/e30a7ee9-7ea5-4633-882e-98d2e0c03342/matches`
- Repository: `https://github.com/ejronin/1ADAAR`
- This project does **not** require the game's RCON password, 1OF1 login, WARCON API key, or a running personal computer.

## One-time deployment checklist

1. Keep **WARCON → Server Settings → Public leaderboards and careers** enabled. The code only calls public `/api/public/servers/.../matches` endpoints.
2. In Discord `#match-recap`, create a **dedicated** webhook named `1ADAAR Match Reports`. Never paste this URL into an issue, code, commit, or chat.
3. In **GitHub → Repository Settings → Secrets and variables → Actions → New repository secret**, create `DISCORD_MATCH_WEBHOOK` and paste the full Discord webhook URL. Only that single secret is required.
4. In **GitHub → Settings → Pages → Build and deployment**, select **GitHub Actions** as source (if not already configured).
5. In **GitHub → Actions**, run **Collect WARCON and publish 1ADAAR** once using `Run workflow`. The first run imports the existing archive **without posting older matches**. New completed matches post automatically on subsequent runs.
6. Run **Deploy dashboard to GitHub Pages** if needed. Open the published Pages URL and verify the data / status / match report link.
7. The community-approved official 1AD logo is already integrated as `docs/assets/1ad-logo.svg`, alongside the tactical hero artwork. No manual logo upload is needed.
8. In repository **Settings → Rules → Rulesets**, protect `main`: require pull requests and successful CI checks for human contributors. Keep repository collaborators to the minimum necessary. GitHub-hosted schedule requires Actions enabled, and branch protection should be tested alongside the bot's data write permissions.

## What is automated

- Every **10 minutes**, the Actions collector polls up to three WARCON match-list pages, then fetches details for new completed matches.
- Abandoned matches, unfinished matches and records without final scores are **not published**.
- New matches after the initial baseline produce one Discord embed with faction scores, map, duration, peak players, optional verified awards and a link to WARCON plus the 1ADAAR dossier.
- A GitHub-committed checkpoint prevents reposting the same match in normal operation. As with webhook delivery systems generally, an interruption *after Discord accepts a post but before the checkpoint is committed* can cause a duplicate on recovery. Do not represent this as transactional exactly-once delivery.
- The Pages dashboard uses sanitized JSON fields, with no SteamID64, RCON passwords, moderation notes, WARCON tokens or webhook URLs.
- Public site is static; no persistent server, database, or paid cloud subscription. Actions and Pages remain subject to GitHub's plan, fair-use, and usage limits; no perpetual availability guarantee.

## Security and operations

- The public repository is intentionally readable, but never stores `DISCORD_MATCH_WEBHOOK` or privileged API keys. `.gitignore` protects common local secrets; **GitHub Secrets** is mandatory for delivery credentials. `.gitignore` cannot erase secrets committed accidentally.
- Scheduled workflows trigger only on the default branch; forks cannot deliver to the real webhook without that secret.
- `allowed_mentions` is disabled for webhook messages. The collector sanitizes usernames and includes no SteamIDs in generated public JSON.
- Fetches are restricted to the WARCON **public** origin and response size capped at 2 MB. Only HTTPS Discord webhook destinations are accepted.
- A manual first-run baseline avoids flooding `#match-recap` with old historical results.
- If WARCON public pages go offline, the collector fails safely and leaves the existing Pages data intact, with GitHub Actions showing failure.
- Never hit **Purge Stats** in WARCON: it irreversibly deletes its recorded match results.
- No Discord bot tokens, WARCON master RCON credentials or host-file changes are required.

## Test locally

```sh
python -m unittest discover -s tests -v
python -m http.server 8000 --directory docs
```

Open `http://localhost:8000/`. Use `python -m src.recap --dry-run` to inspect collector behavior against the live public API without writing data or posting to Discord.

## WARCON source contract

Verified against `warcon-app/warcon`:
- `src/lib/matches.ts` — `MatchSummary`, `MatchView` and `MatchAward` types.
- `src/routes/api/public/servers/[id]/matches/+server.ts` — `{ok,matches,live,page,pageSize,total,pages}`.
- `src/routes/api/public/servers/[id]/matches/[matchId]/+server.ts` — `{ok,match,factions,lines,timeline,awards,kills,hasFeed,feed,more}`.

The WARCON API is unversioned; monitor CI and update the connector if the upstream schema changes. Actual live end-to-end Discord success cannot be asserted until a matching completed match and valid Discord webhook exist.

## Build responsibility / expert reviews

- **Integration engineer:** WARCON schema contract, new-match detection, graceful upstream failure.
- **Discord engineer:** webhook embed limits, mention suppression, delivery/recovery behavior.
- **UX engineer:** accessible, responsive static dashboard and final official 1AD logo.
- **GitHub / security engineer:** least privilege, repository secrets, CI, Pages deployment, rulesets.
- **Delivery owner:** test acceptance, final deployment verification and incident/runbook maintenance.

The roles above are a review plan, not additional people or paid services.

## Phase 1.5 — Official 1AD identity

The public dashboard now uses a transparent vector trace of the **supplied official 1AD logo** for the sidebar emblem, hero graphic and favicon. The source is the community-approved black-and-white mark, not an AI-generated lookalike. The accent palette is 1AD green over a dark tactical-map backdrop (`docs/assets/tactical-terrain.svg`). The Discord icon is a path from [Simple Icons](https://github.com/simple-icons/simple-icons) under its published license. All visual assets are stored locally in this repository, not fetched from a paid service.

The hero and header link to the existing community invitation. `docs/assets/brand.css` is intentionally layered after the existing `style.css`, preserving the match card and data logic. Phase 2 player lookup is **not** enabled by this cosmetic release. This release does not modify match ingestion, API calls, Discord message delivery or webhook secrets.

## Phase 2 — Player intelligence (automatic; no bot)

- Browse `https://ejronin.github.io/1ADAAR/players.html` from the **Player lookup** navigation entry.
- Search by in-game name (partial match) or enter a 17-digit SteamID64. The app clears entered SteamID64 after lookup and never renders the identifier on results pages.
- The collector requests WARCON's **public leaderboard**, `range=all&scope=server&minMinutes=0`, up to the public limit of 20 pages (top 1,000), and saves `docs/data/players.json` automatically. This is an all-time leaderboard *snapshot*, not a private player dossier.
- Career totals include kills, deaths, matches, wins/losses/draws, playtime and seeded minutes. Headshots, vehicle kills and kill streaks are shown only when WARCON indicates its kill feed is enabled.
- Recent-match tables and by-map/by-faction summaries are derived from the **retained 1ADAAR match archive only**, never labeled as complete lifetime statistics. The archive retains up to 120 recorded matches.
- Player identities are matched by an SHA-256 lookup digest based on their SteamID64, not by mutable display name. **No raw SteamID64 is written to any public HTML or JSON artifact.**
- **Privacy limitation:** unsalted one-way digests can be compared against candidate public SteamID64 values, so this is pseudonymization, *not* secure anonymization. There is no public player-to-Steam link or comment feature. Fully private/account-gated lookups would require a backend and authentication, which are intentionally excluded from this architecture.
- WARCON's public interface may be rate limited or its schema may change; leaderboards are not a guaranteed complete roster. If the leaderboard request fails, the collector retains the prior player index and continues ordinary match reporting.
- Deep weapon-by-weapon statistics, accuracy, revives, or military "rank" are intentionally **not claimed** because those are not available in the verified WARCON public leaderboard contract.

**Operational note:** All public data is sourced from WARCON. No Discord slash command, always-on bot, paid database, local computer or game-host INI change is used.

## Official WARDOGS hero photography

The Match Intelligence and Player Intelligence hero backgrounds use the user-supplied WARDOGS official press-pack helicopter screenshot. It is color-graded, cropped and darkened for readable 1ADAAR text without inventing aircraft, uniforms, or other game assets. Source artwork credited to WARDOGS/BULKHEAD. The photograph is part of the GitHub Pages static assets; no external image host or paid service is required.

## WARDOGS branding and Discord one-time smoke test

The homepage and Player Intelligence view show the official **WARDOGS: Tactical All Out Warfare** fullmark alongside community 1AD identity. The game logo was supplied by the community owner and rendered from the original official SVG into a local optimized PNG. Player statistics remain unchanged.

To validate Discord delivery without waiting for live game data, open **Actions → Verify Discord match recap webhook → Run workflow**. The workflow uses the pre-existing repository secret `DISCORD_MATCH_WEBHOOK`, posts **one clearly marked TEST** embed, and prints only Discord's acknowledgment message ID (not the secret). It never writes to match history or the delivery ledger. This workflow also performs one automatic test when first merged with the designated smoke-test commit title; subsequent routine pushes do not repeat it.

**Public index capacity:** WARCON publicly exposes 20 pages of 50 leaderboard rows, so 1ADAAR's lookup indexes a maximum of 1,000 distinct ranked player entries. It is unrelated to Discord member counts or server capacity. Players ranked outside that public cap are not automatically searchable. A 60-day inactivity deletion would erase useful player lookup history and would not remove WARCON's public API cap, so **no destructive 60-day purge has been enabled**. Historical completed-match records remain bounded by the existing match archive policy.


## Visual Discord recaps and test-only PlayerOne demo

- **Actual match delivery** renders a locally generated PNG card from the real WARCON map, mode, duration, faction scores, winner, and supplied match awards. The actual image is attached to a Discord webhook embed, with a clickable verified WARCON report and 1ADAAR links. The image's official WARDOGS artwork is decorative; it is never claimed to be the specific map screenshot.
- No fabricated MVP, K/D, or longest-shot awards appear if WARCON does not supply them. Missing awards are labeled unavailable in the graphic.
- Both the standard collector and the smoke-test Action install a pinned version of Pillow on ephemeral GitHub runners. Nothing runs on a personal machine or paid image-rendering service.
- **Test a card:** GitHub Actions → Verify Discord match recap webhook → Run workflow. This posts one boldly labeled **TEST / FICTIONAL DATA** card using PlayerOne, PlayerTwo, and PlayerThree. It does not touch the production match ledger or leaderboard.
- **PlayerOne preview:** Player Intelligence → **Preview PlayerOne demo stats**. The separately stored \`docs/data/demo-player.json\` includes fictional example K/D, match history, and map/faction results to exercise the *real dossier UI*. It never enters \`players.json\`, \`matches.json\`, the collector or Discord production posts.
- Tests cover PNG generation, multipart payload, test labeling, and fixture separation.

## UI/navigation and complete-match delivery (October 2026)

- The main **Match reports** navigation opens the existing archive. Its redundant **Explore match reports** hero button was removed. Player Lookup stays in the navigation rather than appearing again as an extra hero text link.
- On the homepage, **Latest match report** is intentionally hidden until the public WARCON match archive contains a completed match. When available it opens that specific match dossier; a direct GitHub Pages `#match-<id>` link also opens the same dossier from Discord.
- A completed-match Discord image embeds its main title link to the specific **1ADAAR GitHub Pages dossier**; the source WARCON URL remains visible as a secondary provenance link. Webhook posts only for new matches containing WARCON `endedAt` plus verified final faction scores, at the next scheduled collector pass (typically up to ten minutes, though GitHub scheduling can be delayed). A manual smoke test is the only exception, prominently marked TEST.
- At narrow viewport widths, all four unique navigation items are accessible in a compact two-column menu; the previous rule that hid inactive navigation is overridden. Tables can scroll horizontally on small screens while card layouts reflow to one or two columns. The main menu remains keyboard accessible without JavaScript.


## Community sharing and onboarding

- The **New to WARDOGS?** panel beneath the match archive explains that server join instructions are in the OneAverageDan Discord and links to the existing permanent invite. It creates no new Discord invite or sidebar item.
- **Share match** appears only inside a real completed-match dossier and shares the exact GitHub Pages `index.html#match-<id>` deep link. It cannot fabricate a match when WARCON has no results.
- **Share player stats** appears only on a resolved, real public player dossier and shares `players.html#player-<public lookup key>`. The URL contains no raw SteamID64 or Steam-community profile link. The key is derived from the identifier and should not be represented as secret or anonymous.
- **Share demo profile** publishes a link to the clearly labeled fictional PlayerOne page, separate from actual player records.
- On phones, the native share sheet is used where supported. Otherwise, the URL is copied; browsers denying clipboard access display a selectable link. No tracking scripts or third-party share service are used.


## Branded community profile sharing

- **Share Player Stats** on a verified player dossier now shares the copy `Check out my stats on the OneAverageDan WARDOGS Community Server!` plus that individual profile URL and the existing 1AD Discord invite.
- The native mobile share sheet includes the community message and the report URL. Clipboard-based sharing copies the complete multi-line message rather than only a URL. When clipboard permissions are unavailable, a selectable multiline message appears.
- The PlayerOne demo share message is similarly branded but explicitly marked **DEMO / fictional**, and it never links to a real user's Steam profile.
- **Share Match** retains its existing link-only behavior. No changes to WARCON integration, Discord webhooks, data indexing or match delivery.


## Phase 3 — Player Performance Analytics

- The Player Intelligence dossier adds **Performance Over Time**: match K/D, kills versus deaths, five-match rolling K/D, and actual career K/D snapshots, using a single interactive, responsive chart. The selector offers last 10/25/all available observations. The graph is calculated in the browser from published data with no new on-demand WARCON calls.
- Career snapshots are captured by the existing collector **only on successful WARCON leaderboard reads**, no more than once per player per UTC date; same-day changes replace the earlier point. The first genuine snapshot is captured only when a player has nonzero match or combat activity. No history is manufactured before tracking begins.
- Snapshots contain only the already-public SHA-256-derived lookup key and counters, **never raw SteamIDs or player names**. They are stored in 16 one-hex-prefix JSON shards under `docs/data/history/`, so browser loads are limited to the selected player's shard.
- Retention is capped at **60 changed daily observations / 180 days per player**, **125 player tracks per shard** (2,000 overall maximum). History is a bounded trend window, not a forever record, and is independent of the archive's latest 120 server matches.
- The **PlayerOne demonstration** uses explicitly fictional match and career history, loaded from local static JavaScript with no API fetch. Live production JSON never contains fictional records.
- No new hosting services, bot, database, tokens, subscriptions, webhook posts or collector polling intervals. The GitHub Actions job that already publishes players and matches also commits only changed history shards.

## Faction emblems and color identity

- The Lonestar **blue**, Valkyra **red**, and Manticore **green** SVGs in `docs/assets/factions/` are compact vector contours derived from the three faction emblem images supplied for 1ADAAR. Each retains the source emblem silhouette and official team color identity; they are not invented stock graphics. Unknown WARCON faction names remain readable in neutral styling.
- Faction identity is applied to the Player Intelligence faction panel, recent-match table, completed match card winner, faction score bars, and match dossier player scoreboard. All retain actual text labels and adequate dark-mode contrast, including mobile layouts. No synthetic team stats are introduced into WARCON.

## Server status and Discord faction recap

- The homepage includes a read-only WARCON status panel updated by the existing scheduled collector (~10-minute cadence). It shows **connected players** and **current map** only when a fresh, confirmed online observation exists. Empty servers may correctly show **0 players**. The public WARCON status endpoint does **not** expose an explicit restarting flag: yellow **RECONNECTING** indicates a fresh server-unreachable observation immediately after a confirmed online state, *not* proof of a restart; the next unreachable observation becomes red **OFFLINE**. Unknown or stale data stays neutral, never falsely green/red. Red strobes; yellow and green pulse; prefers-reduced-motion disables animation.
- The browser refreshes the GitHub Pages snapshot approximately every 2 minutes while visible; actual observation cadence is approximately every 10 minutes via GitHub Actions. Server status is therefore **near-live, not instant**; the observed time is displayed.
- `docs/data/server-status.json` is published as part of the Pages artifact **without being git-staged**, so frequent status timestamps/player counts do not generate Git commits. The small `server-status-state.json` file commits **only when state changes** to identify an online-to-offline transition. Private roster, Steam IDs, join code and RCON information are not published in 1ADAAR.
- Discord recap PNGs use the **same official-source faction SVG artwork** as the site and each faction's correct team color. The renderer reads only repo-local assets and renders only verified WARCON faction labels; no fake scores or extra Discord posts are introduced.


## Advanced analytics — verified feasibility (October 2026)

WARCON's **public match detail** contains score, map, faction, per-player kills/deaths/playtime and awards. If the kill feed is transmitting and the public match kill-feed pages are available, events additionally contain weapon/cause tags, timestamps, killer/victim names and factions; kill-feed pages are paginated and can be rate-limited. An event's cause may describe a vehicle/environment rather than a specific rifle. Show only named verified metrics, e.g. **Most kills by weapon**; do not call kill counts **most used** or **favorite** without loadout/usage telemetry.

No verified public event supports true bullet-to-death **TTK**, precise **life span from spawn to death** or **player levels**. Missing firing/damage/spawn/level telemetry is not an invitation to infer or fabricate these metrics. Player-level per-weapon K/D is also not a simple public-contract feature: public kill events identify people by names rather than pseudonymous player keys, so joining historical names to account-specific player profiles could misattribute events. If later added, build bounded, sanitized **aggregate match/faction weapon counts**, not raw named kill logs in the public repo.

Website requests download static, published files from GitHub Pages; charts calculate locally. Heavy aggregation, if introduced later, should run **once per new completed match** inside the existing scheduled collector and publish only compact approved statistics. Never fetch hundreds of WARCON event pages per dashboard visitor. Currently match archive contains the most recent 120 completed server matches, player index up to 1,000 entries, and career history up to 60 changed daily observations over 180 days.

### Published player data minimization

The October 2026 audit removed **exact last-seen timestamps** and **in-game cash totals** from live public player JSON because the dashboard does not use them. Names, performance totals and pseudonymous matching keys remain intentionally public. No previously committed file can be made private by adding a .gitignore entry; consider GitHub historical secret scanning separately from current-tree tests. Test fixtures may use clearly synthetic IDs to exercise the sanitizers; production files must never contain raw SteamID64.

**Scheduled update reliability:** GitHub Actions can delay or skip scheduled tasks. The 1ADAAR collector targets minutes 04, 14, 24, 34, 44 and 54 (UTC) rather than the top of each hour. Always rely on the WARCON observation timestamp, and use the live WARCON link when data is old.

## Community ownership and non-placeholder filters

This is the **OneAverageDan WARDOGS Community Server**, operated by the community, **not an official developer-run server**. The server-status panel and page footers state this clearly.

The fictional PlayerOne demo includes 32 completed match observations and 32 aligned career snapshots. Its chart's Last 10 / Last 25 / All Available views show 10 / 25 / 32 genuinely different data points (the static recent-match table intentionally stays at ten). The current window and metric totals update with the selection. The live dashboard never manufactures player observations: a window without enough actual history is disabled with an explanation.

Match-report sorting uses verified completion timestamps and changes the actual report order. With zero or one report visible, sorting is disabled and the reason is shown; it automatically activates when two or more real reports are available. Fictional sample matches stay out of the production WARCON archive and Discord recaps.

## Staged v1.0.1: more frequent, lighter status polling

The proposed v1.0.1 schedule keeps all existing match/player collection and Discord recaps at their current approximately 10-minute interval, plus one **status-only WARCON request at the five-minute midpoint**. GitHub may still delay or skip a scheduled job; this is **not a real-time uptime monitor**. A missing or stale reading becomes neutral **STATUS UNKNOWN**, never red/offline or green/live. The link to WARCON's own live page remains visible. Only changes of status are committed; individual player counts and observation timestamps are published to Pages without committing new data on every check.

Production v1.0.0 continues running unchanged until a reviewed PR is merged. Work planned for weekly intelligence is tracked in `planning/V1.0.1.md` and must not publish fictional reports or auto-post a weekly message before first-match validation.
