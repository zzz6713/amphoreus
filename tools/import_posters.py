# -*- coding: utf-8 -*-
"""把桌面上的黄金裔海报 avif 转成 webp，按角色 id 放入 assets/heirs/。"""
import glob
import os
import shutil

from PIL import Image

DESKTOP = os.path.expanduser("~/Desktop")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "heirs")

# 哈希前缀 -> 角色 id（已逐张人工核对）
MAP = {
    "0fd16a15": "cerydra",    # 刻律德菈
    "2ebccfc8": "cipher",     # 赛飞儿
    "3512acaf": "mydei",      # 万敌
    "3edac3db": "anaxa",      # 那刻夏
    "67e18b9f": "evernight",  # 长夜月
    "691cbb68": "castorice",  # 遐蝶
    "8592f78c": "tribbie",    # 缇宝
    "a070875a": "aglaea",     # 阿格莱雅（有两份，取其一）
    "a15a0f67": "phainon",    # 白厄
    "c23461cf": "danheng",    # 丹恒·腾荒
    "f18ba14e": "hysilens",   # 海瑟音
}


def main():
    os.makedirs(OUT, exist_ok=True)
    files = sorted(glob.glob(os.path.join(DESKTOP, "*.avif")))
    done, seen = [], set()

    for f in files:
        base = os.path.basename(f)
        key = base[:8]
        slug = MAP.get(key)
        if not slug:
            print("SKIP", base)
            continue
        if slug in seen:
            print("DUP ", base, "->", slug, "(skipped)")
            continue
        seen.add(slug)

        im = Image.open(f).convert("RGB")
        w, h = im.size
        if w > 744:
            im = im.resize((744, round(h * 744 / w)), Image.LANCZOS)
        dest = os.path.join(OUT, slug + ".webp")
        im.save(dest, "WEBP", quality=84, method=6)
        done.append(slug)
        print(f"{slug:10s} {w}x{h} -> {os.path.getsize(dest)/1024:.0f}KB")

    # 风堇缺图：先用她的光锥立绘临时占位，等补图后同名覆盖即可
    hy = os.path.join(OUT, "hyacine.webp")
    if not os.path.exists(hy):
        src = os.path.join(ROOT, "assets", "lightcones", "hyacine.webp")
        if os.path.exists(src):
            shutil.copyfile(src, hy)
            print("hyacine   缺失，暂用光锥立绘占位")

    print("done:", len(done), sorted(done))


if __name__ == "__main__":
    main()
