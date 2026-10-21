# 1ADAAR v1.1.0 — digital IA/UX/UI handoff

**Status: empty handoff workspace — awaiting independent engineer's actual mockups.** This repository branch is NOT the approved final design. Production `main` is untouched.

## Where to work

Repository: `ejronin/1ADAAR`  
Design branch: `design/v1.1.0-ia-handoff`  
Implementation branch: `staging/v2.0-foundation` (owned by the implementation engineer).  
Independent assessment: [PR #27](https://github.com/ejronin/1ADAAR/pull/27) — reference only; do **not** assume its concepts are applied to staging.  
Baseline staging commit: `26da372ea9c076bfe3751a0716ee8382161e811d`.

**The IA engineer commits or uploads actual editable visual artifacts here, NOT into the production or implementation branches.** If GitHub push access is unavailable, provide a ZIP with this exact directory layout, then the implementation lead can import it. Do not rely on a ZIP as the only surviving design source.

## Required directory structure

```text
design/v1.1.0/
  README.md                  — this handoff protocol
  screen-manifest.json       — status, code target and exact links per screen
  tokens.template.json       — must become approved tokens.final.json
  component-spec-template.md — per-component acceptance format
  prototypes/
    index.html               — review portal; add REAL clickable visual prototypes
    home.html                — homepage visual source (to be created)
    player.html              — player dossier + charts (to be created)
    map-team.html            — map/faction views (to be created)
    weekly.html              — awards/podium + real empty state (to be created)
    recap.html               — Discord recap representation (to be created)
    shared.css               — common prototype CSS source (to be created)
    shared.js                — interactive demo only when needed (to be created)
  components/
    README.md                — individual editable donut, podium, etc
  screenshots/
    README.md                — static evidence matching named prototype files
  assets/
    README.md                — only NEW design assets; reference approved originals
```

## Minimum acceptance package for each screen

1. **Editable, complete source**: one browser-readable HTML prototype with its CSS and JS; Figma links are welcome but NOT a substitute for exportable implementation material. A static screenshot alone is not enough.
2. Screenshots of the **same** prototype at **390px and 1440px**, plus tested layouts at **320, 375, 768, 1024**. Include clearly labeled real empty states and fictional demonstration states.
3. Exact specs for every major component: font family/size/weight/line-height; stroke and donut-ring thickness; radii; spacing; alignment; color tokens; responsive breakpoints; motion/reduced-motion; focus targets; source/data definition.
4. An updated `screen-manifest.json` entry referencing the real prototype and both screenshots. Do not mark a screen delivered until its referenced files exist.
5. Component-to-implementation file mapping in the screen spec, down to selectors/modules. Identify **keep / replace / remove** and feature parity for controls, real data and state logic. Do not invent WARCON fields.
6. Before/after critique and severity-ranked discrepancies; a line-weight and typography audit covering the win-rate donut, chart axes/paths, KPI labels, borders and avatar/podium graphics.

## Brand and data guardrails

- **DO NOT redraw or overwrite** `docs/assets/1ad-logo.svg`, official WARDOGS artwork, or `docs/assets/factions/*.svg`; prototype pages should link to these originals, via relative paths from this directory (e.g. `../../../docs/assets/1ad-logo.svg` from `prototypes/`).
- Everyday design: charcoal / white / restrained green. Week/awards: separate muted amber, silver, bronze. Real faction colors only for faction identity; kills green and deaths yellow.
- No fabricated live matches, verified winners, RCON telemetry or player-specific activity heatmaps. Fictional fixtures must be explicitly labeled. No real Steam/Discord IDs or secrets in prototypes or screenshots.
- Do not post demo webhooks or enable collection jobs. No live admin credentials are required to deliver visual designs.
- Preserve exact analytical mode semantics and dropdown behavior; visually distinguish WARCON career stats, saved completed matches, captured snapshots and weekly/season data.

## How the implementation lead uses the deliverable

1. Owner opens the clickable `prototypes/index.html` review and approves named screen revisions; rejected screens return to IA engineering.
2. IA engineer tags the manifest entry `ownerApproval: approved` **only when the owner explicitly approves**. Do not self-approve.
3. Implementation lead reads the exact HTML/CSS, `tokens.final.json`, specs, and real screenshots; builds these onto `staging/v2.0-foundation` without importing fictitious data or overwriting production.
4. Lead produces browser screenshots from implemented staging at matching widths and a discrepancy matrix. IA engineer compares visual output with approved source until deviations are resolved.
5. Owner signs off the entire release after visual, automated, live-source, and native Discord app QA. The design branch is never merged into production as part of a documentation-only approval.

## Running the prototypes locally (works without GitHub Pages)

In a checked-out copy of the design branch, run from the **repository root**:

```bash
python -m http.server 8000
```

Open `http://localhost:8000/design/v1.1.0/prototypes/index.html`. This loads the approved original game/1AD artwork from the same checkout and avoids browser `file://` limitations. No paid host, cloud secrets or live WARCON access is needed.

## Link and review protocol

Optional review UI (source branch through a third-party proxy, **not** production; availability must be checked):
`https://raw.githack.com/ejronin/1ADAAR/design/v1.1.0-ia-handoff/design/v1.1.0/prototypes/index.html`

Code and changes: GitHub draft PR from `design/v1.1.0-ia-handoff` into `staging/v2.0-foundation`. Screenshots included under `design/v1.1.0/screenshots/` and linked by the manifest.

The review site is a *skeleton* until the designer adds editable prototypes, working component files, and documented screenshots. **Do not advertise these placeholders as approved mockups.**
