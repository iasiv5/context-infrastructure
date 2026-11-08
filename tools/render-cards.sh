#!/usr/bin/env bash
# 渲染 guizang 社交卡片（guizang-social-card-skill）的统一入口。
# 只做一件事：把字体缓存指进 workspace——沙箱对 ~/.cache 只读，直接渲染会
# EACCES 失败并回退成每次在线下载字体；缓存落盘后首次下载、之后离线秒渲。
# 用法：bash tools/render-cards.sh local-tests/<slug> [render.mjs 其余参数原样透传]
# 依赖：playwright / subset-font 从 DSH profile 顶层 node_modules 向上解析，
#       无需在 skill 根目录 npm install（那里在沙箱外，装了也要审批）。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_ROOT="${GUIZANG_CARD_SKILL:-$HOME/.dsh/profiles/web/node_modules/@iasiv5/dsh-skills/skills/guizang-social-card-skill}"
export GUIZANG_FONT_CACHE="${GUIZANG_FONT_CACHE:-$REPO_ROOT/.cache/guizang-fonts}"
mkdir -p "$GUIZANG_FONT_CACHE"
exec node "$SKILL_ROOT/scripts/render.mjs" "$@"
