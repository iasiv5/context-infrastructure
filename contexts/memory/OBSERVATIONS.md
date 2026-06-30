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

🔴 High: AI Heartbeat 状态语义闭环完成：执行入口收敛到 `.github/prompts/ai-heartbeat.prompt.md`，`--command-spec` 忽略 `last_prompted_on`，`collect_due_tasks()` 视 `skipped` 为已处理。本地时区切日、reminder-only 两步语义、same-day skipped 测试均已覆盖。

Date: 2026-06-04

🔴 High: AI Heartbeat 完成跨平台重构的主仓库侧迁移。薄壳入口引用独立 SOP，Claude Code 入口共享同一份合同。首次验证"子仓库先行重构→主仓库跟进迁移"的跨仓知识同步模式。
🟡 Medium: 主仓 06-04 至 06-07 持续扩展 SKILL_ECOSYSTEM（10 个 PR）：新增 Google Maps 路由、Circle Post 社交发布、PDF-to-Markdown CLI、delayed agent jobs 路由等。
🟡 Medium: iasi 插件体系新增 brainstorming、writing-plans、handoff、cleanup 四个 skills，均标注 obra/superpowers 致敬和 MIT 许可证。

Date: 2026-06-09

🔴 High: ob-harness 子仓经历 06-02 到 06-09 的爆发式开发周期（40+ commits），仓库名从 `openbmc-aware-harness` 简化为 `ob-harness`。期间完成：ob 脚本迁至根目录、machine 校验关卡与 single-source lock、rules 数字前缀统一、README 重写为人类手册。核心能力演进：`ob init` 增加镜像加速克隆、HTTPS→SSH 自动检测、bare mirror 缓存、WSL 并行度调优；`ob build` 全新实现（init-done 标记、三遍 machine 确认）；`ob status` 三段式总览；`ob` 交互菜单。context infrastructure 骨架的可移植性和可演进性得到实战确认。

Date: 2026-06-13

🔴 High: ob-harness V1.1 完成开发与发布，新增 `ob start-qemu` 和 `ob stop-qemu`，把 BMC 镜像的 QEMU 仿真启停纳入 `ob` 工作台。核心设计决策：（1）QB 变量通过 `bitbake -e` 解析不做 fallback（ADR 0002），架构由 `QB_SYSTEM_NAME` 自动区分 AST2600/AST2700；（2）QEMU binary URL 配置化落盘到 `workspace/qemu-bin/`，按 source_label × 架构索引；（3）community 源通过比对 Jenkins `lastSuccessfulBuild` build number 提示更新，custom 源首次交互输入后持久化复用；（4）PID 文件记录进程信息防误杀，端口冲突前置检测。`ob` 覆盖 init / build / start-qemu / stop-qemu 完整开发回路。
🟡 Medium: ob-harness 新增 npm 网络超时 bestpractice skill（`bestpractice_05-npm_network_timeout_in_yocto.md`），`ob build` 已内置 npm 注册表自动探测（并行测试 npmjs.org 与 npmmirror.com）、600 秒超时参数注入和 24 小时探测缓存。Skills INDEX 更新至 5 个 skill 条目。
🟡 Medium: 完成 BU6 第二轮内部技术分享会 PPT 稿《Agent Harness 工程：固件开发工作流的蒸馏与固化》（`adhoc_jobs/2026/20260612-Agent Harness 工程： 固件开发工作流的蒸馏与固化.md`），定位在从"AI 能生成代码"到"AI 能按固件流程交付"之间的 Harness 概念压实。配套 release note 文章 V1.1 已产出。

Date: 2026-06-15

