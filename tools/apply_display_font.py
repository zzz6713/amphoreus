# -*- coding: utf-8 -*-
"""把标题类字体切到艺术字体（Cinzel + ZCOOL XiaoWei），并修 about 网格居中。"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS = os.path.join(ROOT, "css")

DISPLAY = "var(--display)"

# 需要换成艺术字体的选择器 -> 所在文件
TARGETS = {
    "layout.css": [
        r".nav-brand",
        r".hero-title",
        r".section-head h2",
        r".foot-inf",
        r".foot-line",
    ],
    "components.css": [
        r".about-card h3",
        r".heir-info h3",
        r".rail-name",
        r".flip-front em",
        r".flip-meta b",
        r".numeral",
        r".cone-fallback span",
        r".modal-name",
    ],
}


def patch_fonts():
    for fname, sels in TARGETS.items():
        path = os.path.join(CSS, fname)
        text = open(path, encoding="utf-8").read()
        changed = 0
        for sel in sels:
            pattern = re.compile(r"(" + re.escape(sel) + r"\s*\{)([^}]*)\}")

            def repl(m):
                body = m.group(2)
                if "font-family" in body:
                    body = re.sub(r"font-family:[^;]+;", "font-family:%s;" % DISPLAY, body)
                else:
                    body = body.rstrip() + " font-family:%s;" % DISPLAY
                return m.group(1) + body + "}"

            text, n = pattern.subn(repl, text, count=1)
            changed += n
        open(path, "w", encoding="utf-8", newline="\n").write(text)
        print(fname, "patched:", changed)


def patch_vars():
    path = os.path.join(CSS, "base.css")
    text = open(path, encoding="utf-8").read()
    if "--display" not in text:
        text = text.replace(
            '  --serif: "Noto Serif SC","Source Han Serif SC","Songti SC","STSong","SimSun",serif;',
            '  --display: "Cinzel","ZCOOL XiaoWei","Noto Serif SC","Source Han Serif SC","Songti SC","STSong","SimSun",serif;\n'
            '  --serif: "Noto Serif SC","Source Han Serif SC","Songti SC","STSong","SimSun",serif;'
        )
    open(path, "w", encoding="utf-8", newline="\n").write(text)
    print("base.css display var:", "--display" in text)


def patch_about():
    path = os.path.join(CSS, "layout.css")
    text = open(path, encoding="utf-8").read()
    old = """.about-grid{
  display:grid; gap:20px;
  grid-template-columns:repeat(auto-fit,minmax(280px,1fr));
}"""
    new = """.about-grid{
  display:grid; gap:20px;
  grid-template-columns:repeat(2,minmax(0,1fr));
  max-width:980px;
  margin:0 auto;
}"""
    if old in text:
        text = text.replace(old, new)
        print("about-grid -> 2x2 centered")
    else:
        print("about-grid pattern not found")
    open(path, "w", encoding="utf-8", newline="\n").write(text)

    path = os.path.join(CSS, "effects.css")
    text = open(path, encoding="utf-8").read()
    if ".about-grid{ grid-template-columns:1fr; }" not in text:
        text = text.replace(
            "  .tri-path{ grid-template-columns:1fr; }",
            "  .tri-path{ grid-template-columns:1fr; }\n  .about-grid{ grid-template-columns:1fr; }"
        )
        print("about-grid mobile -> 1 column")
    open(path, "w", encoding="utf-8", newline="\n").write(text)


def patch_entry():
    path = os.path.join(CSS, "style.css")
    text = open(path, encoding="utf-8").read()
    if "../assets/fonts" in text:
        return
    text = text.replace(
        '@import url("base.css");',
        '@import url("../assets/fonts/cinzel.css");\n'
        '@import url("../assets/fonts/zcool.css");\n'
        '@import url("base.css");'
    )
    open(path, "w", encoding="utf-8", newline="\n").write(text)
    print("style.css -> font imports")


if __name__ == "__main__":
    patch_vars()
    patch_fonts()
    patch_about()
    patch_entry()
