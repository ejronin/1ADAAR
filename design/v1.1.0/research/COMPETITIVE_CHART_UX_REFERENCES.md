# Competitive UX references and usable lessons

This is a design-adaptation study, not a license to copy competitor brand assets or invent equivalent WARCON statistics.

## Leetify CS2 — https://leetify.com/blog/profiles-update/ (published Aug 17, 2026)
Leetify's update prioritizes top stats, replacing an unwieldy continuous scroll with clear categories/tabs, and supports drill-down from summary to match history, map performance and rank history. The profile differentiates recent performance from best-ever achievements and lets users select relevant benchmarks.
**Apply:** Source-specific trend tabs, an identity header with real Steam image, only a few primary numbers, followed by map/team drill-down. Do not import Leetify's proprietary aim/utility/positioning scores without comparable game telemetry.

## Tracker.gg Valorant — https://tracker.gg/valorant/
Tracker.gg puts player search, high-signal profile summaries, detailed match history and match timeline behind a clear navigation hierarchy.
**Apply:** Find player → career/recorded snapshot → match evidence. Use source-coded faction marks and labeled session/match views. Avoid unsupported scouting/agent-selection features for WARDOGS.

## OP.GG statistics — https://help.op.gg/hc/en-us/articles/31091864581657-How-to-view-league-team-and-player-stats
OP.GG supports comparisons by season and role and uses charts for role-specific metrics when the underlying game actually records those dimensions. Its League match history includes positional movement heatmaps because that game's game-specific telemetry exists.
**Apply:** Season-scoped view and compare only where we have real WARCON data. Do not replicate positional movement charts or six-role performance radars without WARDOGS telemetry.

## Data journalism guidance — https://github.com/Financial-Times/chart-doctor/blob/main/visual-vocabulary/README.md
The FT visual vocabulary selects chart encodings by question type: distributions, ranking, part-to-whole, change and correlation. Small multiples and aligned point positions are usually more accurate for comparison than decorative circles.
**Apply:** W/L/D fingerprints for categorical outcomes; ranked dot charts for per-map aggregate K/D; signed score-lead timelines from verified score samples; calendar and hourly heatmaps for real timestamps; absolute counts remain large legible numerals.

## Source, accuracy, branding and hierarchy constraints
- Only derive metrics from genuinely verified WARCON/RCON fields. Distinguish server-wide match-start activity from individual player online sessions.
- Original community/game faction artwork and exact category colors are not redrawn or appropriated from competitors.
- Do not add an arbitrary skill rating/percentile on a 0–100 scale merely because other trackers do; their telemetry or benchmark method is not available here.
- Only include a radar polygon when all six roles have comparable verified levels or role-specific contribution metrics.
- Standardize typography, corner radii and SVG line weights; clean chart design is less generic than adding irrelevant sci-fi glows.

Sources were consulted on October 21, 2026. See CHART_METHODS_AND_FIELD_GATE.md for field-by-field chart eligibility.