# Frontend and graphics tools: what is worth adding?

This is the technology review for v1.1.0, written October 22, 2026. It isn't an instruction to replace a working site or add every library listed below.

## What 1ADAAR runs today

On `staging/v2.0-foundation`, the pages are plain HTML, CSS and JavaScript under `docs/`. Player charts are drawn with custom SVG. Python handles data collection and Discord images. The existing `.github/workflows/pages.yml` uploads `docs/` straight to GitHub Pages when `main` changes.

There is **no** `package.json`, Vite, Sass, React or Astro build pipeline in that staging branch. Any new bundler would be a deliberate project change. GitHub Pages only serves static output; it cannot run Python or handle private Steam login callbacks.

## Recommended tools

| Tool | Where it helps | Decision |
|---|---|---|
| **Dart Sass / SCSS** | One organized source for fonts, spacing, colors, components and mobile layouts | **Add first**, compiling to the CSS files the site already loads |
| **Vite** | Bundles modern JS/CSS and handles imports when we introduce chart libraries | **Add only if needed**; preserve the multi-page site |
| **Custom HTML/CSS/SVG/JavaScript** | The 1AD sheen, border laser, podium and existing lightweight charts | **Keep** as the main design foundation |
| **D3 modules** | Precisely controlled dumbbell charts, lollipop charts, scales and time heatmaps | **Preferred for a handful of harder charts** |
| **Observable Plot** | Layered statistical marks and quick small-multiple layouts | Consider instead of hand-building complex charts |
| **Apache ECharts** | A broader ready-made interactive chart set, including radar and heatmaps | Alternative to D3/Plot, **not another engine to install alongside them** |
| **Motion for JavaScript** | Timed SVG animation when CSS alone isn't precise enough | Optional; only for a measurable interaction |
| **Python Pillow + CairoSVG** | Generates sharp, branded Discord PNG reports from original SVG artwork | **Keep and expand** |
| **Matplotlib** | Offline statistical figures and exported SVG/PNG | Optional, when an actual report needs it |
| **NumPy / pandas / Polars** | Processing unusually large match/event sets | Only when Python's built-in tools become a bottleneck |
| **Playwright** | Browser tests, screenshot comparisons and keyboard checks | **Use for every staging release** |
| **Bootstrap** | Generic page layout and premade controls | Skip as the visual system: we'd spend time overriding it |
| **Tailwind** | Compile-time CSS utilities | Not necessary for the existing CSS codebase |
| **Astro** | Shared layouts and static page components | Revisit if repeated page markup becomes hard to maintain |
| **React / Vue / Svelte** | Larger state-heavy interactive apps | No rewrite needed just to improve appearances |
| **Kivy / Tkinter** | Desktop Python windows | Wrong target: GitHub Pages and Discord image jobs don't need desktop GUI frameworks |
| **Three.js / PixiJS / WebGL** | Real 3D or unusually rich visual scenes | Not needed for a static stats dashboard |

**Choose one chart approach.** The existing SVG code already does quite a lot. Where it gets cumbersome, try a small D3-based chart and compare it with an ECharts example if needed. Don't bundle D3, Observable Plot, ECharts and Plotly together without a clear reason.

The difference between a premium dashboard and a generic one is usually the work done on hierarchy, source labels, chart choices and the original artwork—not whether the site uses a fashionable framework.

## How the technology fits together

### Shared styles come first

Move repeated values into shared tokens: 1AD green, faction blue/red/green, weekly metallic shades, spacing, type scale, line thickness and focus states. Use modern Sass `@use`/`@forward` and compile it into the existing CSS layout.

Keep the current site working while migrating styles. The original WARDOGS and 1AD assets shouldn't be recreated or changed.

For the hero, keep the light sweep masked to the **same SVG and size** as the logo, not a sliding duplicate. A small laser segment should travel the entire rounded hero border once, then disappear. Respect reduced-motion settings.

### A build tool is useful when imports grow

Vite makes sense once the site needs modules or package imports. It can build a multi-page site **without React**.

If it's added:
- Keep the existing page paths, player deep links and data fetches working.
- Set the GitHub Pages base path to `/1ADAAR/` and test every image, font and JSON reference.
- Keep a lockfile and use a clean install in GitHub Actions.
- Build and publish an **isolated staging preview** first. Do not modify the production Pages workflow or merge because a build passed.
- Measure the JS bundle and check dependency licenses/security updates.

### Charts follow the data

Useful additions, with actual supporting data:

- Paired-dot kills versus deaths for a recorded match.
- Recorded K/D by map as an ordered dot/lollipop chart.
- A scored lead-change timeline from saved match score samples.
- Weekday/hour match-start heatmap; a separate authorized player-session minutes view only if that data is complete enough.
- Six-role **progression level** radar with exact XP beside it, drawn only for an accessible synced WARDOGS Tracker profile and a verified level scale.

A waterfall chart is not right for a non-additive K/D ratio. Don't draw weapon usage, loadout combinations, map movement or made-up role performance from fields that aren't available.

For static Discord reports, keep Pillow and CairoSVG. For analytical images generated in Actions, consider Matplotlib. Neither Kivy nor Tkinter helps with this workflow.

### Private account data stays outside Pages

The website can publish small, sanitized JSON files computed by Python in GitHub Actions. If the archive grows, SQLite or DuckDB can help with temporary build-time calculations; that does **not** make GitHub Pages a writable database.

A real, cross-device Steam connection needs a secure HTTPS identity/consent backend and private storage. It cannot be implemented with Pages and Actions alone. The [progression connection plan](PLAYER_PROGRESSION_OPT_IN_IMPLEMENTATION.md) covers that separately.

## How a technology choice is evaluated

The decision is easier to evaluate when it includes:

- Which tools are being adopted, with one sentence explaining why each is needed.
- The packages, versions, licenses and effect on bundle size and GitHub Actions time.
- A staging build showing that all pages, assets and deep links still work.
- Comparison screenshots against the approved design at 320, 375, 390, 768, 1024 and 1440 pixels.
- Working chart controls, accessible tables, keyboard focus and reduced-motion checks.
- A clear note on any extra service, cost, privacy or long-term maintenance burden.

The actual compiled staging site—not just the source mockups—is what matters for a release decision. Any new paid service or production dependency also needs to be agreed on before it is introduced.

## Useful documentation

- [GitHub Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)
- [Vite static deployment](https://vite.dev/guide/static-deploy.html)
- [Sass modules](https://sass-lang.com/documentation/at-rules/use/)
- [D3/Observable Plot](https://observablehq.github.io/plot/features/marks)
- [Apache ECharts](https://echarts.apache.org/en/feature.html)
- [Motion SVG animation](https://motion.dev/docs/svg-animation)
- [Kivy](https://kivy.org/) and [Tkinter](https://docs.python.org/3/library/tkinter.html)
- [CairoSVG](https://cairosvg.org/documentation/)
- [Playwright screenshots](https://playwright.dev/docs/test-snapshots)
