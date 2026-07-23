# 外部写作与成文工作流

## 元数据

- **类型**：Workflow
- **适用场景**：把已核实的调研转化为 external-facing 中文分析文章、公开 survey report、课程或客户内容。
- **前置依赖**：`workflow_deep_research_survey.md` Phase 1-3，或等价的事实底稿。
- **最后更新**：2026-07-22

## 1. 核心原则

外部写作包含三种不同工作，不能交给同一个 context 同时完成：

1. **编辑判断**：文章为什么值得写，读者应改变什么认识，证据按什么顺序到达。
2. **完整成文**：把已经锁定的内容写成自然、连贯的 prose。
3. **结果验收**：检查事实是否漂移、约束是否满足、整篇声音是否成立。

Main Agent 是编辑、事实负责人和最终验收者。Antigravity Writer 只生成完整候选稿，不为自己的文章写 QA，也无权宣布 PASS。确定性脚本检查数字、URL、图片和格式；Main Agent 判断事实含义、读者路径和整篇声线。

禁止让 Writer 读取本 workflow、整份 `bestpractice_external_prose.md` 或全部历史反馈。Main Agent 必须把本题真正需要的要求压缩到一个短 task packet。长篇规则是 Manager 的参考资料，不是模型生成时的上下文。

## 2. 输出路由与交付边界

- 用户只说 external-facing：默认保存到 `contexts/survey_sessions/`。
- 用户明确说写博客或发博客：保存到目标项目约定的博客目录，并遵循该项目格式。
- 本地最终 Markdown 是写作终点。发布、排程、社交媒体、社区或其他外发动作必须等待用户明确授权。
- 配图是交付的一部分，按第 10 节执行。

## 3. 成稿标准

一篇文章通过验收，需要同时满足以下条件：

- 聪明但没有共享上下文的读者能从第一段开始读懂，不需要向后寻找关键定义。
- 前 25% 已经交代文章对象、当下触发点、核心判断与继续阅读的增量。
- 全文只有一个核心 thesis；每一节都推动这项判断，不按研究材料分类。
- 概念沿动作、冲突和后果出现。文章不连续采用“定义对象、解释机制、抽象总结”的讲义节奏。
- 读者不必同时维护多组尚未落地的分类或比较轴。确有三个以上并列项时，先给局部地图。
- H2 之间由同一个对象、动作、限制或后果连接；遮住标题仍能读出为什么下一段此刻出现。
- 数字、URL、归因、限定语、图片和专有名词与 source of truth 一致，没有生成模型补出的场景或因果。
- 文章读起来像熟悉问题的人在自然介绍发现，既不端着，也不靠俚语、夸张比喻或网络文案表演亲切。

任何一项失败，都不能由 Writer 的自评或 QA 报告抵消。

## 4. 写作前先选对文章

### 4.1 三个 thesis-and-outline 方案

用户没有明确锁定主线时，Main Agent 在动笔前先给出约三个真正不同的方案。它们不能只是标题同义改写；选择另一个方案后，文章主角、证据顺序、舍弃材料和结尾判断都应发生变化。

默认可从三种距离寻找候选，但不强套模板：

- **对象解释型**：把项目、论文或事件本身讲清楚。
- **Landscape / belief-change 型**：用当前对象修正读者对一个长期问题的认识。
- **判断框架 / decision 型**：把对象作为 worked example，帮助读者以后判断同类问题。

每个方案至少说明：

```markdown
## 方案名

一句话 thesis：读者读完后会改变什么判断？
为什么现在写：新事件、新证据或持续困惑是什么？
目标读者：他已经知道什么，为什么会继续读？
文章主角：对象、landscape，还是读者的判断任务？
Proof route：4-6 步证据路径，不写材料目录。
必须讲深：省略后 thesis 就不成立的机制或比较。
主动舍弃：有研究价值但会稀释 takeaway 的材料。
最大风险：为何可能显得平、空、旧、太专业或证据不足？
推荐度：Main Agent 推荐哪个，依据是什么？
```

用户已经明确给出主线时，不重新发明三个方案。Main Agent 只把它复述为 reader takeaway、proof route 与 depth boundary，暴露可能的误解后继续。

### 4.2 Article warrant 与 reasoning architecture

进入写作前，Main Agent 必须能回答：

