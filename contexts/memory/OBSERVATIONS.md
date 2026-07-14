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

或使用语义搜索做跨日期语义检索（安装 [semantic-search-skill](https://github.com/grapeot/semantic-search-skill)）。

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
🟡 Medium: [reflector 2026-06-19] ob-harness 子仓已由用户删除，以后不再出现。rules/WORKSPACE.md 的 openbmc-aware-harness 路由条目已移除（本地目录亦确认不存在）；OBSERVATIONS 中 06-04/06-09/06-13/06-15/06-18 的 ob-harness 记录转为历史归档，不再代表活跃项目。其中 06-18 的 confirmation banner（视觉强调与确认逻辑分离）模式有跨项目 CLI 复用价值，暂留观测、未晋升 skill。docs/specs 与 docs/plans 下的 ob-harness 设计文档作为历史归档保留，未改动。
Date: 2026-06-21

🟡 Medium: [项目里程碑] ob-harness V1.2 发布（子仓独立 git 仓库）。四条互锁主线：重构（§1-§7 物理分层 + 抽 5 个公共函数 + 清死代码，4200 行脚本重新可维护）、退出码协议统一（取消 exit0/exit2 混用、bitbake 码不再透传、领域函数层前提 1→3，修了 menu 把取消误报 Init succeeded 的 bug，统一到 0/2/3/1 四档）、从零搭起四层测试体系（protocol/unit/orchestration/integration + run_all + CI + 双核心层交叉覆盖 + multiset shellcheck baseline 防同类告警静默吸收）、ob-first 共识（ADR 0003 + bestpractice_06 skill + AGENTS.md 守卫 + usage↔dispatch 防漂移测试）。ob 从「能用」升级到「可被 agent 稳定依赖」。
🟡 Medium: [写作方法论] V1.2 发布文章采用「技术深度 + 故事门槛」双轨策略：`adhoc_jobs/2026/20260621-ob-harness-v1.2-release-未发表.md` 完整展开四条主线工程含量供固件同行深度阅读；`adhoc_jobs/2026/20260621-ob-harness-v1.2-release-故事版.md` 用「管家 ob」拟人化隐喻降低阅读门槛，面向破圈与公众号沟通。发文过程踩到「只看 release notes 漏掉 PR 工程含量、把系统性治理窄化成单一主题」的坑，完整教训已沉淀进 user memory（`ob-harness-v1.2-article.md`）。
🟡 Medium: [方法论/CLI 协议设计] V1.2 退出码 0/2/3/1 四档语义配合 exit 3 的 remedy line（如 `Run 'ob init romulus' first`），让 AI agent 按退出码区分「该重试」vs「该放弃」，是 CLI 工具为 agent 调用方专门设计稳定协议的实例，可作为后续 ob 或类似 CLI 工具设计的参考范式。
Date: 2026-06-30

🟡 Medium: [LLM cache billing 成本结构] `adhoc_jobs/2026/20260624-llm_cache_billing_analysis.md` 基于 ob-harness 41 个会话日志解释 AI 编程账单：5.75 亿输入 token 对 663 万输出 token，输入约为输出 87 倍；总体缓存命中率 93.6%，100 轮以上长会话命中率 94.4%，实际全额计费的新鲜输入约 3679.9 万 token。结论是长会话的高上下文依赖通过前缀缓存被显著摊薄，prompt caching 是当前重上下文 agent 工作流成本可承受的关键机制。

Date: 2026-07-03

🟡 Medium: [ob-harness 持续重构工作流文章产出] 今日 commit 7f896eb 新增三篇 ob-harness 持续重构工作流文章（`adhoc_jobs/2026/20260703-*`），用不同叙事角度拆解 pick-one-arch-task 工作流：（1）三个 Skill 串联的流水线——improve-codebase-architecture（浅模块发掘，删除测试法）→ grill-with-docs（逐个极端输入追问生成 ADR）→ writing-plans（分钟粒度执行计划）；（2）双 Agent 对抗验证——基于 1M 上下文让顾问 Agent 与主力 Agent 多轮 PK 消除逻辑漂移；（3）防回归结构锁——`grep -c 旧函数名` 断言为 0、bitbake 调用次数锁。核心论点是 prompt 只负责路由+约束（"只挑一条"），真正的智能在 skill，把架构决策从直觉搬进有纪律的流程。
🟢 Low: [SKILL_ECOSYSTEM 扩展] duck 哥 PR #48（6096677，07-02）把 open_router_data_scraper 纳入 skill ecosystem，延续前期的独立 skill 单体打包→生态索引迁移模式。
🟢 Low: [observer 扫描噪音排查] 本日全仓文件 LastWriteTime 集中在 10:56:08，系一次批量 checkout/clone 的时间戳归一，非真实内容变动；按 KB §2 指引须用 git log + 内容读取区分机械噪音与有效认知，本次真实变动仅 commit 7f896eb 与 6096677 两个提交。
Date: 2026-07-05

🟡 Medium: [框架工程资产新增] commit 48aed2c 新增 `adhoc_jobs/2026/20260704-harness-loop-engineering-diagram-zh.html` 与配套 `adhoc_jobs/2026/20260704-harness-loop-engineering-diagram.gif`，把 Prompt/Context/Harness/Loop Engineering 关系图沉淀为可复用可传播的可视化资产，延续 Harness Engineering 叙事从文字到图形表达的体系化推进。
🟢 Low: [observer 噪音过滤] 目标日期窗口内同时命中 `periodic_jobs/ai_heartbeat/state/heartbeat_status.json` 更新，该文件属于心跳运行态自动记账，不作为新认知写入观测主记录。

Date: 2026-07-12

🟡 Medium: [跨分叉分支 cherry-pick 的维护权属核查] 把 main 最近提交同步到严重分叉的 iasi 分支（iasi 领先 main 98 提交，main 领先 73）时，模块化大重构提交（如 731a3bb 拆 external writing、14cd828 拆 internal writing）会直接覆盖目标分支独有演进。核查方法：`git log <merge-base>..<branch> -- <file>` 确认目标分支分叉后是否动过该文件 + 检查作者权属。iasi 写作方法论文档（COMMUNICATION/workflow_*.md）经核查全是鸭哥（Yan Wang）提交、用户未维护，故直接 checkout main HEAD 对齐；INDEX.md 含用户自有 skill 条目需手动合并。决策模式已存 memory（iasi-writing-docs-align-main）。
🟡 Medium: [写作方法论文档对齐 main 模块化重构] commit f94993b 将 main 上鸭哥的 external/internal writing 模块化重构同步到 iasi：3 个 workflow/COMMUNICATION 文档对齐 main 最新版，新增 bestpractice_external_prose.md（外部文章文风手册）、reference_writing_thesis_catalog.md（L1-L8 分析视角）、bestpractice_internal_visuals.md（内部视觉组件规范）。main 重构方向是把臃肿单一 workflow 文件拆成「精简 workflow + 独立 bestpractice/reference 文件」，iasi 原为鸭哥早期未精炼版本。
🟢 Low: [SKILL_ECOSYSTEM 扩展] commit 1d176a2（cherry-pick 自 main 3a2e89b）把 innovation-assistant-skill 纳入 public skill ecosystem，定位为 SIT + Think Bigger 结构化创新流水线，延续独立 skill 单体打包→生态索引的扩展模式。
🟢 Low: [observer 噪音过滤] find -newermt 命中大量 adhoc_jobs/articles_archive 归档文件，系批量操作时间戳归一噪音（同 07-03 记录的归一现象），非真实内容变动；本次真实认知变动仅来自 07-12 会话的 cherry-pick + sync 工作。

Date: 2026-07-14

🟡 Medium: [合规科普] commit 2f936a6 新增欧盟 CRA（网络韧性法案）科普文章（`adhoc_jobs/2026/20260713-eu-cra-kepu.md`）。核心要点：安全责任从"出厂前测试"延伸到"产品全生命周期漏洞处理"；覆盖所有连网设备含独立芯片/固件/App；四项核心义务（出厂不带已知漏洞、提供安全更新至少 5 年、维护 SBOM 并跟踪漏洞影响、技术文件保存 10 年）；两个关键节点——2026-09-11 通报时钟开启（24h 早期预警 + 72h 正式报告）、2027-12-11 全面验牌（未贴 CE 标志不得进入欧盟市场）；罚款上限 1500 万欧元或全球营收 2.5%。与固件/BMC 安全领域直接相关，是 OpenBMC 产品出口欧洲需关注的合规背景。
🟢 Low: [observer 噪音过滤] 142 个文件命中 -newermt 窗口，但 141 个为 adhoc_jobs/articles_archive/scripts_archive/webpage 等归档目录的批量时间戳归一噪音，仅 commit 2f936a6 为真实内容变动。
