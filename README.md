# 1ADAAR — OneAverageDan After Action Report

**One match. One recap. One linked dossier. No paid backend.**

Production-oriented static dashboard and scheduled Discord recap workflow for the 1OF1-hosted OneAverageDan WARDOGS server. The WARCON public API supplies historical match results; GitHub Actions takes snapshots and posts to Discord; GitHub Pages presents the player-friendly dashboard.

- Dashboard: `https://ejronin.github.io/1ADAAR/` (**available only after Pages is enabled and deployment succeeds**)
- Data source: `https://console.warcon.app/s/e30a7ee9-7ea5-4633-882e-98d2e0c03342/matches`
- Repository: `https://github.com/ejronin/1ADAAR`
- This project does **not** require the game's RCON password, 1OF1 login, WARCON API key, or a running personal computer.

## One-time deployment checklist

1. Keep **WARCON → Server Settings → Public leaderboards and careers** enabled. The code only calls public `/api/public/servers/.../matches` endpoints.
2. In Discord `#match-recap`, create a **dedicated** webhook named `1ADAAR Match Reports`. Never paste this URL into an issue, code, commit, or chat.
3. In **GitHub → Repository Settings → Secrets and variables → Actions → New repository secret**, create `DISCORD_MATCH_WEBHOOK` and paste the full Discord webhook URL. Only that single secret is required.
4. In **GitHub → Settings → Pages → Build and deployment**, select **GitHub Actions** as source (if not already configured).
5. In **GitHub → Actions**, run **Collect WARCON and publish 1ADAAR** once using `Run workflow`. The first run imports the existing archive **without posting older matches**. New completed matches post automatically on subsequent runs.
6. Run **Deploy dashboard to GitHub Pages** if needed. Open the published Pages URL and verify the data / status / match report link.
7. Upload the **approved official 1AD logo** to `docs/assets/1ad-logo.png` and replace the temporary text wordmark in `docs/index.html`. The current wordmark is deliberately a neutral typographic placeholder, **not a purported reproduction of the corporate logo**.
8. In repository **Settings → Rules → Rulesets**, protect `main`: require pull requests and successful CI checks for human contributors. Keep repository collaborators to the minimum necessary. GitHub-hosted schedule requires Actions enabled, and branch protection should be tested alongside the bot's data write permissions.

## What is automated

- Every **10 minutes**, the Actions collector polls up to three WARCON match-list pages, then fetches details for new completed matches.
- Abandoned matches, unfinished matches and records without final scores are **not published**.
- New matches after the initial baseline produce one Discord embed with faction scores, map, duration, peak players, optional verified awards and a link to WARCON plus the 1ADAAR dossier.
- A GitHub-committed checkpoint prevents reposting the same match in normal operation. As with webhook delivery systems generally, an interruption *after Discord accepts a post but before the checkpoint is committed* can cause a duplicate on recovery. Do not represent this as transactional exactly-once delivery.
- The Pages dashboard uses sanitized JSON fields, with no SteamID64, RCON passwords, moderation notes, WARCON tokens or webhook URLs.
- Public site is static; no persistent server, database, or paid cloud subscription. Actions and Pages remain subject to GitHub's plan, fair-use, and usage limits; no perpetual availability guarantee.

## Security and operations

- The public repository is intentionally readable, but never stores `DISCORD_MATCH_WEBHOOK` or privileged API keys. `.gitignore` protects common local secrets; **GitHub Secrets** is mandatory for delivery credentials. `.gitignore` cannot erase secrets committed accidentally.
- Scheduled workflows trigger only on the default branch; forks cannot deliver to the real webhook without that secret.
- `allowed_mentions` is disabled for webhook messages. The collector sanitizes usernames and includes no SteamIDs in generated public JSON.
- Fetches are restricted to the WARCON **public** origin and response size capped at 2 MB. Only HTTPS Discord webhook destinations are accepted.
- A manual first-run baseline avoids flooding `#match-recap` with old historical results.
- If WARCON public pages go offline, the collector fails safely and leaves the existing Pages data intact, with GitHub Actions showing failure.
- Never hit **Purge Stats** in WARCON: it irreversibly deletes its recorded match results.
- No Discord bot tokens, WARCON master RCON credentials or host-file changes are required.

## Test locally

```sh
python -m unittest discover -s tests -v
python -m http.server 8000 --directory docs
```

Open `http://localhost:8000/`. Use `python -m src.recap --dry-run` to inspect collector behavior against the live public API without writing data or posting to Discord.

## WARCON source contract

Verified against `warcon-app/warcon`:
- `src/lib/matches.ts` — `MatchSummary`, `MatchView` and `MatchAward` types.
- `src/routes/api/public/servers/[id]/matches/+server.ts` — `{ok,matches,live,page,pageSize,total,pages}`.
- `src/routes/api/public/servers/[id]/matches/[matchId]/+server.ts` — `{ok,match,factions,lines,timeline,awards,kills,hasFeed,feed,more}`.

The WARCON API is unversioned; monitor CI and update the connector if the upstream schema changes. Actual live end-to-end Discord success cannot be asserted until a matching completed match and valid Discord webhook exist.

## Build responsibility / expert reviews

- **Integration engineer:** WARCON schema contract, new-match detection, graceful upstream failure.
- **Discord engineer:** webhook embed limits, mention suppression, delivery/recovery behavior.
- **UX engineer:** accessible, responsive static dashboard and final official 1AD logo.
- **GitHub / security engineer:** least privilege, repository secrets, CI, Pages deployment, rulesets.
- **Delivery owner:** test acceptance, final deployment verification and incident/runbook maintenance.

The roles above are a review plan, not additional people or paid services.