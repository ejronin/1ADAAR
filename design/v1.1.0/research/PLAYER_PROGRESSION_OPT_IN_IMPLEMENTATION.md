# Implementation engineer handoff — Optional WARDOGS player progression connection

**1ADAAR v1.1.0 design decision.** Owner confirms exactly these optional player-profile fields: **six role levels and XP**, **overall WARDOG level**, **career XP**, and **account cash and gold**. Keep the personal time heatmap workstream independently scoped to WARCON authorized sessions. **No loadout builder, unlock gallery, or weapons module in this deliverable.** Weapon kills-with/deaths-by analytics may be reassessed only when complete WARCON kill-event feeds and player attribution have been independently validated; do not make it a release gate.

## 0. Authority and verified source

WARDOGS Tracker independently documents a free read-only public API: https://wardogstracker.gg/developers and https://wardogstracker.gg/api/v1/openapi.json. Base `https://wardogstracker.gg/api/v1`; `GET /players/{steamId}` returns `player.stats.wardogLevel`, `careerXp`, nullable `cash` and `gold`, `roles.assault/medic/recon/support/driver/pilot.{level,xp}`, and `syncedAt`. Unknown/private profiles return HTTP 404; unsynced records can have `stats: null`. API is read-only, CORS-enabled, cached ~60s, 120 requests/min/IP (respect 429 Retry-After); attribution WARDOGS Tracker required. These are **game account progression values**, not WARCON per-server combat metrics or live RCON `cash`. The source operator is an unofficial third party; obtain any extra permission needed for retention and republication.

Official WARCON remains the source of 1ADAAR match/career combat analytics. No WDRCON or WARCON six-role XP endpoint is documented. Tracker is an **opt-in synchronized profile**, not an inventory of all players who visit Dan's server. Tracker's https://wardogstracker.gg/stats describes Steam login on *their* site, press **Track my stats**, close WARDOGS to sync, and later background updates. Cash/gold are independently `null` for hidden values. Game seasons may reset progression/cash; gold is said to carry over, so store `syncedAt` and label all values as game-account stats.

## 1. User experience, two separate consents

Existing 1ADAAR player dossier (WARCON stats) must work **without** external account linkage.

New panel title **Your WARDOGS progression** under career/performance, with an attractive but **unfilled** six-role radar and four source-label teaser cards:
- **Wardog level** (overall);
- **Career XP**;
- **Account cash** (do NOT say in-match “Cash in pocket”);
- **Gold**.

Below radar: Assault, Medic, Recon, Support, Driver, Pilot rows with `Level — · XP —` until synced. No fake values. Label `Optional · WARDOGS Tracker` and `Last synced: —`. The normalized actual values replace dashes only after eligibility and privacy checks. Absent/hidden cash or gold stay **Hidden or unavailable**; zero is only shown when the source explicitly says 0.

Two independent actions:
**(A) Sync with WARDOGS Tracker ↗** — open https://wardogstracker.gg/stats in a new tab, preserving the current 1ADAAR dossier. This is a plain verified external link, NOT an invented OAuth exchange or tracker callback.
**(B) I've synced — check progression** — when implemented, calls the approved 1ADAAR backend to refresh the specific already identity-bound profile; if not available, show an accurate explanation and keep the user on the dossier. Do not create a fake-success button in the design preview.

A small explanation: "Sign in with Steam on WARDOGS Tracker, close the game and synchronize. Return to this tab and check again. Your 1ADAAR match stats work without this." Credit https://wardogstracker.gg. If tracker later documents a `return_to` protocol, support it only after official validation; currently there is **no verified callback parameter**.

## 2. Identity, privacy and persistent connection — two implementation tiers

**Tier 1 (no new hosted backend):** Show a read-only optional external Sync link and stat availability notice. A user may revisit/check their profile, but **a click or localStorage value must NOT be interpreted as verified Steam ownership or permanent cross-device consent**. Do not publish raw SteamID in a static Pages fetch URL. This tier has no genuine persistent account connection.

**Tier 2 (required for durable, cross-device opt-in):** Use a secure, owner-approved free-tier serverless identity/consent store (example architecture: HTTPS edge functions + managed Postgres with row-level security, or an existing equivalent connected identity service). Still no paid server and no owner's personal PC. Engineer must confirm free-tier limits, retention, backups, and OAuth/OpenID capabilities before selecting provider.

