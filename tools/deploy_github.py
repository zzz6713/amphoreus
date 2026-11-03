# -*- coding: utf-8 -*-
"""把 amphoreus 站点通过 GitHub API 推上去并开启 Pages（不需要本机装 git）。

用法：
    $env:GITHUB_TOKEN = "github_pat_xxx"
    python tools/deploy_github.py [仓库名]
"""
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()
REPO = (sys.argv[1] if len(sys.argv) > 1 else "amphoreus").strip()
BRANCH = "main"
SKIP_DIRS = {"original", ".git", ".preview"}


def api(method, path, body=None, expect=(200, 201, 204)):
    url = "https://api.github.com" + path
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": "Bearer " + TOKEN,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "amphoreus-deploy",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            return json.loads(raw) if raw else {}, r.status
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        if e.code in expect:
            return json.loads(raw) if raw else {}, e.code
        raise RuntimeError("HTTP %s %s %s -> %s" % (e.code, method, path, raw[:400]))


def collect():
    out = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, ROOT).replace("\\", "/")
            if rel.startswith(".") and not rel.startswith(".vscode"):
                if rel != ".gitignore":
                    continue
            out.append((rel, full))
    out.sort(key=lambda x: x[0])
    return out


def main():
    if not TOKEN:
        raise SystemExit("缺少 GITHUB_TOKEN")

    user, _ = api("GET", "/user")
    owner = user["login"]
    print("账号:", owner)

    # 1. 建仓库（已存在则复用）
    try:
        repo, _ = api("POST", "/user/repos", {
            "name": REPO,
            "description": "翁法罗斯 · AMPHOREUS —— 十二黄金裔主题站",
            "private": False,
            "auto_init": False,
            "has_issues": True,
            "has_wiki": False,
        })
        print("仓库已创建:", repo["full_name"])
    except RuntimeError as e:
        if "already exists" not in str(e):
            raise
        repo, _ = api("GET", "/repos/%s/%s" % (owner, REPO))
        print("仓库已存在，复用:", repo["full_name"])

    # 1.5 空仓库拿不到 Git Data API，先用 Contents API 落一个初始提交
    try:
        api("GET", "/repos/%s/%s/git/ref/heads/%s" % (owner, REPO, BRANCH))
        print("已有分支:", BRANCH)
    except RuntimeError:
        init = base64.b64encode(b"# amphoreus\n").decode("ascii")
        api("PUT", "/repos/%s/%s/contents/.init" % (owner, REPO), {
            "message": "init", "content": init
        })
        print("已创建初始提交（用于初始化仓库）")

    # 2. 上传文件
    files = collect()
    print("待上传文件:", len(files))
    tree = []
    for i, (rel, full) in enumerate(files, 1):
        with open(full, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        blob, _ = api("POST", "/repos/%s/%s/git/blobs" % (owner, REPO), {
            "content": b64, "encoding": "base64"
        })
        tree.append({"path": rel, "mode": "100644", "type": "blob", "sha": blob["sha"]})
        if i % 20 == 0 or i == len(files):
            print("  已上传 %d/%d" % (i, len(files)))

    # 3. 建 tree / commit / 分支
    tree_res, _ = api("POST", "/repos/%s/%s/git/trees" % (owner, REPO), {"tree": tree})
    commit, _ = api("POST", "/repos/%s/%s/git/commits" % (owner, REPO), {
        "message": "翁法罗斯主题站 v1.0",
        "tree": tree_res["sha"],
    })
    try:
        api("POST", "/repos/%s/%s/git/refs" % (owner, REPO), {
            "ref": "refs/heads/" + BRANCH, "sha": commit["sha"]
        })
    except RuntimeError:
        api("PATCH", "/repos/%s/%s/git/refs/heads/%s" % (owner, REPO, BRANCH), {
            "sha": commit["sha"], "force": True
        })
    print("提交完成:", commit["sha"][:10])

    # 4. 开启 Pages
    try:
        page, _ = api("POST", "/repos/%s/%s/pages" % (owner, REPO), {
            "source": {"branch": BRANCH, "path": "/"}
        }, expect=(201, 409))
        print("Pages 已开启")
    except RuntimeError as e:
        print("Pages 开启失败（可在仓库设置里手动开）:", str(e)[:200])

    # 5. 等待构建
    url = "https://%s.github.io/%s/" % (owner, REPO)
    print("\n仓库地址: https://github.com/%s/%s" % (owner, REPO))
    print("页面地址:", url)
    for _ in range(20):
        time.sleep(6)
        try:
            with urllib.request.urlopen(url, timeout=15) as r:
                if r.status == 200:
                    print("页面已可访问 ✅")
                    break
        except Exception:
            pass
    else:
        print("Pages 还在构建，通常 1-2 分钟内生效")


if __name__ == "__main__":
    main()
