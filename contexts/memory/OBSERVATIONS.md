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
🟡 Medium: [reflector 2026-06-19] ~~ob-harness 子仓已由用户删除，以后不再出现。~~ **⚠️ 已被 07-20~08-06 后续观测推翻：ob-harness 在 07-20 起恢复活跃开发（07-30 know-how 优化、07-31 GDD、08-02 内置 Goal-Driven、08-05 互检均在该子仓），本条"不再出现"判断失效。** 保留此条仅因其附带的"06-18 confirmation banner（视觉强调与确认逻辑分离）模式有跨项目 CLI 复用价值"的观察仍成立；但不要据此认为 ob-harness 已废弃。06-04/06-09/06-13/06-15/06-18 的早期记录应与 07-20+ 后续记录连读方可还原项目全貌。
Date: 2026-06-21

🟡 Medium: [项目里程碑] ob-harness V1.2 发布（子仓独立 git 仓库）。四条互锁主线：重构（§1-§7 物理分层 + 抽 5 个公共函数 + 清死代码，4200 行脚本重新可维护）、退出码协议统一（取消 exit0/exit2 混用、bitbake 码不再透传、领域函数层前提 1→3，修了 menu 把取消误报 Init succeeded 的 bug，统一到 0/2/3/1 四档）、从零搭起四层测试体系（protocol/unit/orchestration/integration + run_all + CI + 双核心层交叉覆盖 + multiset shellcheck baseline 防同类告警静默吸收）、ob-first 共识（ADR 0003 + bestpractice_06 skill + AGENTS.md 守卫 + usage↔dispatch 防漂移测试）。ob 从「能用」升级到「可被 agent 稳定依赖」。
🟡 Medium: [写作方法论] V1.2 发布文章采用「技术深度 + 故事门槛」双轨策略：`adhoc_jobs/2026/20260621-ob-harness-v1.2-release-未发表.md` 完整展开四条主线工程含量供固件同行深度阅读；`adhoc_jobs/2026/20260621-ob-harness-v1.2-release-故事版.md` 用「管家 ob」拟人化隐喻降低阅读门槛，面向破圈与公众号沟通。发文过程踩到「只看 release notes 漏掉 PR 工程含量、把系统性治理窄化成单一主题」的坑，完整教训已沉淀进 user memory（`ob-harness-v1.2-article.md`）。
🟡 Medium: [方法论/CLI 协议设计] V1.2 退出码 0/2/3/1 四档语义配合 exit 3 的 remedy line（如 `Run 'ob init romulus' first`），让 AI agent 按退出码区分「该重试」vs「该放弃」，是 CLI 工具为 agent 调用方专门设计稳定协议的实例，可作为后续 ob 或类似 CLI 工具设计的参考范式。
Date: 2026-06-30

🟡 Medium: [LLM cache billing 成本结构] `adhoc_jobs/2026/20260624-llm_cache_billing_analysis.md` 基于 ob-harness 41 个会话日志解释 AI 编程账单：5.75 亿输入 token 对 663 万输出 token，输入约为输出 87 倍；总体缓存命中率 93.6%，100 轮以上长会话命中率 94.4%，实际全额计费的新鲜输入约 3679.9 万 token。结论是长会话的高上下文依赖通过前缀缓存被显著摊薄，prompt caching 是当前重上下文 agent 工作流成本可承受的关键机制。

Date: 2026-07-03

🟡 Medium: [ob-harness 持续重构工作流文章产出] commit 7f896eb 新增三篇 ob-harness 持续重构工作流文章（`adhoc_jobs/2026/20260703-*`），用不同叙事角度拆解 pick-one-arch-task 工作流：（1）三个 Skill 串联的流水线——improve-codebase-architecture（浅模块发掘，删除测试法）→ grill-with-docs（逐个极端输入追问生成 ADR）→ writing-plans（分钟粒度执行计划）；（2）双 Agent 对抗验证——基于 1M 上下文让顾问 Agent 与主力 Agent 多轮 PK 消除逻辑漂移；（3）防回归结构锁——`grep -c 旧函数名` 断言为 0、bitbake 调用次数锁。核心论点是 prompt 只负责路由+约束（"只挑一条"），真正的智能在 skill，把架构决策从直觉搬进有纪律的流程。
🟡 Medium: [SKILL_ECOSYSTEM 持续扩展] 06-04 至 07-14 期间持续把独立 skill 单体打包纳入 `docs/SKILL_ECOSYSTEM.md` 索引（如 Google Maps 路由、Circle Post、PDF-to-Markdown、delayed agent jobs、open_router_data_scraper、innovation-assistant 等），延续"独立 skill repo → 生态索引"的扩展模式。单条 PR 不再单独记录。

