"""No-dependency WARCON public API -> sanitized 1ADAAR pages -> Discord recap.

Public pages deliberately omit SteamIDs, contact information and WARCON credentials.
Schema verified against warcon-app/warcon src/lib/matches.ts (October 2026).
"""
from __future__ import annotations

import argparse
from src.player_index import player_key, safe_name, collect_players
import datetime as dt
import json
import os
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

WARCON_ORIGIN = "https://console.warcon.app"
SERVER_ID = "e30a7ee9-7ea5-4633-882e-98d2e0c03342"
PUBLIC_MATCHES = f"{WARCON_ORIGIN}/api/public/servers/{SERVER_ID}/matches"
PUBLIC_BOARD = f"{WARCON_ORIGIN}/api/public/servers/{SERVER_ID}/leaderboard"
PUBLIC_SITE = f"{WARCON_ORIGIN}/s/{SERVER_ID}/matches"
SITE_URL = "https://ejronin.github.io/1ADAAR/"
DATA = Path(__file__).resolve().parents[1] / "docs" / "data"
MAX_MATCHES = 120
MIN_SCORE = 1
MAP_LABELS = {"NorthAmerica": "Zestafona", "Europe": "Ozeti", "Kavkazi": "Bakurani"}
MAX_PAGES_PER_RUN = 3
TIMEOUT = 18
USER_AGENT = "1ADAAR/1.0 (+https://github.com/ejronin/1ADAAR)"


def fetch_json(url: str, *, attempts: int = 3) -> dict:
    if not url.startswith(WARCON_ORIGIN + "/api/public/servers/"):
        raise ValueError("Refusing non-public or foreign API URL")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
                if response.geturl() != url:  # block token forwarding via redirects
                    raise ValueError("Unexpected redirect from WARCON public API")
                if int(response.headers.get("Content-Length", 0)) > 2_000_000:
                    raise ValueError("WARCON API response too large")
                raw = response.read(2_000_001)
                if len(raw) > 2_000_000:
                    raise ValueError("WARCON API response too large")
                result = json.loads(raw.decode("utf-8"))
                if not isinstance(result, dict) or result.get("ok") is not True:
                    raise ValueError("Unexpected WARCON API response")
                return result
        except (urllib.error.URLError, TimeoutError) as error:
            if attempt + 1 >= attempts:
                raise RuntimeError(f"Public WARCON API unavailable: {type(error).__name__}") from error
            time.sleep(min(2 ** attempt, 4))
    raise RuntimeError("unreachable")


def parse_time(value: str) -> dt.datetime:
    if not isinstance(value, str):
        raise ValueError("Missing match timestamp")
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(dt.timezone.utc)


def clean(value: object, limit: int = 70) -> str:
    if not isinstance(value, str):
        return ""
    return "".join(ch for ch in value if ch.isprintable() and ch not in "@`<>{}\\").strip()[:limit]


def score_rows(raw: object) -> list[dict]:
    if not isinstance(raw, list):
        return []
    out = []
    for item in raw[:6]:
        if not isinstance(item, dict):
            continue
        name = clean(item.get("name"), 40)
        score = item.get("score")
        if name and isinstance(score, (int, float)) and not isinstance(score, bool):
            out.append({"name": name, "score": round(float(score), 1)})
    return sorted(out, key=lambda s: -s["score"])


def usable_match(raw: dict) -> bool:
    if not isinstance(raw, dict) or raw.get("endedAt") is None:
        return False
    try:
        if parse_time(raw["endedAt"]) < parse_time(raw["startedAt"]):
            return False
    except (ValueError, TypeError):
        return False
    # WARCON treats finalScores absent as abandoned; never publish fake completed games.
    scores = score_rows(raw.get("finalScores"))
    return bool(scores) and max(s["score"] for s in scores) >= MIN_SCORE


