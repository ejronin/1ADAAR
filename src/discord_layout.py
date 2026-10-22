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
    """Native Discord Components V2; no claims from incomplete player lines."""
    from src.discord_contract import build_design_recap
    identifier = match.get("id")
    if not (isinstance(identifier, int) and identifier > 0):
        raise ValueError("A completed match needs a positive integer ID")
    # Only the validated WARCON completed-match collector may certify this.
    # A caller-supplied timestamp or score row is NOT proof of completion.
    verified = match.get("verifiedCompleted") is True
    payload = build_design_recap(
        {**match, "verifiedCompleted": verified,
         "playerLinesComplete": match.get("playerLinesComplete") is True},
        dashboard_url=SITE_URL + "#match-" + str(identifier)
    )
    # Original verified faction accent remains meaningful in Discord.
    accent = {"lonestar":0x465EFF, "valkyra":0xEE4138, "manticore":0x3EBA42}
    payload["components"][0]["accent_color"] = accent.get(
        str(match.get("winner") or "").strip().lower(), ACCENT_GREEN
    )
    return payload


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
