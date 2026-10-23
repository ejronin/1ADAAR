# Progression connections and privacy

1ADAAR reads **already-public** WARDOGS Tracker records directly from the browser. It does not sign in to Steam, request a Steam password, or claim that loading a public profile verifies ownership.

## Save a profile once

On **My WARDOGS progression**, paste the public WARDOGS Tracker profile URL or SteamID64 and select **Load public stats**. Enable **Remember this public profile on this browser only** to reopen it automatically on this device. The browser retains the SteamID64 in localStorage only with explicit opt-in. **Clear saved profile** deletes it. No SteamID is committed to public GitHub Pages snapshots or sent to WARCON or the 1ADAAR collector; the browser sends it only to WARDOGS Tracker's documented public API. Private/unsynced accounts are not accessible.

Public game-wide level, career XP, six role levels/XP, unlock count and public profile image come from Tracker. Optional cash/gold are shown only after separate UI selection; null values remain unavailable, while genuine zero is displayed as zero. On a server-specific dossier, the account key must match that WARCON player.

## Community-server combat

The separate community form requests `GET /api/v1/servers/{server}/leaderboard?range=7d&limit=100` from Tracker. It reports only recorded kill-feed data for connected, claimed community servers. The input is prefilled with a **public** Digital Anarchy server join code. If the server is not connected or the player is absent from the top-100 response, 1ADAAR does not treat the missing record as zero kills or a missing game session. WARCON match records from OneAverageDan's server remain a separate source and cannot account for play on other servers.

Sources: https://wardogstracker.gg/developers and https://wardogstracker.gg/about.

## Steam ownership verification is disabled pending an anonymous hostname

The previous Steam OpenID Worker used an account-subdomain containing a person's name. It is no longer linked or called by the public frontend. **Do not restore the previous URL or mask it with deceptive text.** Rebranding a UI disclaimer does not change a hostname Steam displays.

To restore account ownership verification later:

1. In Cloudflare **Workers & Pages**, change the account's `workers.dev` subdomain to a non-personal identifier (check whether other Workers share the account and will be affected), or configure a separately owned neutral custom hostname and disable the old public `workers.dev` route.
2. Update `AUTH_ORIGIN` in the Worker and `endpoint` in the frontend to exactly the new HTTPS origin. OpenID `return_to`, `realm`, verified callback and accepted origin must all agree.
3. Deploy the Worker through Cloudflare, verify `/health`, the real Steam OpenID response, approved consent and disconnect. Never publish SteamIDs, token hashes or real names as logs. Only then re-enable an optional verified Steam connection.
4. Disable the legacy Worker route from Cloudflare, revoke old active sessions if possible, and confirm the old personal-domain URL no longer responds.

Cloudflare instructions: https://developers.cloudflare.com/workers/configuration/routing/workers-dev/

The GitHub connection can edit the source and publish 1ADAAR, but it cannot independently change Cloudflare account subdomain/DNS, disable the already-running Worker route, or inspect the owner's Steam session.
