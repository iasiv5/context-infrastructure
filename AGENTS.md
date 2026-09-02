# AGENTS.md - Your Workspace

This folder is home. Treat it that way.

## Every Session

Before doing anything else:

1. Read `rules/SOUL.md` — this is who you are
2. Read `rules/USER.md` — this is who you're helping
3. Read `rules/WORKSPACE.md` — file routing table, check before searching for files
4. Read `rules/COMMUNICATION.md` — how to think and communicate (especially for non-coding tasks)
5. Read `rules/skills/INDEX.md` — understand available skills
6. **检查 external skill overlays（强制）**：运行 `python tools/install_overlays.py --check`。退出码非 0 即表示有 overlay 缺失，必须先运行 `python tools/install_overlays.py` 补齐 clone 再开始任何依赖它的工作（公司内网 git clone 超时加 `--proxy http://L7IC.inventec.com.cn:3129`）。**写作任务在检查通过前视为阻塞**：`rules/skills/` 下的写作 skill 只是转发桩，真正内容在本地 clone `external_skills/writing-skill/`；新机器 clone 主仓后该目录默认不存在，不补齐就没有写作 skill 可触发。

## Multi-Agent Nudge

This harness can delegate work to multiple sub-agents. You don't need to use them by default, but keep the capability in mind for tasks that are large, parallelizable, research-heavy, or benefit from independent cross-checking.

Before using sub-agents, read `rules/skills/workflow_parallel_subagents.md`. The current OpenCode pattern is `multi_tool_use.parallel` wrapping multiple `functions.task` calls in the same assistant message.

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

**写文章 / 公众号 / 外部文档** → 读 `rules/skills/writing_skill_local_overlay.md`
- 极度重要：严禁 AI 直接输出最终文章。只要用户要求“写短文”、“写公众号”、“写锐评”，必须先读取该文件以接入 external writing workflow。
- 若 `external_skills/writing-skill/` 不存在（新机器常见），先跑 `python tools/install_overlays.py` 补齐，再按 overlay 路由读取完整 skill。

**深度调研任务** → `rules/skills/workflow_deep_research_survey.md`
- 初步扫描 → 分割维度 → 多 Agent 并行 → 交叉验证 → 写报告
- 输出：`contexts/survey_sessions/`

**调用后台 Agent / 并行 Subagent** → `rules/skills/workflow_parallel_subagents.md`
- 何时拆分任务、什么时候不要拆、如何并行派出多个 subagent
- 准备调用多个 `functions.task` 前，先把这个 skill 读一遍再执行
- 当前并行方式是 `multi_tool_use.parallel`；不要使用旧 `run_in_background` / `background_output` 写法

**merge main to iasi branch** → `rules/skills/bestpractice_forked_upstream_sync.md`
- 先读这个 bp 再执行同步；即使判断 already-up-to-date 也不能短路
- merge 完成后**必须**跑一遍 overlay refresh（见 `rules/skills/bestpractice_external_skill_overlay.md`）：`cd external_skills/<repo> && git pull && pip install -e .`

## Axioms（公理）

从个人经历提炼的决策原则，用于启发深度思考。分类索引、使用指南和触发词见 `rules/axioms/INDEX.md`。

## Sub-agent 模型路由

不同工具有各自的 subagent 机制和模型选择策略。当前主用 GitHub Copilot，偶尔用 Claude Code：

- **GitHub Copilot**：subagent 由 Copilot 自动调度，无需手动配置路由
- **Claude Code**：如需指定模型或并行 subagent，参考自身配置文件

创意性工作（brainstorm、文章结构、观点碰撞）可考虑在后台跑一个独立 agent，与主线程并行推进。

## 高能力模型工作模式

当使用高能力模型（如 Opus、Sonnet 等）时，注意 token 预算的合理分配：

- **设计**：拆分问题、设计计划、分配 sub-agent 任务
- **质量把关与写作**：最终文本自己写，sub-agent 结果自己验证
- **调研和数据处理**：交给 sub-agent 执行

核心原则：把 token 预算集中在只有高能力模型才能做好的事情上，常规执行类工作交给 sub-agent。

## Memory System（记忆系统）

三层记忆架构：
- **L3（全局约束）**：`rules/` 下的所有文件，每次 session 被动加载
- **L1/L2（动态记忆）**：`contexts/memory/OBSERVATIONS.md`，agent 主动检索
- **自动积累**：`periodic_jobs/ai_heartbeat/` 保留 observer（L1，当天观测）与 reflector（L2，每周反思）两种任务；默认由 SessionStart hook 按到期状态提醒，真正的执行入口是当前 chat 中的 `/ai-heartbeat`，cron 只是可选增强

## Safety

- Don't exfiltrate private data. Ever.
- Don't run destructive commands without asking.
- When in doubt, ask.