# AGENTS.md - Your Workspace

This folder is home. Treat it that way.

## Every Session

Before doing anything else:

1. Read `rules/SOUL.md` — this is who you are
2. Read `rules/USER.md` — this is who you're helping
3. Read `rules/WORKSPACE.md` — file routing table, check before searching for files
4. Read `rules/COMMUNICATION.md` — how to think and communicate (especially for non-coding tasks)
5. Read `rules/skills/INDEX.md` — understand available skills

Don't ask permission. Just do it.

## SessionStart Hook: AI Heartbeat

AI Heartbeat 的会前提醒由 `.github/hooks/pre-session.ps1` 直接处理。SessionStart hook 会在新会话开始时自动执行 `heartbeat_preflight.py`，检查 observer / reflector 是否到期并给出提醒。Windows 默认弹窗提醒；若仓库 policy 关闭弹窗，则显示一个 8.88 秒自动消失的轻提醒窗，点击后复制 `/ai-heartbeat`。如果需要处理，在当前 chat 中运行 `/ai-heartbeat`。

## File Routing

**找文件时，先查 `rules/WORKSPACE.md`，再搜索。** WORKSPACE.md 是这个 workspace 的目录索引，记录了每类内容的存放位置。绝大多数情况下查一下就能定位到目标目录，不需要全盘 glob/grep。如果发现新目录或项目没被收录，顺手更新 WORKSPACE.md。

## Skills

**Skills** 是 AI 可复用的能力，包括工作流、API 指南、最佳实践等。

**重要：遇到"怎么做 X"时，先查 skill 再查系统工具。** 搜索顺序：(1) 下方速查表 → (2) `rules/skills/INDEX.md` → (3) 系统工具。

**需要执行某项任务** → 先查 `rules/skills/INDEX.md` 找到对应的 skill  
**想添加新能力** → 参考现有 skill 格式，更新 INDEX.md

### 常用 Skill 速查（以 INDEX.md 为准）

**深度调研任务** → `rules/skills/workflow_deep_research_survey.md`  
- 初步扫描 → 分割维度 → 多 Agent 并行 → 交叉验证 → 写报告  
- 输出：`contexts/survey_sessions/`

**调用后台 Agent / 并行 Subagent** → `rules/skills/workflow_parallel_subagents.md`  
- 何时拆分任务、如何并行派出多个 subagent  
- 准备使用并行 subagent 前，先把这个 skill 读一遍
- 派出 agent 后等系统通知即可，不需要轮询

## Axioms（公理）

从个人经历提炼的决策原则，用于启发深度思考。分类索引、使用指南和触发词见 `rules/axioms/INDEX.md`。

## Sub-agent 模型路由

不同工具有各自的 subagent 机制和模型选择策略。当前主用 GitHub Copilot，偶尔用 Claude Code：