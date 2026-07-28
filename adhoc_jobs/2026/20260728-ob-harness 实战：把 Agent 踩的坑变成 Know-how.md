# ob-harness 实战：把 Agent 踩的坑变成 Know-how

最近我把 ob-harness 框架下的 SKILL 改成了 KNOW-HOW，避免和 Agent Skill 中的 Skill 在语义上混淆。

概念理清只是一方面，更重要的是如何把它用起来。在实际开发中，用 GitHub Copilot (GHC) 以 Pure-Agent 模式跑 ob-harness 时，我们常需人工干预它的错误决策。既然干预了，就不能让坑白踩。不同于 /ai-heartbeat 机制那套“observer + reflector + GC/晋升”半自动的隐性收集，本文将实录一次**纯手动发现盲区、阻断错误，并将教训收进 Know-how**的全过程。

## Round 1：首次尝试与逻辑断裂

**任务设定**：新开 GHC 会话，让 Agent 独立下载 OpenBMC 社区代码并尝试编译 `gb200nvl-obmc` machine。

从 COT 里我看到 Agent 有几个误解：

（一）Agent 从 gb200nvl-obmc 项目名推测这是 NVIDIA 的平台，可能不在 OpenBMC 社区代码中，并反复强调这一点；

（二）Agent 虽然检查到当前仓库并没有下载任何版本的 OpenBMC 主仓，仍然坚持用 DRY-RUN 跑一次 ob init，来确认当前是否支持 gb200nvl-obmc 这个 machine。

> Screenshot here: Agent COT 中的两处误解

Agent 的推演基础存在逻辑断裂：DRY-RUN 不会下载社区代码，随后的 machine check 失去物理校验依据。我通过以下方式对其进行阻拦与引导。

> Screenshot here: 对 Agent 进行动作阻拦和引导

并明文要求 Agent 把这条经验补齐，落盘进 ob-harness。

> Screenshot here: 要求 Agent 补齐经验并落盘

## Round 2：踩中交互盲区并强制落盘

**前置条件**：吸收第一步经验后新开会话，使用完全相同的提示词，观察第一条 Know-how 是否生效。

Agent 放弃了 DRY-RUN，但在执行 ob init 时遗漏了跳过交互指令，导致进程在主仓源码地址输入窗口挂起。

> Screenshot here: 卡在 OpenBMC 主仓地址交互窗口

我再次中断进程，将这一教训强制落盘。

> Screenshot here: 再次纠正 + 落盘经验

经验写好后，Agent 果然用上了正确的 --url 参数，并开启了后台自动下载。我手动打断了它的 clone 过程，并让它顺手修掉那个莫名其妙的 clone 命名错误。

> Screenshot here: 使用 --url 参数后台下载，手动打断 clone，并修复 clone 命名错误

## Round 3：经验生效，一次跑通全流程

**前置条件**：带着前两轮强化的护栏再次新开会话，验证能否一次跑通。

Agent 先梳理当前的任务意图和仓库状态，再开始写 to-do list。

> Screenshot here: Agent 梳理任务意图与仓库状态，开始写 to-do list

过程中，第一部分那条 "CWD 中没有 OpenBMC 主仓库时，不要用 DRY-RUN" 的经验正常触发：

> Screenshot here: 经验 1 触发

第二部分那条 "交互场景若卡壳，需自行完成交互或使用 ob 脚本提供的逃生通道" 的经验也正常触发：

> Screenshot here: 经验 2 触发

ob init 顺利完成，进入编译。

> Screenshot here: ob init 完成，开始编译

本地有 Downloads 缓存，整个流程最终一次性快速跑通。

> Screenshot here: 编译完成

## 后记

ob-harness 目前支持的双通道经验积累体系，可以让大家在使用过程中，主动或被动地把和 Agent 协作时踩到的坑，逐步沉淀进 harness 中。本文只是抛砖引玉，供大家参考。我也会另起一篇，专门聊另一种经验沉淀机制 / ai-heartbeat，敬请期待。

## 内容摘要

本文以三次 GHC 会话为例，演示如何在 ob-harness 里纯手动把与 Agent 协作时踩到的坑沉淀成 Know-how，最终经验生效一次跑通。手动沉淀与 /ai-heartbeat 半自动机制互为补充，共同构成 ob-harness 的双通道经验积累体系。