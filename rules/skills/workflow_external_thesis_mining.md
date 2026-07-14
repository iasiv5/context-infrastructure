# External-Facing Thesis Mining Workflow

## 元数据

- **类型**: Workflow
- **适用场景**: 已有一个值得关注的 topic 和初步调研材料，需要决定它能否形成 external-facing 分析文章，以及文章真正要证明什么。
- **输入**: 深度调研工作流 Phase 1-3 的产物或等价 research packet。
- **输出目录**: `tmp/<session_slug>/`

## 目标与边界

本 workflow 把“一个有趣 topic”转化为“一个有证据、可反驳、对读者有增量、符合作者长期判断的核心 thesis”。它是调研与 external writing 之间的判断层。

它不负责发现每日候选新闻，不负责补齐大规模事实调研，也不负责写最终 prose。Axioms 和 Thesis Catalog 仍是 canonical 观点来源；本 workflow 只负责检索、组合、压力测试和编辑决策。

如果用户已明确给出 thesis，不要为了流程完整重新发明一个。保留原 thesis，只执行证据、边界、反方和读者增量的压力测试。

## 成功标准

进入 external writing 前，结果必须同时满足：

1. **单一判断**：能用 2-3 句话表达一个可被同意或反对的判断，不是新闻复述、话题标签或“值得关注”。
2. **证据承载**：至少有两类相互独立的证据支撑关键推理；事实、推断和作者判断彼此分开。
3. **读者增量**：明确说明读者在公开摘要之外会获得什么机制、边界、反例、比较或后果。
4. **作者连续性**：检索过相关 Axioms、既有文章和 survey。判断更新时写清新证据。
5. **语料增量**：与近期同渠道文章相比，不重复同一结论、入口和论证骨架。
6. **可证伪与边界**：写清最强反方、关键不确定性、适用范围和 falsifier。
7. **可写性**：能形成 3-5 个相互推进的论证节点。

证据不足时缩窄 thesis 或输出 `DO_NOT_WRITE_YET`。不得因为 topic 热或已经投入调研成本而降低门槛。

## 必须读取的认知材料

主线程建立一个小而有区分度的 comparison set：

- `../axioms/INDEX.md` 及 1-3 个直接相关的 Axiom 原文。
- [Thesis Catalog](./reference_writing_thesis_catalog.md) 中 1-3 个强相关视角。视角只用于启发，不得把 L1-L8 当作文章结构。
- `contexts/blog/`、`contexts/survey_sessions/` 中的相关历史判断。
- 目标发布环境中的 3-6 篇相邻文章或历史语料，优先覆盖同 topic、同推理结构和经历过明显人工 correction 的文章。具体路径由目标项目提供，不假设固定目录。
- 当前 topic 的 research packet、来源 URL、事实核查和已知证据缺口。

把检索结果和选择理由写入 `tmp/<session_slug>/thesis_inputs.md`。该文件只是本次决策的证据清单，不是新知识库。

## 独立候选生成与 AGY Reader 路由

topic 价值较高、判断不确定性较大时，按 [并行 Subagent 工作流](./workflow_parallel_subagents.md) 启动两个独立 sub-agent，并按 [Antigravity CLI 文件式调用](./antigravity_cli.md) 启动一个独立 AGY reader。三者读取同一份 `thesis_inputs.md`，但不得共同编辑同一文件。

- **证据与机制 reader**：从最强证据反推可成立的机制判断，优先发现归因越界和 scope 过大。
- **作者连续性与增量 reader**：对照 Axioms、历史文章和 correction 经验，寻找尚未写过的判断。
- **陌生读者与反命题 reader**：AGY CLI / `Gemini 3.5 Flash (High)`。完整任务写入 `agy_reader_prompt.md`，使用独立 `agy --print` conversation，判断读者为什么在意、提出最强替代解释，并检查候选是否只是业内常识换句话说。result、stdout、stderr 和 events 分别落盘。

每个 reader 输出 2-4 个候选到各自文件。候选统一包含：Thesis、Reader delta、推理链、最强证据、最强反方、适用边界与 falsifier、与历史写作的关系、现在是否应成文。reader 可以明确判断没有合格 thesis，禁止凑数。

轻量、低风险或用户已给出清晰 thesis 的任务可以跳过并行发散，由主线程直接进入 critique；跳过原因写入 `thesis_decision.md`。

## Fresh Critique Gate

候选生成后，用一个未参与 brainstorm 的全新高可靠推理 context 做盲审。critic 可以看到 research packet、历史材料和全部候选，但不看候选作者身份，也不负责润色。

critic 逐项检查证据是否真实承载 thesis、是否存在更简单的替代解释、reader delta 是否具体、与既有文章相比是否有增量、scope 与证据强度是否匹配、候选是否应淘汰或合并，以及是否应输出 `DO_NOT_WRITE_YET`。结果写入 `tmp/<session_slug>/thesis_critique.md`。

## 主线程决策与输出

主线程保留最终编辑判断，不能按票数选 thesis，也不能把多个候选机械拼成双 thesis。最终写入 `tmp/<session_slug>/thesis_decision.md`，包含：

- `Verdict: PROCEED | DO_NOT_WRITE_YET`
- Core Thesis
- Reader Contract
- 3-5 个节点的 Argument Spine 及对应证据
- Boundaries and Counterargument
- Continuity and Novelty
- Evidence Gaps
- Rejected Candidates 及淘汰理由

只有 `PROCEED` 才能生成 `writing_brief.md` 并进入 [外部写作工作流](./workflow_external_writing.md)。`DO_NOT_WRITE_YET` 是有效产出，不得改写成模糊的“持续关注”。

## 已知失败模式

- 先选 L1-L8，再把事实塞进框架。
- 把共识、新闻摘要或 topic 热度包装成 thesis。
- 用多模型投票替代核证。
- 把两个候选拼成无法聚焦的双 thesis。
- 在本阶段提前优化标题和 prose；表达工作应留给 external writing 的 IC-1 至 IC-3。
