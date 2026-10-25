"""Store actual four-hour WARDOGS GOLD price observations (not synthetic OHLC).

The game sets the bar price daily. Six readings normally repeat one day's quote.
Observations retain actual UTC retrieval timestamps; missed polls are never filled.
"""
from __future__ import annotations

import datetime as dt
import json
import urllib.request
from pathlib import Path

URL = "https://wardogserverlist.com/api/gold-bars"
OUTPUT = Path(__file__).resolve().parents[1] / "docs/data/gold-observations.json"
DAY_MS = 86400000
MAX_AGE_MS = 2 * DAY_MS
RETENTION_MS = 400 * DAY_MS

def validate(payload: dict, observed_ms: int) -> tuple[int, int]:
    latest = payload.get("latest")
    points = payload.get("points")
    if not isinstance(latest, dict) or not isinstance(points, list) or not points:
        raise ValueError("Gold source has no daily latest/history")
    day, price = latest.get("ts"), latest.get("price")
    if type(day) is not int or day < 0 or day % DAY_MS != 0:
        raise ValueError("Gold source day invalid")
    if type(price) is not int or not 0 < price <= 100_000_000:
        raise ValueError("Gold source price invalid")
    if points[-1] != [day, price]:
        raise ValueError("Latest quote does not match history")
    if day > observed_ms or observed_ms - day > MAX_AGE_MS:
        raise ValueError("Daily quote is outdated or in the future")
    return day, price

def append(existing: object, observed_ms: int, day: int, price: int) -> dict:
    observations = []
    if isinstance(existing, dict) and existing.get("version") == 1:
        raw = existing.get("observations", [])
        if isinstance(raw, list):
            for item in raw:
                if not isinstance(item, dict):
                    continue
                ts, quoted, amount = item.get("observedAt"), item.get("priceDay"), item.get("price")
                if all(type(x) is int for x in (ts, quoted, amount)) and \
                        0 < amount <= 100_000_000 and 0 <= quoted <= ts and \
                        ts >= observed_ms - RETENTION_MS:
                    observations.append({"observedAt": ts, "priceDay": quoted, "price": amount})
    observations = [r for r in observations if r["observedAt"] != observed_ms]
    observations.append({"observedAt": observed_ms, "priceDay": day, "price": price})
    observations.sort(key=lambda row: row["observedAt"])
    return {"version": 1, "source": URL, "observations": observations}

def run(now: dt.datetime | None = None) -> None:
    moment = now or dt.datetime.now(dt.timezone.utc)
    if moment.utcoffset() != dt.timedelta(0):
        moment = moment.astimezone(dt.timezone.utc)
    observed_ms = int(moment.timestamp() * 1000)
    request = urllib.request.Request(URL, headers={
        "Accept": "application/json",
        "User-Agent": "1ADAAR-GoldObserver/1.0 (+https://github.com/ejronin/1ADAAR)"
    })
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise RuntimeError("Gold API HTTP " + str(response.status))
        payload = json.loads(response.read(500_000).decode("utf-8"))
    day, price = validate(payload, observed_ms)
    existing = json.loads(OUTPUT.read_text("utf-8")) if OUTPUT.exists() else {}
    document = append(existing, observed_ms, day, price)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(document, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"Observed {price:,} cash on {moment.isoformat()} from quote day {day}")

if __name__ == "__main__":
    run()
