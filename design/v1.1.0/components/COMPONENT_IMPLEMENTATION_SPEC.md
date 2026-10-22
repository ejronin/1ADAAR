# 1ADAAR v1.1.0 — Component implementation specifications

**Visual handoff only. Owner approval pending.** Editable sources: prototypes/index.html and six prototypes, shared.css and shared.js. Tokens: tokens.final.json (candidate, not signed off).

## Layout / typography
- Base background #090e0c, surface #121d16, separator #304537. All normal screens use restrained green #86f4a4. Kills green; deaths #f5c84b. Original faction SVGs must not change: Lonestar #465eff; Valkyra #ee4138; Manticore #3eba42.
- Weekly palette solely muted gold #e4bd78 / silver #bec9c7 / bronze #c78d62. 1AD and WARDOGS original assets linked directly to docs/assets.
- Display/numeric: Barlow Condensed 700/800; body: Inter/system UI. Hero title 42–68px, section 30px, main KPI 31–47px, body 14px/1.52, legend >=11px. Metric values tabular aligned.
- Card radius 11px, border 1px, grid gaps 16px, section gaps 22px. 2.5px series stroke, chart 1px guides, 11px donut track/arc, 2px portrait outline. All interactive targets >=44px.
- Desktop fixed sidebar 214px, collapses to horizontally scrollable nav at 800px. At 1060px KPI grid 2 columns and trend/snapshot stack. At <=520px 2-column cards and all major panels full width. At 320px chart fits page and table alone may scroll.

## Component-to-staging mapping
| Candidate | Exact production-bound files | What to keep/change | Gate |
|---|---|---|---|
| home.html .hero | docs/index.html; docs/assets/motion-v11.css | Keep genuine artwork; simplify perimeter laser, circular alpha sheen | One shot, reduced motion fallback |
| home.html .metric | docs/index.html; docs/js/app.js | Keep actual empty states; do not invent status | Match data evidence |
| player.html .identity | docs/players.html; docs/js/players.js | Keep Steam avatar matching by ID, circular initial | Privacy, not Discord proof |
| player.html .metric | docs/players.html; docs/assets/player-v11.css | Reweight all original career + supporting KPIs | Fixture parity |
| player.html #performance-chart | docs/js/performance.js; docs/js/performance-core.js | Preserve tracked K/D, match K/D, rolling-five K/D and five-match avg counts | Correct zero-death semantics; table |
| player.html win ring + faction/map meters | docs/js/player-snapshot.js; docs/assets/player-v11.css | Replace multi-donut with one correctly scaled win ring and two appearance strips | Career vs recent scope labels |
| map-team.html fingerprint / dots | docs/map-team.html; docs/js/map-team.js; docs/assets/map-team.css | Add to existing season/drill-down controls without dropping filters | Match N and known outcome denominators |
| weekly.html podium | docs/weekly.html; docs/assets/weekly.css; docs/assets/motion-v11.css | Preserve no-winner state and eligibility; use fictional study for crown only | No award to unverified Discord member |
| recap.html Discord shell | src/recap_card.py; src/discord_layout.py | Reproduce media art in Python Pillow/CairoSVG; native layout controlled by Discord | Separate real client QA |
| activity.html heatmap | docs/activity.html; docs/js/activity.js | Preserve captured match starts, empty state, Eastern timezone. Gate session view. | No unverified player activity |

## Animation
Hero border: 1450ms narrow trace once only. Emblem sheen: 1100ms after hero; the mask comes from original circular 1AD SVG, not a rectangular overlay. Champion crown: 650ms fade after verified winner renders; separate from rank number. All three disable animation under prefers-reduced-motion and reveal content without movement. No infinite animation or layout changes.

## Data-engineering source gates
All public browser charts must use precomputed sanitized sources. Historical personal sessions require properly scoped authorized WARCON server.view API access, not the direct privileged game RCON secret. WARCON protected dossier has only a recent bounded session list; avoid pretending it covers all active days. The six role levels ARE documented as available via opted-in public sync through WARDOGS Tracker, but NOT via documented WDRCON/WARCON. Keep the radar blank unless the particular player's public six-field record passes privacy, source, season, timestamp and maximum-level gates. No Bootstrap dashboard skin or Kivy/Tkinter runtime.

## Approval and final verification
Each screenshot filename in screen-manifest.json must refer to real rendered browser evidence from identical prototype source. Browser QA at 320,375,390,768,1024,1440px and keyboard focus is mandatory. Owner decides whether each screen is approved. Then and only then the implementation engineer ports changes to staging; visual-fidelity review compares actual implementation screenshots with this design before production approval.

## Weekly podium restoration — owner-supplied previous design reference