Date: 2026-07-05

🟡 Medium: [框架工程资产新增] commit 48aed2c 新增 `adhoc_jobs/2026/20260704-harness-loop-engineering-diagram-zh.html` 与配套 `adhoc_jobs/2026/20260704-harness-loop-engineering-diagram.gif`，把 Prompt/Context/Harness/Loop Engineering 关系图沉淀为可复用可传播的可视化资产，延续 Harness Engineering 叙事从文字到图形表达的体系化推进。

Date: 2026-07-12

🟡 Medium: [跨分叉分支 cherry-pick 的维护权属核查] 把 main 最近提交同步到严重分叉的 iasi 分支（iasi 领先 main 98 提交，main 领先 73）时，模块化大重构提交（如 731a3bb 拆 external writing、14cd828 拆 internal writing）会直接覆盖目标分支独有演进。核查方法：`git log <merge-base>..<branch> -- <file>` 确认目标分支分叉后是否动过该文件 + 检查作者权属。iasi 写作方法论文档（COMMUNICATION/workflow_*.md）经核查全是鸭哥（Yan Wang）提交、用户未维护，故直接 checkout main HEAD 对齐；INDEX.md 含用户自有 skill 条目需手动合并。决策模式已晋升为 skill `rules/skills/bestpractice_forked_upstream_sync.md` 并存 memory（iasi-forked-upstream-sync）。
🟡 Medium: [写作方法论文档对齐 main 模块化重构] commit f94993b 将 main 上鸭哥的 external/internal writing 模块化重构同步到 iasi：3 个 workflow/COMMUNICATION 文档对齐 main 最新版，新增 bestpractice_external_prose.md（外部文章文风手册）、reference_writing_thesis_catalog.md（L1-L8 分析视角）、bestpractice_internal_visuals.md（内部视觉组件规范）。main 重构方向是把臃肿单一 workflow 文件拆成「精简 workflow + 独立 bestpractice/reference 文件」，iasi 原为鸭哥早期未精炼版本。

Date: 2026-07-14

🟡 Medium: [合规科普] commit 2f936a6 新增欧盟 CRA（网络韧性法案）科普文章（`adhoc_jobs/2026/20260713-eu-cra-kepu.md`）。核心要点：安全责任从"出厂前测试"延伸到"产品全生命周期漏洞处理"；覆盖所有连网设备含独立芯片/固件/App；四项核心义务（出厂不带已知漏洞、提供安全更新至少 5 年、维护 SBOM 并跟踪漏洞影响、技术文件保存 10 年）；两个关键节点——2026-09-11 通报时钟开启（24h 早期预警 + 72h 正式报告）、2027-12-11 全面验牌（未贴 CE 标志不得进入欧盟市场）；罚款上限 1500 万欧元或全球营收 2.5%。与固件/BMC 安全领域直接相关，是 OpenBMC 产品出口欧洲需关注的合规背景。

Date: 2026-07-16

