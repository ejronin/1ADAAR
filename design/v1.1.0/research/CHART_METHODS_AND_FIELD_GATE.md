# 1ADAAR 1.1.0 — Data-science chart audit and source gates

**Status: candidate handoff, owner approval pending.** Research: Financial Times Visual Vocabulary https://github.com/Financial-Times/chart-doctor/blob/main/visual-vocabulary/README.md ; Observable Plot https://observablehq.github.io/plot/ ; Plotly Python static export https://plotly.com/python/static-image-export/ ; WARCON and WDRCON source contracts reviewed in this project.

## Chart acceptance policy
Every chart requires an analytical question, verified field list, temporal scope, correct denominator, 0/unknown handling, sampling coverage, a table or keyboard-accessible values, and a tested mobile presentation. Avoid trendy chart types when they distort evidence.

| Decision | Visualization | Analytical question | Required source and gate | Placement |
|---|---|---|---|---|
| KEEP | Numeric primary KPIs: career kills, deaths, matches, K/D | Exact career totals | Public WARCON all-time scoreboard | Player |
| CONSOLIDATE | Win-rate ring (one only) + W/L/D outcome mosaic | What fraction of matches were wins? | WARCON wins / known wins+losses+draws; 0 denominator = unavailable | Player snapshot |
| NEW | Paired dumbbell per match, kills green / deaths yellow | How far apart were kills and deaths in each match? | Public saved match player lines; count scale from zero; show 10–15 matches | Optional player trend alternative |
| KEEP | Observed match K/D line and rolling-five ratio line | Is efficiency changing from match to match? | Saved completed match kills/deaths; rolling sum K / sum D, not average of ratios | Player trend |
| KEEP | Five-match averages, two-series | How does average combat volume change? | Five consecutive completed records, first four undefined | Player trend |
| KEEP | Tracked WARCON cumulative career snapshot line | Is all-time ratio moving? | Genuine dated snapshots; gaps, partial capture | Player trend |
| NEW | Outcome fingerprint grid W/L/D marks | Were results consistent or mixed? | Saved completed matches with known results | Map/team and weekly |
| NEW | Rank-order lollipop / dot plot | Which map/faction has highest recorded aggregate K/D? | Per-map/faction sample counts and kills/deaths; zero-death handling | Map/team |
| NEW | Center-zero signed lead timeline | When did the lead change during a match? | WARCON public match timeline and two faction scores | Match detail |
| KEEP | Weekday x hour recorded-match heatmap | When do saved completed matches start? | Captured startedAt, timezone America/New_York; zero cells mean no saved starts | Activity |
| FUTURE GATED | Day calendar and time-of-week *session-minute* heatmap | When did a player actually play? | Protected complete joinedAt/leftAt session records and privacy review | Player activity |
| FUTURE GATED | Session duration dot-strip / ECDF | What is a typical session versus long-tail sessions? | At least 10 ended sessions; ongoing censoring | Player activity |
| FUTURE GATED | Uptime temporal status ribbon | Was server offline, or was observation missing? | Protected WARCON duration-weighted up/down/coverage | Admin ops |
| FUTURE GATED | Population horizon + interval band | How crowded were periods? | Protected population points, avg/max and coverage seconds | Admin ops |
| FUTURE GATED | Kill-cause Pareto / distance boxplot | Which combat causes dominate and how far are shots? | Optional kill feed cause/distance/headshot tags; enough valid observations | Advanced combat |
| FUTURE GATED | Return-player cohort heatmap | Do new players return within 7/30 days? | Complete protected session history, pseudonymous cohorts | Community ops |
| CONDITIONAL / API DOCUMENTED | Six-axis role progression radar | Relative progression across Assault, Medic, Support, Recon, Driver, Pilot | Public opt-in synced WARDOGS Tracker player API has six {level,xp} fields; not exposed by ordinary WDRCON/WARCON. Require synced public profile, maxLevel, season, attribution, privacy | Player profile |
| BLOCKED | Six-axis role performance radar | Genuine contribution in all six roles | No validated healing, revives, logistics, recon and piloting gameplay events | Future |
| REJECT | Generic multi-gauge dashboard / radar overall skill / three faction donuts | Does it look intricate? | No interpretable scale, duplicated purpose or ambiguous fraction | Never |

## Derived KPIs, carefully defined
- K/D = sum(kills) / sum(deaths) according to documented WARCON zero-death display rules; do not assume an alternative convention.
- Win rate = wins / (wins+losses+draws) where the source has known outcomes.
- Five-match average kills/deaths = sum of respective counts in five consecutive completed rows divided by five; first four points unavailable.
- Rolling K/D = sum of five kills / sum of five deaths; overlapping five-match points must be described as overlapping.
- Faction participation = faction appearances / selected observed-match denominator, with unknown faction counted separately when captured.
- Daily session minutes = overlap of verified session interval with calendar-day intervals in chosen timezone. Split at local DST boundaries.
- Seeding share = seedMinutes / totalMinutes only if the WARCON definitions confirm the former is subset of the latter; otherwise retain two separate values.
- Map/faction comparison win rate and confidence bands only if sample count and interval assumptions are shown. Do not invent a player skill percentile.

## Python / graphics technology decision
| Technology | Best use / tradeoff | Decision |
|---|---|---|
| Custom HTML/CSS/SVG + small JS | Exact branded shapes, semantic DOM, fast static hosting | Preferred website implementation |
| Observable Plot / D3 | Advanced layered marks, faceted distributions, grammar of graphics; check bundle and accessibility | Optional where vanilla SVG becomes complex |
| Python Pillow + CairoSVG | High fidelity deterministic image composition for Discord PNG | Preferred batch rendering |
| Python matplotlib | Statistical exploration, offline static SVG/PNG, scripted QA | Useful for non-interactive exports |
| Plotly + Kaleido | Advanced interactive or research reports but larger runtime and Chrome export dependency | Only if complexity justifies cost |
| Altair / Vega-Lite | Declarative exploratory visual grammars; added runtime dependency | Research tool, not necessary baseline |
| Kivy / Tkinter | Native desktop GUI surfaces, windows and event loop | NOT appropriate for GitHub Pages or deterministic Discord PNG |
| Bootstrap | Fast generic grid styles, conflicting visual identity | Do not use as skin; custom system instead |

## Data availability status
Public WARCON covers scoreboard totals and completed match lines with results and optional combat feeds. Its server-wide private analytics has population, map, uptime, hourly periods and sessions. A protected player dossier includes joinedAt, leftAt, faction, session kills/deaths, seeded minutes but returns a bounded recent set (25 in inspected source). Direct game RCON /v1/players returns current name, steamId, faction, kills/deaths, cash and ping, with no six levels. **Separately**, the documented public WARDOGS Tracker API can return all six role levels/XP for opted-in synchronized public player profiles (see ROLE_PROGRESSION_ACCESS_VALIDATION.md). Do not claim those values are direct WARCON/RCON data or invent spatial accuracy metrics.

The checked-in staged recorded-activity.json has 0 captured completed match starts. The design uses a true empty state and a separately toggled fictional heatmap only; the live dashboard must never infer inactivity from this 0. Production delivery is not authorized.