- **Reader start state**：读者目前怎样理解这个对象，缺什么前提？
- **Target belief change**：文章要把哪项认识从 A 推到 B？
- **Article warrant**：为什么需要一篇文章，而不是一条摘要？
- **Causal model**：3-7 个有方向的 claim 怎样共同支撑 thesis？
- **Evidence roles**：每份核心证据负责证明、解释或限制哪个 claim？
- **Concrete carrier**：哪个请求、任务、数字、人物或业务记录可以贯穿论证？
- **Answer timing**：读者何时看到问题、证据和完整答案？真实认知冲突不必在第一句被消灭，但答案必须在前 25% 成立。

分析工具不自动成为对外 thesis。时间线、taxonomy、三条轴或四问法可以帮助发现判断；除非读者本身需要学习该方法，否则只把它们作为证据组织方式。

## 5. Round 1：Main Agent 建立唯一 source of truth

Main Agent 完成研究、编辑选择和内容底稿。这个阶段生成四个工件：

### `source_contract.md`

这是后续所有 Writer 的事实依据，必须包含：

- 每项可进入正文的 claim 及对应来源。
- 精确数字、日期、版本、URL、图片引用和不可改术语。
- 归因、统计口径、比较基准与不得外推的边界。
- 明确禁止补写的未知信息。
- 对 running example 的说明：哪些动作来自来源，哪些只能写成假想示例。

不要只列链接。每条来源要说明它具体支持什么。

### `writing_brief.md`

至少包含：

- reader start state、reader takeaway、精确 thesis 与 article warrant；
- 文章主角、当下触发点和首屏承诺；
- 与作者既有观点的连续性：当前证据是在填补、修正还是反驳旧判断，并记录相关旧文 URL；
- claim dependency、H2 顺序及章节 handoff；
- concrete carrier、必须讲深与主动舍弃的内容；
- 三至五个不同角度的候选标题，以及最终标题为何准确表达对象与文章增量；
- 哪条新证据会削弱或推翻 thesis。

### `voice_contract.md`

Writer 实际读取的文风要求必须控制在一页左右，只写本题需要的内容：

- 两三句话描述目标叙述姿态。
- 一至两段用户明确认可、且解释难度相近的正向摘录，并说明只学习什么。
- 本稿最可能出现的两至三段负例，直接指出段落为什么端着或表演。
- 本题允许的第一人称、问句、技术密度与局部列表边界。
- 不超过八条高影响 voice constraints。

不要粘贴整篇已发布文章，不要转录通用禁词表，也不要要求 Writer 阅读 `COMMUNICATION.md`、本 workflow 或完整 prose guide。

### `article_source.md`

Main Agent 写一份完整、可核查的内容稿。它需要有正确的 thesis、事实、证据顺序、H2、链接和图片位置，但不追求最终 prose。它不是关键词提纲，也不是让 Writer 自行补全的 claim 列表。具体信息越完整，后续 Writer 越不需要发明动作和因果。

Round 1 结束前，Main Agent 必须把 `article_source.md` 与 `source_contract.md` 对照一次。事实缺口在这里补，不把 research 任务转嫁给 prose Writer。

## 6. Round 2：Antigravity 并行生成完整候选

默认启动两个互相独立的 Antigravity conversation，并行从同一 task packet 生成 `candidate_a.md` 与 `candidate_b.md`。短文或明确只需一个版本时可以只生成一个，但不得串行让 B 改写 A。

每个 Writer 只读取：

1. `source_contract.md`
2. `writing_brief.md`
3. `voice_contract.md`
4. `article_source.md`
5. 本轮自己的短 prompt

Writer 的任务是交付完整文章，不输出 audit、解释、计数或 PASS 自述。两个候选使用相同事实和 thesis；并行的价值是获得独立 prose 路径，不是让它们故意表演两种夸张风格。

Round 2 prompt 只需强调：

- 从空白页成文，但不得补充 `source_contract.md` 之外的事实、场景和因果。
- 保留 thesis、claim strength、数字、URL、图片与必要术语。
- 可以重写段落入口、句法和 H2 wording；若结构本身阻碍自然表达，在正文外不解释，仍按 brief 完成最佳候选。
- 沿 concrete carrier 自然推进，不按规则分类授课。
- 只写文章本身。

所有调用遵循 `antigravity_cli.md` 的文件式契约。prompt、结果、stdout、stderr 和 events 分别落盘。

## 7. Round 3：Main Agent 冷读验收