🟡 Medium: [外部写作体系重构 + Antigravity CLI 接入] commit 9aee80c 大规模重构外部写作 skill 矩阵：新增 `rules/skills/antigravity_cli.md`（Antigravity CLI 即 `agy` 文件式调用 guide，区分 `agy-ide` launcher 与 `agy` headless agent；已验证版本 1.1.2），新增 `rules/skills/workflow_external_thesis_mining.md`（调研与 external writing 之间的判断层，把 topic 转化为有证据可反驳的 thesis，7 项成功标准含单一判断/证据承载/读者增量/作者连续性/语料增量/可证伪/可写性），重构 `workflow_external_writing.md`（193→精简并模块化），扩展 `ai_agent_cli_guide.md` 和 `workflow_deep_research_survey.md`。延续 main 的"精简 workflow + 独立 bestpractice/reference"模块化重构方向。
🟡 Medium: [AI Session Search & Archive 跨供应商会话检索] commit 0ae58e5 新增 `rules/skills/ai_session_search_archive.md`，定位为多供应商 AI 会话历史的统一检索工作流。源归档按 `contexts/ai_sessions/{opencode,claude_code,codex,antigravity,second_mind}` 路由，策略是先词法搜 names/identifiers 再语义搜 approximate wording，依赖第三方归档导出器 `ai_session_export`。填补了"跨 Claude/Codex/Antigravity/OpenCode 查历史会话"的工具空白，WORKSPACE.md 与 CRONTAB.md 同步更新。
🟡 Medium: [内部写作理解门槛理论完善] commit 8b0f63a 在 `workflow_internal_writing.md` 中引入两层核心判断：①"项目上下文 vs 概念上下文"分离——共享项目背景不等于共享术语，本轮新概念仍须建立完整依赖；②"双层结论"原则——首屏先普通语言层（不含术语也能复述发生了什么）再技术精确层，应对"负载术语但无含义"的标签代替解释问题。结论卡片标题从英文改为中文（Bottom Line→核心结论 / Why This Matters→为什么重要 / Recommended Action→建议行动）。适用场景描述也收紧为"熟悉同一项目或决策背景的协作者"。

Date: 2026-07-18

🔴 High: [iasi 跟踪 main 策略升级 cherry-pick→merge] 对严重分叉的上游（iasi 与 main 双向各领先数十提交）逐提交 cherry-pick 会让结构性分叉点反复冲突；改用 `git merge main` 一次性处理 + 建立增量基线（merge commit b1b4a50），后续同步只处理增量。dry-run merge（`--no-commit` 后 `--abort`）是评估策略代价的有效手段：本次 33 文件自动合并、13 文件冲突。**完整方法论（含 5 类冲突决策表、已知分叉点清单、dry-run 流程）已晋升为 skill `rules/skills/bestpractice_forked_upstream_sync.md`，user memory 同步存 `iasi-forked-upstream-sync.md`。**
🟡 Medium: [merge 冲突解决决策模式] 13 个结构性冲突的处理范式：modify/delete 保留 iasi 有意删除（observer/opencode_client/reflector.py 三脚本 `git rm`）；main 引用 iasi 已删文件的（CRONTAB/setup_guide 的 reflector.py/observer.py）保留 iasi preflight 版；iasi 领先 main 的改动（cognitive 的 semantic-search repo 升级）保留 iasi；纯 main 增益（Google Maps 列表、trailing whitespace 清理、`functions.task` API 纠正、ChatGPT OAuth）取 main。
🟡 Medium: [main 内容同步] 本次带入 main 上游内容：7 个新 skill（35e5d94：deployment_github_actions_koyeb / growth_analytics / ios_test_acceleration / openreview / skill_download_paper / workflow_public_consensus_net_income_audit / workflow_research_paper_survey_writing）+ 公开写作工作流术语更新（2510988，thesis gate→reasoning architecture 等）+ ChatGPT OAuth ecosystem 引用（32c96e）+ 代码清理（7902adf）。

Date: 2026-07-20

