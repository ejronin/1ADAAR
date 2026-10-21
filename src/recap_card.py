"""Render the v1.1 WARDOGS AFTER ACTION REPORT image for Discord.

One editorial system across dashboard, recap and weekly:
official source artwork, charcoal/green, faction colors only for real results.
All data comes from a verified WARCON match; the optional demo is unmistakably
fictional and is never used by the live match collector.
"""
from __future__ import annotations

from functools import lru_cache
from io import BytesIO
from pathlib import Path

from cairosvg import svg2png
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "docs" / "assets" / "wardogs-official-hero.webp"
WORDMARK = ROOT / "docs" / "assets" / "wardogs-fullmark.png"
EMBLEM = ROOT / "docs" / "assets" / "1ad-logo.svg"
FACTION_ASSETS = ROOT / "docs" / "assets" / "factions"
FACTION_COLORS = {"lonestar": "#465eff", "valkyra": "#ee4138", "manticore": "#3eba42"}
WIDTH, LEFT, RIGHT = 1080, 50, 1030
BG, PANEL, EDGE = "#0d1411", "#151d19", "#314b3a"
GREEN, LIGHT, MUTED = "#86f4a4", "#f5f8f5", "#a9bfaf"
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")


def faction_color(name: object) -> str | None:
    return FACTION_COLORS.get(name.strip().lower()) if isinstance(name, str) else None


@lru_cache(maxsize=12)
def faction_emblem(name: str, size: int = 52) -> Image.Image:
    if name not in FACTION_COLORS:
        raise ValueError("Unknown faction emblem")
    path = FACTION_ASSETS / f"{name}.svg"
    png = svg2png(bytestring=path.read_bytes(), output_width=size, output_height=size)
    with Image.open(BytesIO(png)) as original:
        return original.convert("RGBA")


@lru_cache(maxsize=1)
def community_emblem() -> Image.Image:
    png = svg2png(bytestring=EMBLEM.read_bytes(), output_width=84, output_height=84)
    with Image.open(BytesIO(png)) as original:
        return original.convert("RGBA")


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    paths = [
        FONT_DIR / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/liberation2") /
            ("LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf"),
    ]
    for path in paths:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    raise RuntimeError("Required Linux font unavailable")


def truncate(draw: ImageDraw.ImageDraw, text: object, face, maximum: int) -> str:
    value = str(text or "—").replace("\n", " ").replace("\r", " ")
    value = "".join(ch for ch in value if ch.isprintable())
    if draw.textbbox((0, 0), value, font=face)[2] <= maximum:
        return value
    while value and draw.textbbox((0, 0), value + "…", font=face)[2] > maximum:
        value = value[:-1]
    return value + "…"


def duration_text(seconds: object) -> str:
    n = max(0, int(seconds or 0))
    return (f"{n // 3600}h {(n % 3600) // 60}m" if n >= 3600
            else f"{n // 60}m")


def alpha_paste(im: Image.Image, icon: Image.Image, xy: tuple[int, int]) -> None:
    im.paste(icon, xy, icon)


def draw_header(im: Image.Image, draw: ImageDraw.ImageDraw, match: dict, demo: bool) -> None:
    """Hero art and brand are sourced from approved, unchanged repo assets."""
    if ART.exists():
        with Image.open(ART) as original:
            battlefield = ImageOps.fit(original.convert("RGB"), (WIDTH, 294),
                                        method=Image.Resampling.LANCZOS,
                                        centering=(.54, .44))
        im.paste(battlefield, (0, 0))
    # An intentionally strong dark scrim makes the report readable on mobile.
    scrim = Image.new("RGBA", (WIDTH, 294), (0, 0, 0, 0))
    shade = ImageDraw.Draw(scrim)
    for y in range(294):
        opacity = min(241, 132 + int(y * .38))
        shade.line((0, y, WIDTH, y), fill=(3, 10, 6, opacity), width=1)
    im.paste(Image.alpha_composite(im.crop((0, 0, WIDTH, 294)).convert("RGBA"),
                                   scrim).convert("RGB"), (0, 0))
    alpha_paste(im, community_emblem(), (LEFT, 25))
    draw.text((147, 35), "1ADAAR", fill=LIGHT, font=font(29, True))
    draw.text((147, 76), "ONEAVERAGEDAN COMMUNITY SERVER", fill=GREEN, font=font(16, True))
    if WORDMARK.exists():
        with Image.open(WORDMARK) as original:
            mark = original.convert("RGBA")
            mark.thumbnail((257, 80), Image.Resampling.LANCZOS)
            alpha_paste(im, mark, (RIGHT - mark.width, 26))
    draw.line((LEFT, 124, RIGHT, 124), fill="#699d76", width=2)
    draw.text((LEFT, 146), "AFTER ACTION REPORT / COMPLETED MATCH",
              fill=GREEN, font=font(19, True))
    map_name = truncate(draw, str(match.get("map") or "Unknown map").upper(),
                        font(62, True), 965)
    draw.text((LEFT, 183), map_name, fill=LIGHT, font=font(62, True))
    mode = truncate(draw, match.get("mode") or "Mode unavailable", font(22), 600)
    draw.text((LEFT, 259), mode, fill="#dfebdf", font=font(22))
    if demo:
        draw.rounded_rectangle((696, 253, RIGHT, 288), radius=6, fill="#a46928")
        draw.text((709, 259), "FICTIONAL SAMPLE • NOT LIVE", fill="#10120e",
                  font=font(16, True))
    draw.rectangle((0, 292, WIDTH, 295), fill=GREEN)


