"""Render verified WARCON match results as a real PNG for Discord embeds.

Uses only the game's approved locally stored press-pack background artwork.
No guessed statistics, Steam IDs, external image services, or remote fonts.
"""
from __future__ import annotations

from functools import lru_cache
from io import BytesIO
from cairosvg import svg2png
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "docs" / "assets" / "wardogs-official-hero.webp"
WORDMARK = ROOT / "docs" / "assets" / "wardogs-fullmark.png"
WIDTH, LEFT, RIGHT = 1080, 52, 1028
BG = "#0a0e0c"
GREEN = "#76e59a"
LIGHT = "#f4f8f5"
MUTED = "#a5b9ac"
# Official-source local SVGs used by the website and the Discord PNG alike.
FACTION_COLORS = {"lonestar": "#465eff", "valkyra": "#ee4138", "manticore": "#3eba42"}
FACTION_ASSETS = ROOT / "docs" / "assets" / "factions"


def faction_color(name: object) -> str | None:
    return FACTION_COLORS.get(name.strip().lower()) if isinstance(name, str) else None


@lru_cache(maxsize=3)
def faction_emblem(name: str) -> Image.Image:
    if name not in FACTION_COLORS:
        raise ValueError("Unknown faction emblem")
    path = FACTION_ASSETS / f"{name}.svg"
    # No remote URLs. The repo's already-approved vector is rendered locally.
    rendered = svg2png(bytestring=path.read_bytes(), output_width=52, output_height=52)
    with Image.open(BytesIO(rendered)) as source:
        return source.convert("RGBA")

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        FONT_DIR / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/liberation2") / ("LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    raise RuntimeError("Required Linux font unavailable; refusing unreadable recap")


def truncate(draw: ImageDraw.ImageDraw, text: object, f, width: int) -> str:
    value = str(text or "—").replace("\n", " ").replace("\r", " ")
    value = "".join(c for c in value if c.isprintable())
    if draw.textbbox((0, 0), value, font=f)[2] <= width:
        return value
    while value and draw.textbbox((0, 0), value + "…", font=f)[2] > width:
        value = value[:-1]
    return value + "…"


