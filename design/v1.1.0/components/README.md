# Reusable design components

This folder contains the editable pieces behind the six full-page prototypes. The source files—not screenshots—are what the implementation engineer should work from.

Key files:
- `COMPONENT_IMPLEMENTATION_SPEC.md` — dimensions, states, data rules and staging targets
- `win-rate-ring.svg` — one properly sized win-rate ring
- `outcome-fingerprint.svg` — W/L/D results from the PlayerOne sample
- `six-role-radar-empty.svg` and `role_radar.js` — six role axes, filled only with validated values
- `progression_adapter.py` — validates the optional third-party progression data
- `session_aggregator.py` — day/hour session totals when private session access and consent allow them
- `discord_recap_contract.py` — Discord Components V2 message structure and link button
- `weekly-crown.svg`, `hero-border-trace.svg` — editable motion artwork

The matching page layouts are in `../prototypes/`. Every component is listed in `../screen-manifest.json` with screenshots and the implementation files it will affect.

Keep the official 1AD/WARDOGS/faction artwork unchanged. Design examples can use fictional records, but the final application must use verified sources and respect missing data.
