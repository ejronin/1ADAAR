"""Send one explicitly marked Discord delivery smoke-test embed. Never create match data."""
from __future__ import annotations
import os
from .recap import send_discord, SITE_URL

def smoke_payload():
    return {
        "username": "1ADAAR | WARDOGS",
        "allowed_mentions": {"parse": []},
        "embeds": [{
            "title": "🧪 TEST — 1ADAAR MATCH RECAP DELIVERY",
            "description": (
                "**THIS IS A TEST, NOT A COMPLETED MATCH.**\n"
                "GitHub Actions successfully reached the WARDOGS #match-recap Discord webhook. "
                "Real match recaps will publish after WARCON records a completed match."
            ),
            "url": SITE_URL,
            "color": 0x56CE71,
            "fields": [
                {"name": "Game", "value": "WARDOGS — Tactical All Out Warfare", "inline": False},
                {"name": "Community", "value": "OneAverageDan / 1AD", "inline": True},
                {"name": "Result", "value": "Webhook delivery test only", "inline": True}
            ],
            "footer": {"text": "1ADAAR delivery diagnostic • no match data was created"}
        }]
    }

def main():
    webhook = os.environ.get("DISCORD_MATCH_WEBHOOK", "").strip()
    if not webhook:
        raise SystemExit("DISCORD_MATCH_WEBHOOK secret missing; test not sent")
    message_id = send_discord(webhook, smoke_payload())
    print(f"Discord smoke test acknowledged with message ID {message_id}")

if __name__ == "__main__":
    main()
