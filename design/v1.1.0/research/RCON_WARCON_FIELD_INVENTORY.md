# WARDOGS RCON and WARCON: available fields

This list comes from the published [WARCON source](https://github.com/warcon-app/warcon) and documented WDRCON routes. It has **not** been checked against Dan's live, authenticated game server. Before adding private collection, ask the operator to check `GET /v1/capabilities` on the installed build and confirm exactly which read-only routes are available.

## Game-server RCON (private)
| Read route | Useful fields | What they could support | Notes |
|---|---|---|---|
| GET /v1/capabilities | apiVersion, build, auth.scheme/header, limits.maxBodyBytes/maxRequestsPerMinutePerIp, routes, config.writable/document | Schema gates, poll budget | Observe actual installed build. No game play changes. |
| GET /v1/status | serverName, map, experiences[], lighting, alternator, scoreTick, optional scoreCap/matchSeconds, players.current/max, factionScores[name,colorHex,score], rotation.nowIndex/nextIndex | Live capacity indicator, score segments, map state, faction scores | scoreCap/matchSeconds absent in inspected live builds; do not invent. |
| GET /v1/players | count, players[name,steamId,faction,kills,deaths,cash,pingMs] | Online counts, faction composition, active per-player K/D, latency if sampled | CURRENT roster only; no sessions, role levels, six-role XP or healing. STEAMID sensitive. |
| GET /v1/health | status, uptimeSeconds, connections.active, gameThreadQueue.inFlight/depth/rejectedTotal | Uptime/queue ribbon and restart observability | Operational/admin-only data; do not publish raw sensitive detail. |
| GET /v1/server-id | serverId (game join identifier) | Join source / corroboration | Not always present in early builds; public join code distinct from secret. |
| GET /v1/rotation | enabled, mode, entries[index,map,experiences,lighting,zoneAlternator,status,denied] | Scheduled maps, selection overview | May differ by build; planned map != verified next map. |
| GET /v1/catalog/maps | maps[id,displayName] | Canonical map labels | Useful for static labels, not performance counts. |
| GET /v1/catalog/lightings | lightings[id,displayName] | Map/mode environmental label | Dynamic build list; do not assume always present. |
| GET /v1/catalog/experiences | experiences[id,displayName] | Mode filters | Source catalogs only. |
| GET /v1/catalog/maps/{map}/experiences | map, experiences, count | Map-mode compatibility | No performance data. |
| GET /v1/catalog/maps/{map}/alternators | alternators[index,tag,displayName], map,count | Zone configuration | No player location telemetry. |
| GET /v1/sponsor | imageUrl | Branding check | Not a player metric. |
| GET /v1/bans | bans[steamId,bannedAtUtc,bannedBy,reason], count | Private moderation operations | Never publish; irrelevant to the public player dossier. |
| GET /v1/reserved-slots | reservedSlots[steamId],count | Private queue administration | Never expose identifiable lists. |
| GET /v1/audit?limit=N | entries[timestampUtc,peer,sessionId,event,detail] | Private listener health/error triage | Contains network/admin metadata; do not publish. |
| GET /v1/config | revision,writable,text,sections,warnings | Admin config verification | May contain passwords/feed tokens; never publish or cache. |

RCON also has routes that **change** players, matches, bans and settings. Don't use them for analytics. The game listener may use plain HTTP, so don't expose its full-control password or open its port to the internet just to collect 1ADAAR statistics. Prefer an approved read-only WARCON HTTPS route.

## Public WARCON data
| Endpoint | Fields | Use |
|---|---|---|
| GET /api/public/servers/{id} | Sanitized server snapshot, status and map; freshness/source as supplied | Server briefing, current map/state, eventual uptime if captured separately |
| GET /api/public/servers/{id}/leaderboard | rows [steamId,name,rank,minutes,seedMinutes,kills,deaths,matches,wins,losses,draws, optional feed headshots/teamKills/vehicleKills/killStreak]; aggregate scope and range | Career numeric KPIs, win ring, ranked cards, duration, match totals; sanitize IDs before Pages |
| GET /api/public/servers/{id}/players/{steamId} | Public career view: rank, streak, wins/losses/draws, maps/factions, season summaries, last ten match lines | Per-player career/map/faction aggregate; endpoint path includes a SteamID |
| GET /api/public/servers/{id}/matches | Finished match summary [id,startedAt,endedAt,map,experiences,lighting,peakPlayers,finalScores,winner] | Match archive, outcomes, recorded start heatmap |
| GET /api/public/servers/{id}/matches/{matchId} | match, factions, lines [faction,seconds,kills,deaths,cashDelta,headshots,teamKills,suicides,vehicleKills,longestM,killStreak,deathStreak,result], score timeline, awards, kills,hasFeed, paged public feed [cause,distanceM,headshot] | K/D curves, win-rate bars, faction matrix, signed score lead, optional kill cause & distance statistics |

Public access is governed by WARCON public settings and quotas. Not every metric is available for every server/season. First observed date and denominators must be surfaced to avoid lifetime-completeness claims.

## Private WARCON data (requires permission)
| Endpoint | Fields | Possible charts and limits |
|---|---|---|
| GET /api/servers/{id}/analytics?range=24h,7d,30d | summary uniquePlayers, peakPlayers, avgPlayers, uptimePct, onlineNow, samples, matches, coveredHours; population points avg/max/up/down; cash points; map shares; faction wins; top players; hourly traffic; combat aggregates if feed | Properly weighted population ribbon, map usage, kills by cause, historical uptime coverage |
| GET /api/servers/{id}/analytics/periods?range=...&tz=... | periods [ts,players,newPlayers,sessions,avgSessionS,medianSessionS], unit hour/day, timezone | Hourly new-vs-returning players, distribution of session durations at aggregate level; these are SERVER-WIDE, not the selected player's activity |
| GET /api/servers/{id}/players/{steamId} | Protected dossier.summary sessions,minutes,seedMinutes,firstSeen,lastSeen,kills,deaths; perServer; recent SESSION rows with joinedAt,leftAt,lastSeen,minutes,seedMinutes,faction,kills,deaths,cash; online; private staff notes/actions | A real personal session heatmap when coverage/access/privacy confirmed; per-session outcome chart. Current source limits recent list to 25 rows; not a complete long-term session ledger |
| GET /api/servers/{id}/players/{steamId}/career | rank, streak, matches, wins/losses/draws, kills/deaths, minutes, feed headshots/vehicleKills/longestM/streaks, map/faction rollups, ten recent lines, season summaries | More complete career/K-D and per-map outcome analytics, source-scoped |
| GET /api/servers/{id}/kills | Kill events killer/victim (sensitive IDs), cause, distance, headshot, teamkill/suicide, match cursor, timestamp | Cause Pareto, distance distribution, headshot share with actual feed coverage; anonymize |

## Privacy and unavailable fields
- Never publish raw SteamID64, API credentials, RCON passwords, private staff notes/actions, moderation list records, or protected data not explicitly authorized for public display.
- Steam public PFP is separately identifiable and should be shown only when source-association and privacy treatment are accepted; it is not Discord membership proof.
- The player level/rank, the six Assault/Medic/Support/Recon/Driver/Pilot levels/XP and role-specific support events are absent in documented WDRCON /v1/players and inspected WARCON responses. Those sources do not provide those levels, but the separate publicly documented WARDOGS Tracker player API has all six for opted-in synced public profiles; see ROLE_PROGRESSION_ACCESS_VALIDATION.md. Never infer them from kills/cash/faction.
- No verified player position/aim telemetry, recoil/accuracy or movement tracks are exposed; do not create positional heatmaps.
- The current 1ADAAR stored recorded-activity.json contains 0 captured completed matches; the real server heatmap stays empty. Protected personal session heatmap must not be published until authorized complete session range and privacy gates pass.

## How to add another data source
Phase 1: preserve public match career and map data; enhance bounded static JSON shards and chart components. Phase 2 (authorized access): private read-only WARCON API key with server.view, verify one endpoint at a time, sanitize in Python Actions, preaggregate personal session minutes by day/hour and store ONLY approved output without raw IDs. Do not scrape raw RCON from a public browser. SQLite can be an ephemeral Actions build index only if monthly JSON scan latency becomes a measured concern. Keep GitHub Pages static, no paid host.

Test actual /v1/capabilities and WARCON protected credentials **without logging secrets**, read-only GET calls only. Record route success vs 403/404, field presence, retention coverage, timezone and DST proof before marking any derived chart eligible.