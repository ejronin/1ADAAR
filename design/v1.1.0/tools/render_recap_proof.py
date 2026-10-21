#!/usr/bin/env python3
"""Design-only 1080px Python recap image. Fictional event, no webhook/network."""
from io import BytesIO
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import cairosvg

ROOT = Path(__file__).resolve().parents[4]
ART = ROOT / "docs" / "assets"
OUT = ROOT / "design" / "v1.1.0" / "screenshots"
OUT.mkdir(exist_ok=True)

def font(size, bold=False):
    names = (["/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"] if bold else
             ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"])
    for name in names:
        if Path(name).is_file():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default()

def source_svg(name, width):
    data = cairosvg.svg2png(url=str(ART / name), output_width=width)
    return Image.open(BytesIO(data)).convert("RGBA")

def main():
    w,h = 1080,675
    base = Image.new("RGB", (w,h), (12,19,15))
    hero = ART / "wardogs-official-hero.webp"
    if hero.is_file():
        art = Image.open(hero).convert("RGB")
        ratio = max(w/art.width,h/art.height)
        crop = art.resize((math.ceil(art.width*ratio),math.ceil(art.height*ratio)))
        crop = crop.crop(((crop.width-w)//2, (crop.height-h)//2, (crop.width+w)//2, (crop.height+h)//2))
        base = Image.blend(base,ImageEnhance.Brightness(crop).enhance(.65),.5)
    draw = ImageDraw.Draw(base)
    for y in range(h):
        a = y / h
        draw.line((0,y,w,y), fill=(int(8+13*a), int(20+8*a), int(12+9*a)), width=1) if y>310 else None
    draw.rounded_rectangle((19,19,w-19,h-19),radius=17,outline=(86,134,96),width=2)
    draw.line((59,85,1020,85),fill=(95,143,104),width=1)
    draw.text((58,44), "ONEAVERAGEDAN  /  WARDOGS COMMUNITY SERVER",font=font(19,True),fill=(154,231,170))
    draw.text((60,120),"AFTER ACTION",font=font(76,True),fill=(245,251,246),stroke_width=1)
    draw.text((60,204),"REPORT",font=font(91,True),fill=(245,251,246))
    badge=source_svg("1ad-logo.svg",132)
    base.paste(badge,(885,115),badge)
    draw=ImageDraw.Draw(base)
    draw.rounded_rectangle((59,319,1020,366),radius=5,fill=(64,46,27),outline=(152,119,68),width=1)
    draw.text((75,329),"DESIGN FIXTURE  /  FICTIONAL MATCH — NOT SENT TO DISCORD",font=font(18,True),fill=(255,222,166))
    draw.text((64,393),"BAKURANI  ·  KOTH",font=font(33,True),fill=(234,243,234))
    draw.text((64,441),"EXAMPLE SCOREBOARD",font=font(19,True),fill=(149,194,159))
    draw.rounded_rectangle((63,492,1015,520),radius=5,fill=(47,61,51))
    draw.rounded_rectangle((63,492,593,520),radius=4,fill=(70,94,249))
    draw.rounded_rectangle((599,492,1015,520),radius=4,fill=(238,65,56))
    a=source_svg("factions/lonestar.svg",50);b=source_svg("factions/valkyra.svg",50)
    base.paste(a,(61,541),a);base.paste(b,(555,541),b)
    draw=ImageDraw.Draw(base)
    draw.text((120,550),"LONESTAR  100",font=font(30,True),fill=(240,244,255))
    draw.text((610,550),"VALKYRA  78",font=font(30,True),fill=(253,239,238))
    draw.text((64,621),"Only actual verified completed match data may appear in released recaps.",font=font(18),fill=(183,214,188))
    out=OUT/"recap-python-render.png"
    base.save(out,optimize=True)
    print("Wrote design-only Python raster:",out)

if __name__=="__main__":main()