🔴 High: [internal-writing skill 三层构架落地] rules/skills/workflow_internal_writing.md 经三连 PR（#30-#32）引入视觉认知负载完整方法论体系。三条核心公理：（1）Visual 是 bandwidth 工具不是装饰；（2）Adaptive 优于静态；（3）MD-first + HTML 优化层。配套前置 gate/后置 gate/武器库/delta 对照表/HTML-in-MD 试验规则。
🟡 Medium: [Harness 演讲稿完整产出] 完成 BU6 第二轮分享会演讲稿（adhoc_jobs/2026/20260614-演讲稿.MD），13 页逐页讲稿，核心叙事线覆盖 AI 缺固件上下文、三条路径、Harness 两层结构、固化四层级、ob-harness、Venice OTS 三个月数据、质量写进平台。
🟡 Medium: [GLM-5.2 上下文窗口探测工具] 新增 adhoc_jobs/2026/20260613-ctx_window_probe.py，零依赖实测 GLM-5.2 最大输入上下文，区分上下文超限与 HTTP 413，锚点优先 + 二分精扫。
🟡 Medium: [ob-harness QEMU SSH host key 自动清理] ob start-qemu 主动检测并清理陈旧 SSH known_hosts host key（ee4c7ff），解决 QEMU 重启后连接被拒问题。
🟡 Medium: [Skills 跨仓同步] 从 main 同步 compressor skill、SOUL 自主执行契约和 docling macOS CPU workaround 至 iasi 分支。

Date: 2026-06-18

🟡 Medium: ob-harness 把 destructive confirmations 的视觉层统一成 confirmation banner：`ob` 新增 `print_confirm_banner` 纯展示函数，替换 build/init/start-qemu/update community QEMU binary 四处手写块，并补齐 kill-and-restart 与 stop-qemu 两个缺口；确认循环、`--force` 分支和退出语义保持原样。`CONTEXT.md` 与实施计划同步把 banner 定义为“只负责视觉强调，不承载确认逻辑”的术语。
🟡 Medium: Harness Engineering 内部演讲稿收敛成 14 页版本，主线固定为 inner/outer harness、蒸馏与固化、四层固化路径、ob-harness 工作台与 Venice 试点数据。分享重点已经从“AI 会不会写代码”转向“如何把固件经验写进平台与流程”，这是当前专案叙事的明显收口。

Date: 2026-06-19

🔴 High: [observer 扫描方法论与实际环境脱节，已于本次 reflector 修正 KNOWLEDGE_BASE §2] 两处实测发现：(1) Windows git-bash 下 `find -mtime -N` 静默漏报——本次 `-mtime -1` 返回空，而 `-newermt "2026-06-17 00:00"` 正常命中 06-18 的演讲稿等文件；KB §2.1 推荐的扫描示例 `-mtime -1` 在本环境不可靠，observer/reflector 扫描应统一改用 `-newermt`。(2) KB §2.2/2.3 列为扫描白名单的 `contexts/blog/content/` 与 `contexts/life_record/*.csv` 在本仓不存在（`contexts/` 实际只有 daily_records/memory/survey_sessions/thought_review，WORKSPACE.md 也未收录这两条路径）。这两点已于本次 reflector 修正进 KNOWLEDGE_BASE §2.1（mtime→newermt）与 §2.2/2.3（白名单路径加存在性注记）。
🟢 Low: 主仓处于沉淀期——自 06-18 observer 以来无新独立认知变动，唯一实质内容变动是 Harness Engineering 演讲稿经 commit a99f1f3（删旧版、加最终版）落盘定稿，其 14 页叙事与结构已由 06-18 条目覆盖，本次不重复记录。
🟡 Medium: [reflector 2026-06-19] ob-harness 子仓已由用户删除，以后不再出现。rules/WORKSPACE.md 的 openbmc-aware-harness 路由条目已移除（本地目录亦确认不存在）；OBSERVATIONS 中 06-04/06-09/06-13/06-15/06-18 的 ob-harness 记录转为历史归档，不再代表活跃项目。其中 06-18 的 confirmation banner（视觉强调与确认逻辑分离）模式有跨项目 CLI 复用价值，暂留观测、未晋升 skill。docs/specs 与 docs/plans 下的 ob-harness 设计文档作为历史归档保留，未改动。
Date: 2026-06-21

