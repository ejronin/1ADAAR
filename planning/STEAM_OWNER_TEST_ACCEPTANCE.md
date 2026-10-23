# Steam-verified progression — owner-only acceptance route

This is a **narrow deployment review**, separate from larger PR #36. It adds exactly one new route, `docs/progression.html`, with separate JavaScript/CSS and no fictional player fixtures.

**Status:** code prepared for owner approval. This branch has not been merged into the public GitHub Pages production site.

## Purpose

Once reviewed and merged, the new page will be reachable at:

https://ejronin.github.io/1ADAAR/progression.html

It will call the already-deployed owner-controlled Cloudflare Worker at:

<owner-controlled-neutral-auth-origin>

The Worker now has a confirmed /health response and D1 binding, but no real Steam login has been completed yet.

## Privacy & scope

- Page initially shows empty role axes/XP fields, until real Steam ownership and consent are completed.
- Steam OpenID login occurs at Steam, not 1ADAAR; Worker verifies the OpenID response with Steam.
- Account identifiers are used privately in the Worker and never rendered on the page.
- Return code exchange uses PKCE and a one-time, short-lived code. Tokens are stored only in tab sessionStorage and expire.
- WARDOGS Tracker's public player API supplies game-wide six-role levels/XP, overall level, career XP, synchronization date; optional cash/gold only with separate consent.
- No WARCON server match results are modified. No other live 1ADAAR pages or menus change. The existing `docs/js/progression.js` remains unchanged.
- This public test route is **not access-controlled by username** after deployment. Anyone can open it, but each user must verify their own Steam account to access their own data.

## Owner acceptance checklist

1. Explicitly approve merging this narrow PR and publishing its new standalone page. Do not merge the entire draft PR #36 at this stage.
2. In Chrome, open the published progression page and select **Connect with Steam**. Confirm Steam's official domain for credential entry.
3. Complete Steam sign-in, return to 1ADAAR, then approve game-wide progression consent. Leave economy off for the first pass.
4. Compare returned values with the owner-supplied WARDOGS Tracker screenshots, taken in Season 2 with a very recent sync: WARDOG level **17**, career XP **31,264**, Assault level **6**/11,605 XP, Support level **6**/11,370 XP, Medic level **5**/8,106 XP, Recon level **0**/125 XP, Driver and Pilot at level **0**. Do **not** hardcode or publish these as a user's permanent stats; they are a time-specific acceptance reference only.
5. Verify account economy values remain hidden until separately consented; then test refresh and disconnect.
6. On failure, capture only the UI error message, URL host and Cloudflare request time. Do not share Steam login cookies, callback codes, SteamIDs or auth tokens.
7. Leave the broader v1.1.0 feature rollout and map/banner/hero-copy PRs independently staged until owner review.

## Notes

Source: [WARDOGS Tracker Developers](https://wardogstracker.gg/developers), endpoint `/api/v1/players/{steamId}`. Tracker's `stats` is null without synchronization and 404 is used for unknown/private profiles. Tracker does not provide a separate OAuth callback for 1ADAAR.

The owner-provided screenshot's visible 'Sign in' button belongs to the **Tracker** site. An already synchronized *public* profile can be browsed while signed out; it does not establish ownership or consent on 1ADAAR.

## Exit criteria

Do not announce live ownership verification until the browser reaches the verified connected state, all six exact role values match Tracker, and disconnect revokes consent. A healthy Worker alone is not sufficient.
