"""Branded weekly Discord artwork built from saved, validated match summaries.

There is no external art request: the actual official 1AD SVG is rendered
locally, using the same pinned Pillow/CairoSVG dependencies as match recaps.
"""
from __future__ import annotations
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw
from cairosvg import svg2png
from src.recap_card import font, truncate

ROOT = Path(__file__).resolve().parents[1]
LOGO = ROOT / "docs" / "assets" / "1ad-logo.svg"
ART = ROOT / "docs" / "assets" / "wardogs-official-hero.webp"
W, H = 1080, 1030
BG = "#101114"
PANEL = "#202025"
EDGE = "#65553b"
GOLD = "#e4bd78"
WHITE = "#f9f5e9"
MUTED = "#c3bdad"


def render_weekly_card(report: dict) -> bytes:
    segments = [s for s in report.get("segments", []) if s.get("completedMatchesInArchive", 0) > 0]
    if not segments:
        raise ValueError("No completed matches available for a weekly card")
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    if ART.is_file():
        with Image.open(ART) as bg:
            layer = bg.convert("RGB").resize((W, H))
            im.paste(Image.blend(layer, Image.new("RGB", (W, H), BG), .82))
            d = ImageDraw.Draw(im)
    d.rounded_rectangle((32, 28, 1048, 1003), radius=24, fill="#151719", outline=EDGE, width=2)
    d.rectangle((32, 28, 1048, 37), fill=GOLD)
    if LOGO.is_file():
        logo_bytes = svg2png(bytestring=LOGO.read_bytes(), output_width=116, output_height=116)
        with Image.open(BytesIO(logo_bytes)) as original:
            logo = original.convert("RGBA")
            im.paste(logo, ((W - 116) // 2, 58), logo)
    d.text((W//2, 181), "ONEAVERAGEDAN WARDOGS COMMUNITY SERVER", font=font(24, True),
           fill=WHITE, anchor="mt")
    d.text((W//2, 212), "COMMUNITY-RUN  •  NOT OPERATED BY THE GAME DEVELOPERS",
           font=font(15), fill=MUTED, anchor="mt")
    d.text((W//2, 266), "WEEKLY ROUNDUP", font=font(57, True), fill=GOLD, anchor="mt")
    ending = str(report.get("weekEndingEastern", ""))
    d.text((W//2, 344), "WEEK ENDING " + ending, font=font(23, True), fill=WHITE, anchor="mt")
    total = sum(s["completedMatchesInArchive"] for s in segments)
    d.rounded_rectangle((64, 405, 1016, 520), radius=13, fill=PANEL, outline=EDGE, width=2)
    d.text((91, 422), "COMPLETED MATCHES SAVED", font=font(19, True), fill=MUTED)
    d.text((91, 447), str(total), font=font(51, True), fill=GOLD)
    d.text((280, 455), "Results include only matches 1ADAAR saved.",
           font=font(20), fill=WHITE)
    d.text((280, 483), "Some played matches may be missing.", font=font(18), fill=MUTED)
    # Season-separated summaries: never mix award winners across seasons.
    y = 550
    for segment in segments[:2]:
        d.rounded_rectangle((64, y, 1016, y + 163), radius=11, fill="#1d2020", outline=EDGE, width=2)
        d.text((86, y + 13), str(segment["seasonName"]).upper(), font=font(24, True), fill=GOLD)
        d.text((86, y + 47), f'{segment["completedMatchesInArchive"]} saved matches',
               font=font(20), fill=WHITE)
        best = segment.get("awards", {}).get("mostKills")
        if best:
            name = truncate(d, best.get("name", "Player"), font(22, True), 520)
            d.text((86, y + 80), "MOST KILLS", font=font(17), fill=MUTED)
            d.text((86, y + 105), name, font=font(22, True), fill=WHITE)
            d.text((949, y + 106), f'{best["value"]} kills', font=font(22, True), fill=GOLD, anchor="rt")
        else:
            d.text((86, y + 93), "Not enough player details for awards", font=font(18), fill=MUTED)
        y += 183
    d.text((W//2, 944), "Only saved match results  •  Source: WARCON",
           font=font(19, True), fill=MUTED, anchor="mt")
    buff = BytesIO()
    im.save(buff, format="PNG", optimize=True)
    return buff.getvalue()
