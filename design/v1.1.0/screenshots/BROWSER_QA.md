# Browser QA of editable design candidates

Source: design/v1.1.0/prototypes/*.html (not current implementation pages).
These are browser screenshots, not native Discord-app screenshots. All data in mockups is explicit fictional fixture or no-data.

| Screen | CSS width | Page JS errors | Body overflow px | Result |
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

## Data acceptance caveats
The activity heatmap has zero actual saved match starts and is neutral by default.
The fictional interaction captures deliberately show sample-only states, not live data.
The six-role radar has no filled role-level data polygon.
Sourced PlayerOne plot / 32 rows, Last 10 selector, paired-dot encoding, historical snapshots and faction/map switch tested.
A first real WARCON source and actual Discord desktop/mobile visual acceptance are separate release gates.

## Errors
- None in source/prototype browser checks