The owner identified the earlier **“COMMUNITY PLAYERS OF THE WEEK”** three-place composition as the preferred weekly podium reference on 2026-10-21. Restore that arrangement in design and require the implementation engineer to follow the *committed browser screenshots*, not the flatter prior v1.1.0 podium illustration.

**Source of truth:** `design/v1.1.0/prototypes/weekly.html`, the scoped `.weekly-spotlight`/`.weekly-podium` classes in `prototypes/shared.css`, and the fully editable crown vector `components/weekly-crown.svg`. Visual evidence: `screenshots/weekly-1440.png`, `screenshots/weekly-390.png`, and `screenshots/weekly-fictional-interaction-1440.png`, regenerated from those sources.

**Geometry:** 3-column horizontal podium at desktop: silver (02) / elevated gold (01) / bronze (03), with a **slightly wider and 22px taller** central gold card. Equal rank-number family and weight, ranks top-left within each card, centered circular portraits below. Gold crown **above the first-place card** aligned to the portrait midpoint. Visible empty-state wording:

- Section title: **Community players of the week**
- Supporting copy: “Top three places remain unassigned until players and Discord eligibility are verified.”
- Status: **Awaiting results**
- Each vacant card: **Awaiting results** / **Second place**, **Player of the week**, or **Third place** / **No player selected**
- Eligibility note: “These are empty places, not awards. Member eligibility and profile-picture verification must be confirmed before activating the spotlight.”

**Material treatment:** Silver uses cool-grey metallic border (`#B9CBD3`) and charcoal-grey background; first uses muted gold (`#E5BC70`); third uses warm bronze (`#C18A6D`). Metallic appearance comes from **a restrained one-pixel upper rim highlight, cool/warm color-specific gradient, and subtle inset reflection**, not neon glows or continuous shimmer. Borders remain readable in reduced motion and screenshots. Current empty-state avatar circle has matching metal stroke; no invented image or recipient name.

**Crown states:** The unoccupied gold slot has a static emblematic crown at the top center—it signals *placement*, not a winner. When a legitimate and identity-verified first-place player populates that slot, the same-sized crown fades in once over **650 ms**, positioned above the actual avatar (no oversized crown or title obstruction). Under `prefers-reduced-motion: reduce`, the crown is shown statically without fade or translation. The design-only checkbox reveals **clearly fictional** recipient names exclusively for animation review; production must not include that demo switch.

**Mobile:** Three places remain in silver/gold/bronze order; avatar and typography reduce at <=680px, 320px layout must neither clip names nor force body horizontal scroll. Long verified gamer tags need wrapping/ellipsis rules with full accessible names. Empty cards never imply eligibility confirmed.

**Data gates:** **Do not assign winners** until weekly period, top-three eligibility, Discord identity constraints, and actual qualifying match data are verified. Do not confuse “highest WARDOGS player score” with unauthorized, estimated role rank. All displayed player photographs must be sourced from the correct authorized/public Steam association.

**Implementation targets:** `docs/weekly.html`, `docs/assets/weekly.css`, `docs/assets/motion-v11.css`, and the existing weekly data-rendering code. Preserve the rest of the weekly roundup analytics. No production changes in this design revision.

**Acceptance:** Compare final desktop/mobile implementation against `weekly-1440.png` and `weekly-390.png` side by side; test real empty archives, three full winners, only one/two available winners, motion/reduced motion, long nicknames, Steam-avatar fallback, 320px viewport, and keyboard/screen reader labels.


## Owner-directed design corrections: hero, player trends, map comparison, Discord and role access

**Update scope:** design branch / PR #28 only; no production or staging implementation merges.

### Hero animations (non-negotiable)

- Source: `prototypes/home.html` + `prototypes/shared.css`, `.hero .laser` and `.hero-logo-mark .hero-logo-sheen`. Perimeter rect uses `pathLength=100`, one 4.2% bright stroke segment, dash offset sweeping the WHOLE perimeter in 1.45 seconds, opacity zero on completion. Stable low-brightness border remains; no fixed laser dash.
- 1AD sheen background is a narrow metallic luminance gradient with **stationary alpha-mask** sourced from the original `docs/assets/1ad-logo.svg`; wrapper size exactly equals displayed source emblem, with circular clipping. Do not move or scale a duplicate logo; animate light gradient position, *not* the logo element. Sheen opacity 0 after 1.1s pass; never bleeds outside emblem. Support reduced motion.
- QA must inspect the actual border animation beyond its duration, measured element rectangles, and screenshots of resting desktop/mobile states; static screenshot cannot itself prove movement timing.

### Player performance control model