🟡 Medium: [ob-harness 项目里程碑] commit e5c1a5d（07-19）新增 ob dev 首次开发体验文章（`adhoc_jobs/2026/20260719-ob-dev-first-experience.md`）。`ob dev` 命令组（list/modify/refresh/reset/status/finish 共 6 个子命令）把 Yocto devtool 工作流转译为对 Agent 透明的 API，标志 ob-harness 从"外围统筹（init/build/qemu）"跨入"源码深水区"。以替换 gb200nvl-obmc webui logo 为真案例，验证 Agent 一气呵成跑通"方案对齐（bbappend vs devtool modify 取舍）→ 源码替换 → ob build 后台挂起监控 → ob dev finish 生成 patch 落盘 meta-phosphor → ob run-qemu 浏览器验真"全闭环。PR iasiv5/ob-harness#21。这是"AI 合伙人"叙事从外围打杂到代码区输出的关键一步。
🟡 Medium: [AI 采纳阶梯方法论] commit cfb88b3（07-19）新增《AI 采纳的阶梯》中文翻译与 iasi-remix 版（`adhoc_jobs/2026/20260716-steps-of-ai-adoption-zh.md` + `20260718-steps-of-ai-adoption-iasi-remix.md`），原作者 Boris Cherny（Claude Code 作者，Anthropic）。5 级阶梯（Step 0 受限/1 辅助/2 并行/3 有监督自治/4 AI 原生），核心判断是"单兵 10 倍→全团队 10 倍"的差距不是 token 和模型档位，而是每一级各自的瓶颈与验证护栏构成。关键分水岭是"机器校验机器的闭环"和"信任迭代的速度"，而非"再多买点 token"。iasi-remix 版把判定红线提炼为"这件事本是不是某个工程师会做的？是就发 AI 自动化，不是就交人工审核"。Anthropic 自评 Step 3、Cherny 个人 Step 4。该阶梯与 ob-harness V1.0→V1.2 的工程化路径形成方法论↔实践互证，后续可作 harness engineering 叙事的对标框架。

Date: 2026-07-21

🟡 Medium: [AI 编程工作流方法论收口 IPDD] commit ce700d0 新增文章 `adhoc_jobs/2026/20260721-从Plan first 到 SDD 再到 IPDD.md`，把 AI 编程工作流演进拆为三阶段：Plan First（Plan Mode 事无巨细指挥）→ SDD（GSD/OpenSpec 强制全量 proposal/specs/design/tasks 落盘，质量兜底但推广阻力大）→ IPDD（实施计划驱动，GPT-5.4/Opus-4.6 + 百万 token 让 Agent 内化工程素养后，一份实施计划即可全自主闭环）。除模型进化外，2026-06 GitHub Copilot Enterprise 改 Usage-based Billing 是第二驱动力，倒逼轻重任务分轨：logo 替换/调用链分析直出指令，跨文件接口改造走 IPDD。三步走固定为 grill-with-docs 锚定意图 → writing-plans + 顾问 Agent 对抗审查 → 新会话主力执行 + 顾问 Agent 闭环验收。与 07-20《AI 采纳阶梯》形成互证：约束随模型升维消退是趋势，但"动手前确立计划"是底线。harness engineering 叙事从"四层固化"向"实施计划为王"收口。

Date: 2026-07-29

