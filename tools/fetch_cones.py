# -*- coding: utf-8 -*-
"""从 BWIKI 拉取翁法罗斯十二黄金裔（+昔涟）的光锥立绘到 assets/lightcones/。"""
import json
import os
import sys
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
    ("aglaea", "将光阴织成黄金"),
    ("tribbie", "如果时间是一朵花"),
    ("mydei", "血火啊，燃烧前路"),
    ("castorice", "让告别，更美一些"),
    ("anaxa", "生命当付之一炬"),
    ("hyacine", "愿虹光永驻天空"),
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
    names = []
    cont = None
    while True:
        p = {
            "action": "query",
            "list": "allimages",
            "aiprefix": "光锥-",
            "ailimit": "500",
            "format": "json",
            "formatversion": "2",
        }
        if cont:
            p["aicontinue"] = cont
        d = api(p)
        names += [x["name"] for x in d.get("query", {}).get("allimages", [])]
        cont = d.get("continue", {}).get("aicontinue")
        if not cont:
            break
        time.sleep(0.4)
    return names


def download(title, dest):
    url = "https://wiki.biligame.com/sr/Special:FilePath/" + urllib.parse.quote(title)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    with open(dest, "wb") as f:
        f.write(data)
    return len(data)


def main():
    os.makedirs(OUT, exist_ok=True)
    pool = all_cone_images()
    report = {"images": len(pool), "ok": [], "fail": [], "size": {}}

    # 去掉“-无背景”等变体，优先完整卡面
    def pick(name):
        base = name.replace(".png", "")
        base = base.replace("-无背景", "")
        parts = base.split("-")
        return parts[-1] if len(parts) >= 3 else ""

    index = {}
    for n in pool:
        key = pick(n)
        if key and key not in index:
            index[key] = n

    for slug, cone in TARGETS:
        fname = index.get(cone)
        dest = os.path.join(OUT, slug + ".png")
        if not fname:
            report["fail"].append([slug, cone, "no-file"])
            continue
        try:
            size = download(fname, dest)
            report["ok"].append([slug, cone, fname])
            report["size"][slug] = size
        except Exception as e:  # noqa: BLE001
            report["fail"].append([slug, cone, str(e)])
        time.sleep(0.6)

    with open(os.path.join(ROOT, "tools", "fetch-report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("downloaded", len(report["ok"]), "of", len(TARGETS))
    for item in report["fail"]:
        print("FAIL", item[0], item[2])


if __name__ == "__main__":
    main()
