"""Lightweight public WARCON server-status check (no combat collector or dependencies).

Designed for the five-minute midpoint job. Never publishes credentials,
join code, player roster, IP address, or Steam IDs. GitHub Pages gets a
transient status snapshot; only genuine state transitions are git-staged.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
import urllib.error
import urllib.request

from src.server_status import project, unknown

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs" / "data"
URL = "https://console.warcon.app/api/public/servers/e30a7ee9-7ea5-4633-882e-98d2e0c03342"
UA = "1ADAAR-status/1.0 (+https://github.com/ejronin/1ADAAR)"
MAX_BYTES = 2_000_000


def fetch_status() -> dict:
    req = urllib.request.Request(URL, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=18) as response:
        if response.geturl() != URL:
            raise ValueError("Unexpected redirect from WARCON public API")
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("Oversized WARCON status response")
    document = json.loads(data.decode("utf-8"))
    if not isinstance(document, dict) or document.get("ok") is not True:
        raise ValueError("Unexpected WARCON public status response")
    return document


def write_json(path: Path, doc: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(doc, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    temp.replace(path)


def poll(directory: Path = DATA, *, now: dt.datetime | None = None,
         fetch=fetch_status) -> dict:
    when = now or dt.datetime.now(dt.timezone.utc)
    prior_file = directory / "server-status-state.json"
    try:
        previous = json.loads(prior_file.read_text(encoding="utf-8")).get("state", "unknown")
    except (FileNotFoundError, ValueError, AttributeError):
        previous = "unknown"
    if previous not in {"online", "offline", "reconnecting", "unknown"}:
        previous = "unknown"
    try:
        response = fetch()
        status = project(response.get("server"), previous, now=when)
    except (urllib.error.URLError, TimeoutError, ValueError, TypeError, AttributeError):
        status = unknown(when)
    write_json(directory / "server-status.json", status)
    if status["state"] != previous:
        write_json(prior_file, {"schemaVersion": 1, "state": status["state"]})
    return {"state": status["state"], "changed": status["state"] != previous,
            "source": "WARCON public server status"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh public status only, without match reports")
    parser.parse_args()
    print(json.dumps(poll(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
