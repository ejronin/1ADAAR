"""Test-only weekly recap image matching the approved navy Discord mockup.

Never imported by the live collector. All player names and totals are fictional,
visibly identified as such in the artwork and Discord message.
"""
from __future__ import annotations
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
from src.recap_card import font, truncate, community_emblem, alpha_paste

ROOT = Path(__file__).resolve().parents[1]
MAPS = ROOT / "docs" / "assets" / "map-banners"
W, H = 1080, 1290
NAVY = "#152439"
PANEL = "#213448"
LINE = "#40586e"
WHITE = "#f4f7fa"
MUTED = "#b7c8da"
BLUE = "#9acbfa"
GOLD = "#e8c779"
SILVER = "#d0dce6"
BRONZE = "#d19b78"


def _text(d, xy, value, size, fill=WHITE, bold=False, anchor=None):
    d.text(xy, value, font=font(size, bold), fill=fill, anchor=anchor)


def _rounded(d, coords, color=PANEL, edge=LINE, radius=12, width=2):
    d.rounded_rectangle(coords, radius=radius, fill=color, outline=edge, width=width)


def render_weekly_smoke_card() -> bytes:
    im = Image.new("RGB", (W, H), "#101823")
    d = ImageDraw.Draw(im)
    _rounded(d, (30, 25, 1050, 1265), NAVY, "#56728e", 19)
    d.rectangle((30, 25, 1050, 33), fill=BLUE)
    alpha_paste(im, community_emblem(), (72, 62))
    _text(d, (178, 67), "1ADAAR  /  WEEKLY INTELLIGENCE", 24, BLUE, True)
    _text(d, (74, 176), "THIS WEEK ON THE SERVER", 52, WHITE, True)
    _text(d, (75, 240), "TEST PREVIEW  •  ALL PLAYER DATA IS FICTIONAL", 21, GOLD, True)
    d.line((72, 284, 1006, 284), fill=LINE, width=2)
    _text(d, (74, 305), "COMMUNITY TOP 3", 26, BLUE, True)
    podium = [
        (76, 383, 372, 542, "02", "PLAYER BRAVO", "42 KILLS", SILVER),
        (382, 353, 699, 542, "01", "PLAYER ALPHA", "55 KILLS", GOLD),
        (710, 405, 1004, 542, "03", "PLAYER CHARLIE", "35 KILLS", BRONZE),
    ]
    for x, y, x2, y2, place, name, total, color in podium:
        _rounded(d, (x, y, x2, y2), "#233549", color, 12, 3)
        _text(d, (x+17, y+17), place, 30, color, True)
        # Different podium heights, shared visual baselines: no clipped bronze score.
        center = (x+x2)//2
        _text(d, (center, y2-80), name, 21, WHITE, True, anchor="mm")
        _text(d, (center, y2-32), total, 23, color, True, anchor="mm")
    _text(d, (74, 565), "MAP LEADERS  /  MOST KILLS", 26, BLUE, True)
    maps = [
        ("Bakurani", "PLAYER ALPHA", "27 KILLS"),
        ("Ozeti", "PLAYER ECHO", "22 KILLS"),
        ("Zestafona", "PLAYER CHARLIE", "24 KILLS"),
    ]
    for index, (name, who, score) in enumerate(maps):
        y=615+index*112
        _rounded(d, (74,y,1005,y+99), "#20354b", LINE, 9)
        path=MAPS / f"{name.lower()}-card.webp"
        if path.exists():
            with Image.open(path) as art:
                sample=ImageOps.fit(art.convert("RGB"), (226, 91))
            im.paste(sample,(79,y+4))
        else:
            d.rectangle((79,y+4,305,y+95),fill="#254f4d")
            _text(d,(95,y+32),name.upper(),18,WHITE,True)
        # Player and score share the same vertical center on every map row.
        _text(d,(328,y+50),who,23,WHITE,True,anchor="lm")
        _text(d,(984,y+50),score,23,BLUE,True,anchor="rm")
    _text(d,(74,970),"ADDITIONAL WEEKLY AWARDS",26,BLUE,True)
    awards=[
        ("MOST RANK GAINED","Not verified"),
        ("LONGEST SHOT","PLAYER DELTA  ·  486 m"),
        ("MOST KILLS","PLAYER ALPHA  ·  55 KILLS"),
        ("BEST K/D (20+ MATCHES)","No qualified player"),
    ]
    for i,(label,value) in enumerate(awards):
        y=1016+i*48
        _rounded(d,(74,y,1005,y+42),"#20354b",LINE,7,1)
        _text(d,(87,y+11),label,17,MUTED,True)
        _text(d,(991,y+11),value,18,WHITE,False,anchor="ra")
    d.line((74,1222,1004,1222),fill=LINE,width=2)
    _text(d,(77,1234),"TEST ONLY  •  NO LIVE WEEKLY RESULTS WERE PUBLISHED",16,GOLD,True)
    output=BytesIO()
    im.save(output,format="PNG",optimize=True)
    return output.getvalue()