1. On the 1ADAAR player dossier, click **Connect my Steam account**. Start login through a **trusted Steam OpenID** integration or the approved identity provider, with signed nonce, state, CSRF protection, short expiry and HTTPS-only callback. Steam OpenID authenticates the user to **1ADAAR**, not to WARDOGS Tracker. Verify OpenID response server-side against Steam and match returned SteamID64 against the player's existing private WARCON identity mapping. Never accept a typed SteamID as proof of account ownership.
2. In the same authenticated session, obtain explicit granular consent: **show my six role levels/XP and overall level/career XP**; separately **show my account cash/gold** (opt-out possible independently). Record time, consent version, source and revocation ability. Consent belongs to the player, not simply a browser clicking an external link.
3. Serverless private function queries the read-only WARDOGS Tracker public endpoint, verifies source and matching 17-digit SteamID64, `stats` present, all six roles correctly typed and finite, source `syncedAt`, known common level axis maximum, and permitted profile privacy. Null economy readings stay null. The role radar should **not be filled until the game/season's common axis maximum is verified**; if unknown use ranked exact level bars/rows first.
4. Persist a *private* row keyed to the already existing 1ADAAR opaque internal `player_key` plus identity-link credential, consent flags, last `syncedAt`, last successful check time, status, source URI, and limited normalized level/XP/cash/gold snapshot in private storage. **Raw SteamID remains private only**, never as a Pages URL, commit, downloadable JSON shard, webhook or frontend log. Do not store Steam login or game-session tokens. The per-player public profile uses only approved normalized fields after privacy recheck.
5. Return through a **1ADAAR-controlled callback**, not WARDOGS Tracker, to the **existing local dossier path** using an allowlisted opaque `player_key` and authenticated session. No open redirects, long-lived tokens or SteamID in query strings. Check and show `Connected` only when account proof, permission and API data all succeed.
6. Subsequent visits read the private consent link across devices. Refresh at a sensible cadence with a cache >=60s and backoff on 429, 5xx and network errors; check `syncedAt`, because tracker data is not automatically realtime. Do not hammer the API by repeated dashboard browsing. If profile becomes private, 404, is deleted, or consent revoked, hide previously cached progression immediately and purge/expire cached copies according to retention policy. **Don't commit per-player sensitive economic data to GitHub Pages or Git history**, since removal cannot be guaranteed there.
7. Include **Disconnect / Stop displaying progression**, a conspicuous source credit, `Last synced`, stale-data label, and a short privacy explanation. Failure is normal and non-blocking: `No synchronized public Tracker profile`, `Private profile` (if 404 does not distinguish unknown, use combined wording), `Tracker unavailable`, `Data older than X`, `Economy hidden`, `Verification pending`.

Even if opt-in consent is granted, the source's own hidden cash/gold values MUST NOT be inferred or shown.

## 3. Data mapping and visuals

| Tracker field | Public normalized field | Display | Notes |
|---|---|---|---|
| stats.roles.assault..pilot.level | levels[Assault...Pilot] | Six-axis **level** radar, or exact ranked levels if axis limit unknown | Same scale; include each numeric level |
| stats.roles.assault..pilot.xp | xp[Assault...Pilot] | Exact rows / grouped detail | XP is NOT proportional to level scale by default |
| stats.wardogLevel | wardogLevel | Prominent numeric KPI | Game account, not server ranking |
| stats.careerXp | careerXp | Numeric KPI | Scope, syncedAt |
| stats.cash | cash / status | Numeric economy card | Nullable independently; NOT in-match cash |
| stats.gold | gold / status | Numeric economy card | Nullable independently; 0 valid |
| stats.syncedAt | capturedAt | Sync freshness | Source timestamp, not site collection time |

Implementation-friendly existing source:
- `design/v1.1.0/components/progression_adapter.py` — validates six roles, matches private SteamID, normalizes overall level/XP/cash/gold with privacy-safe nullable semantics.
- `design/v1.1.0/components/role_radar.js` and `role_radar.schema.json` — source-gated six-axis renderer, only if real complete levels and a common axis maximum.
- `design/v1.1.0/prototypes/player.html` + `shared.css` — optional progression teaser and real outbound link.
- `design/v1.1.0/research/ROLE_PROGRESSION_ACCESS_VALIDATION.md` — provenance and RCON/WARCON limitations.
- Tests in `design/v1.1.0/tools/test_progression_adapter.py` must pass before staging.

## 4. Acceptance for implementation engineer

**Proof required:** Real player who voluntarily synced: Steam identity verified to 1ADAAR, 200 response from Tracker, actual level/XP fields match source, economy permissions respected, no raw SteamID in public assets/network URLs/logs, and redirection back to correct dossier. Test another user trying to opt into a different player's dossier: must fail. Test a private/unsynced user, hidden cash alone, hidden gold alone, genuine zero cash, consent revocation, session expiry, 429 backoff, current season, all six axis labels and mobile. Confirm no promises of exact live match money or equipped weapons.

After owner approval, implementation engineer ports design source to staging, returns a hosted working player dossier and privacy-safe test report, and requests IA visual-fidelity verification before any production deployment.

**Owner decision needed from implementation engineer:** whether to start with Tier 1 link-only or approve Tier 2 identity/consent backend to achieve true durable cross-device opt-in. Do NOT present Tier 1 as “always connected.” Free hosting does not eliminate the need for an authenticated persistence system.
