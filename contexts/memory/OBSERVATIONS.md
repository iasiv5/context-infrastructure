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

Date: 2026-05-27 ~ 2026-08-24（2026-10-25 reflector 合并归档）

🟡 Medium: [ob-harness 里程碑链] 种子骨架（05-29，context infrastructure 骨架可移植性首次验证）→ 更名 ob-harness 并完成 init/build/status 工作台（06-09）→ V1.1 引入 QEMU 启停（06-13）→ V1.2 物理分层重构 + 退出码 0/2/3/1 协议 + 四层测试体系（06-21）→ ob dev 进入源码深水区（07-20，PR #21）→ test-qemu 基线测试框架（08-24，PR #42~#45）。架构与评审细节一律以子仓 `ob-harness/contexts/memory/OBSERVATIONS.md` 为权威，主仓只留里程碑指针。
🟡 Medium: [harness engineering 叙事线] BU6 分享会 PPT 与 14 页演讲稿（06-13/06-18，主线收口为"如何把固件经验写进平台与流程"）→ Prompt/Context/Harness/Loop 关系图资产（07-05）→ 《AI 采纳的阶梯》翻译+iasi-remix（07-20，分水岭是机器校验机器的闭环与信任迭代速度）→ IPDD 收口线（07-21 Plan First→SDD→IPDD；07-29 重定义为 Intent & Plan Driven Development；07-30 与 GitHub 官方博客互证，共同内核"锁定变量、降方差"）→ 持续重构工作流三连文（07-03，pick-one-arch-task 流水线）与 GDD/know-how/防过度设计四连文（08-06）。全部文章落盘 `adhoc_jobs/2026/`，当前叙事状态：约束越做越薄、方向越做越锋利。
🔴 High: [harness 互检方法论] （08-06）用外部 harness（better-harness 五维）反向体检 ob-harness 得 65/100：有效诊断不是看文档严密程度，而是对照"文档承诺 vs 门禁实际触发面"的落差——Stop hook 自检只覆盖 `ob/lib`，know-how 与 tools 的改动收口不到验证；任务理解扎实不等于变更验证到位，缺口总在最后一公里。与 07-29 reviewer gate / test-mapped failure mode 判据互补，构成可复现的假门禁诊断路径。
🟡 Medium: [skill 与写作体系里程碑（内容以 skill 文件与文章本体为权威）] skill 生态模型确立（05-27 image-generation 拆分起步，延续 Tavily/Stripe/PPTX 路径）→ internal writing 视觉认知负载三层构架与三公理（06-15）→ 外部写作模块化重构 + workflow_external_thesis_mining 判断层 + Antigravity CLI 接入（07-16）→ 内部写作"项目上下文 vs 概念上下文"分离与双层结论原则（07-16）→ external prose lint CLI 确定性自查闭环（08-06，PR #84，Round 4 强制 CLI 自查）→ m/ 子仓 brainstorming/grill 双设计轨道 + 单向 pull handoff + reviewer gate / test-mapped failure mode 判据（07-29，ADR 0001 与 m/GLOSSARY.md 为权威）→ 认知画像工作流 Round 驱动迭代引擎（07-29）。
🟡 Medium: [LLM cache billing 实测结论] （06-30）基于 ob-harness 41 个会话日志：输入 token 约为输出的 87 倍、总体缓存命中率 93.6%、百轮以上长会话 94.4%，prompt caching 是重上下文 agent 工作流成本可承受的关键机制（分析见 `adhoc_jobs/2026/20260624-llm_cache_billing_analysis.md`）。
🟡 Medium: [欧盟 CRA 合规背景] （07-14 科普文）安全责任从出厂前测试延伸到产品全生命周期；固件/BMC 产品出口欧盟关键节点：2026-09-11 漏洞通报时钟已开启、2027-12-11 起未贴 CE 不得进入欧盟市场（文章 `adhoc_jobs/2026/20260713-eu-cra-kepu.md`）。