🔴 High: [iasi skill 双设计轨道 + 单向 pull handoff 模式] m/ 子仓完成 brainstorming/writing-plans/handoff/cleanup 四 skill 的结构性优化，沉淀出新词汇与 ADR 0001。核心设计：（1）两条对等设计轨道——brainstorming（澄清式，本地可改）与 grill-with-docs（对抗式，上游冻结不可改）；（2）单向 pull handoff——下游靠识别上游产物承接上游，而非依赖上游 push payload，专门解决上游冻结 skill 无法加出口指针的难题；（3）reviewer gate（reviewer 可单独拒绝某任务才成立为独立单元）与 test-mapped failure mode（反例段挑选用已知失败案例做依据）两个判据。配套词汇表 m/CONTEXT.md 建立设计轨道/单向 pull/reviewer gate/test-mapped failure/中模型校准/检索难度轴六术语。
🟡 Medium: [IPDD 定义修订] `adhoc_jobs/2026/20260724-IPDD定义修订.md` 把 IPDD 从"Implementation-Plan Driven Development"重定义为"Intent & Plan Driven Development"，三阶段对齐 workflow：I=Intent（对齐意图，确保人机认知一致）、P=Plan（生成计划，含任务拆分/执行顺序/预期结果）、DD=Driven Development（计划指导下 Agent 自主执行 + 代码审查验收）。与 07-21 收口的 IPDD 文章呼应，harness engineering 叙事从"实施计划为王"进一步收紧为"意图锚定先于计划"。
🟡 Medium: [ob-harness Know-how 双通道经验沉淀] `adhoc_jobs/2026/20260728-ob-harness 实战：把 Agent 踩的坑变成 Know-how.md` 实录纯手动把 Agent 协作坑沉淀成 Know-how 的三轮迭代：Round1 阻断 DRY-RUN 逻辑断裂（CWD 无主仓时 machine check 失去物理依据）→ Round2 阻断交互盲区（ob init 遗漏 --url 卡在交互窗口）→ Round3 经验生效一次跑通。框架内 SKILL 改名 KNOW-HOW 避免与 Agent Skill 语义混淆。手动沉淀与 /ai-heartbeat 半自动机制互为补充，构成 ob-harness 双通道经验积累体系。
🟡 Medium: [认知画像提取工作流成熟] `rules/skills/workflow_cognitive_profile_extraction.md` 基于多源大规模实践（6.9M 字 → 8 条公理/6 轮）更新：Guardrail 区分 Opus（设计/QA/写作不 delegate）与非 Opus（暂停确认）；Round 驱动迭代引擎（Discover/Verify/Finalize/Restructure 四动作）替代固定线性 Phase；确立"写作不 delegate"硬约束保证概念一致性与文风统一。INDEX.md 已同步。

Date: 2026-07-30

🟡 Medium: [harness engineering 叙事延续] commit 7c7e003 新增文章 `adhoc_jobs/2026/20260730-从 GitHub 到 IPDD：约束凭什么越做越薄.md`，把 GitHub 官方博客《The harness is all you need (mostly)》八步原生循环（原型→plan 模式→Autopilot→rubber duck review）与 IPDD 三阶段（Intent/Plan/DD）互证，提炼出共同内核是"锁定变量、降方差"：同一 session 不换模型保 prompt cache、一份计划锁死意图防发散。区分大众场景（原生 harness 足够）与严肃工程深水区（需 IPDD 对抗式审查兜底 mostly 余量）。与 07-21/07-29 的 IPDD 收口叙事连续，从"实施计划为王"进一步收紧为"约束越做越薄、方向越做越锋利"。
🟡 Medium: [iasi 跟踪 main 第五次同步] commit ffba3d5 合并 main `c3e9d9c`（PR #81+#80+#78+#77，共 7 个上游提交）到 iasi，纯增益零冲突 auto-merge 直接通过（+112 行）。带入内容：新增 M5StickS3 skill、增强 project_scaffold skill（加 context/CI-CD/common pitfalls）。这是自 07-18 建立增量基线以来第 5 次连续零冲突纯增益同步，持续验证"iasi 只新增不重构上游文件 → auto-merge 直接通过"模式成立。下次同步起点锚定 `ffba3d5`。

Date: 2026-08-06

