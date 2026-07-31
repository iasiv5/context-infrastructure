# ob-harness实战：Know-how沉淀机制优化  （未发表）

近期我将 ob-harness 中原先定义的 SKILL 更名为 knowhow，并用实战文章演示了如何沉淀 Agent 踩过的坑。目前作为开源项目，ob-harness 只有一个 knowhow 沉淀目录。不同用户下载使用后，本地踩坑经验容易和上游 knowhow 混搭，引发后续分支同步冲突。发现这个缺陷后，我直接启动 IPDD (Intent & Plan Driven Development) 流程开展机制重构。

向 Agent 下发提示词发起源头追问：`/grill-with-docs 深入分析一下：ob-harness 当前的 know-how沉淀机制是否有值得优化的地方？比如：手动沉淀时，是否有固定的好用的workflow可参考？可否自动化？ai-heartbeat 机制是否可优化？再比如：know-how 沉淀的落点是否可以分为 ob-harness作为开源产品的自带know-how 或者 ob-harness 未来用户沉淀的用户定制（OEM）know-how？`
> [截图：下发提示词开启脑暴]

第一问：明确 ob-harness 产品定位。我将其定位于可分发开源产品，确立后续架构基调。
> [截图：对齐第一问，选择开源产品定位]

第二问：用户定制的 knowhow 存放位置。我将其归置于 `context/knowhow/` 目录，与上游自带内容落实物理隔离。
> [截图：对齐第二问，确立目录层级的物理隔离]

第三问：新建手动沉淀工作流。我制定新建 `workflow_04` 的目标，要求 Agent 排查、清理并合并旧有冗余 knowhow 文件。
> [截图：对齐第三问，确认新建文件与冗余清理]

第三问反馈后，Agent 结合仓库文档与上文沟通，输出归纳的 shared understanding (共识决策树)。
> [截图：Agent 输出梳理好的 shared understanding]

基于这份共识决策树，我补充纠正了两处细节：要求彻底清理已经废弃的 `workflow_03` 及周边链路引用，同时要求基于 Claude Code 与 GHC 双端工具环境分别开发 `/sediment` 自动化提交流程命令。
> [截图：纠正两点细节要求及双端命令设计]

由于下发的补充约束覆盖密集，Agent 判定意图对齐彻底完毕，自行脱离 Grilling 对抗状态，尝试直接落盘写代码。发生典型的自驱滑坡现象。
> [截图：Agent 擅自退出审查，发生典型的“自驱滑坡”并试图写文件]

我立刻执行拦截。强制 Agent 退回 IPDD 流程闭环，要求其通过 `/writing-plans` 生成完整的实施拆解计划，并输出用于启动下一步评审 Agent 的唤醒指令。
> [截图：强制拦截 Agent 滑坡，要求输出计划和评审指令]

经过内部角色三端博弈，实施计划迭代至 V3 版本并予以评审通过，方案进入执行窗口期。
> [截图：实施计划 V3 版本及评审通过记录]

我中止原窗口的直接生成响应，要求 Agent 自主校验并输出当前开发动作的交接步骤。
> [截图：让 Agent 评估执行角色]

当前 Agent 排查后，依据要求输出跨会话 handoff (交接) 文档基线。
> [截图：Agent 梳理输出 handoff 交接文案]

(New Session) 为避免上下文污染干涉，我启动净室 Agent Session，投喂交接文档，令其严格执行既定方案落地。
> [截图：新开会话，贴入 handoff 文案平推执行]

主线代码变更抵达终点后，我唤醒独立顾问 Agent，对新引入架构和工具脚本做全维度的系统评审与意见回拢。
> [截图：独立的顾问 Agent 确认产物无误]

二重评审通过。执行本地代码存盘，将工程节点 PUSH 至远端系统并启动分支请求 (PR)。
> [截图：提交并推送代码开 PR]

代码并入 main 主干。框架知源机制迭代与双端自动化执行指令正式合流。
> [截图：PR 合并入 main 分支界面]

## 后记

至此，ob-harness的经验沉淀路径分为两条：
1、纯手动的 `/sediment` 命令 —— 及时反馈与执行konwhow的沉淀，可人工引导。参考  D:\_context-infrastructure\adhoc_jobs\2026\20260728-ob-harness 实战：把 Agent 踩的坑变成 Know-how.md
2、半自动的`/ai-heartbeat`命令 —— 周期性的对仓库的改动、Agent的变更做【沉淀】、【晋升】与【退役】，knowhow从【晋升】中提炼。

---
**📖 内容摘要**
本文实录 ob-harness 框架 knowhow 沉淀体系底层扩容与自动化提效流程，延续业务单步图解节奏。全程验证 IPDD 方法论的核心基建价值：强硬前置意图收敛边界，有效阻断大语言模型自驱滑坡陷阱，辅以交接文案 (Handoff) 调度净室执行，引入顾问 Agent 夯实交叉验收闭环。