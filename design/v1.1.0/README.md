# 1ADAAR v1.1.0 — digital IA/UX/UI handoff

**Status: EDITABLE DIGITAL HANDOFF COMMITTED — Chromium desktop/mobile screenshots and browser QA complete; OWNER APPROVAL PENDING.** Source is a proposed direction, NOT the approved final design. Production `main` and staging implementation are untouched.

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
  tokens.template.json       — starter reference; candidate tokens.final.json now included
  component-spec-template.md — starter reference; components/COMPONENT_IMPLEMENTATION_SPEC.md now included
  prototypes/
    index.html               — active owner review portal with six editable prototypes
    home.html                — editable homepage design candidate
    player.html              — editable profile, charts and user identity
    map-team.html            — editable map/faction outcome comparison
    weekly.html              — verified empty podium + isolated fictional crown
    recap.html               — editable Discord message composition
    shared.css               — shared production-target visual tokens and styling
    shared.js                — source-labeled interactive charts and controls
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

The review site now contains six real editable design candidates, shared CSS/JS, source-gated chart research, and exact component specs. The branch-scoped GitHub Actions screenshot workflow generated actual 390px and 1440px Chromium captures for all six screens and updated the manifest with tested viewports. The digital package is ready for OWNER VISUAL REVIEW, not self-approved or staged. **Design delivery does not imply owner approval or staging implementation.**

## Chart research and high-end rendering decisions

- See `research/CHART_METHODS_AND_FIELD_GATE.md` and `research/ROLE_PROGRESSION_ACCESS_VALIDATION.md` for the updated decision inventory: paired dumbbells, ranked dot plots, outcome fingerprints, score-lead timelines, time heatmaps, cohort matrices, and a properly unfilled six-role progression radar.
- This is a **custom HTML/CSS/SVG/JS visual system** with no Bootstrap template; it is compatible with static GitHub Pages. Python Pillow/CairoSVG produces the deterministic high-resolution Discord image proof, while matplotlib is suitable for optional offline research. Kivy/Tkinter serve desktop GUI applications and are not useful for a static web/Discord-image pipeline.
- `tools/render_screenshots.py` renders real desktop/mobile browser PNGs at 390px and 1440px for each of the six prototypes and tests 320/375/390/768/1024/1440 widths. `tools/render_recap_proof.py` generates a separate 1080px genuine Python raster design illustration. Both scripts are design-only, do not call WARCON, RCON or Discord, and never alter staging or production.
- The workflow `.github/workflows/design-handoff-screenshots.yml` only runs against `design/v1.1.0-ia-handoff`; if successful it commits images and updates `screen-manifest.json` on that same branch. Any QA failure is a blocker, not an approved package.

## Data design caveats

- Saved server activity is a heatmap of captured *completed-match starts*, not personal time online. Staging's checked-in data is zero; genuine cells remain neutral until recorded matches exist. The prototype's fictional heatmap toggle exists for design evaluation only.
- Full personal session activity requires authorized private WARCON data beyond the current bounded recent dossier; do not place privileged RCON credentials in GitHub Pages or imply verified identity from pictures.
- Six role progression levels are not present in inspected WDRCON/WARCON schemas, **but** WARDOGS Tracker's documented public opt-in player API exposes all six levels/XP for players who have synced and permitted access. This opens a conditional source-supported radar, with no fabricated example; see research/ROLE_PROGRESSION_ACCESS_VALIDATION.md and components/progression_adapter.py.
- Owner approval for any named screen is the required gate before implementation engineering ports the design into staging. Native Discord mobile/desktop rendering remains an implementation acceptance gate.