def render_match_card(match: dict, *, demo: bool = False) -> bytes:
    """Return the real 1080px image layout used by the Discord media gallery."""
    scores = [r for r in match.get("scores", []) if isinstance(r, dict)][:3]
    awards = [a for a in match.get("awards", [])
              if isinstance(a, dict) and a.get("name")][:3]
    height = 962 if awards else 816
    im = Image.new("RGB", (WIDTH, height), BG)
    draw = ImageDraw.Draw(im)
    draw_header(im, draw, match, demo)
    draw.rounded_rectangle((LEFT, 312, RIGHT, 430), radius=12, fill=PANEL, outline=EDGE, width=2)
    names = {str(row.get("name") or "").casefold(): str(row.get("name") or "")
             for row in scores}
    winner = names.get(str(match.get("winner") or "").casefold(), "")
    color = faction_color(winner) or GREEN
    draw.rounded_rectangle((LEFT + 1, 313, LEFT + 7, 429), radius=2, fill=color)
    draw.text((LEFT + 25, 327), "MATCH WINNER" if winner else "WINNER NOT VERIFIED",
              font=font(17, True), fill=GREEN)
    if winner and faction_color(winner):
        alpha_paste(im, faction_emblem(winner.casefold(), 57), (LEFT + 23, 359))
    winner_left = LEFT + (93 if winner and faction_color(winner) else 25)
    draw.text((winner_left, 363), truncate(draw, winner or "Awaiting verified result",
                                           font(35, True), 560),
              font=font(35, True), fill=LIGHT)
    draw.line((758, 332, 758, 411), fill=EDGE, width=2)
    draw.text((784, 331), "MATCH DURATION", fill=MUTED, font=font(16, True))
    draw.text((784, 359), duration_text(match.get("durationSeconds")),
              fill=LIGHT, font=font(35, True))
    draw.text((LEFT, 453), "FINAL FACTION SCORES", fill=LIGHT, font=font(24, True))
    draw.text((746, 458), "REPORTED BY WARCON", fill=MUTED, font=font(15, True))
    highest = max((float(x.get("score") or 0) for x in scores), default=1)
    highest = max(1, highest)
    if not scores:
        draw.text((LEFT, 509), "No verified faction scores available", fill=MUTED,
                  font=font(24))
    for index, row in enumerate(scores):
        y = 493 + 82 * index
        name = str(row.get("name") or "Unknown team")
        draw.rounded_rectangle((LEFT, y, RIGHT, y + 72), radius=9,
                               fill="#18231d", outline="#314d3b", width=1)
        tint = faction_color(name) or "#779483"
        if faction_color(name):
            alpha_paste(im, faction_emblem(name.casefold(), 47), (LEFT + 13, y + 10))
        x_label = LEFT + (75 if faction_color(name) else 20)
        draw.text((x_label, y + 9), truncate(draw, name.upper(), font(26, True), 575),
                  fill=LIGHT, font=font(26, True))
        score = max(0, float(row.get("score") or 0))
        label = f"{score:g}"
        label_width = draw.textbbox((0, 0), label, font=font(36, True))[2]
        draw.text((RIGHT - 18 - label_width, y + 7), label, fill=LIGHT, font=font(36, True))
        draw.rounded_rectangle((x_label, y + 52, RIGHT - 17, y + 60),
                               radius=4, fill="#34423a")
        fill_end = x_label + int((RIGHT - 17 - x_label) * score / highest)
        if fill_end > x_label:
            draw.rounded_rectangle((x_label, y + 52, fill_end, y + 60),
                                   radius=4, fill=tint)
    if awards:
        draw.line((LEFT, 757, RIGHT, 757), fill=EDGE, width=2)
        draw.text((LEFT, 775), "RECORDED MATCH HIGHLIGHTS", fill=GREEN,
                  font=font(21, True))
        card_width = (RIGHT - LEFT - 22) // 3
        for i, award in enumerate(awards):
            x = LEFT + i * (card_width + 11)
            draw.rounded_rectangle((x, 815, x + card_width, 880), radius=7,
                                   fill="#1a271e", outline="#39533f", width=1)
            draw.text((x + 13, 821),
                      truncate(draw, award.get("label") or award.get("key") or "Highlight",
                               font(14, True), card_width - 26),
                      fill=MUTED, font=font(14, True))
            draw.text((x + 13, 844),
                      truncate(draw, award.get("name"), font(19, True), card_width - 26),
                      fill=LIGHT, font=font(19, True))
            draw.text((x + 13, 866),
                      truncate(draw, award.get("value"), font(13), card_width - 26),
                      fill=GREEN, font=font(13))
    draw.rectangle((0, height - 69, WIDTH, height), fill="#1c3122")
    draw.rectangle((0, height - 69, WIDTH, height - 66), fill="#7de39a")
    foot = ("DESIGN SAMPLE · FICTIONAL MATCH · DO NOT POST"
            if demo else f"MATCH #{match.get('id', '—')} · WARCON CAPTURE")
    draw.text((LEFT, height - 48), foot, fill=GREEN, font=font(17, True))
    draw.text((790, height - 48), "1ADAAR / FULL REPORT →",
              fill=LIGHT, font=font(16, True))
    draw.rectangle((0, 0, WIDTH - 1, height - 1), outline="#3d6650", width=2)
    buf = BytesIO()
    im.save(buf, "PNG", optimize=True)
    data = buf.getvalue()
    if len(data) > 7_000_000:
        raise ValueError("Discord recap image exceeds safe upload size")
    return data
