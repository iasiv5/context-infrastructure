#!/usr/bin/env python3
"""external_skills overlay 一键安装 / 校验。

按 .github/deps.yml 声明，把主仓依赖的外部 skill clone 到
external_skills/<name>/ 约定路径，并可选 editable 安装其 CLI。

用法（repo 根目录, 任意 OS）:
  python tools/install_overlays.py            # 缺什么装什么，已存在的显示状态
  python tools/install_overlays.py --check    # 只校验不改动（退出码非 0 = 有缺失）
  python tools/install_overlays.py --proxy http://host:port   # 网络受限时注入代理

设计: manifest 与行为分离（deps.yml 是数据），网络可选注入（--proxy），
幂等（已 clone 的只 fetch 不 force，脏工作树只警告不动）。
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import yaml  # PyYAML
except ImportError:  # pragma: no cover
    print("缺少 PyYAML: pip install pyyaml 后重试", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent
DEPS = ROOT / ".github" / "deps.yml"
OVERLAY_DIR = ROOT / "external_skills"


def run(cmd: list[str], cwd: Path | None = None, proxy: str | None = None) -> subprocess.CompletedProcess:
    env_cmd = list(cmd)
    if proxy and cmd[0] == "git" and cmd[1] in {"clone", "fetch", "pull"}:
        env_cmd = ["git", "-c", f"http.proxy={proxy}"] + cmd[1:]
    return subprocess.run(env_cmd, cwd=cwd, check=False, capture_output=True, text=True, encoding="utf-8", errors="replace")


def is_git_repo(path: Path) -> bool:
    return (path / ".git").exists()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="只校验不改动")
    ap.add_argument("--proxy", help="给 git clone/fetch/pull 注入 http.proxy")
    ap.add_argument("--no-pip", action="store_true", help="跳过 pip editable 安装")
    args = ap.parse_args()

    deps = yaml.safe_load(DEPS.read_text(encoding="utf-8")) or {}
    packages = deps.get("packages") or []
    if not packages:
        print(f"[warn] {DEPS} 未声明任何 overlay")
        return 0

    OVERLAY_DIR.mkdir(exist_ok=True)
    missing = 0

    for pkg in packages:
        name, repo, branch = pkg["name"], pkg["repo"], pkg.get("branch", "master")
        target = OVERLAY_DIR / name
        print(f"== {name} ({repo})")

        if is_git_repo(target):
            head = run(["git", "rev-parse", "--short", "HEAD"], cwd=target).stdout.strip()
            dirty = run(["git", "status", "--porcelain"], cwd=target).stdout.strip()
            state = "dirty" if dirty else "clean"
            print(f"   已存在: {target} @ {head} ({state}) -- 跳过 clone")
        elif target.exists():
            print(f"   [warn] {target} 存在但不是 git 仓，请手动处理")
            missing += 1
            continue
        elif args.check:
            print(f"   [缺失] {target}")
            missing += 1
            continue
        else:
            r = run(["git", "clone", "--branch", branch, repo, str(target)], proxy=args.proxy)
            if r.returncode != 0:
                print(f"   [error] clone 失败:\n{r.stderr.strip()}")
                print(f"           网络受限可加 --proxy，如 --proxy http://L7IC.inventec.com.cn:3129")
                missing += 1
                continue
            print(f"   已 clone: {target} ({branch})")

        if pkg.get("pip") and not args.no_pip and not args.check:
            pip_target = ROOT / pkg["pip"]
            have = shutil.which("pip") or shutil.which("pip3")
            if not have:
                print("   [warn] 找不到 pip，跳过 editable 安装")
            else:
                r = run([sys.executable, "-m", "pip", "install", "-e", str(pip_target)])
                print("   pip -e 安装: " + ("OK" if r.returncode == 0 else f"失败\n{r.stderr.strip()[-300:]}"))

    if args.check:
        print(f"\n校验完成: {'全部就绪' if missing == 0 else f'{missing} 个 overlay 缺失'}")
        return 0 if missing == 0 else 1
    print("\n完成。overlay 路由文档见 rules/skills/*_local_overlay.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
