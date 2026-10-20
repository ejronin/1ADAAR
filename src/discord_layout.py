"""Short, image-first Discord Components V2 recap and separate next-round post.

Webhook-only, no bot token or paid hosting. Discord clients choose final image
display width; Media Gallery is larger/cleaner than burying the card in a
traditional rich embed. No Discord test messages are sent automatically.
"""
from __future__ import annotations

JOIN_CODE = "a071b4aa-9574-4e7d-858c-0da3bea80f52"
V2_FLAG = 1 << 15
SITE_URL = "https://ejronin.github.io/1ADAAR/"
ACCENT_GREEN = 0x56CE71


def _button(url: str, label: str) -> dict:
    return {"type": 1, "components": [{"type": 2, "style": 5, "label": label, "url": url}]}


def match_recap(match: dict) -> dict:
    """A single large graphic, one follow-up sentence, and 1ADAAR button."""
    ident = int(match["id"])
    winner = str(match.get("winner", "")).strip().lower()
    color = {"lonestar": 0x465EFF, "valkyra": 0xEE4138,
             "manticore": 0x3EBA42}.get(winner, ACCENT_GREEN)
    return {
        "username": "1ADAAR | WARDOGS",
        "allowed_mentions": {"parse": []},
        "flags": V2_FLAG,
        "components": [
            {"type": 17, "accent_color": color, "components": [
                {"type": 10, "content": "## MATCH RECAP"},
                {"type": 12, "items": [{
                    "media": {"url": "attachment://match-recap.png"},
                    "description": "WARDOGS completed match results with game map, mode, faction scores and verified awards"
                }]},
                {"type": 10, "content": "We'll post the next map and conditions here shortly, once confirmed."},
            ]},
            _button(SITE_URL + "#match-" + str(ident), "See more on 1ADAAR")
        ],
    }


def next_map_post(match: dict, confirmed: dict) -> dict:
    """Only called with a verified NEW map and verified weather conditions."""
    from src.next_round import MAPS, CONDITIONS
    name = confirmed.get("map")
    condition = confirmed.get("conditions")
    if (confirmed.get("source") != "WARCON public observed server status" or
            name not in set(MAPS.values()) or condition not in set(CONDITIONS.values()) or
            name == MAPS.get(match.get("map"))):
        raise ValueError("Refusing unverified next-round announcement")
    code_fence = chr(96) * 3
    return {
        "username": "1ADAAR | WARDOGS",
        "allowed_mentions": {"parse": []},
        "flags": V2_FLAG,
        "components": [
            {"type": 17, "accent_color": ACCENT_GREEN, "components": [
                {"type": 10, "content": "## NEXT MAP: " + name},
                {"type": 10, "content": "**CONDITIONS:** " + condition},
                {"type": 14, "divider": True, "spacing": 1},
                {"type": 10, "content": "**SERVER JOIN CODE**\n" +
                    code_fence + "text\n" + JOIN_CODE + "\n" + code_fence},
            ]},
            _button(SITE_URL, "See more on 1ADAAR")
        ],
    }
