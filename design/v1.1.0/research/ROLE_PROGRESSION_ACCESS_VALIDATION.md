# Can 1ADAAR read the six WARDOGS role levels?

**Research note, October 21–22, 2026.** The answer depends on which service we're using. The six levels are documented in a public third-party API, but we have **not** tested access for Dan's players or found them in the dedicated-server RCON feed.

## What each source provides

**WDRCON (the game's server RCON)**

The [documented dedicated-server API](https://github.com/warcon-app/warcon/blob/main/docs/wardogs-api.md) gives the current roster's name, Steam ID, faction, kills/deaths, cash and ping. It doesn't document Assault, Medic, Support, Recon, Driver or Pilot XP/levels. The actual server's `GET /v1/capabilities` should still be checked against its installed build before making a broader claim.

**WARCON (the server-history service)**

[WARCON's published code](https://github.com/warcon-app/warcon) covers matches, historical scoreboards, factions, sessions and optional kill events. The reviewed API fields likewise do not include six-role game-account progression.

**WARDOGS Tracker (optional public player profiles)**

[Developer API documentation](https://wardogstracker.gg/developers) and its [OpenAPI file](https://wardogstracker.gg/api/v1/openapi.json) describe:

```text
GET https://wardogstracker.gg/api/v1/players/{steamId}
player.stats.roles.{assault,medic,recon,support,driver,pilot}.{level,xp}
player.stats.wardogLevel
player.stats.careerXp
player.stats.cash
player.stats.gold
player.stats.syncedAt
```

Players sign in with Steam on [WARDOGS Tracker](https://wardogstracker.gg/stats) and synchronize their own game profiles. The API is read-only and documented as free, with no API key, roughly a 60-second cache and a limit of 120 requests a minute per IP. It only works when the player's synchronized profile is accessible; unknown/private profiles return 404 and unsynced profiles may have `stats: null`. Cash and gold may be hidden independently.

This is a **documented integration route**, not proof that the connection has been tested with a real account in 1ADAAR. Verify the current endpoint, rate limits, privacy rules and field meanings during implementation. Credit WARDOGS Tracker on the profile.

**WARDOGS Zone**

[WARDOGS Zone's privacy information](https://wardogs.zone/privacy) describes using an authorized player login and a game-backend session to collect progression. This backs up the conclusion that account progression exists outside RCON. It is **not** permission to copy that service's account-session method or collect Steam tokens ourselves.

**Developer and community discussion**

The [community-server discussion](https://www.reddit.com/r/WarDogs/comments/1w1qe66/wardogs_devs_community_servers_update/) treats RCON as an administration tool, not a public account-progression export. Players discuss leveling in these threads: [progression feedback](https://www.reddit.com/r/WarDogs/comments/1wgarem/progression_feedback_from_someone_who_has_tried/) and [Assault leveling](https://www.reddit.com/r/WarDogs/comments/1wmqbnl/assault_class_is_by_far_the_hardest_to_progress/). None of these establishes a new RCON route or an official developer-backed public account API.

## What we can build

For a player who has synced and allowed access, show:

- Six role **levels** on a common-scale radar, plus exact level/XP rows. Confirm the current game's level maximum and season first; if the scale is unknown, show rows or ranked bars without a radar polygon.
- Overall WARDOG level and career XP.
- Account cash and gold **only when visible**. These aren't the same as a live match's RCON cash value.
- Source credit and `syncedAt` so readers know how old the data is.

When a profile is private, missing or unsynced, leave the numbers empty and offer the optional sync link. A player shouldn't need Tracker to use the rest of 1ADAAR.

Keep raw SteamIDs and any login details out of Pages assets. The match collector may privately match the already-known player ID to a public Tracker response, but account ownership and permission need their own verified process. Never calculate role levels from kills, cash, faction or rank.

## What remains uncertain

The documented endpoint still needs a real test with a consenting, synchronized player. Its terms, privacy behavior, level scale and data storage options are also unverified for 1ADAAR. A lasting connection across browsers needs proper identity verification; Tracker hasn't documented an automatic third-party return callback.

Six-role **progression** is possible in principle through Tracker. Six-role **gameplay contribution** (healing, logistics, recon work, piloting effectiveness and so on) is still unproven and must not be drawn as a performance radar.

Read [the connection plan](PLAYER_PROGRESSION_OPT_IN_IMPLEMENTATION.md) for the setup, privacy and acceptance tests. No private credentials were accessed during this research.
