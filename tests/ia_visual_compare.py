"""Side-by-side reference comparison for IA/UX/UI review.

A generated pair is evidence, NOT a visual-fidelity pass. Source screenshots
may contain fictional design fixtures while implementation uses actual or
truthful empty source states. Compare structure and line/typographic geometry,
not identical fictional numbers. Images come from the independent design
branch checked out read-only into ia-reference/.
"""
from __future__ import annotations

from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ACTUAL = ROOT / "visual-review"
REFERENCE = ROOT / "ia-reference" / "design" / "v1.1.0" / "screenshots"
OUT = ACTUAL / "ia-side-by-side"
OUT.mkdir(parents=True, exist_ok=True)

SCREENS = {
    "home": ("home-{w}.png", "home-{w}px.png"),
    "player": ("player-{w}.png", "playerone-{w}px.png"),
    "map-team": ("map-team-{w}.png", "map-team-{w}px.png"),
    "weekly": ("weekly-{w}.png", "weekly-unawarded-{w}px.png"),
    "activity": ("activity-{w}.png", "recorded-activity-{w}px.png"),
}
CROP_HEIGHT = {390: 1300, 1440: 1500}
PANEL_WIDTH = 580
FRAME_PADDING = 14
HEADER_HEIGHT = 78


def panel(path: Path, *, w: int) -> Image.Image:
    with Image.open(path) as src:
        image = src.convert("RGB")
    image = image.crop((0, 0, image.width, min(image.height, CROP_HEIGHT[w])))
    ratio = PANEL_WIDTH / image.width
    image = image.resize((PANEL_WIDTH, round(image.height * ratio)), Image.Resampling.LANCZOS)
    return image


def comparison(name: str, w: int, a: Path, b: Path) -> dict:
    left = panel(a, w=w)
    right = panel(b, w=w)
    tall = max(left.height, right.height)
    canvas = Image.new("RGB", (PANEL_WIDTH * 2 + FRAME_PADDING * 3,
                               HEADER_HEIGHT + tall + FRAME_PADDING), "#151b18")
    draw = ImageDraw.Draw(canvas)
    draw.text((FRAME_PADDING, 13), "IA REFERENCE - PR #28 / design candidate",
              fill="#e9d2aa")
    draw.text((PANEL_WIDTH + FRAME_PADDING * 2, 13), "IMPLEMENTATION - PR #29 / staged",
              fill="#b5f6c7")
    draw.text((FRAME_PADDING, 41), f"{name}  |  {w}px  |  upper page crop",
              fill="#d9e8dd")
    canvas.paste(left, (FRAME_PADDING, HEADER_HEIGHT))
    canvas.paste(right, (PANEL_WIDTH + FRAME_PADDING * 2, HEADER_HEIGHT))
    filename = f"{name}-{w}-comparison.png"
    canvas.save(OUT / filename, optimize=True)
    return {"screen": name, "width": w, "image": filename,
            "referenceFile": str(a.relative_to(ROOT)), "implementationFile": str(b.relative_to(ROOT)),
            "referenceCropPx": CROP_HEIGHT[w],
            "result": "PENDING INDEPENDENT HUMAN VISUAL-FIDELITY REVIEW"}


def main() -> None:
    evidence = []
    for screen, (reference_tmpl, actual_tmpl) in SCREENS.items():
        for w in (390, 1440):
            a = REFERENCE / reference_tmpl.format(w=w)
            b = ACTUAL / actual_tmpl.format(w=w)
            if not a.is_file() or not b.is_file():
                raise FileNotFoundError(f"Missing visual comparison input: {a}, {b}")
            evidence.append(comparison(screen, w, a, b))
    # Real Discord message shape cannot be compared with HTML using pixels.
    # Compare only the two separately generated Python recap artworks.
    recap_reference = REFERENCE / "recap-python-render.png"
    recap_actual = ACTUAL / "discord-recap-v11-FICTIONAL.png"
    if not recap_reference.is_file() or not recap_actual.is_file():
        raise FileNotFoundError("Missing recap PNGs")
    # Artificial images are labeled fictional in BOTH pipelines.
    a = panel(recap_reference, w=1440)
    b = panel(recap_actual, w=1440)
    canvas = Image.new("RGB", (PANEL_WIDTH * 2 + FRAME_PADDING * 3,
                               HEADER_HEIGHT + max(a.height, b.height) + FRAME_PADDING),
                       "#151b18")
    d = ImageDraw.Draw(canvas)
    d.text((FRAME_PADDING, 13), "IA PYTHON DESIGN PNG / FICTIONAL", fill="#e9d2aa")
    d.text((PANEL_WIDTH + FRAME_PADDING * 2, 13), "ACTUAL PYTHON RECAP PNG / FICTIONAL",
           fill="#b5f6c7")
    canvas.paste(a, (FRAME_PADDING, HEADER_HEIGHT))
    canvas.paste(b, (PANEL_WIDTH + FRAME_PADDING * 2, HEADER_HEIGHT))
    canvas.save(OUT / "discord-artwork-comparison.png", optimize=True)
    evidence.append({"screen":"discord-recap-artwork", "image":"discord-artwork-comparison.png",
                     "result":"NOT PROOF OF ACTUAL DISCORD CLIENT V2 RENDERING"})
    (OUT / "comparisons.json").write_text(json.dumps({
       "status":"FOR INDEPENDENT IA REVIEW; NOT ACCEPTED",
       "referenceBranch":"design/v1.1.0-ia-handoff",
       "implementationBranch":"feature/v1.1-ia-implementation",
       "note":"Content may differ intentionally: only actual verified server data is published. Layout and artwork fidelity require manual review. No production changes.",
       "evidence":evidence},indent=2)+"\n",encoding="utf-8")
    print(f"Built {len(evidence)} labelled visual comparisons in {OUT}")


if __name__=="__main__":
    main()
