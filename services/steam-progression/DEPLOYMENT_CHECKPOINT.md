# Cloudflare Worker build checkpoint — 2026-10-22

GitHub repository: `ejronin/1ADAAR`

Cloudflare Worker: `1adaar-steam-progression`

Cloudflare production branch: `feature/v1.1.0-steam-verified-progression`

Workers Builds root directory: `/services/steam-progression/`

Deploy command: `npx wrangler deploy`

D1 binding: `DB` → `1adaar-steam-consent`

Expected public health endpoint: `https://1adaar-steam-progression.shawn-k-gordon.workers.dev/health`

This non-secret document is committed after the owner connected GitHub to the existing Worker. It deliberately triggers the first production-branch build using the configured Cloudflare Workers Builds integration. It is not evidence that the deployment has succeeded; confirm the Cloudflare build log and the actual `/health` response before enabling the public 1ADAAR sign-in button. Do not include SteamIDs, personal tokens, or private user data in this repository.

The GitHub Pages production site must remain unchanged pending owner acceptance of the authenticated Steam-flow test.
