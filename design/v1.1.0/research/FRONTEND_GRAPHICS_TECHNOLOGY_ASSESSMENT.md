# 1ADAAR v1.1.0 — Frontend, Charting and Python Graphics Technology Assessment
**Owner handoff addendum · October 22, 2026 · Design branch only · not an approved production dependency change**

## Finding from the actual repository
Checked `staging/v2.0-foundation`: the site is currently authored in `docs/*.html`, `docs/assets/*.css`, and `docs/js/*.js`; `docs/js/performance.js` builds accessible SVG charts without dependencies. The existing `.github/workflows/pages.yml` directly uploads `./docs` to GitHub Pages on a `main` push. No `package.json`, Sass pipeline, Vite, React or Astro configuration exists on that staging branch. Python batch image rendering already exists in `src/recap_card.py`.

**Implication:** Do not assume Vite, Bootstrap, Sass or a Python GUI is already installed. Introduce a source-controlled build pipeline cautiously; GitHub Pages itself serves static output and cannot execute Python/server-side functions. Owner must first approve integration staging and visually verify final built output. Source: https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site .

## Decision matrix (compatibility and fit)

| Technology | Use in 1ADAAR | GitHub fit | Recommendation |
|---|---|---|---|
| **Dart Sass (SCSS)** | Token-derived CSS variables, shared mixins, consistency of chrome/typography, gradients, spacing and mobile layouts | Compile in GitHub Actions or locally into static CSS; Pages serves resulting CSS | **Adopt in staging first, with `@use`/`@forward`, not deprecated `@import`; keep CSS runtime variables for light/dark/data tints.** |
| **Vite** | Minimal Node.js build/dev/bundle pipeline for CSS modules and optional JS chart packages, optimized assets | Actions runs `npm ci && npm run build`; Pages publishes dist or the carefully generated docs output | **Prefer when bundling third-party modules.** Does NOT require rewriting HTML into React. Preserve multi-page routes and set `base:'/1ADAAR/'`. |
| **Custom SVG/CSS/JS** | Hero border laser and 1AD alpha-masked sheen; podium metal rims; exact logo rendering; ring, grid, W/L/D marks | Native browser runtime supported by Pages | **Keep as brand/animation foundation.** The best visuals need precise art direction, not generic UI skins. |
| **D3 (shape/scale/axis)** | Branded score-lead timeline, lollipop/dumbbell, matched-map dot charts, calendar heatmap, nuanced label placement | JS bundler / ES modules and static Pages | **Selective**; add only modules needed for source-verified charts. Preserve the accessibility table. |
| **Observable Plot** | Grammar-of-graphics for quick layered dot, rect, slope, distributions and interval plots | JS module dependency bundled at build, static output | **Candidate** if it reduces chart implementation time without surrendering design control. Do not stack both Plot and full D3 for no reason. |
| **Apache ECharts** | Broad stock catalog: radar, heatmap, lines, custom series, interactive dashboards | Tree-shaken JS dependency and SVG/Canvas renderer, static Pages | **Alternative to D3/Plot** when many complex conventional interactive plots justify library weight. Avoid running two competing chart engines. |
| **Motion for JavaScript** | Exact path offsets, sequenced SVG effects, first-place crown entrance, transform/opacity animation | Small optional JS dependency; browser runtime | **Optional** only if CSS/WAAPI cannot make hero tracing/sheens deterministic and testable. Must fade laser to zero and keep mark clipping exact. |
| **Pillow + CairoSVG** | Compose Discord AAR PNGs from genuine faction/1AD SVGs and art; controlled pixels, typography, color | Python dependencies installed in Actions; PNG attached to Discord post | **Keep/expand**; compatible with GitHub Actions, not a browser UI framework. |
| **Matplotlib** | Offline validation, probability intervals, distributions, comparative static SVGs | Python Actions job outputs files | **Optional** for genuine statistical graphics, not a requirement for live Pages interactivity. |
| **NumPy / pandas / Polars** | Precompute large match-event aggregates and time-series derivations | Python in Actions, emits sanitized JSON | **Add only if row volume and transforms justify it.** Existing Python stdlib is enough for simple 5-match windows and compact server samples. |
| **Playwright Test** | Real screenshot diff tests and keyboard interaction at 320/375/390/768/1024/1440 | Headless browsers on Actions, CI artifacts | **Adopt/retain** and validate generated staging site, not just standalone mockups. |
| **Bootstrap / pre-styled admin templates** | Layout / buttons / cards | Technically compatible | **Avoid as primary UI.** Overrides introduce styles and dependencies while obscuring custom 1AD identity. A grid utility alone would be acceptable only if justified. |
| **Tailwind CSS** | Design-token-driven utilities | Compile-time static CSS via Actions | **Not needed now.** Could be reasonable on a component-heavy rewrite, but migration cost from existing CSS and design would be substantial. |
| **Astro** | Static page components and shared templates with optional interactive islands | Actions static build to GitHub Pages | **Defer** until the number of pages and duplicated layouts justifies a static site generator. Do not migrate simultaneously with chart and animation revisions. |
| **React / Vue / Svelte** | State-intensive component applications | Compiled JS to GitHub Pages | **Defer**: the present six-screen read-only dashboard does not warrant rewriting its existing HTML/JS just for visual quality. |
| **Kivy / Tkinter (Python)** | Native desktop/mobile Python GUI | They can run on desktops and CI virtual displays, but not as a GitHub Pages website | **Reject for website / Discord images.** Use Pillow+CairoSVG or static SVG output instead. |
| **Three.js, PixiJS, WebGL** | Animated 2D/3D scenes | Static JS bundles can run on Pages, but runtime cost & mobile GPU complexity | **Reject for the current 1ADAAR requirements.** Neither a border laser nor a circular masked sheen needs WebGL. |

