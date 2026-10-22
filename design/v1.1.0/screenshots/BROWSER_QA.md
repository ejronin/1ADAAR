# Browser checks for the design previews

These results are from `design/v1.1.0/prototypes/*.html`, **not** the implemented staging site. Chromium captured the pages at the sizes below. Fictional examples are labeled, and missing real data stays missing. This doesn't replace testing a real Discord message.

| Page | Width (px) | JavaScript errors | Horizontal overflow (px) | Result |
|---|---:|---:|---:|---|
| home | 320 | 0 | 0 | PASS |
| home | 375 | 0 | 0 | PASS |
| home | 390 | 0 | 0 | PASS |
| home | 768 | 0 | 0 | PASS |
| home | 1024 | 0 | 0 | PASS |
| home | 1440 | 0 | 0 | PASS |
| player | 320 | 0 | 0 | PASS |
| player | 375 | 0 | 0 | PASS |
| player | 390 | 0 | 0 | PASS |
| player | 768 | 0 | 0 | PASS |
| player | 1024 | 0 | 0 | PASS |
| player | 1440 | 0 | 0 | PASS |
| map-team | 320 | 0 | 0 | PASS |
| map-team | 375 | 0 | 0 | PASS |
| map-team | 390 | 0 | 0 | PASS |
| map-team | 768 | 0 | 0 | PASS |
| map-team | 1024 | 0 | 0 | PASS |
| map-team | 1440 | 0 | 0 | PASS |
| weekly | 320 | 0 | 0 | PASS |
| weekly | 375 | 0 | 0 | PASS |
| weekly | 390 | 0 | 0 | PASS |
| weekly | 768 | 0 | 0 | PASS |
| weekly | 1024 | 0 | 0 | PASS |
| weekly | 1440 | 0 | 0 | PASS |
| recap | 320 | 0 | 0 | PASS |
| recap | 375 | 0 | 0 | PASS |
| recap | 390 | 0 | 0 | PASS |
| recap | 768 | 0 | 0 | PASS |
| recap | 1024 | 0 | 0 | PASS |
| recap | 1440 | 0 | 0 | PASS |
| activity | 320 | 0 | 0 | PASS |
| activity | 375 | 0 | 0 | PASS |
| activity | 390 | 0 | 0 | PASS |
| activity | 768 | 0 | 0 | PASS |
| activity | 1024 | 0 | 0 | PASS |
| activity | 1440 | 0 | 0 | PASS |

## What wasn't tested here

The saved-match activity heatmap has no real completed-match starts yet. Its normal state stays empty. The role radar is also empty without a synced player profile. Fictional views are deliberately separate.

The PlayerOne sample covers 32 plotted records, the Last 10 control, paired-dot mode, career snapshots and the map/faction selector. Real WARCON collection and native Discord desktop/mobile rendering still need their own checks.

**Browser errors in this capture:** None.
