# -*- coding: utf-8 -*-
"""把光锥原图压成 webp，原图归档到 original/。"""
import os
import shutil
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "lightcones")
ORIG = os.path.join(SRC, "original")
WIDTH = 760
QUALITY = 84


def main():
    os.makedirs(ORIG, exist_ok=True)
    slugs = sorted(
        f[:-4] for f in os.listdir(SRC)
        if f.lower().endswith(".png") and not f.startswith("_")
    )
    if not slugs:
        print("nothing to do")
        return

    total_before = total_after = 0
    for slug in slugs:
        png = os.path.join(SRC, slug + ".png")
        webp = os.path.join(SRC, slug + ".webp")
        if os.path.exists(webp) and os.path.exists(os.path.join(ORIG, slug + ".png")):
            continue
        before = os.path.getsize(png)
        im = Image.open(png).convert("RGB")
        w, h = im.size
        if w > WIDTH:
            im = im.resize((WIDTH, round(h * WIDTH / w)), Image.LANCZOS)
        im.save(webp, "WEBP", quality=QUALITY, method=6)
        after = os.path.getsize(webp)
        shutil.move(png, os.path.join(ORIG, slug + ".png"))
        total_before += before
        total_after += after
        print(f"{slug:10s} {w}x{h} -> {im.size[0]}x{im.size[1]}  "
              f"{before/1024/1024:.2f}MB -> {after/1024:.0f}KB")

    print(f"TOTAL {total_before/1024/1024:.2f}MB -> {total_after/1024/1024:.2f}MB")


if __name__ == "__main__":
    main()