Five metrics: `Kills & deaths`, `Match K/D`, `Trailing 5-match K/D`, `Trailing 5-match averages`, `Career K/D`. Selector `Last 10 / Last 20 / All` controls the **number of displayed points**, not rolling-window width or map count. A trailing point at match N uses current and prior four saved completed matches, *e.g. observation 12 summarizes matches 8 through 12*. Rolling K/D = sum kills ÷ sum deaths in that five-match window; trailing means = each count's sum / 5; first four complete-window positions are unavailable. Career K/D is actual tracked snapshots, not inferred full prior history.

- The chart presentation selector is **ONLY VISIBLE in Kills & deaths mode**, with two valid views: green/yellow time-series and per-match paired dots. For `Match K/D`, `Trailing 5-match K/D`, `Trailing 5-match averages`, and `Career K/D`, forcibly hide incompatible controls; never display a selectable mode that does nothing.
- For paired dots, same count scale starts at zero, each row is one match and each dot has exact kills/deaths in accessible table. In a rolling line show one point per valid trailing five-match window; label source/denominator, never silently switch to five maps.
- A **waterfall chart is rejected** for raw K/D and rolling ratios because they are *non-additive*; optional signed `kills minus deaths` contribution bars may be evaluated separately if they answer a player question.

### Maps and factions local control / explanatory label

- Title: **Aggregate K/D by map**, not `Performance contrast`. Show explicit formula: sum recorded kills / sum recorded deaths per map in the selected completed-match sample. All plotted dots share one numeric K/D scale and a visible recorded-match count. Example only uses canonical fictional fixture.
- Move `Match outcomes / Team share / Map share` selectors **inside Result composition**, because they affect only that panel's dynamic breakdown. Other panels intentionally do not change, and must not be visually implied global. Match W/L/D outcome totals stay displayed and labeled at all times.
- Large `5 / 4 / 1` uses the SAME Barlow Condensed + legible Arial/sans-serif fallback as every other KPI, not serif browser fallback.
- Do not eliminate original faction SVGs and exact source-specific colors.

### Discord message: exact supported Components V2 contract

- Source contract: `components/discord_recap_contract.py` and `tools/test_discord_recap_contract.py`. Native Discord docs: https://docs.discord.com/developers/components/reference .
- Use `flags=32768` and only supported `type:17` Container with `type:10` Text Display, `type:12` Media Gallery referencing an uploaded PNG at `attachment://match-recap.png`, and `type:1` Action Row containing `type:2, style:5` **real external link button** with approved HTTPS first-party URL. This button HAS `url`, MUST NOT have `custom_id`; do not pretend a styled HTML `span` is a Discord component. Discord client final widths/layout controlled by the client; native desktop/mobile QA required later. Existing `src/discord_layout.py` is implementation target, not modified by this handoff.
- **One leading performer for each of Lonestar, Valkyra, Manticore:** computed by **most kills in that completed match**, not all-time or unrecorded points, using source-verified complete `match.players` entries and original faction. Aggregate duplicate entries by player key per faction. If tied, show `N players tied`, not a randomly chosen champion. If match data incomplete, omit claims and show a neutral unavailable state. See source/test contract.
- Preserve source data, live delivered image, working dashboard URL, verified match-id link; never post sample fixture webhooks.

### Six-role progression — RESEARCH CORRECTION

The user requested actual investigation into game and other trackers. WDRCON and WARCON alone have NO documented six-role progression API, but **WARDOGS Tracker** https://wardogstracker.gg/developers confirms a public opt-in synced `/api/v1/players/{steamId}` API with level + XP for all Assault, Medic, Recon, Support, Driver, Pilot. A separate WARDOGS Zone implementation https://wardogs.zone/privacy describes player-authorized game backend account progression reads. This independently demonstrates feasibility for synced players, **not for everyone who has joined Dan's server**. See `research/ROLE_PROGRESSION_ACCESS_VALIDATION.md`.

- Adapter `components/progression_adapter.py` validates response shape, exact SteamID association privately, six present finite level/XP values, maximum-level scale, timestamp, publication authorization; publishes no SteamID or authenticated session.
- Renderer `components/role_radar.js` and schema `role_radar.schema.json` take those six values ONLY if provided a verified source, common bound, and consented public record; in all other cases radar remains neutral. Season and syncedAt must be presented beside genuine data with attribution and approved cache policy.
- v1.1.0 role module **conditionally eligible** pending a real synced player data test and owner consent. Six-role *gameplay performance* radar remains unavailable without role-specific event telemetry. No auto-scraping private sessions or Steam auth tokens.

### Final gate

New screenshots and manifest must reflect exact latest edits. Browser regression tests at 320/375/390/768/1024/1440, plus 200% zoom where possible, relevant control show/hide, correct local selector behavior, hero final opacity, official assets, and real Discord JSON shape. Native Discord verification and Dan-server live WARCON/RCON probes are implementation-stage gates after owner approval, not substituted with an HTML mock.