def public_match(raw: dict, detail: dict | None = None) -> dict:
    if not usable_match(raw):
        raise ValueError("Match is unfinished or abandoned")
    identifier = raw.get("id")
    if not isinstance(identifier, int) or isinstance(identifier, bool) or identifier <= 0:
        raise ValueError("Invalid match ID")
    started, ended = parse_time(raw["startedAt"]), parse_time(raw["endedAt"])
    awards = []
    if isinstance(detail, dict):
        for entry in detail.get("awards", [])[:5]:
            if not isinstance(entry, dict):
                continue
            key = entry.get("key")
            if key not in {"kills", "kd", "longest", "streak", "cash"}:
                continue
            winner_name = safe_name(entry.get("name"))
            if not winner_name:
                continue
            awards.append({"key": key, "label": clean(entry.get("label"), 30),
                           "name": winner_name, "value": clean(entry.get("value"), 25)})
    # Do not publish per-player SteamIDs or full raw WARCON payloads.
    players = []
    if isinstance(detail, dict):
        for line in sorted((x for x in detail.get("lines", []) if isinstance(x, dict)),
                           key=lambda x: -(x.get("kills") if isinstance(x.get("kills"), int) else 0))[:120]:
            def safe_int(key: str) -> int:
                value = line.get(key, 0)
                return max(0, value) if isinstance(value, int) and not isinstance(value, bool) else 0
            key = player_key(line.get("steamId"))
            if not key:
                continue
            name = safe_name(line.get("name"))
            if not name:
                continue
            players.append({"key": key, "name": name,
                            "faction": clean(line.get("faction"), 30),
                            "result": clean(line.get("result"), 5) if line.get("result") in ("win", "loss", "draw") else "",
                            "kills": safe_int("kills"), "deaths": safe_int("deaths"),
                            "seconds": safe_int("seconds"),
                            "cashDelta": line.get("cashDelta") if isinstance(line.get("cashDelta"), int) else 0,
                            "headshots": safe_int("headshots") if detail.get("hasFeed") else None,
                            "longestM": safe_int("longestM") if detail.get("hasFeed") else None,
                            "killStreak": safe_int("killStreak") if detail.get("hasFeed") else None})
    return {"schemaVersion": 2, "id": identifier, "startedAt": started.isoformat().replace("+00:00", "Z"),
            "endedAt": ended.isoformat().replace("+00:00", "Z"),
            "durationSeconds": max(0, int((ended - started).total_seconds())),
            "map": MAP_LABELS.get(clean(raw.get("map"), 55), clean(raw.get("map"), 55)) or "Unknown map",
            "mode": "King of the Hill" if "_KOTH_" in str(raw.get("experiences") or "") else (clean(raw.get("experiences"), 90) or "Unknown mode"),
            "lighting": clean(raw.get("lighting"), 50),
            "winner": clean(raw.get("winner"), 35),
            "scores": score_rows(raw.get("finalScores")),
            "peakPlayers": max(0, int(raw.get("peakPlayers") or 0)),
            "players": players, "awards": awards,
            "hasFeed": bool(detail.get("hasFeed")) if isinstance(detail, dict) else False,
            "warconUrl": f"{PUBLIC_SITE}/{identifier}"}


def discord_payload(match: dict) -> dict:
    scores = match["scores"]
    score_text = "\n".join(f"**{r['name']}**  ·  {r['score']:g}" for r in scores) or "Unavailable"
    duration = match["durationSeconds"]
    mm = f"{duration // 3600}h {duration % 3600 // 60}m" if duration >= 3600 else f"{duration // 60}m"
    awards = match.get("awards") or []
    fields = [
        {"name": "🗺️ Map", "value": match["map"], "inline": True},
        {"name": "⏱ Duration", "value": mm, "inline": True},
        {"name": "👥 Peak players", "value": str(match["peakPlayers"]), "inline": True},
        {"name": "FINAL FACTION SCORES", "value": score_text[:1024], "inline": False},
    ]
    if awards:
        summary = "\n".join(f"**{a['label']}** · {a['name']} — {a['value']}" for a in awards[:4])
        fields.append({"name": "🎖 Match awards", "value": summary[:1024], "inline": False})
    fields.append({"name": "📊 Full after-action report", "value":
                   f"[Open 1ADAAR]({SITE_URL}#match-{match['id']}) · [WARCON source]({match['warconUrl']})",
                   "inline": False})
    winner = match["winner"] or "Draw"
    return {"username": "1ADAAR | WARDOGS", "allowed_mentions": {"parse": []},
            "embeds": [{"title": f"MATCH COMPLETE · {winner}",
                        "url": match["warconUrl"], "color": 0xD8A851,
                        "description": "**OneAverageDan WARDOGS Community Server** · Official match recap",
                        "fields": fields, "footer": {"text": f"1ADAAR • Match #{match['id']} • Data: WARCON"},
                        "timestamp": match["endedAt"]}]}


