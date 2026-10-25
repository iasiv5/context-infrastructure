#!/usr/bin/env python3
"""check_repo_health.py — iasi fork 一键机械体检。

覆盖 bestpractice_forked_upstream_sync.md 验收清单中的机械项：

1. tracked .md 无遗留合并冲突标记（<<<<<<< / >>>>>>>；孤立 ======= 视为
   setext 标题不报，与硬标记同文件共存时才计为冲突残留）
2. rules/skills/INDEX.md 相对链接全部可解析
3. 同步基线锚点（OBSERVATIONS.md 最后一个「下次增量起点锚定」）真实存在、
   可达当前分支 HEAD；加 --post-sync 时进一步断言 origin/main 零领先
   （仅 merge 落地后立即跑才有意义）

语义抽查（fork 曾改文件 hunk 级是否重叠）不在脚本能力内，仍须人工。

仅用标准库；无 pip 的机器（DSH Linux 服务器）可直接跑：
    python3 tools/check_repo_health.py [--post-sync]
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

CONFLICT_HARD = re.compile(r"^<{7}(?: |$)|^>{7}(?: |$)", re.M)
CONFLICT_SEP = re.compile(r"^={7}\s*$", re.M)
MD_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
ANCHOR = re.compile(r"锚定\s+`?([0-9a-f]{7,40})`?")
INDEX_DEFAULT = Path("rules/skills/INDEX.md")
OBSERVATIONS = Path("contexts/memory/OBSERVATIONS.md")


def run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, capture_output=True, text=True, cwd=cwd)


def git(*args: str, cwd: Path | None = None) -> str:
    r = run("git", *args, cwd=cwd)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


def toplevel() -> Path:
    return Path(git("rev-parse", "--show-toplevel").strip())


def check_conflict_markers(root: Path) -> tuple[bool, list[str]]:
    """Check 1: tracked .md 无遗留冲突标记。"""
    problems: list[str] = []
    scanned = 0
    # -z：非 ASCII 路径不做八进制转义/加引号；cwd=root 保证相对路径基于仓库根
    tracked = git("ls-files", "-z", "--", "*.md", cwd=root).split("\0")
    for rel in filter(None, tracked):
        path = root / rel
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            problems.append(f"{rel}: 读取失败 {exc}")
            continue
        scanned += 1
        hard_lines = [
            f"{rel}:{i}" for i, line in enumerate(text.splitlines(), 1) if CONFLICT_HARD.search(line)
        ]
        if hard_lines:
            problems.extend(hard_lines)
        elif CONFLICT_SEP.search(text):
            problems.append(f"{rel}: 孤立 ======= 且同文件含 <<<<<<< / >>>>>>>，疑似冲突残留")
    detail = f"扫描 {scanned} 个 tracked .md"
    return not problems, problems + ([detail] if not problems else [])


def check_index_links(root: Path, index_rel: Path) -> tuple[bool, list[str]]:
    """Check 2: INDEX.md 相对链接可解析。"""
    index_path = root / index_rel
    if not index_path.is_file():
        return False, [f"INDEX 文件不存在: {index_rel}"]
    index_dir = index_path.parent
    missing: list[str] = []
    total = 0
    for target in MD_LINK.findall(index_path.read_text(encoding="utf-8")):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        total += 1
        resolved = (index_dir / target.split("#", 1)[0]).resolve()
        if not resolved.exists():
            missing.append(f"{index_rel}: 断链 -> {target}")
    detail = f"{total} 个相对链接全部可解析" if not missing else f"{len(missing)} 个断链"
    return not missing, missing + [f"{index_rel}: {detail}"]


def check_sync_anchor(root: Path, post_sync: bool) -> tuple[bool, list[str]]:
    """Check 3: 基线锚点存在、可达当前分支 HEAD；--post-sync 时要求 origin/main 零领先。"""
    obs = root / OBSERVATIONS
    if not obs.is_file():
        return False, [f"{OBSERVATIONS} 不存在，无法提取基线锚点"]
    anchors = ANCHOR.findall(obs.read_text(encoding="utf-8"))
    if not anchors:
        return False, [f"{OBSERVATIONS} 中没有「下次增量起点锚定」记录"]
    anchor = anchors[-1]
    problems: list[str] = []
    verify = run("git", "rev-parse", "--verify", "--quiet", f"{anchor}^{{commit}}")
    if verify.returncode != 0:
        return False, [f"锚点 {anchor} 不是有效提交（检查 {OBSERVATIONS} 末条记录）"]
    # 锚点是 fork 侧的 merge commit，不可能也不需要是 origin/main 的祖先；
    # 正确不变式：锚点可达当前分支 HEAD（防基线记错/记到别的分支）
    is_ancestor = run("git", "merge-base", "--is-ancestor", anchor, "HEAD")
    if is_ancestor.returncode != 0:
        problems.append(f"锚点 {anchor} 不可达当前分支 HEAD（基线记错或不在本分支）")
    ahead = git("rev-list", "--count", f"{anchor}..origin/main").strip()
    if post_sync and ahead != "0":
        problems.append(f"--post-sync：origin/main 领先锚点 {anchor} 共 {ahead} 个提交，基线未推进")
    detail = f"锚点 {anchor} 可达当前分支 HEAD，origin/main 领先 {ahead}"
    return not problems, problems + [detail]


def main() -> int:
    parser = argparse.ArgumentParser(description="iasi fork 机械体检（冲突标记 / INDEX 链接 / 同步基线）")
    parser.add_argument("--post-sync", action="store_true", help="merge 落地后立即跑：断言 origin/main 零领先于基线锚点")
    parser.add_argument("--index", type=Path, default=INDEX_DEFAULT, help="INDEX.md 路径（默认 rules/skills/INDEX.md）")
    args = parser.parse_args()

    try:
        root = toplevel()
    except RuntimeError as exc:
        print(f"[错误] 不在 git 仓库内：{exc}", file=sys.stderr)
        return 2

    checks = [
        ("冲突标记", check_conflict_markers(root)),
        ("INDEX 链接", check_index_links(root, args.index)),
        ("同步基线锚点", check_sync_anchor(root, args.post_sync)),
    ]

    failed = False
    for i, (name, (ok, lines)) in enumerate(checks, 1):
        status = "PASS" if ok else "FAIL"
        print(f"[{i}/{len(checks)}] {name}: {status}")
        for line in lines:
            print(f"  - {line}")
        failed |= not ok

    if failed:
        print("体检未通过：先解决以上 FAIL 项再提交/推送。")
        return 1
    print("体检通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
