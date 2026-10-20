"""Publish one honest, season-separated weekly roundup from saved WARCON results.

Runs after each full collector. Before Sunday noon Eastern or without completed
saved matches, there is no Discord call. GitHub Actions is best-effort: an overdue
run may publish after noon, but never labels missing match data as complete.
"""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
import sys

from src.weekly import EASTERN, summarize_week
from src.recap import DATA, SITE_URL, atomic_write_json, read_json, send_discord
from src.weekly_card import render_weekly_card

ARCHIVE = DATA / "weekly"
FIRST_RELEASE_SUNDAY = dt.date(2026, 10, 25)


def last_finished_sunday(now: dt.datetime) -> dt.date:
    local = now.astimezone(EASTERN)
    sunday = local.date() - dt.timedelta(days=(local.weekday() + 1) % 7)
    if local.weekday() == 6 and local.hour < 12:
        sunday -= dt.timedelta(days=7)
    return sunday


def payload(report: dict) -> dict:
    end = report["weekEndingEastern"]
    segments = [s for s in report["segments"] if s["completedMatchesInArchive"] > 0]
    count = sum(s["completedMatchesInArchive"] for s in segments)
    season_lines = [f'**{s["seasonName"]}** — {s["completedMatchesInArchive"]} saved matches'
                    for s in segments]
    return {
        "username": "1ADAAR | WARDOGS",
        "allowed_mentions": {"parse": []},
        "embeds": [{
            "title": f"WARDOGS weekly roundup · {end}",
            "url": f"{SITE_URL}weekly.html?week={end}",
            "color": 0xD8AC65,
            "description": ("**OneAverageDan WARDOGS Community Server**\n"
                            f"{count} completed matches saved this week. "
                            "This may not include every match played.\n" +
                            "\n".join(season_lines)),
            "image": {"url": "attachment://match-recap.png"},
            "fields": [{"name": "See the weekly results",
                        "value": f"[Open the weekly roundup]({SITE_URL}weekly.html?week={end})",
                        "inline": False}],
            "footer": {"text": "Saved matches only • Data: WARCON • Community-run server"}
        }]
    }


def run(*, directory: Path = ARCHIVE, matches_file: Path | None = None,
        webhook: str = "", now: dt.datetime | None = None,
        send=send_discord, renderer=render_weekly_card) -> dict:
    when = now or dt.datetime.now(dt.timezone.utc)
    if when.tzinfo is None:
        raise ValueError("A timezone-aware clock is required")
    ending = last_finished_sunday(when)
    if ending < FIRST_RELEASE_SUNDAY:
        return {"status": "before-launch-week", "weekEnding": str(ending)}
    key = str(ending)
    match_doc = read_json(matches_file or DATA / "matches.json", {"matches": []})
    if not isinstance(match_doc, dict) or not isinstance(match_doc.get("matches"), list):
        raise ValueError("Malformed public match archive")
    summary = summarize_week(match_doc["matches"], key)
    segments = [s for s in summary["segments"] if s["completedMatchesInArchive"] > 0]
    if not segments:
        return {"status": "no-completed-matches", "weekEnding": key}
    index_file = directory / "index.json"
    ledger_file = directory / "delivery.json"
    index = read_json(index_file, {"schemaVersion": 1, "weeks": []})
    ledger = read_json(ledger_file, {"schemaVersion": 1, "posted": {}})
    if not isinstance(index, dict) or not isinstance(index.get("weeks"), list):
        raise ValueError("Malformed weekly archive index")
    if not isinstance(ledger, dict) or not isinstance(ledger.get("posted"), dict):
        raise ValueError("Malformed weekly delivery checkpoint")

    if not any(row.get("weekEnding") == key for row in index["weeks"]):
        links = []
        for s in segments:
            name = f'{s["seasonKey"]}/{key}.json'
            doc = {k: v for k, v in s.items()}
            doc["schemaVersion"] = 1
            doc["weekEndingEastern"] = key
            doc["source"] = "Completed WARDOGS matches saved in 1ADAAR from WARCON"
            doc["warning"] = "Some played matches may be missing."
            atomic_write_json(directory / name, doc)
            links.append({"seasonKey": s["seasonKey"], "seasonName": s["seasonName"],
                          "file": f"data/weekly/{name}"})
        index["weeks"].insert(0, {
            "weekEnding": key,
            "completedMatchesSaved": sum(s["completedMatchesInArchive"] for s in segments),
            "seasons": links,
        })
        index["weeks"] = sorted(index["weeks"], key=lambda r: r["weekEnding"], reverse=True)
        atomic_write_json(index_file, index)

    if key in ledger["posted"]:
        return {"status": "already-posted", "weekEnding": key}
    if not webhook:
        return {"status": "archive-ready-no-webhook", "weekEnding": key}
    image = renderer(summary)
    # Never retry an ambiguous Discord POST inside one run. Persist confirmed
    # message ID; GitHub Actions job serializes writes before the Pages deploy.
    message_id = send(webhook, payload(summary), image_bytes=image)
    ledger["posted"][key] = message_id
    atomic_write_json(ledger_file, ledger)
    return {"status": "posted", "weekEnding": key, "savedMatches":
            sum(s["completedMatchesInArchive"] for s in segments)}


def main() -> int:
    try:
        print(json.dumps(run(webhook=os.environ.get("DISCORD_MATCH_WEBHOOK", "").strip()),
                         sort_keys=True))
        return 0
    except Exception as error:
        # No webhook, SteamID, or private fields in error output.
        print(f"1ADAAR weekly roundup error: {type(error).__name__}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
