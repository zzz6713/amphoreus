# -*- coding: utf-8 -*-
"""补齐剩余光锥立绘（带重试与退避）。"""
import json
import os
import random
import time
import urllib.parse
import urllib.request

API = "https://wiki.biligame.com/sr/api.php"
UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "lightcones")

TARGETS = [
    ("cipher", "谎言在风中飘扬"),
    ("phainon", "黎明恰如此燃烧"),
    ("hysilens", "海洋为何而歌"),
    ("cerydra", "没有回报的加冕"),
    ("evernight", "致长夜的星光"),
    ("danheng", "纵然山河万程"),
    ("cyrene", "爱如此刻永恒"),
]


def api(params):
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read().decode("utf-8"))


def all_cone_images():
    names, cont = [], None
    while True:
        p = {
            "action": "query", "list": "allimages", "aiprefix": "光锥-",
            "ailimit": "500", "format": "json", "formatversion": "2",
        }
        if cont:
            p["aicontinue"] = cont
        d = api(p)
        names += [x["name"] for x in d.get("query", {}).get("allimages", [])]
        cont = d.get("continue", {}).get("aicontinue")
        if not cont:
            break
        time.sleep(1.0)
    return names


def download(title, dest, tries=4):
    url = "https://wiki.biligame.com/sr/Special:FilePath/" + urllib.parse.quote(title)
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            with open(dest, "wb") as f:
                f.write(data)
            return len(data)
        except Exception as e:  # noqa: BLE001
            last = e
            wait = 20 + i * 25 + random.random() * 10
            print("  retry", os.path.basename(dest), "in", round(wait), "s", e)
            time.sleep(wait)
    raise last


def main():
    pool = all_cone_images()
    index = {}
    for n in pool:
        base = n.replace(".png", "").replace("-无背景", "")
        parts = base.split("-")
        if len(parts) >= 3:
            index.setdefault(parts[-1], n)

    done = []
    for slug, cone in TARGETS:
        dest = os.path.join(OUT, slug + ".png")
        if os.path.exists(dest) and os.path.getsize(dest) > 200000:
            done.append(slug)
            continue
        fname = index.get(cone)
        if not fname:
            print("NOFILE", slug, cone)
            continue
        try:
            size = download(fname, dest)
            done.append(slug)
            print("OK", slug, size)
        except Exception as e:  # noqa: BLE001
            print("FAIL", slug, e)
        time.sleep(18 + random.random() * 8)

    print("total ok:", len(done), done)


if __name__ == "__main__":
    main()
