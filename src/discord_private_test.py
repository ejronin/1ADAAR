"""Manual **private test-channel only** native Discord Components V2 QA.

Must be executed manually with a dedicated DISCORD_TEST_WEBHOOK secret. The
production recap webhook is NEVER read. Default is local generation only.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import os

from src.discord_smoke import DEMO_MATCH
from src.discord_contract import build_design_recap
from src.recap import send_discord
from src.recap_card import render_match_card

OUTPUT = Path("visual-review/discord-native-FICTIONAL.png")
CONFIRM = "SEND_FICTIONAL_TO_PRIVATE_TEST_CHANNEL"


def prepared():
    # No fictitious real match ID or unconfirmed player achievements enter the
    # durable match collector. There are no verified per-faction leaders.
    match = {**DEMO_MATCH, "id": 1, "verifiedCompleted": True,
             "playerLinesComplete": False}
    payload = build_design_recap(match,
        dashboard_url="https://ejronin.github.io/1ADAAR/")
    payload["components"][0]["components"][0]["content"] = (
        "## FICTIONAL TEST DELIVERY — NOT A REAL MATCH\n"
        "Actual production-bound Components V2 image-first format")
    payload["components"][0]["components"][1]["items"][0]["description"] = (
        "FICTIONAL 1ADAAR screenshot. Test-channel validation ONLY.")
    png = render_match_card(DEMO_MATCH, demo=True)
    return payload, png


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("--send", action="store_true",
                     help="Send precisely one fictional message to dedicated TEST webhook")
    cli.add_argument("--confirm", default="")
    args = cli.parse_args()
    payload, png = prepared()
    OUTPUT.parent.mkdir(exist_ok=True, parents=True)
    OUTPUT.write_bytes(png)
    if not args.send:
        print(f"Generated {OUTPUT}; no Discord message sent.")
        return
    if args.confirm != CONFIRM:
        raise SystemExit("Missing explicit private-test-channel confirmation")
    webhook = os.environ.get("DISCORD_TEST_WEBHOOK", "").strip()
    if not webhook:
        raise SystemExit("Dedicated DISCORD_TEST_WEBHOOK secret missing; NO message sent")
    # send_discord validates discord.com HTTPS URL, flag, attachment bytes, and
    # confirmation response; no automatic retry on ambiguous network failures.
    message_id = send_discord(webhook, payload, image_bytes=png)
    print(f"One TEST Discord Components V2 message acknowledged: {message_id}")


if __name__ == "__main__":
    main()