🟡 Medium: [项目里程碑] ob-harness V1.2 发布（子仓独立 git 仓库）。四条互锁主线：重构（§1-§7 物理分层 + 抽 5 个公共函数 + 清死代码，4200 行脚本重新可维护）、退出码协议统一（取消 exit0/exit2 混用、bitbake 码不再透传、领域函数层前提 1→3，修了 menu 把取消误报 Init succeeded 的 bug，统一到 0/2/3/1 四档）、从零搭起四层测试体系（protocol/unit/orchestration/integration + run_all + CI + 双核心层交叉覆盖 + multiset shellcheck baseline 防同类告警静默吸收）、ob-first 共识（ADR 0003 + bestpractice_06 skill + AGENTS.md 守卫 + usage↔dispatch 防漂移测试）。ob 从「能用」升级到「可被 agent 稳定依赖」。
🟡 Medium: [写作方法论] V1.2 发布文章采用「技术深度 + 故事门槛」双轨策略：`adhoc_jobs/2026/20260621-ob-harness-v1.2-release-未发表.md` 完整展开四条主线工程含量供固件同行深度阅读；`adhoc_jobs/2026/20260621-ob-harness-v1.2-release-故事版.md` 用「管家 ob」拟人化隐喻降低阅读门槛，面向破圈与公众号沟通。发文过程踩到「只看 release notes 漏掉 PR 工程含量、把系统性治理窄化成单一主题」的坑，完整教训已沉淀进 user memory（`ob-harness-v1.2-article.md`）。
🟡 Medium: [方法论/CLI 协议设计] V1.2 退出码 0/2/3/1 四档语义配合 exit 3 的 remedy line（如 `Run 'ob init romulus' first`），让 AI agent 按退出码区分「该重试」vs「该放弃」，是 CLI 工具为 agent 调用方专门设计稳定协议的实例，可作为后续 ob 或类似 CLI 工具设计的参考范式。
🟢 Low: [任务流水] 顺势修订 `20260612-ob-harness-v1.1-release.md` 并提交到 adhoc_jobs 子仓 iasi 分支（commit 7d903bc）。
Date: 2026-06-30

🔴 High: [external-writing skill 升级] `rules/skills/workflow_external_writing.md` 已把 external-facing 写作收敛为更严格的两遍写作与认知负担流程：主线程负责 thesis、结构、删减和验收；`writer_deepseek`/DeepSeek Pro 负责第一遍成稿与第二遍语言层重写；当读者反馈看不懂时，先砍信息和重组疑问链，再做语言重写。新增的关键门控包括非专家能复述 thesis、一个 section 只放一个核心判断加一个具体故事、砍掉比添加更重要、禁止 taxonomy 宣布和机械承接词。
🟡 Medium: [1M context 双 Agent 协作范式] `adhoc_jobs/2026/20260622-context_1m_workflow_upgrade.md` 记录了 GLM-5.2 Max 1M 主力 Agent 与 Copilot/Opus 1M 顾问 Agent 的闭环协作：`/brainstorming` 或 `/grill-with-docs` 做前置澄清，`/writing-plans` 输出实施计划，再通过多轮对抗评审、反驳和再校准把方案收敛到可执行状态。核心变化是超长上下文让人从频繁补记忆和裁决，转向最终品味判断与验收。
🟡 Medium: [LLM cache billing 成本结构] `adhoc_jobs/2026/20260624-llm_cache_billing_analysis.md` 基于 ob-harness 41 个会话日志解释 AI 编程账单：5.75 亿输入 token 对 663 万输出 token，输入约为输出 87 倍；总体缓存命中率 93.6%，100 轮以上长会话命中率 94.4%，实际全额计费的新鲜输入约 3679.9 万 token。结论是长会话的高上下文依赖通过前缀缓存被显著摊薄，prompt caching 是当前重上下文 agent 工作流成本可承受的关键机制。