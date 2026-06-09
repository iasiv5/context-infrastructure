# Memory Observations

这是三层记忆系统的动态记忆日志。observer 会把当天观测追加到这里；reflector 会回看这里的近期内容，清理低价值项，并据此产出规则晋升与报告。默认触发方式是 SessionStart hook 在会前提醒用户于当前 chat 显式运行 `/ai-heartbeat`，observer / reflector 的状态由 `heartbeat_status_cli.py` 自动记账。

## 格式说明

每个日期条目格式如下：

```raw
Date: YYYY-MM-DD

🔴 High: [方法论/约束] 描述
🟡 Medium: [项目状态/决策] 描述
🟢 Low: [任务流水] 描述
```

### 优先级定义

- **🔴 High**：跨项目通用的经验教训、硬性约束、影响系统架构的重大决策。永久保留，候选晋升为 axiom 或 skill。
- **🟡 Medium**：活跃项目的关键进展、技术决策背景、未来几周仍需参考的信息。
- **🟢 Low**：日常任务流水、瞬时 debug 记录、临时上下文。定期垃圾回收。

## 如何加载记忆

不要全文加载这个文件（可能很大）。按需检索：

```bash
# 搜索特定主题
grep -n "关键词" contexts/memory/OBSERVATIONS.md

# 搜索最近 N 天
grep -A 20 "Date: $(date -v-7d +%Y-%m-%d)" contexts/memory/OBSERVATIONS.md
```

或使用语义搜索（`rules/skills/semantic_search.md`）做跨日期语义检索。

---

<!-- 以下是记录区域，由 /ai-heartbeat 追加与整理 -->

Date: 2026-05-27

🟡 Medium: 图片生成能力从 workspace 内置 skill 拆分为独立 public repo `grapeot/image-generation-skill`。删除了 `rules/skills/generate_image.md`、`tools/generate_image.py` 及测试，改为在 `docs/SKILL_ECOSYSTEM.md` 引用。这是 skill 管理从单体打包向生态系统模型迁移的延续，已有 Tavily、Stripe、PPTX 等多个 skill 走了同样的路径。
🟡 Medium: 新增 PQC（后量子密码）芯片安全文章 `adhoc_jobs/2026/20260526-pqc-chip-security-foundation.md`，覆盖 NIST FIPS 203/204/205、Caliptra 2.0 RTL 冻结集成 ML-KEM/ML-DSA、ASPEED AST2700 BMC SoC 的 PQC 落地方案。文章定位在固件安全与新密码标准交汇点，与 iasi 的固件专家身份高度契合。

Date: 2026-05-29

🔴 High: openbmc-aware-harness 子项目作为独立 Git 仓库完成种子态骨架搭建。核心决策是采用"先高保真迁移 context infrastructure 骨架，再做第一轮收敛到 OpenBMC 语境"的双阶段路线，第一版排除 periodic_jobs 和 tools。设计文档 `docs/specs/2026-05-29-openbmc-aware-harness-design.md`，实施计划 `docs/plans/2026-05-29-openbmc-aware-harness-implementation-plan.md`。子仓已有独立 AGENTS.md、CLAUDE.md、rules/、docs/、contexts/memory/OBSERVATIONS.md，启动链路自洽。这是 context infrastructure 从个人 workspace 向领域专用可发布仓库迁移的第一个实例，验证了整个骨架的可移植性。
🟡 Medium: 新增 Harness Engineering 文章 `adhoc_jobs/2026/20260528-harness-engineering-copilot-verified.md`，将 Anthropic 七层扩展模型（CLAUDE.md / Hooks / Skills / Plugins / MCP / LSP / Subagents）对应到 VS Code + GitHub Copilot Chat 的落地路径，并给出固件团队的具体实施顺序。配套社交卡片项目 `adhoc_jobs/2026/social_card_harness_engineering/`。

Date: 2026-05-30

🔴 High: AI Heartbeat 已完成架构收口：当前 chat 中的 `/ai-heartbeat` 是唯一主执行入口，SessionStart hook 仅做 reminder，observer / reflector 的 due 判定与状态回写统一收敛到 `heartbeat_preflight.py` 和 `heartbeat_status_cli.py`；相关实现与 `AGENTS.md`、`README.md`、`setup_guide.md`、`docs/CRONTAB.md`、`periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md`、`periodic_jobs/ai_heartbeat/docs/PRD.md` 已对齐。

