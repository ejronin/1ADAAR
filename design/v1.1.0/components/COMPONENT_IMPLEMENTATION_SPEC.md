# Component notes for v1.1.0

These are the measurements and behavior to carry from the editable design into staging. The owner still needs to approve the actual working result. The source pages are in `../prototypes/`; file-by-file component links are in `../screen-manifest.json`.

## Shared styling

The ordinary dashboard uses dark charcoal, off-white and restrained green (`#86f4a4`). Kills are green; deaths are yellow (`#f5c84b`). Use original faction colors only for their factions: Lonestar `#465eff`, Valkyra `#ee4138`, Manticore `#3eba42`. Weekly awards have their own muted gold, silver and bronze.

Use Barlow Condensed for display numbers/headings and the project's readable sans-serif for body copy. Target 14px/1.5 for normal text, clear source captions, 1px panel borders, 2.5px chart strokes, an 11px win-rate ring and controls at least 44px high. Use `tokens.final.json` as a **candidate** until reviewed.

Desktop: sidebar and paired content panels. At narrower widths, move navigation above the content, reduce cards to two columns and stack larger charts. Check 320, 375, 390, 768, 1024 and 1440 CSS pixels. Tables can scroll inside their own areas, but the page shouldn't overflow.

## What each screen needs

| Design source | Staging files to update | Key points |
|---|---|---|
| `home.html` | `docs/index.html`, `docs/assets/motion-v11.css`, `docs/js/app.js` | Keep real logo/artwork, honest status and saved-match empty states; fix laser and logo sheen |
| `player.html` | `docs/players.html`, `docs/js/players.js`, `docs/assets/player-v11.css` | Keep Steam avatar fallback, career KPIs, one win-rate ring, faction/map participation and original combat stats |
| Player chart | `docs/js/performance.js`, `docs/js/performance-core.js`, `docs/assets/performance.css` | Correct five modes, 10/20/all points, exact-value table; paired dots only for raw kills/deaths |
| Player progression | `docs/players.html`, `docs/js/players.js` and a separately approved private identity service | Six role levels/XP, WARDOG level, career XP, nullable account cash/gold, or clear unavailable state |
| `map-team.html` | `docs/map-team.html`, `docs/js/map-team.js`, `docs/assets/map-team.css` | Recorded K/D by map, sample counts, outcome fingerprint, original faction logos and panel-local controls |
| `weekly.html` | `docs/weekly.html`, `docs/assets/weekly.css`, `docs/assets/motion-v11.css` | Restored silver/gold/bronze podium and verified winners only |
| `recap.html` | `src/recap_card.py`, `src/discord_layout.py`, `src/recap.py` | Real Python image, supported Discord Components V2 payload, working link button and eligible faction leaders |
| `activity.html` | `docs/activity.html`, `docs/js/activity.js` | Saved match-start heatmap; personal online time remains separate until private session access and permission are confirmed |

The proposed design doesn't authorize replacing the real data collector or adding fictional player stats. Carry across the already-working behavior as well as the appearance.

## Home: border and logo motion

The laser is a **short moving segment** on the rounded hero perimeter. It goes once around the border in about **1.45 seconds**, fades out and leaves no bright segment behind. The resting outline stays subtle.

The logo sheen is a light gradient **masked by the actual `docs/assets/1ad-logo.svg`**, with the same displayed size and silhouette. The emblem itself does not translate, enlarge or become a second transparent image. Start the roughly **1.1-second** sheen after the border trace. Turn both animations off under reduced motion; the art remains visible.

Check the whole animation in a browser, not just one screenshot. There must be no square glow across the hero or oversized logo copy.

## Player cards and charts

The four prominent career totals are K/D, kills, deaths and matches. Show wins, playtime and seeding as supporting figures. Retain optional headshots, vehicle kills, best kill streak and team kills when real WARCON feed data supports them.

The win-rate ring is roughly **140–165px across**, with an **11px** arc and track. The fictional PlayerOne fixture is **27 wins in 48 matches = 56.25%**. Write the denominator beside the percentage. Most-played faction and map should use labeled participation bars, not duplicate win-rate donuts.

Performance modes:

| Mode | Meaning | Valid display |
|---|---|---|
| Kills & deaths | Counts in each saved completed match | Two-series trend or paired-dot/dumbbell |
| Match K/D | Kills divided by deaths **in one match** | Ratio points/line |
| Trailing 5-match K/D | Sum kills ÷ sum deaths in the current and previous four matches | One ratio per completed trailing window |
| Trailing 5-match averages | The separate five-match mean kills and deaths | Two-series trend; first four windows missing |
| Career K/D | Dated saved all-time WARCON career snapshots | Chronological career line |

