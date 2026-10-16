"""Send one explicitly marked Discord delivery smoke-test embed. Never create match data."""
from __future__ import annotations
import os
from .recap import send_discord, SITE_URL
from .recap_card import render_match_card

def smoke_payload():
    return {
        "username": "1ADAAR | WARDOGS",
        "allowed_mentions": {"parse": []},
        "embeds": [{
            "title": "🧪 TEST — 1ADAAR VISUAL MATCH RECAP",
            "image": {"url": "attachment://match-recap.png"},
            "description": (
                "**THIS IS A TEST, NOT A COMPLETED MATCH. ALL SCORES AND PLAYERS ARE FICTIONAL.**\n"
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

# This fixture exists exclusively in the manually triggered smoke workflow.
# It is NEVER ingested by the WARCON collector or persisted to match history.
DEMO_MATCH = {
    "id": 0,
    "map": "Bakurani",
    "mode": "King of the Hill",
    "durationSeconds": 42 * 60,
    "scores": [
        {"name": "Lonestar", "score": 100},
        {"name": "Valkyra", "score": 82},
        {"name": "Manticore", "score": 64},
    ],
    "awards": [
        {"key": "kills", "label": "Most kills", "name": "PlayerOne", "value": "38 kills"},
        {"key": "kd", "label": "Best K/D", "name": "PlayerTwo", "value": "4.20"},
        {"key": "longest", "label": "Longest shot", "name": "PlayerThree", "value": "527 m"},
    ],
}

def main():
    webhook = os.environ.get("DISCORD_MATCH_WEBHOOK", "").strip()
    if not webhook:
        raise SystemExit("DISCORD_MATCH_WEBHOOK secret missing; test not sent")
    message_id = send_discord(webhook, smoke_payload(), image_bytes=render_match_card(DEMO_MATCH, demo=True))
    print(f"Discord smoke test acknowledged with message ID {message_id}")

if __name__ == "__main__":
    main()