### Single chart-engine discipline

**Do not install D3 + Observable Plot + Apache ECharts + Plotly in the same initial release.** Start with current custom SVG and use modular D3 for the one or two charts that demand complex axes or hit-testing. If engineer benchmarks reveal large feature demand and maintainability problems, compare a small ECharts prototype with the D3 alternative. The existing custom six-role radar stays source-gated until real player consent/source data is verified.

**High-value, source-led visualizations:** UTC/Eastern daily and weekday-hour activity heatmaps (separate captured match starts vs authorized player sessions), actual six-role level radar + exact level/XP list, per-match kills-versus-deaths dumbbells, ranked map K/D lollipops, faction W/L/D result fingerprints, real score momentum timeline. **Do not** create weapon usage/loadout graphics from Tracker unlock IDs or waterfalls of nonadditive K/D ratios. See `CHART_METHODS_AND_FIELD_GATE.md` and `PLAYER_PROGRESSION_OPT_IN_IMPLEMENTATION.md`.

## Phased staging migration (no production change)

**Phase A: polish without changing the delivery mechanism**
1. Apply `tokens.final.json` *as an owner-review candidate* to one CSS design-token source. Consolidate typography, 1px card/axis strokes, circular logo geometry, greens, faction palettes, amber-gold weekly finishes and consistent metric numeral sizes.
2. Keep current SVG and HTML operational while visual corrections are ported. Use precise `stroke-dashoffset`/path-length with fade to zero for the moving perimeter laser; use a static, original-sized alpha mask + moving light gradient for the 1AD sheen. Honor `prefers-reduced-motion`.
3. If improving CSS modularity, install **Dart Sass** in the staging developer dependencies and compile `src/styles/*.scss` to existing CSS artifact paths; author in SCSS with `@use` and `@forward`. During transition, do not break current `docs/assets/*.css` links or the live deployment process. Commit lockfile and generated output only according to the agreed build ownership.

