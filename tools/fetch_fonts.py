# -*- coding: utf-8 -*-
"""把 Google Fonts 的 Cinzel / ZCOOL XiaoWei 下载到本地，并生成 @font-face CSS。"""
import os
import re
import time
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "fonts")

FAMILIES = {
    "cinzel": "https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600&display=swap",
    "zcool": "https://fonts.googleapis.com/css2?family=ZCOOL+XiaoWei&display=swap",
}
FAMILY_NAME = {"cinzel": "Cinzel", "zcool": "ZCOOL XiaoWei"}


def fetch(url, binary=False, tries=3):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read() if binary else r.read().decode("utf-8")
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(3 + i * 4)
    raise last


def main():
    os.makedirs(OUT, exist_ok=True)
    lines_all = []

    for slug, css_url in FAMILIES.items():
        css = fetch(css_url)
        blocks = re.findall(r"@font-face\s*{(.*?)}", css, re.S)
        folder = os.path.join(OUT, slug)
        os.makedirs(folder, exist_ok=True)

        cache = {}
        out = []
        for i, block in enumerate(blocks):
            weight = (re.search(r"font-weight:\s*([^;]+);", block) or [None, "400"])[1].strip()
            style = (re.search(r"font-style:\s*([^;]+);", block) or [None, "normal"])[1].strip()
            url = (re.search(r"url\((https://[^)]+)\)", block) or [None, None])[1]
            ur = (re.search(r"unicode-range:\s*([^;]+);", block) or [None, None])[1]
            if not url:
                continue
            if url in cache:
                fname = cache[url]
            else:
                data = fetch(url, binary=True)
                fname = "%03d.woff2" % i
                with open(os.path.join(folder, fname), "wb") as f:
                    f.write(data)
                cache[url] = fname
                time.sleep(0.15)

            out.append(
                "@font-face{font-family:'%s';font-style:%s;font-weight:%s;font-display:swap;"
                "src:url('%s/%s') format('woff2');%s}"
                % (
                    FAMILY_NAME[slug], style, weight,
                    slug, fname,
                    ("unicode-range:%s;" % ur.strip()) if ur else "",
                )
            )
        print(slug, "faces:", len(out), "files:", len(cache))

        css_path = os.path.join(OUT, slug + ".css")
        header = "/* %s 本地字体（下载自 Google Fonts, SIL OFL） */\n" % FAMILY_NAME[slug]
        with open(css_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(header + "\n".join(out) + "\n")

    total = sum(
        os.path.getsize(os.path.join(dp, f))
        for dp, _, fs in os.walk(OUT) for f in fs
    )
    print("total font bytes:", total)


if __name__ == "__main__":
    main()