def send_discord(url: str, payload: dict) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in {"discord.com", "discordapp.com"} or \
       not re.fullmatch(r"/api/webhooks/\d+/[A-Za-z0-9_-]+/?", parsed.path):
        raise ValueError("Invalid Discord webhook URL")
    url = url.rstrip("/") + "?wait=true"
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"),
                                 headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
                                 method="POST")
    # Do not retry POST automatically; an ambiguous network timeout may have delivered the post.
    with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
        data = json.load(response)
        if not isinstance(data, dict) or not str(data.get("id", "")).isdigit():
            raise ValueError("Discord did not acknowledge message id")
        return str(data["id"])


def atomic_write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def read_json(path: Path, default: dict) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def run(*, webhook: str = "", dry_run: bool = False) -> dict:
    DATA.mkdir(parents=True, exist_ok=True)
    db_file = DATA / "matches.json"
    ledger_file = DATA / "delivery.json"
    old = read_json(db_file, {"matches": []})
    ledger = read_json(ledger_file, {"posted": {}, "initialized": False})
    old_matches = {int(x["id"]): x for x in old.get("matches", []) if isinstance(x, dict) and isinstance(x.get("id"), int)}
    fetched = {}
    for page in range(1, MAX_PAGES_PER_RUN + 1):
        data = fetch_json(f"{PUBLIC_MATCHES}?page={page}")
        items = data.get("matches", [])
        if not isinstance(items, list):
            raise ValueError("WARCON match list is malformed")
        for item in items:
            if usable_match(item):
                fetched[item["id"]] = item
        if page >= int(data.get("pages", 1)) or not items:
            break
    # Fail closed: no output change when the upstream request/schema is broken.
    for match_id, raw in fetched.items():
        try:
            if match_id not in old_matches or old_matches[match_id].get("schemaVersion") != 2:
                detailed = fetch_json(f"{PUBLIC_MATCHES}/{match_id}")
                if not isinstance(detailed.get("match"), dict) or detailed["match"].get("id") != match_id:
                    raise ValueError("Match detail mismatch")
                old_matches[match_id] = public_match(detailed["match"], detailed)
        except (RuntimeError, urllib.error.HTTPError) as error:
            # Never publish half-populated latest match when detailed result is unavailable.
            raise RuntimeError(f"WARCON match {match_id} detail unavailable") from error
    latest = sorted(old_matches.values(), key=lambda x: x["endedAt"], reverse=True)[:MAX_MATCHES]
    if not dry_run and old.get("matches") != latest:
        atomic_write_json(db_file, {"schemaVersion": 1, "source": "WARCON public matches API",
                                    "lastCheckedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
                                    "matches": latest})
    # Enrich the static player lookup using WARCON's public, all-time scoreboard.
    # This is independent of recap delivery: a leaderboard outage never blocks
    # a completed match or causes the existing lookup index to be erased.
    player_count = None
    if not dry_run:
        try:
            index = collect_players(fetch_json, PUBLIC_BOARD)
            player_count = len(index["players"])
            player_file = DATA / "players.json"
            if read_json(player_file, {}) != index:
                atomic_write_json(player_file, index)
        except (RuntimeError, ValueError, urllib.error.HTTPError) as exc:
            print(f"1ADAAR player snapshot skipped: {type(exc).__name__}", file=sys.stderr)
    # First run is baseline-only: never spam Discord with historical recaps.
    if not ledger.get("initialized", False):
        ledger["initialized"] = True
        ledger["posted"] = {str(m["id"]): "baseline" for m in latest}
    elif webhook:
        unposted = [m for m in reversed(latest) if str(m["id"]) not in ledger["posted"]]
        # A failed delivery raises and stops; retry next schedule with the committed ledger.
        for match in unposted[:15]:
            if dry_run:
                continue
            message_id = send_discord(webhook, discord_payload(match))
            ledger["posted"][str(match["id"])] = message_id
            atomic_write_json(ledger_file, ledger)
    # Keep checkpoint data bounded, but preserve recent delivery information.
    if not dry_run:
        recent = {str(m["id"]) for m in latest}
        ledger["posted"] = {key: value for key, value in ledger["posted"].items() if key in recent}
        atomic_write_json(ledger_file, ledger)
    return {"matches": len(latest), "initialized": ledger["initialized"], "webhookConfigured": bool(webhook), "playerCount": player_count}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        result = run(webhook=os.environ.get("DISCORD_MATCH_WEBHOOK", ""), dry_run=args.dry_run)
        print(json.dumps(result))
        return 0
    except Exception as exc:
        # Safe errors: never print webhook or RCON token values.
        print(f"1ADAAR collector error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