Date: 2026-05-31

🔴 High: AI Heartbeat 的执行合同从“架构收口”继续落到状态语义闭环：`.github/prompts/ai-heartbeat.prompt.md` 现在是唯一执行入口，`heartbeat_preflight.py --command-spec` 在命令侧显式忽略 `last_prompted_on`，所以 SessionStart hook 的同日提醒去重不会屏蔽用户手动运行 `/ai-heartbeat`；同时 `heartbeat_state.collect_due_tasks()` 把同一 `target_date` 的 `skipped` 视为已处理，observer 因幂等跳过后不会继续被判定为 due。
🟡 Medium: AI Heartbeat 的逻辑日期已切到本地时区，`target_date` 与 `last_prompted_on` 以本地日期记账，UTC 只保留给 attempt/success 时间戳；相关测试已经覆盖本地逻辑日期、same-day skipped、以及 reminder-only hook 的命令侧合同。
🟡 Medium: SessionStart hook 现在稳定为 reminder-only 的两步语义：`知道了` 不改状态，`今天不再提醒` 才写 `last_prompted_on`。提醒去重与执行状态因此解耦，用户同一天手动补跑 `/ai-heartbeat` 不会被错误地判成 `none`。
Date: 2026-06-01

🟢 Low: AI Heartbeat 6 月 1 日运行确认：`reminder_policy.json` schema 不变；`--command-spec` 返回 `observer_and_reflector`；`pre-session.ps1` text reminder 机制与测试链通过 seam 驱动验证正常。

Date: 2026-06-04

🔴 High: AI Heartbeat 完成跨平台重构的主仓库侧迁移。`.github/prompts/ai-heartbeat.prompt.md` 从厚文件（~100 行）瘦身为薄壳（~22 行），只保留 OS 探测 + SOP 引用；独立 `periodic_jobs/ai_heartbeat/docs/AI_HEARTBEAT_SOP.md` 成为执行合同单一事实来源；新增 `.claude/commands/ai-heartbeat.md` 作为 Claude Code 入口。两个平台入口共享同一份 SOP，消除了平台耦合和内容重复。首次验证了"子仓库先行重构→主仓库跟进迁移"的跨仓知识同步模式。
🟡 Medium: openbmc-aware-harness 子仓库经历密集演进周期（6 月 2-3 日）。已完成：ob 脚本从 `tools/ob` 迁移至仓库根目录并新增 machine 校验关卡与 single-source lock（`openbmc-source.lock`）；rules 体系加数字前缀统一加载顺序，删除 5 个低价值 skill（净减 895 行）；README 重写为人类使用手册；文档一致性清理补齐路由表和幽灵路径。

Date: 2026-06-09

🔴 High: ob-harness 子仓经历从 06-04 到 06-09 的爆发式开发周期（40+ commits），仓库名从 `openbmc-aware-harness` 简化为 `ob-harness`。核心能力演进：`ob init` 增加了本地镜像加速克隆、智能 clone URL 路由（HTTPS→SSH 自动检测）、DL_DIR/git2 bare mirror 缓存、WSL 自动并行度调优（`??=` → `?=` 覆盖 OE-core 默认值）、machine 选择 Y/N 确认；`ob build` 全新实现，含 init-done 标记、三遍醒目 machine 确认、glob 匹配构建状态检测；`ob status` 重构为三段式总览面板（环境、源、构建时间）；`ob` 交互菜单模式全量实现。这是 context infrastructure 骨架迁移到领域专用工具链后第一次大规模验证——骨架的可移植性和可演进性得到实战确认。
🟡 Medium: 主仓 `_context-infrastructure` 在 06-04 至 06-07 期间通过 10 个 PR 持续扩展 SKILL_ECOSYSTEM：新增 Google Maps 路由 skill、Circle Post 社交发布 skill、PDF-to-Markdown CLI skill、delayed agent jobs 路由、OpenCode subagent 模型路由更新。技能生态从"仓库内打包"向"独立 repo + ecosystem registry"的迁移模式持续验证。
🟡 Medium: iasi 插件体系（`m/plugins/iasi/`）新增四个 skills：brainstorming、writing-plans、handoff、cleanup；同步向 ob-harness 子仓分发 brainstorming 和 writing-plans。所有新增 skill 均标注 obra/superpowers 致敬和 MIT 许可证（ATTRIBUTIONS.md），建立了规范的开源致谢流程。