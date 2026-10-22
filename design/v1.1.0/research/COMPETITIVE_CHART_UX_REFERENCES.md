# Ideas from other player-stat sites

These are examples of useful layouts and charts. We're borrowing the approach, not their branding or statistics that WARDOGS doesn't supply.

## Leetify (Counter-Strike)

[Leetify's profile redesign, August 17, 2026](https://leetify.com/blog/profiles-update/) puts the important numbers near the top, groups details in tabs and makes match history and map performance easy to reach.

For 1ADAAR: keep the player header clean, show only a few prominent career stats, and put the match and map detail underneath. Don't add Leetify's aim or utility ratings; WARCON doesn't give us the matching data.

## Tracker.gg (Valorant)

[Tracker.gg](https://tracker.gg/valorant/) makes the path from player search to profile to individual matches easy to follow.

For 1ADAAR: use **Find a player → career summary → saved match details**. Keep faction identity and data periods visible, particularly where current-season and career figures sit near each other.

## OP.GG (League of Legends)

[OP.GG's stats guide](https://help.op.gg/hc/en-us/articles/31091864581657-How-to-view-league-team-and-player-stats) shows comparisons by season and role. League can use movement heatmaps because that game records position data.

For 1ADAAR: season filters and role progression are useful only when supported by real fields. There is no case for inventing WARDOGS movement paths or a six-role *performance* score. Actual six-role **level/XP** data for public synced profiles is a separate, documented WARDOGS Tracker source.

## Picking the right chart

The [Financial Times Visual Vocabulary](https://github.com/Financial-Times/chart-doctor/blob/main/visual-vocabulary/README.md) is a useful reminder to choose a chart for the question:

- **Ranking:** dots or ordered rows for aggregate K/D by map.
- **Individual comparisons:** paired dots for kills versus deaths in the same match.
- **Mix of outcomes:** W/L/D blocks or a segmented bar.
- **Change over time:** a line for match K/D or a recorded score-lead timeline.
- **Activity by time:** a calendar or weekday/hour heatmap when the timestamps are available.
- **Straight totals:** a clear number is often better than a chart.

The WARDOGS/1AD logos and faction colors remain unchanged. Source dates, denominators and missing-data labels matter more than visual effects.

References reviewed October 21, 2026. See [the chart and data notes](CHART_METHODS_AND_FIELD_GATE.md) for which ideas are actually possible.