**Phase B: add Vite if justified by new chart dependencies**
1. Add `package.json` and lockfile with pinned/controlled dependencies, TypeScript only if complexity justifies a migration (not mandatory). Keep entry HTML pages functioning; set up multi-page Vite entries, preserving existing player queries, paths, images and existing source fetch.
2. Set `base: '/1ADAAR/'` for `https://ejronin.github.io/1ADAAR/`. Audit hard-coded relative paths, embedded static JSON/data, favicon, faction SVG/logo, CDN references, and any `attachment://` image URLs (which belong to Discord payloads, not to GitHub Pages).
3. Build in staging Actions with a clean install and publish compiled **staging-only** static assets to a separately accessible, owner-verified preview. Do not modify or automatically fire the production `main` Pages workflow. Update `.github/workflows/pages.yml` only in a reviewed subsequent PR once the output is visually approved.
4. Select **one** advanced visualization approach: modular D3/Plot for custom marks OR ECharts for generalized interactive categories. Bundle modules where needed, avoid shipping broad irrelevant dependencies. Use motion only for genuinely measurable SVG sequences. All chart calculations remain separately unit-tested in JS/Python, not buried in DOM animation code.

**Phase C: data back end and privacy**
1. Continue read-only WARCON ingestion in GitHub Actions and publish only approved nonidentifying summaries. Derived data cached as small structured JSON shards; optional CSV for developer debugging. SQLite / DuckDB can be used inside CI to transform aggregates but is NOT a writable database hosted on Pages.
2. Player Steam OpenID callback, account ownership, consent and persistent cross-device role/economy connection require an **external secure serverless provider and private database** if the owner opts in; GitHub Pages/GitHub Actions cannot service an on-demand, private player auth callback by themselves. Never commit private cash/gold or Steam IDs to `docs/data` or artifacts.
3. Generate Discord recap images with Pillow/CairoSVG in Actions; validate actual Discord Components V2 payloads and real client desktop/mobile behavior. Static preview isn't acceptance.

## Non-generic visual quality: evidence-based criteria

The engine alone does not produce a premium dashboard. Require one coherent custom brand system: exact original 1AD/WARDOGS/faction assets, correct color meanings, controlled microinteractions, 1px boundary strokes, consistent numerical hierarchy, official avatar crops, contrast, clear chart interpretation, genuine data provenance, and no gratuitous sci-fi glows. Owner should approve the **compiled staging site**, not just hand-authored prototype source.

**Acceptance:** Build and test at 320/375/390/768/1024/1440 widths, keyboard + reduced motion, all chart filters/real datasets and error states, correct source math, no horizontal scroll, genuine deployed asset links, Lighthouse/accessibility where practical, and side-by-side screenshot comparison against owner-approved design commit. Use Playwright `toHaveScreenshot()` with a consistent runner OS/fonts for screenshot baselines.

**Implementation engineer handoff requirement:** Return a short written **architecture decision record** showing adopted tools, rejected alternatives, package license and security audit, bundle-size impact, staging build workflow changes, visual/functional QA, hosting/cost implications and rationale. No gratuitous rewrites, new paid hosting, or production changes without owner authorization.

## Primary documentation references
- GitHub Pages server-side limits: https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site
- Vite GitHub Pages `base` and Actions deploy: https://vite.dev/guide/static-deploy.html
- Sass modules: https://sass-lang.com/documentation/at-rules/use/ and import deprecation https://sass-lang.com/documentation/breaking-changes/import/
- D3 vs layered Plot marks: https://observablehq.github.io/plot/features/marks
- ECharts chart families / SVG and Canvas: https://echarts.apache.org/en/feature.html and https://github.com/apache/echarts-doc/blob/master/en/tutorial/renderer.md
- Motion SVG path drawing: https://motion.dev/docs/svg-animation
- Kivy / Tkinter target platforms: https://kivy.org/ and https://docs.python.org/3/library/tkinter.html
- Python CairoSVG: https://cairosvg.org/documentation/
- Playwright screenshot regression: https://playwright.dev/docs/test-snapshots
- Astro static GitHub Pages deployment (deferred): https://v5.docs.astro.build/en/guides/deploy/github/