Date: 2026-10-04 ~ 2026-10-16（2026-10-25 reflector 合并归档）

🟡 Medium: [GHC prompt 格式变更] （10-09）GitHub Copilot 最新版不再支持 `*.prompt.md`，删除 ai-heartbeat 与 wen-zhang-rui-ping 两个 prompt 文件，入口暂用 `.claude/commands/`。
🟡 Medium: [iasi 跟踪 main 第 14~16 次同步锚点] #14 `72a0bd9`←`e2d50ae`（11 提交 PR #99–#104，iOS skills 外部化到 ios-development-skill）；#15 `7ba1000`←`0656c59`（9 提交 PR #105–#109，零冲突）；#16 `4abd542`←`bb5bebe`（9 提交 PR #110–#114，零冲突）。各次 overlay refresh 均完成；下次同步冲突预案以 #17 的已知分叉点清单为准。

Date: 2026-10-25

🟡 Medium: [iasi 跟踪 main 第十七次同步（1 文件冲突，逐段合并）] merge commit `9702efd` 合并 `origin/main` `c747317`（从上次基线 `bb5bebe` 增量 18 个提交，PR #115–#126：voice-memos、niview、vlog、bilibili-upload、orchestral-midi、bilibili-live-monitor、youtube-upload、zoom-recording、video_export 共 9 个 skill 生态条目；compressor.md 迁出为外部 repo；#118 委派策略澄清）。冲突仅 AGENTS.md 共 2 hunks，按决策表逐段处理——①Sub-agent 模型路由取 fork：Copilot/Claude Code 是本 fork 实际工具链，main 版 explore/general/Antigravity 属上游生态概念；②高能力模型工作模式手动合并：采纳 main #118 政策澄清（实现与最终验收默认留主线程，取代 fork 旧版"调研/数据处理交 sub-agent"），保留 fork 泛化措辞。auto-merge 抽查通过——iasi 自 4abd542 仅动 OBSERVATIONS.md，其余文件均为纯 main 增益；INDEX.md fork 专属条目（L94-96）完好；compressor.md 删除属 main 纯增益迁移（SKILL_ECOSYSTEM.md 已有外部条目）。overlay refresh：writing-skill @ `8f83b6c` already up to date，本机无 pip 按已知陷阱 CLI 层留主力机，内容层完整（install_overlays --check 全部就绪，INDEX 42 链接无缺失）。已知分叉点清单更新：新增 AGENTS.md 两节（Sub-agent 模型路由 / 高能力模型工作模式）为首选冲突位——main 侧已引入 explore/general 与 Antigravity 语义，下次 main 再动这两节预期复冲突，处置基准见 `9702efd` commit message；INDEX.md fork 专属条目区仍列第二。下次增量起点锚定 `9702efd`。

<!-- 2026-10-25 reflector GC：将 05-27~08-24 的 21 个条目折叠为 6 条合并记录（ob-harness 里程碑链 / harness engineering 叙事线 / harness 互检方法论 / skill 与写作体系里程碑 / LLM cache billing / EU CRA 背景），详情以子仓 memory、adhoc_jobs 文章本体与 rules/skills 文件为权威；10-04/10-08/10-16 三次同步摘要折叠为 #14~#16 锚点单条（沿用 09-07 GC"保留近期锚点、折叠历史摘要、当天新鲜观测不折叠"口径），10-09 GHC prompt 格式条目保留。被删 🔴（05-29 种子骨架、05-31 心跳状态闭环、06-04 跨平台重构、06-09/06-13 ob 爆发期与 V1.1、06-15 internal writing 构架、07-29 双设计轨道）均已由 SOP/入口文件/skill 文件/子仓 memory 固化，或已并入上方里程碑链。无 🟢 条目需要回收；未新增 rules/ 晋升（本次 merge 分叉点处置已由 bestpractice_forked_upstream_sync 流程 + commit message + memory 清单覆盖）。observer 因当天条目已存在记 skipped。继承 2026-09-07/09-15 两轮 GC 注记所涉条目均已消化。-->
