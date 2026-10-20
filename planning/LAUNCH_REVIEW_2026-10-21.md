# 1ADAAR / Wednesday 2026-10-21 release decision — staged UX/UI/IA and operations QA

**Status:** Staging-only. This is a source-level review, not proof of a visually inspected live site. Do not merge PR #19 or enable Weekly Intelligence publishing until release gates are met.

## Design and IA verdict

Preserve a restrained tactical command-center appearance: green/black for the normal dashboard, approved official 1AD + WARDOGS artwork, separate amber/charcoal treatment for Weekly Intelligence. Resist a wholesale visual rebrand, a JavaScript charting dependency, rotating hero video, auto-playing sound, or invented server/map statistics the day before release.

### Implemented in staging

- Readability and layout improvements now live in `docs/assets/brand.css` (shared design), `server-status.css` (server panel), `players.css` (player pages) and `performance.css` (charts). The redundant `polish.css` layer was removed; all three web pages use the same component styles, with bigger labels, usable touch controls and reduced-motion support.
- One lightweight CSS-only HUD sweep across the existing WARDOGS press-pack hero art. Does not claim live telemetry, load remote assets, alter scoreboard data or run per-viewer WARCON requests; completely disabled under `prefers-reduced-motion`.
- Static offline server status indicator no longer flashes/strobes. Offline/unknown/reconnecting remain distinct and data-driven.
- Homepage and player pages use everyday terms such as **Match history**, **Find a player**, **Results by map**, and **Sample player**. The match history still holds up to 120 completed matches. The match-history status no longer says `SYNCED` when no match history is present.
- Same-site generic Open Graph share metadata and image using the existing 43 KiB official press-pack hero; hashed profile links cannot provide dynamic per-player social images on GitHub Pages. Avoid claiming personalized preview cards.
- Explicit fallback when a saved/shared profile hash cannot be found in the bounded leaderboard. Reduced-motion setting also controls automatic profile scroll.
- Unit contract checks validate loading order, semantic navigation and skip links, social metadata, bounded-archive copy and motion controls. Existing Python + JS CI also runs.

## Screen-by-screen human visual QA (still required)

Perform screenshots and a real browser walkthrough before signoff on **320 × 700**, **375 × 812**, **390 × 844**, **768 × 1024**, and **1440 × 900** CSS pixel viewports, with 100% and 200% browser zoom:

1. **Home / hero** — 1AD logo legibility, real WARDOGS fullmark fidelity, approved press photo crop, clear headline and CTA. HUD sweep must be subtle, not interfere with links; test reduced motion.
2. **Status / KPIs** — distinct online/offline/reconnecting/unknown labels, current WARCON source link, verified observation time, absence of falsely live/stale player counts. No red strobes. No overflow at 320px.
3. **After-action archive** — no-match state is professional and honest; at 1+ genuine match, sorting/filtering and disclosure work on keyboard and touch; modal scrolls, Escape closes, source link correct; `Copy link`/native share has feedback.
4. **Player lookup** — unknown name, SteamID64 lookup, no-results, ambiguous name, real profile, renamed player, expired hash and shared link; entered raw SteamID never appears in UI/URL; all-time vs recent match scope visible.
5. **Performance charts** — one chart, keyboard tabs and circle point navigation, exact table beneath, 10/25/all windows, empty data, horizontal swipe hint, focus ring, no clipped labels at phone widths.
6. **Discord** — real test-recapped image / official logos and faction emblems at desktop and phone viewing; correct match awards and last-match URLs; no pretend weekly winners. Weekly amber sample in `planning/weekly-preview.html` is **not** a live report.

Ensure search, navigation, dialogs, and share operate using mouse, touch and keyboard. Check 200% zoom, high-contrast preference and iOS/Android WebViews if possible. No WCAG conformance claim is made without a separate accessibility audit.

## Operational and data gates (required for launch)

- [ ] At least one **real** completed WARCON match ingested and visibly rendered with correct season/source, once in `#match-recap` and no duplicate delivery.
- [ ] Verify live WARCON public endpoint and 1ADAAR freshness, without exposing any secret or raw SteamID in public JSON. If data absent, dashboard must accurately state absence.
- [ ] Verify actual scheduled-run cadence and published Pages timestamp freshness over a representative 24–48h window (issue #21). Cron declarations do not prove five-minute operation; maintain neutral `STATUS UNKNOWN` when stale.
- [ ] Check Pages deployments do not regress status timestamps because of concurrency, delayed cron, GITHUB_TOKEN commits, or out-of-order deployment.
- [ ] Latest staging HEAD CI all green, PR mergeable with current `main` and no accidental overwrite of live generated `docs/data/` snapshots. Recheck immediately before merge.
- [ ] Human screenshot/mobile/typeface pass and official logo fidelity signoff.
- [ ] Production dry-run and rollback plan prepared; existing `release/v1.0.0` protected.
- [ ] **Weekly publication remains disabled** until full-week coverage and idempotent Discord ledger are implemented and tested; design mock is only a preview. PlayerOne removal and dynamic share-button personalization remain deferred until real-data acceptance (#18).

## Go/no-go rule

A passing CI run proves source checks, **not** live game ingestion, screenshot quality, actual Pages run cadence, WebView behavior or once-only Discord posting. If live-match or Pages operations evidence is still missing Wednesday, defer the relevant automation/release rather than describe it as fully production-validated. An approved site appearance can be published separately only after ordinary staged-to-production review; never silently merge the draft or switch on experimental weekly content.

## Optional later improvements (not Wednesday release blockers)

- Precomputed static activity sparklines and data-driven week archive navigation **only** when coverage/provenance is defensible. No fabricated populated graphs for an empty archive.
- A build-time image export for each *real* match report's link preview; GitHub Pages hash-based player URLs do not support arbitrary dynamic metadata. Do not create per-player public HTML/dossiers without privacy review.
- After launch, consider a wider stylesheet refactor to reduce older repeated rules between `style.css` and `brand.css`, supported by screenshots. The extra `polish.css` file has already been removed and its rules put in the correct stylesheets.
- Low-noise admin-only incident alerts when reliable status provenance exists, without community-channel spam.

### Review evidence limits

Public Pages URLs could not be opened by the current web inspection tool; local screenshot evidence and real mobile browser testing remain explicitly outstanding. All staged code changes are grounded in the GitHub repository source, not visual proof of a rendered viewport.
