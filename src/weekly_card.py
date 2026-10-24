"""Render the live weekly Discord image from saved WARCON results.

The layout follows the approved navy weekly preview; unlike that preview it
contains no example players or made-up statistics. Awards and map leads stay
within one WARDOGS season when a reporting week crosses a season boundary.
"""
from __future__ import annotations

from io import BytesIO
from PIL import Image, ImageDraw, ImageOps

from src.map_banners import banner_for_map
from src.recap_card import alpha_paste, community_emblem, font, truncate

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


def _text(draw, xy, value, size, color=WHITE, *, bold=False, anchor=None):
    draw.text(xy, str(value), font=font(size, bold), fill=color, anchor=anchor)


def _panel(draw, bounds, *, outline=LINE, fill=PANEL, radius=12, width=2):
    draw.rounded_rectangle(bounds, radius=radius, fill=fill, outline=outline, width=width)


def _award_value(award, suffix, *, missing="Not verified"):
    if not isinstance(award, dict) or not award.get("name"):
        return missing
    value = award.get("value")
    if type(value) not in (int, float) or value < 0:
        return missing
    number = f"{value:,}" if type(value) is int else f"{value:.2f}"
    return f'{award["name"]}  ·  {number} {suffix}'


def _draw_map(im, draw, y, row):
    _panel(draw, (74, y, 1005, y + 99), fill="#20354b", radius=9)
    map_name = str(row.get("name") or "Unknown map")
    path = banner_for_map(map_name)
    if path is not None:
        with Image.open(path) as original:
            art = ImageOps.fit(original.convert("RGB"), (226, 91),
                               method=Image.Resampling.LANCZOS)
        shade = Image.new("RGBA", art.size, (0, 0, 0, 0))
        ImageDraw.Draw(shade).rectangle((0, 59, 226, 91), fill=(8, 20, 32, 215))
        im.paste(Image.alpha_composite(art.convert("RGBA"), shade).convert("RGB"),
                 (79, y + 4))
    else:
        draw.rectangle((79, y + 4, 305, y + 95), fill="#254f4d")
    _text(draw, (92, y + 68),
          truncate(draw, map_name.upper(), font(17, True), 198),
          17, WHITE, bold=True)
    leader = row.get("leader")
    if isinstance(leader, dict) and type(leader.get("kills")) is int and leader["kills"] > 0:
        who = truncate(draw, leader.get("name"), font(23, True), 390)
        score = f'{leader["kills"]:,} KILLS'
    else:
        who, score = "No verified kill leader", "—"
    _text(draw, (328, y + 50), who, 23, WHITE, bold=True, anchor="lm")
    _text(draw, (984, y + 50), score, 23, BLUE, bold=True, anchor="rm")


def render_weekly_card(report: dict) -> bytes:
    """PNG for the real Discord publisher; use no fictional preview data."""
    segments = [s for s in report.get("segments", [])
                if s.get("completedMatchesInArchive", 0) > 0]
    if not segments:
        raise ValueError("No completed matches available for a weekly card")
    # Do not combine players or awards from different seasons into one ranking.
    featured = max(segments, key=lambda row: row["completedMatchesInArchive"])
    total = sum(s["completedMatchesInArchive"] for s in segments)
    im = Image.new("RGB", (W, H), "#101823")
    draw = ImageDraw.Draw(im)
    _panel(draw, (30, 25, 1050, 1265), fill=NAVY, outline="#56728e", radius=19)
    draw.rectangle((30, 25, 1050, 33), fill=BLUE)
    alpha_paste(im, community_emblem(), (72, 62))
    _text(draw, (178, 67), "1ADAAR  /  WEEKLY INTELLIGENCE",
          24, BLUE, bold=True)
    _text(draw, (74, 176), "THIS WEEK ON THE SERVER",
          52, WHITE, bold=True)
    _text(draw, (75, 240),
          f'{featured["seasonName"].upper()}  ·  {total} SAVED MATCHES  ·  WEEK ENDING {report["weekEndingEastern"]}',
          20, GOLD, bold=True)
    draw.line((72, 284, 1006, 284), fill=LINE, width=2)

    _text(draw, (74, 305), "COMMUNITY TOP 3  /  WEEKLY KILLS",
          26, BLUE, bold=True)
    podium = [
        (76, 383, 372, 542, 1, "02", SILVER),
        (382, 353, 699, 542, 0, "01", GOLD),
        (710, 405, 1004, 542, 2, "03", BRONZE),
    ]
    leaders = featured.get("topKillers") or []
    for left, top, right, bottom, rank, place, color in podium:
        _panel(draw, (left, top, right, bottom),
               fill="#233549", outline=color, radius=12, width=3)
        _text(draw, (left + 17, top + 17), place, 30, color, bold=True)
        center = (left + right) // 2
        player = leaders[rank] if rank < len(leaders) else None
        name = (truncate(draw, player["name"], font(21, True), right-left-30)
                if player else "NO PLAYER RECORDED")
        kills = f'{player["kills"]:,} KILLS' if player else "—"
        # Shared name/score baselines despite podiums with different top edges.
        _text(draw, (center, bottom - 80), name, 21, WHITE, bold=True, anchor="mm")
        _text(draw, (center, bottom - 32), kills, 23, color, bold=True, anchor="mm")

    _text(draw, (74, 565), "MAP LEADERS  /  MOST RECORDED KILLS",
          26, BLUE, bold=True)
    maps = featured.get("mapLeaders") or []
    for i in range(3):
        y = 615 + 112 * i
        if i < len(maps):
            _draw_map(im, draw, y, maps[i])
        else:
            _panel(draw, (74, y, 1005, y + 99), fill="#20354b", radius=9)
            _text(draw, (90, y + 50), "No additional recorded map",
                  20, MUTED, anchor="lm")

    _text(draw, (74, 970), "ADDITIONAL WEEKLY AWARDS",
          26, BLUE, bold=True)
    awards = featured.get("awards") or {}
    rows = [
        ("MOST MATCHES", _award_value(awards.get("mostMatches"), "matches")),
        ("LONGEST SHOT", _award_value(awards.get("longestShot"), "m")),
        ("MOST KILLS", _award_value(awards.get("mostKills"), "KILLS")),
        ("BEST WEEKLY K/D (20+ MATCHES)",
         _award_value(awards.get("bestWeeklyKd20"), "K/D", missing="No qualified player")),
    ]
    for i, (label, value) in enumerate(rows):
        y = 1016 + i * 48
        _panel(draw, (74, y, 1005, y + 42),
               fill="#20354b", radius=7, width=1)
        _text(draw, (87, y + 11), label, 16, MUTED, bold=True)
        _text(draw, (991, y + 11),
              truncate(draw, value, font(17), 460),
              17, WHITE, anchor="ra")

    draw.line((74, 1222, 1004, 1222), fill=LINE, width=2)
    foot = ("SEASONS SHOWN SEPARATELY ONLINE  ·  " if len(segments) > 1 else "")
    _text(draw, (77, 1234), foot + "SAVED MATCHES ONLY  ·  SOURCE: WARCON",
          15, GOLD, bold=True)
    output = BytesIO()
    im.save(output, format="PNG", optimize=True)
    data = output.getvalue()
    if len(data) > 7_000_000:
        raise ValueError("Weekly Discord image exceeds upload size limit")
    return data
