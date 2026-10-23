"""Build three readable map-name banners from the licensed WARDOGS RCON previews.

Run after Pillow is installed. Source originals remain unmodified and are
tracked alongside the generated presentation crops. No invented map artwork.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "docs" / "assets" / "map-banners"
MAPS = ("bakurani", "ozeti", "zestafona")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf"


def banner(name: str) -> Path:
    original = FOLDER / f"{name}.webp"
    if not original.is_file():
        raise FileNotFoundError(f"Approved map image missing: {original}")
    with Image.open(original) as source:
        image = source.convert("RGB").resize((1280, 720), Image.Resampling.LANCZOS)
    # Text is baked into the delivered image so the card works on any CSS size.
    veil = Image.new("RGBA", image.size, (0, 0, 0, 0))
    pix = veil.load()
    for x in range(1280):
        strength = max(0, (1 - x / 1170))
        for y in range(720):
            pix[x, y] = (3, 13, 15, int(205 * strength) + 22)
    image = Image.alpha_composite(image.convert("RGBA"), veil)
    draw = ImageDraw.Draw(image)
    label = name.upper()
    font = ImageFont.truetype(FONT, 114)
    while draw.textbbox((0, 0), label, font=font, stroke_width=0)[2] > 1090:
        font = ImageFont.truetype(FONT, font.size - 5)
    eyebrow = ImageFont.truetype(FONT, 27)
    draw.text((75, 243), "WARDOGS  /  MAP INTEL", font=eyebrow, fill="#b4e7cb", stroke_width=1, stroke_fill="#06100d")
    draw.text((72, 310), label, font=font, fill="#f8fff8", stroke_width=4, stroke_fill="#07120e")
    draw.line((78, 452, 545, 452), fill="#96dfb2", width=6)
    target = FOLDER / f"{name}-card.webp"
    image.convert("RGB").save(target, "WEBP", quality=89, method=6)
    return target


if __name__ == "__main__":
    for entry in MAPS:
        output = banner(entry)
        print(output.relative_to(ROOT), output.stat().st_size, "bytes")
