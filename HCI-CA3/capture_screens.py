"""Render every Raktdaan screen from raktdaan.html with headless Chrome and save phone-shaped images
for the slide deck (presentation_assets/screens/*.webp). Also crops the Figma exports used on slides.

Usage: python capture_screens.py
Needs Google Chrome (or Edge) and an internet connection (the prototype loads Figtree/Fraunces from Google Fonts).
"""
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).parent
OUT = HERE / "presentation_assets" / "screens"
FIGMA_OUT = HERE / "presentation_assets" / "figma"
SCREENS = ["welcome", "signin", "otp", "bloodgroup", "home", "find", "centre", "eligibility",
           "slot", "booked", "request", "matching", "tracking", "donorcard", "impact"]
BROWSERS = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]

# Viewer geometry at 1200x1080 CSS px (no zoom step kicks in above 1000 px height):
# 280 px side menu, 32 px stage padding, 412x917 phone centred, 10 px dark ring around it.
SCALE = 2
WIN_W, WIN_H = 1200, 1080
PHONE_X = 280 + 32 + (WIN_W - 280 - 64 - 412) // 2
PHONE_Y = 32
RING, RADIUS = 10, 40


def browser():
    for b in BROWSERS:
        if Path(b).exists():
            return b
    raise SystemExit("Chrome/Edge not found")


def shoot(url, png, w, h, scale):
    subprocess.run([browser(), "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    f"--force-device-scale-factor={scale}", f"--window-size={w},{h}",
                    "--virtual-time-budget=6000", f"--screenshot={png}", url],
                   check=True, capture_output=True)


def rounded(im, radius):
    """Return im with transparent rounded corners (anti-aliased)."""
    ss = 4
    mask = Image.new("L", (im.width * ss, im.height * ss), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, mask.width - 1, mask.height - 1], radius * ss, fill=255)
    out = im.convert("RGBA")
    out.putalpha(mask.resize(im.size, Image.LANCZOS))
    return out


def on_white(im):
    """Flatten transparency onto white (a plain RGB convert turns transparent pixels black)."""
    im = im.convert("RGBA")
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    return Image.alpha_composite(bg, im).convert("RGB")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    FIGMA_OUT.mkdir(parents=True, exist_ok=True)
    page = (HERE / "raktdaan.html").resolve().as_uri()
    box = [(PHONE_X - RING) * SCALE, (PHONE_Y - RING) * SCALE,
           (PHONE_X + 412 + RING) * SCALE, (PHONE_Y + 917 + RING) * SCALE]
    tmp = Path(tempfile.mkdtemp())
    try:
        for sid in SCREENS:
            png = tmp / f"{sid}.png"
            shoot(f"{page}#{sid}", png, WIN_W, WIN_H, SCALE)
            phone = rounded(Image.open(png).crop(box), (RADIUS + RING) * SCALE)
            phone.save(OUT / f"{sid}.webp", "WEBP", quality=90, method=6)
            print("captured", sid)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # Figma exports: component sheet (left part of the design-system board) and the icon strip
    ds = on_white(Image.open(HERE / "Blood Donation App – Design System.png"))
    ds.crop((0, 0, 1145, 1722)).save(FIGMA_OUT / "components.webp", "WEBP", quality=90, method=6)
    on_white(Image.open(HERE / "Icons — Phosphor (Regular + Fill).png")).save(
        FIGMA_OUT / "icons.webp", "WEBP", quality=92, method=6)
    print("cropped figma exports")


if __name__ == "__main__":
    main()
