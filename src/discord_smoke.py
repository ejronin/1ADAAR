"""One-shot delivery of clearly labeled fictional match and weekly test reports.

Invoked only by the guarded Discord smoke workflow. No records are written,
and live collection, scheduling, and weekly awards are unaffected.
"""
from __future__ import annotations
import os
from src.recap import send_discord, SITE_URL
from src.recap_card import render_match_card
from src.discord_preview_cards import render_weekly_smoke_card

def _button(url: str) -> dict:
    return {"type": 1, "components": [
        {"type": 2, "style": 5, "label": "See full report", "url": url}
    ]}

def smoke_payload() -> dict:
    """Match layout, explicitly not a real WARCON match."""
    return {
        "username": "1ADAAR | WARDOGS",
        "allowed_mentions": {"parse": []},
        "flags": 32768,
        "components": [
            {"type": 17, "accent_color": 0x56CE71, "components": [
                {"type": 10, "content": "## TEST — NOT A REAL MATCH"},
                {"type": 12, "items": [{
                    "media": {"url": "attachment://match-recap.png"},
                    "description": "FICTIONAL match recap graphic; this is a layout and webhook test"
                }]},
                {"type": 10, "content":
                    "**FICTIONAL SAMPLE DATA.** The graphic verifies the map, scores, and image layout. "
                    "No real match was recorded or announced. "
                    "The button opens the 1ADAAR homepage; real recaps link to their saved match report."},
                _button(SITE_URL),
            ]}
        ],
    }

def weekly_smoke_payload() -> dict:
    """Approved navy weekly format, unmistakably illustrative."""
    return {
        "username": "1ADAAR | WARDOGS",
        "allowed_mentions": {"parse": []},
        "flags": 32768,
        "components": [
            {"type": 17, "accent_color": 0x709CCB, "components": [
                {"type": 10, "content": "## TEST — WEEKLY ROUNDUP PREVIEW"},
                {"type": 12, "items": [{
                    "media": {"url": "attachment://match-recap.png"},
                    "description": "FICTIONAL three-player podium, map leaders and award layout preview"
                }]},
                {"type": 10, "content":
                    "**FICTIONAL SAMPLE DATA.** This is a design/delivery test, not a weekly award announcement. "
                    "The rank-gain and K/D awards are withheld until source records support them. "
                    "Production reports will use verified completed matches and link to their actual week."},
                _button(SITE_URL+"weekly.html"),
            ]}
        ],
    }

# This sample lives only in an explicitly manually gated smoke test.
DEMO_MATCH = {
    "id": 0,
    "map": "Bakurani", "mode": "King of the Hill",
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
        raise SystemExit("DISCORD_MATCH_WEBHOOK secret missing; neither test sent")
    match_image = render_match_card(DEMO_MATCH, demo=True)
    weekly_image = render_weekly_smoke_card()
    match_id = send_discord(webhook, smoke_payload(), image_bytes=match_image)
    print(f"TEST match recap acknowledged, Discord message ID {match_id}")
    weekly_id = send_discord(webhook, weekly_smoke_payload(),
                             image_bytes=weekly_image)
    print(f"TEST weekly roundup acknowledged, Discord message ID {weekly_id}")

if __name__ == "__main__":
    main()
