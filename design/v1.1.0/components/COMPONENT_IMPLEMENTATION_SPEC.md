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
All public browser charts must use precomputed sanitized sources. Historical personal sessions require properly scoped authorized WARCON server.view API access, not the direct privileged game RCON secret. WARCON protected dossier has only a recent bounded session list; avoid pretending it covers all active days. Six role levels remain unverified and the six-axis radar must stay blank. No Bootstrap dashboard skin or Kivy/Tkinter runtime.

## Approval and final verification
Each screenshot filename in screen-manifest.json must refer to real rendered browser evidence from identical prototype source. Browser QA at 320,375,390,768,1024,1440px and keyboard focus is mandatory. Owner decides whether each screen is approved. Then and only then the implementation engineer ports changes to staging; visual-fidelity review compares actual implementation screenshots with this design before production approval.