def render_match_card(match: dict, *, demo: bool = False) -> bytes:
    """Return optimized PNG bytes; no IO writes or persistent fake match entries."""
    scores = [r for r in match.get("scores", []) if isinstance(r, dict)][:3]
    awards = [a for a in match.get("awards", []) if isinstance(a, dict) and a.get("name")][:3]
    height = 575 + 83 * len(scores) + (126 if awards else 20)
    im = Image.new("RGB", (WIDTH, height), BG)
    draw = ImageDraw.Draw(im)
    if ART.exists():
        with Image.open(ART) as original:
            artwork = ImageOps.fit(original.convert("RGB"), (WIDTH, 265), method=Image.Resampling.LANCZOS, centering=(.53, .45))
        im.paste(artwork, (0, 0))
        overlay = Image.new("RGBA", (WIDTH, 265), (0, 0, 0, 0))
        shade = ImageDraw.Draw(overlay)
        for y in range(265):
            fade = min(225, max(40, int(35 + 195 * y / 265)))
            shade.line((0, y, WIDTH, y), fill=(0, 10, 5, fade))
        im.paste(Image.alpha_composite(im.crop((0, 0, WIDTH, 265)).convert("RGBA"), overlay).convert("RGB"), (0, 0))
    draw = ImageDraw.Draw(im)
    draw.rectangle((0, 0, WIDTH - 1, height - 1), outline="#376345", width=2)
    draw.rectangle((0, 0, 7, 265), fill=GREEN)
    draw.text((LEFT, 37), "1ADAAR / MATCH COMPLETE", font=font(32, True), fill=LIGHT)
    draw.text((LEFT, 85), "ONEAVERAGEDAN · WARDOGS COMMUNITY SERVER", font=font(17, True), fill=GREEN)
    if WORDMARK.exists():
        with Image.open(WORDMARK) as mark:
            mark = mark.convert("RGBA")
            mark.thumbnail((232, 74), Image.Resampling.LANCZOS)
            im.paste(mark, (WIDTH - 258, 33), mark)
    map_name = truncate(draw, str(match.get("map") or "Unknown map").upper(), font(55, True), 750)
    draw.text((LEFT, 154), map_name, font=font(55, True), fill=LIGHT)
    if demo:
        draw.rounded_rectangle((LEFT, 218, 445, 253), radius=6, fill="#824f25")
        draw.text((LEFT + 13, 224), "DEMO • FICTIONAL MATCH DATA", font=font(17, True), fill="#ffffff")
    else:
        draw.text((LEFT, 229), "OFFICIAL GAME ART • MATCH STATISTICS: WARCON", font=font(13), fill="#c6dacb")
    draw.rectangle((LEFT, 283, RIGHT, 286), fill="#335e40")
    draw.text((LEFT, 308), "MAP", font=font(15, True), fill=GREEN)
    draw.text((LEFT, 335), truncate(draw, match.get("map"), font(24, True), 258), font=font(24, True), fill=LIGHT)
    draw.text((402, 308), "MODE", font=font(15, True), fill=GREEN)
    draw.text((402, 335), truncate(draw, match.get("mode") or "Unknown", font(23, True), 410), font=font(23, True), fill=LIGHT)
    draw.text((838, 308), "DURATION", font=font(15, True), fill=GREEN)
    seconds = max(0, int(match.get("durationSeconds") or 0))
    duration = f"{seconds // 3600}h {seconds % 3600 // 60}m" if seconds >= 3600 else f"{seconds // 60}m"
    draw.text((838, 335), duration, font=font(24, True), fill=LIGHT)
    draw.line((LEFT, 389, RIGHT, 389), fill="#294234", width=2)
    draw.text((LEFT, 414), "FINAL FACTION SCORES", font=font(20, True), fill=LIGHT)
    if not scores:
        draw.text((LEFT, 455), "No verified scores available", font=font(19), fill=MUTED)
    maximum = max(1, *(float(row.get("score") or 0) for row in scores))
    for i, row in enumerate(scores):
        y = 465 + i * 83
        faction_name = str(row.get("name") or "")
        faction = faction_name.strip().lower()
        color = faction_color(faction_name)
        if color:
            icon = faction_emblem(faction)
            im.paste(icon, (LEFT, y - 9), icon)
        draw.text((LEFT + (65 if color else 0), y),
                  truncate(draw, faction_name, font(24, True), 710 if color else 775),
                  font=font(24, True), fill=LIGHT)
        val = max(0, float(row.get("score") or 0))
        score = f"{val:g}"
        draw.text((RIGHT - draw.textbbox((0, 0), score, font=font(24, True))[2], y), score, font=font(24, True), fill=LIGHT)
        draw.rounded_rectangle((LEFT, y + 37, RIGHT, y + 52), radius=6, fill="#28332d")
        fill_w = max(0, min(RIGHT - LEFT, int((RIGHT - LEFT) * val / maximum)))
        if fill_w > 0:
            draw.rounded_rectangle((LEFT, y + 37, LEFT + fill_w, y + 52), radius=6, fill=color or "#6b8f79")
    bottom = 465 + len(scores) * 83 + 10
    draw.line((LEFT, bottom, RIGHT, bottom), fill="#294234", width=2)
    if awards:
        draw.text((LEFT, bottom + 23), "MATCH AWARDS · VERIFIED WARCON DATA", font=font(16, True), fill=GREEN)
        cw = (RIGHT - LEFT) // len(awards)
        for i, item in enumerate(awards):
            x = LEFT + cw * i
            title = truncate(draw, (item.get("label") or item.get("key") or "Award").upper(), font(14, True), cw - 23)
            player = truncate(draw, item.get("name"), font(23, True), cw - 24)
            val = truncate(draw, item.get("value"), font(19), cw - 24)
            draw.text((x, bottom + 50), title, font=font(14, True), fill=MUTED)
            draw.text((x, bottom + 72), player, font=font(23, True), fill=LIGHT)
            draw.text((x, bottom + 102), val, font=font(19), fill=GREEN)
    else:
        draw.text((LEFT, bottom + 22), "Combat awards appear when WARCON supplies verified results", font=font(17), fill=MUTED)
    draw.rectangle((0, height - 62, WIDTH, height - 1), fill="#15291b")
    footer = "TEST IMAGE · NOT A REAL MATCH" if demo else f"MATCH #{match.get('id', '—')} · VERIFIED FROM WARCON"
    draw.text((LEFT, height - 43), footer, font=font(17, True), fill=GREEN)
    draw.text((RIGHT - 320, height - 43), "FULL REPORT ON 1ADAAR  ↗", font=font(16, True), fill=LIGHT)
    out = BytesIO()
    im.save(out, "PNG", optimize=True)
    data = out.getvalue()
    if len(data) > 7_000_000:
        raise ValueError("Discord recap image exceeds safe upload size")
    return data