🔴 High: [harness 互检方法论：用 better-harness 给 ob-harness 做证据型体检] 文章 `adhoc_jobs/2026/20260805-better-harness-diagnose-ob-harness.md` 实录用外部 harness（QoderAI/better-harness，Agent Work Loop 五维：任务理解/可控执行/改动验证/可靠交付/经验沉淀）反向审视 ob-harness，打出 65/100。核心发现不是"门禁不存在"而是"门禁宽度窄于文档契约"——Stop hook 自检只覆盖 `ob/lib`，`know-how` 与 `tools/*.py` 的改动收口不到验证（文档承诺改完必跑 `ob_check.sh`，实际门禁触发面比承诺窄一圈）。方法论价值：当一个 harness 审视另一个 harness，有效的不是看文档严密程度，而是对照"文档承诺 vs 门禁实际触发面"的落差；任务理解扎实不等于变更验证到位，缺口总在最后一公里。与 07-29"reviewer gate/test-mapped failure mode"判据互补，提供了从外部视角发现"假门禁"的可复现诊断路径。
🟡 Medium: [ob-harness 连续四篇实战收束 GDD + know-how + 防过度设计] 观察期内 ob-harness 实战叙事加速产出 4 篇文章，三条主线互锁：（1）Goal-Driven（GDD）：`20260731-ob-harness-gdd-wechat-article.md` + `20260802-...` 把 lidangzzz 的 Goal/Criteria 模板落地为 ob-harness 斜杠命令，验证从"接受命令→系统验证→自动落盘 Git"的 E2E 闭环；（2）know-how 沉淀机制重构：`20260730-ob-harness-knowhow-mechanism-optimization.md` 针对"用户本地踩坑经验与上游 knowhow 混搭引发分支同步冲突"缺陷，用 IPDD 流程做产品(oem)与用户(context/knowhow/)物理隔离 + `/sediment` 自动化；(3）防过度设计：08-02 文章以 Q5"拒绝扩散/形式主义/越权"清单实录砍掉 Agent 把小需求张罗成大工程（试图新增冗余 SKILL/ADR/改全局路由）的典型坏味道。三条主线共同把 ob-harness 从"工作台"叙事推向"可分发开源产品 + 治理纪律"叙事。
🟡 Medium: [iasi 跟踪 main 第六/七次同步 + 验证条例升级] commit bf11140（第六次，PR #82+#83，App Store Connect CLI + Codex CLI 第三方 model provider）与 commit 3c7c03c（第七次，PR #84，external prose lint CLI + 强制 Round 4）连续零冲突 auto-merge 通过。第七次出现新模式：不是纯增益——main 对 4 个 iasi-native 改过的写作文件做了实质修改，但双方改动落不重叠 hunk → auto-merge 零冲突通过。由此沉淀出新增验证条例："对有 iasi-native 改动的 auto-merge 结果，必须 diff merge-base→main 确认是 hunk 级不重叠而非语义覆盖，并保留 iasi 独有条目"。月起至今连续 6 次零冲突，下次起点锚定 `3c7c03c`（merge-base `da46eff`）。
🟡 Medium: [main 引入确定性 external prose lint CLI] PR #84（commit 66e6993）新增 `external_prose_lint_cli.py`（798 行）+ skill + tests，把中文 external 文稿的破折号/引号/括注补译/禁词表/单句段/裸 URL 等机械项从"主观语感判断"升级为"确定性 CLI 扫描 + 每条附 skill 问题"，外部写作工作流 Round 4 由"可选 fresh 返工"改"强制 CLI 自查 + 真实 draft residual"。意义：把 voice_contract 这类"开环背景规范"补上"观察真实输出→指出 residual→强制再执行"闭环——这是自 07-16 以来 harness engineering"机器校验机器"原则在写作域的具体落地。

Date: 2026-08-24

🔴 High: [跨仓记忆自治模式确立——主仓 observer 对子仓降级为指针式记录] ob-harness 子仓已自带完整 heartbeat 基础设施（`ob-harness/contexts/memory/OBSERVATIONS.md`），且已于 08-18 自行运行 observer（观测 16 天/86 commits）+ reflector 首次全量 GC（删 30+ 条已固化/过期条目）。配合主仓 08-18 的 .gitignore 改动（d008f61 把 ob-harness/ 与 external_skills/ 全目录排除跟踪），两子仓与主仓仅剩物理相邻关系。由此确立：主仓 observer 对子仓内容只记里程碑级指针条目（发生了什么 + 去子仓哪里看细节），不再复述子仓 commit 级细节，避免双仓记忆重复膨胀。
🟡 Medium: [ob-harness test-qemu 基线测试框架落地（08-07~08-20，89 commits，PR #42~#45）] per-machine baseline 双轨硬路由：`tests/baseline/`（社区标准卷，随上游分发）+ `contexts/baseline/`（定制卷）物理隔离，凭 manifest 谱系嗅探锁定加载路径；`ar_probes.yaml`（产品需求→Redfish 请求+断言原语）与 `applicability.yaml`（skip/xfail 确权）声明式配置；六态 verdict（pass/fail/skip/xfail/xpass/error）+ exit 契约 0/1/2/3（error 属 infra 不进 αtruth 统计）。谱系判定四步演进收口 ADR-0026（优先级覆盖+WARN → 硬路由 → source label 单维度 → 缺失态 fail-closed 对称防御）；CI coverage 哨兵拒绝 EXEMPT 豁免（哨兵不弱化原则），改用 protocol 测试直调补偿 xtrace 子进程盲区。PR #45 把 run.sh bash 编排全量下沉 runner.py（归一化单副本 + schema_version 两仓门禁，ADR-0027）。主仓配套文章 `adhoc_jobs/2026/20260818-ob-harness：新增固件基线测试框架.md`。六轮评审+grilling 两轮八项决策的完整链条见子仓 `contexts/memory/OBSERVATIONS.md` 2026-08-18 条目，不在此复述。
🟡 Medium: [.gitignore 子仓独立化 + WORKSPACE 路由缺口] 主仓 d008f61 把 `external_skills/` 与 `ob-harness/` 加入 ignore，两子仓完全独立演化、主仓不再跟踪其内容变动。但 `rules/WORKSPACE.md` 路由表尚未收录这两条目录（本次 reflector 补录），后续找文件仍可能全盘 glob。
🟡 Medium: [写作/CLI skill 外部化后的本地 overlay 方案落地（08-13 四连提交）] main 于 PR #86/#88 把写作 skill 与 CLI agent skill 迁出到 grapeot 外部 repo，iasi 以 overlay 机制承接本地定制：新增 `rules/skills/bestpractice_external_skill_overlay.md` + `writing_skill_local_overlay.md`（89eb8b0）；修 overlay refresh 在 nothing-to-merge 时被短路的缺口——从条件式尾步骤提升为验收标准无条件项（91d6d80/a81216d）；AGENTS.md 强化"严禁 AI 直接输出最终文章"入口（f2e35a1）。
🟡 Medium: [iasi 跟踪 main 第十次同步] commit f8c9c8c（08-17）合并 main `3f62b8b`（PR #88：CLI agent skills 迁移至 grapeot/ai-agent-cli-skill；PR #89：grok-oauth-skill 入生态索引）。三个被删文件 iasi 零独立改动 → 接受删除；INDEX.md 双方改动 hunk 不重叠，auto-merge 零冲突；权属核查技巧：用 `3d9ce78..HEAD`（上次 merge 之后）限定范围，排除历史回流提交干扰。新增已知分叉点 #8：CLI agent skill 已外部化，自定义需走 ai-agent-cli-skill 本地 overlay（同 writing-skill 模式）。自建立增量基线以来连续 8 次零冲突，下次起点 `f8c9c8c`（merge-base `3f62b8b`）。
🟡 Medium: [m 子仓 5.7.2/5.7.3 发布] 5.7.3（08-18）：skill 跨引用去斜杠命令化（"run the `/grilling` skill" → "call the Skill tool with grilling"），skill-to-skill 调用不再伪装成用户面 slash command；domain-modeling 触发条件从抽象 "ubiquitous language" 改为具体制品锚（编辑 CONTEXT.md / 记录 ADR / 术语讨论）。5.7.2（08-07）：sub-agent 生成指引去工具化，skill 文本跨 agent runtime 可移植。
🟢 Low: [归档迁移] 08-17 09:47-09:50 批量文件时间戳刷新为第十次 merge 的 checkout 结果（git status clean），observer 按 git name-status + 同秒批量时间戳模式过滤为噪音。此为 07-27 / 08-06 后第三次同模式出现，过滤口径已稳定。
<!-- 2026-08-24 reflector GC：删除过时 🟢 三条（07-20 当时 GC 操作的流水、07-27 与 08-06 归档噪音过滤流水——同模式已三次出现，口径稳定进 observer 惯例，不再逐次记录）与 🟡 一条（07-21"文章锐评 slash command 落地"，功能已稳定投入使用，配置文件自明）。08-24 归档 🟢 为当日新记，保留一轮观察期。-->
