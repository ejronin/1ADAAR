# Optional player progression: implementation notes

The v1.1.0 progression feature covers **six role levels and XP, overall WARDOG level, career XP, and account cash/gold when visible**. It doesn't include a loadout builder, unlock gallery or weapon charts. WARCON's server statistics and the activity heatmap remain separate.

## Source and limits

[WARDOGS Tracker](https://wardogstracker.gg/developers) documents a read-only public API at `https://wardogstracker.gg/api/v1`. Its [OpenAPI file](https://wardogstracker.gg/api/v1/openapi.json) describes `GET /players/{steamId}` with six `roles.*.{level,xp}` records, `wardogLevel`, `careerXp`, nullable `cash` and `gold`, and `syncedAt`.

The player must sign into [WARDOGS Tracker](https://wardogstracker.gg/stats) with Steam and sync their own profile. Private/unknown profiles can return 404; unsynced profiles may have `stats: null`. The public endpoint is documented as cached for about 60 seconds and limited to roughly 120 requests/minute/IP. Confirm these details and the service's retention/republication terms before enabling any collector.

These are **game-account progression** figures. They are not the player's performance on Dan's server, and Tracker's account cash must not be called live in-match “cash in pocket.” Cash and gold can be hidden separately. A source value of **0** is a real value; `null` or missing means unavailable, not zero.

## What the player sees

The existing WARCON player dossier should work even if the player never signs in anywhere.

The optional **Your WARDOGS progression** section starts with an empty six-role radar and labeled slots for Wardog level, career XP, account cash and gold. No test numbers in a real profile. It names WARDOGS Tracker as the source and shows the latest sync date when data becomes available.

The first action is **Sync on WARDOGS Tracker ↗**. Open the real Tracker site in a separate tab so the 1ADAAR dossier stays open. Explain that the player signs in on Tracker, closes the game and syncs their stats there.

The next action, implemented as part of the secure connection, is **I've synced — check my progression**. It checks the accessible public record for the **already verified account**. If that record isn't available, give a clear message and leave the rest of the profile alone.

**Tracker does not document a third-party OAuth callback or automatic return URL.** Don't invent `redirect_uri` support or suggest a link click verifies ownership. A real login/return to 1ADAAR would be a separate 1ADAAR-controlled sign-in flow.

## What a connection would mean

There are two ways to stage this feature:

**Simple link-only version:** add the external Tracker link and honest empty/progression-available messaging. No persistent account claim. Browser `localStorage` or a typed SteamID is not account verification. This is the only option that needs no new private backend.

**Full optional connection:** A lasting, cross-device connection would use secure Steam OpenID verification through a separately approved private identity/storage service. GitHub Pages can't process an on-demand private login callback or operate a writable private database. The provider, usage limits, cost, data retention and failure behavior need to be clear before it is enabled.

For the full connection:

1. The player selects **Connect my Steam account** on their existing dossier. Start Steam OpenID through an approved HTTPS service, with a signed short-lived state/nonce, CSRF checks and server-side callback verification.
2. Privately confirm the returned SteamID64 belongs to the same player as the site's internal `player_key`. Never accept a typed ID, copied URL, Discord nickname or hash as proof of ownership.
3. Ask separately for consent to display **role/XP progression** and **account cash/gold**. Keep the consent version, time and a way to revoke either choice.
4. Fetch the allowed public Tracker profile through the private service, verify the matching SteamID, complete six role fields, valid `syncedAt`, profile visibility and current game season. Use a verified common maximum level before drawing the radar; otherwise show exact levels as rows.
5. Store only the necessary link and approved data in the private store, keyed to the site's existing opaque player key. Keep Steam IDs private. Don't store Steam login/game-session tokens or commit private money, account IDs or consent records into `docs/data/` or Git history.
6. Return to the original 1ADAAR player dossier with an allowlisted internal player key and authenticated session. No arbitrary redirect URL, long-lived query token or SteamID in the browser URL.
7. On later visits, read the stored consent and permitted data. Respect Tracker's cache and 429 responses, back off on errors and display `syncedAt`; site visits must not trigger uncontrolled polling.
8. If consent is withdrawn or the source turns private, is deleted, or no longer permits display, stop showing cached data and remove/expire it under the agreed retention policy. Provide **Disconnect / Stop displaying progression**.

Never publish a private roster, session record or hidden cash/gold simply because a player once appeared on Dan's server.

## Data fields and display

| Tracker field | 1ADAAR display | Notes |
|---|---|---|
| `roles.{assault,medic,recon,support,driver,pilot}.level` | Six-role radar or exact level bars | Same verified level scale for all axes |
| `roles.*.xp` | XP beside each role | Don't use XP to fill a level-scale polygon |
| `wardogLevel` | WARDOG level card | Account progression, not server rank |
| `careerXp` | Career XP card | Show the sync date |
| `cash` | Account cash | Nullable and separately hidden |
| `gold` | Gold | Nullable and separately hidden; zero is valid |
| `syncedAt` | Last synced | Source time, not collection-job time |

Reusable source is already in `design/v1.1.0/components/progression_adapter.py`, `role_radar.js`, and `role_radar.schema.json`. The adapter checks the private SteamID association and returns a normalized record without that identifier. Its tests are in `design/v1.1.0/tools/test_progression_adapter.py`. The editable UI is `design/v1.1.0/prototypes/player.html#progression`.

## What a working connection has to prove

Use one **consenting, actually synced player** to prove the endpoint and exact fields. Check that:
- That person can connect only their own player dossier, with no exposed SteamID or sensitive URL.
- Private/unknown and unsynced Tracker accounts stay unavailable, with no invented role levels.
- Hiding cash but not gold (and vice versa) works; an actual zero remains zero.
- Session expiry, revoked consent, disconnect, source downtime and 429 rate limiting are handled.
- The radar scale, six labels, XP rows, current season and sync date match source data.
- A returning user on another device sees only records they're still authorized to see.
- The phone layout, keyboard controls and first-party callback pass the same security and visual checks as the rest of staging.

The working staging page, chosen provider, tests and any remaining data limitations are part of the release record. Production stays unchanged until the finished site and any new service have been reviewed and approved.
