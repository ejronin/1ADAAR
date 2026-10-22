# 1ADAAR v1.1.0 design handoff

This folder has the editable designs, screenshots and implementation notes for the next 1ADAAR release. The six screens are ready for review, **not yet approved for production**.

- [Design PR #28](https://github.com/ejronin/1ADAAR/pull/28)
- Design branch: `design/v1.1.0-ia-handoff`
- Implementation base: `staging/v2.0-foundation`
- Original staging reference: `26da372ea9c076bfe3751a0716ee8382161e811d`

Use the source files here to build the approved changes in staging. Don't merge this folder wholesale into the live site.

## Start here

1. Open `prototypes/index.html` to review the six screens: home, player, map/faction, weekly, recap and activity.
2. Use `screen-manifest.json` to find each component's HTML/CSS/JS/SVG source, screenshots, implementation target and approval status.
3. Check `tokens.final.json` and `components/COMPONENT_IMPLEMENTATION_SPEC.md` for measurements and interaction details. The token file is a **candidate**, not a signed-off design.
4. Compare `screenshots/*-390.png` and `*-1440.png` with the browser implementation. The browser checks also cover 320, 375, 768 and 1024 CSS pixels.
5. Read the integration and chart notes before adding new API calls or dependencies.

The design package is editable. Screenshots are evidence of what the current prototypes rendered, not a substitute for their source files or proof of native Discord behavior.

## What's in the folder

| Location | Contents |
|---|---|
| `prototypes/` | Full HTML pages, shared CSS/JS and a clickable review index |
| `components/` | Standalone SVGs, chart code, progression adapter, Python tests and component specifications |
| `screenshots/` | Captured desktop/mobile layouts and clearly labeled fictional interaction states |
| `assets/` | New licensed design assets only; existing logos remain in `docs/assets/` |
| `research/` | Data-source notes, chart choices, technical options and player connection requirements |
| `screen-manifest.json` | The list of screens/components, their files, targets and review status |
| `tools/` | Screenshot and Python-image generators, plus unit tests |

To view the pages locally, run this from the repository root:

```sh
python -m http.server 8000
```

Then visit `http://localhost:8000/design/v1.1.0/prototypes/index.html`. The local server is important because the pages load images and sample data from other repository folders. Opening an HTML file directly may not work.

There's also an optional [browser preview through raw.githack](https://raw.githack.com/ejronin/1ADAAR/design/v1.1.0-ia-handoff/design/v1.1.0/prototypes/index.html). That's a third-party proxy, not the live site; check it before relying on it.

## What the design covers

The site keeps its WARDOGS look: original 1AD and WARDOGS logos, Lonestar blue, Valkyra red, Manticore green, and restrained green/charcoal throughout the normal dashboard. Gold, silver and bronze belong to the weekly podium. Don't redraw or recolor the original artwork.

The six screens cover:

- **Home:** a clean server briefing, a short border laser that goes dark when finished, and a metallic sheen clipped to the original 1AD mark.
- **Player:** career totals, recent results, properly labeled chart controls, map/faction comparisons, Steam portrait treatment and an optional progression panel.
- **Maps and factions:** win/loss/draw breakdowns, recorded K/D by map and selectors that sit inside the panel they change.
- **Weekly:** the owner's preferred silver/gold/bronze podium, honest empty places and a crown effect reserved for a real qualified first-place player. The sample winner is only a demo.
- **Discord recap:** the image and text hierarchy, per-faction top-kill leaders where the match lines support them, and a real link-button implementation contract. The HTML preview still needs a check inside Discord itself.
- **Activity:** the recorded **match-start** heatmap, separate from any future player-session calendar. Missing session history isn't treated as zero activity.

Keep career totals, archived matches, season data and account progression labeled separately. A five-match trailing K/D point combines the **current match and preceding four**, regardless of whether the chart shows 10, 20 or all points. Raw kills/deaths can use paired dots; that option should disappear for ratio-only charts.

All PlayerOne figures are fictional test data. Live winners, match outcomes, role levels and activity should never be made up to fill a chart.

## External progression: what can actually be connected

The optional WARDOGS Tracker connection is for four things only: **six role levels and XP, overall WARDOG level, career XP, and account cash/gold when visible**. There is no loadout builder or unlock gallery.

WARDOGS Tracker documents a public API for player-synced profiles, but that does **not** mean 1ADAAR can automatically sign someone in or retrieve every visitor's progression. The outbound sync link opens the Tracker site in a separate tab. A persistent connection across browsers needs verified Steam ownership, the player's consent and private storage through an approved backend.

Start with [the connection instructions](research/PLAYER_PROGRESSION_OPT_IN_IMPLEMENTATION.md) and [the API investigation](research/ROLE_PROGRESSION_ACCESS_VALIDATION.md). The Python adapter and six-role radar renderer are in `components/`. Never publish raw Steam IDs, login credentials or hidden account-economy values in GitHub Pages.

Weapon kills-with/died-by charts are a separate possible WARCON kill-feed task, **not part of this release** until attribution is verified.

## Data and release rules

- WARCON provides server and match data. Game-account progression comes from a separately synced public Tracker profile when permitted.
- Only captured completed matches may count toward a saved-match report or server-wide activity heatmap.
- Personal online-time analysis needs authorized complete session timestamps and a privacy review. The existing bounded session list isn't full lifetime history.
- Keep test screenshots, empty states and fictional examples clearly marked.
- No RCON passwords, private WARCON keys, Steam credentials, webhook secrets or real player IDs in the design assets.
- Nobody posts a demo recap to the live Discord channel or activates extra data collection from this folder.
- The implementation engineer builds the actual site in staging; the owner inspects that **working preview**, not just static pictures, before approving deployment.

## Notes worth reading

- [Chart choices and the data each one needs](research/CHART_METHODS_AND_FIELD_GATE.md)
- [WARCON and RCON fields](research/RCON_WARCON_FIELD_INVENTORY.md)
- [Six-role progression research](research/ROLE_PROGRESSION_ACCESS_VALIDATION.md)
- [Player connection and storage](research/PLAYER_PROGRESSION_OPT_IN_IMPLEMENTATION.md)
- [Frameworks, CSS, Python image tools and GitHub builds](research/FRONTEND_GRAPHICS_TECHNOLOGY_ASSESSMENT.md)
- [What needs changing in staging](research/DESIGN_DISCREPANCY_REGISTER.md)
- [Examples from other gaming dashboards](research/COMPETITIVE_CHART_UX_REFERENCES.md)

## Review and sign-off

An approved design is not automatically working code. The implementation engineer ports the approved pieces to staging, runs the data and browser tests, and returns a hosted preview with screenshots at matching sizes. Check that preview against the design source and record any mismatches.

Only the owner can approve the screens and the production release. Keep `ownerApproval` in the manifest pending until that decision is explicit. Don't merge into `main` because a screenshot job passed.