**Last 10 / Last 20 / All** selects plotted **points**, not the number of matches used in a trailing calculation. For example, point 12 in a trailing five-match chart uses matches 8–12; neighboring points overlap. Put that explanation where a player can see it. Keep exact data in a table. The paired-dot encoding control appears **only** in raw kills/deaths mode—hide it elsewhere rather than leaving a nonworking choice.

A waterfall chart doesn't fit a non-additive K/D ratio. Don't manufacture skill scores or assume an undefined zero-death ratio.

For sample map data, the ten most recent PlayerOne records produce **5 wins, 4 losses and 1 draw**. Aggregate map K/D uses total recorded kills divided by total recorded deaths for that map: Zestafona **1.82 (3 matches)**, Bakurani **1.52 (4)**, Ozeti **1.39 (3)**. Label source period, formula and sample size. Keep the result-composition selectors inside that panel because they only change its local breakdown.

The Steam portrait must match a verified real Steam account or use a plain initial fallback. Don't assume a picture proves Discord membership.

## Weekly podium

The owner chose the earlier **Community Players of the Week** layout: **silver #02 on the left, slightly taller gold #01 in the center, bronze #03 on the right**. Use the same rank font and circular portrait treatment on all three. Metal finishes should be quiet: 1px highlighted rims, a soft static reflection and proper silver `#b9cbd3`, gold `#e5bc70`, bronze `#c18a6d` borders. Avoid neon effects.

An unassigned first-place slot may show the **small static placement crown** from `components/weekly-crown.svg`. Only after a real eligible winner is verified may its populated version fade in over **650ms** above the correct avatar. Turn movement off when reduced motion is requested.

Unfilled cards say **Awaiting results**, the place name and **No player selected**. Don't invent three winners or use unverified Steam photos/Discord membership. The sample-player animation switch is for design review only and must not reach production.

The browser proof is `screenshots/weekly-390.png` and `weekly-1440.png`. Also check 320px, unusually long names, one or two eligible winners and the real empty state.

## Discord recap

The design's HTML preview is not proof of Discord rendering. Use the actual Python-rendered **1080px PNG** and supported Discord Components V2 fields:

- Message flag `32768` (IS_COMPONENTS_V2).
- Container `type:17` containing Text Display `type:10` and Media Gallery `type:12`, referencing `attachment://match-recap.png`.
- Action Row `type:1` with a **real external link button**: `type:2`, `style:5`, HTTPS 1ADAAR URL, and **no `custom_id`**.

See `components/discord_recap_contract.py` and its tests for the required payload shape. Test the delivered result in Discord on desktop and mobile.

If the completed match has **complete verified player lines**, show the highest recorded-kill player in each of Lonestar, Valkyra and Manticore. Show ties as ties; if the records are incomplete, don't name a winner. These are *match kills*, not career rankings or role XP. Never post fictional match content to the real channel.

## Activity and role progression

The server activity grid counts **captured completed-match starts** by weekday/hour in Eastern time. Empty cells do not prove that nobody was playing. Keep it separate from personal online hours.

Player online-time heatmaps need complete, authorized `joinedAt`/`leftAt` records and permission to publish. `components/session_aggregator.py` contains tested overlap and daylight-saving calculations; it doesn't itself fetch private records.

Six-role levels and XP are documented by the **public synced WARDOGS Tracker player API**, not by the reviewed WDRCON/WARCON fields. See [the source investigation](../research/ROLE_PROGRESSION_ACCESS_VALIDATION.md) and [the connection guide](../research/PLAYER_PROGRESSION_OPT_IN_IMPLEMENTATION.md). A real role-level radar needs a complete, accessible player record, valid common scale, correct season and a sync date. Otherwise show an empty radar and exact “unavailable” labels, not made-up polygons.

The optional account cards are **WARDOG level**, **career XP**, **account cash** and **gold**. Respect the source's separate hidden/missing cash and gold fields. These are not live match cash. There is no loadout builder or unverified weapon chart in this handoff.

## Final checks

Run the existing Python/JS tests and browser QA at all six widths. Compare **actual staged pages** with the approved source captures, including focus, keyboard controls, reduced-motion and truthful empty-data states. Check source attribution, calculator behavior, secrets and real Discord rendering. The implementation engineer returns a usable staging link and a list of anything still blocked.

No production deployment follows automatically from design approval or passing CI. The owner gets to inspect the finished staging version before approving a merge.