Main Agent 是唯一 PASS authority。验收时先读候选正文，不读 Writer 的 stdout，也不存在 Writer 自评报告。

### 7.1 先做确定性检查

用脚本或直接比对检查：

- 数字、日期与版本；
- URL target 与图片路径；
- 必须保留和不得出现的术语；
- H2 数量及必要顺序；
- Markdown、字数和文件路径。

不要让生成模型用自然语言报告代替这些检查。

### 7.2 再做语义验收

Main Agent 把候选与 `source_contract.md`、`writing_brief.md` 和正向摘录对照，依次判断：

1. 是否出现 source contract 不支持的新事实、动作、因果或绝对化结论？
2. 开头、每个 H2 第一段和结尾是否像自然介绍，还是在宣布主题、下定义和总结意义？
3. 读者能否在概念第一次出现时理解其角色与后果？
4. 是否把 analysis scaffold、编辑反馈或 QA 语言写进正文？
5. 是否为了亲切加入装饰性比喻、俚语、假想事故或未经支持的细节？
6. 章节 handoff 和整体节奏是否成立？
7. 标题是否准确说明文章对象和分析增量，且与最终正文承诺一致？

选择更好的候选不等于从两个版本拼接段落。Main Agent 输出 `acceptance_audit.md`，记录选择、证据与三种 verdict 之一：

- `ACCEPT`：内容与 prose 均可进入 Round 5。
- `RETRY_PROSE`：thesis 和结构成立，但候选存在可由一次完整重写修复的明确问题，进入 Round 4。
- `RETURN_TO_ROUND_1`：问题属于 thesis、证据、结构或 source contract，先由 Main Agent 修复上游工件；不得假装是 prose 问题。

## 8. Round 4：可选的一次 fresh Antigravity 返工

只有 verdict 为 `RETRY_PROSE` 时才运行 Round 4，而且最多一次。使用全新 Antigravity conversation，不延续候选生成 session。

Main Agent 创建 `revision_delta.md`，只列三至五个最高影响 blocker。每项必须包含原文位置、为什么失败以及正确方向。不要重新附加整套 prose taxonomy。

Round 4 Writer 读取：

1. 选中的候选稿；
2. `source_contract.md`；
3. `writing_brief.md`；
4. `voice_contract.md`；
5. `revision_delta.md`。

它输出一份完整修订稿，不写 QA。完成后 Main Agent 重复 Round 3 的确定性与语义验收。若仍有非 surgical blocker，不得自动启动第二次 Round 4 或其他新 Writer。Main Agent 应回到 Round 1 或向用户明确报告未通过，避免无限 mutation loop。

## 9. Round 5：Main Agent surgical completion

通过验收后，Main Agent 可以直接修复：

- 错字、漏字、标点和明显语病；
- Markdown、URL、图片路径和 alt text；
- 专有名词的机械误写；
- 与 source contract 对照后可唯一确定的数字、限定语或归因；
- 不改变段落目的和 claim strength 的单句局部修正。

不得在 Round 5 偷偷更换 thesis、重排章节、拼接不同候选或进行无记录的整段重写。所有改动写入 `completion_edits.md`。若修复需要重新判断文章结构或整篇声线，说明 Round 3 验收错误，应回到相应阶段。

## 10. 配图

配图是 external-facing 成稿的硬约束，必须降低认知负担，不作装饰。短文（少于 2000 字）至少一张，长文至少两至三张。

进入最终 Markdown 的生成图必须使用当前工作区可用的图像生成或重绘工具生成或重绘，并压缩为 JPG/WebP，长边约 1024 px、单图低于 200 KB。定量图先由 Main Agent 用确定性工具画准数据，再交给图像生成或重绘工具处理。所有图片必须有相对路径与有效 alt text。

## 11. 最终检查与交付

Main Agent 在最后一次修改后：

1. 对最终文件执行数字、URL、图片、H2、禁用脚手架术语和 Markdown 扫描。
2. 确认最终归档文件与通过验收的 candidate 加 Round 5 edits 一致。
3. 用 `read` 从开头读取最终交付 Markdown，触发客户端渲染并完成最后一次肉眼检查。
4. 向用户提供最终文件链接与必要的残余风险说明。

最终检查发现机械问题，按 Round 5 修复并再次读取。发现非 surgical 问题，不能以“流程已经结束”为由交付未通过稿件，也不能无限追加 Writer；回到 Round 1，或明确向用户说明 blocker。
