# ob-harness 实战：用 Goal-Driven 范式打通端到端源码修改闭环

在姐妹篇《ob dev：一句 Prompt 让 Agent 开改 OpenBMC 源码》中，我们用一句话驱动 Agent 把 OpenBMC WebUI 的旧图标换成了 Apple Logo。这初步证明 Agent 能够直接触碰OBMC的源码开发了。

但真实的工程任务不会像这个Demo Task 这么简单。这次，我们在 ob-harness 中引入 LidangZZZ 提出的 Goal-Driven（目标驱动，简称 GDD）开发范式，重新挑战这个任务。主要验证的是 Agent 从“接受命令”到“系统验证”再到“自动落盘 Git”的端到端（E2E）全自动化闭环能力。

当前主流大模型在 ob-harness 框架下，配合 GDD 范式，究竟能走多远？

> [截图 - lidangzzz 的 goal driven 介绍]

## 第一步：钉死目标与验收红线

引入 lidangzzz 的“Goal-Driven 提示词模板”，我们直接框定终极目标（GOAL），立下明确的验收标准（CRITERIA）：

> [截图 - 党哥的Goal-Driven 提示词模板 https://github.com/lidangzzz/goal-driven/blob/main/readme_cn.md ]

**Goal:** [[[[[把 gb200nvl-obmc 项目的 webui logo 换成NVIDIA公司的logo]]]]]
**Criteria for success:** [[[[[1. 替换项目中所有的 webui logo；2. 使用 QEMU 模拟器验证并提供详细测试报告；3. 代码修改需以合适格式落盘到本地 Git。]]]]]

> [截图 - Claude Code 的会话窗口]

## 第二步：Master 拆解任务，充当“项目经理”

多 Agent 协同工作流中，必须有一个充当大脑的 Master Agent（主控节点）。它上线后没急着写代码，而是先扫读 ob-harness 规则文档，摸清可用工具。它严格遵守 **ob-first** 纪律：优先用现成的 ob 脚本能力解决问题，不盲目造轮子。

> [截图 - master agent 的自我说明]

排查完环境与上下文，Master Agent 像个资深项目经理，将大目标拆解为具体任务清单。为了避免既当裁判又当运动员，它唤醒了一个干活的 Subagent (logo-worker)，将环境参数与执行命令打包下发。

> [截图 - master agent 开始建立监督跟踪，并创建 Subagent 执行任务]

交接完毕，Subagent 带着任务进入后台运行，Master Agent 则转入全局监工模式。

> [截图 - Subagent logo-worker 的自我说明]

让大模型自己跑流程，最怕跑偏或陷入死循环。Master Agent 为此设定了一套防失控机制：每隔 5 分钟查一次岗；无论 Subagent 自己宣布完工还是超时失联，它都会强行介入。同时，它会在替换源码、构建固件、启动 QEMU 验证、提交 Git、最终评估这五个关键节点向我同步进度，保持执行透明。

> [截图 —— Master Agent 对当前系统状态做了简单说明，并详细汇报了它的监督机制]

## 第三步：子节点完工与双重核验

在后台执行期间，Subagent 不仅修改了源码，还熟练调用命令跑完了漫长的编译与 QEMU 验证操作，最后向主节点发出完工信号。

> [截图 - Subagent logo-worker 报告任务完成]

此时，Master Agent 立刻接管控制权。它不轻信 Subagent 的口头汇报，而是亲自下场做独立核验。

> [截图 - Master Agent 开展独立核验]

逻辑闭环判定无误，Master Agent 给出最终绿灯。

> [截图 - Master Agent 评估通过，目标达成。]

为了见证实战成果，我们用内建浏览器访问 QEMU 实例，WebUI 成功挂上了 NVIDIA Logo。

> [截图 —— QEMU下亲眼验证 NVIDIA Logo]

因为我们在验收标准（CRITERIA）中强制要求了 Git 归档，Agent 已经将源码 Patch 与 BB 文件的修改妥善落盘本地仓库。直接 push 即可收工。

> [截图 - 对应的Patch以及BB文件的修改已正确落盘]

## 后记

跑通这次 GDD 实战闭环，我们沉淀出三个工程认知：

1. **约束力决定成败**：Goal-Driven 的灵魂在于边界。封闭的**目标（GOAL）**划定 Agent 发挥的舞台；不可妥协的**判据（CRITERIA）**则是衡量成败的唯一标准。判据必须是强制的，且易于 Agent 进行自动化验证。

2. **机制代偿智能**：ob-harness 自带的 ob CLI 工具是 Agent 绝佳的外脑。与其让大模型消耗 Token 去推理如何编译固件或抓取日志，不如直接调用 CLI 工具去执行。未来的发力方向，是把工作流中那些靠穷举和固定规则就能解决的脏活，坚决下沉和固化到 ob 脚手架里，用**机制**代替**部分智能**。

3. **Thin-Harness 与算力燃烧**：GDD 倡导一种极薄的调度壳（Thin-Harness）。它不锁死中间步骤，赋予了 Agent 极强的自由探测与试错能力；但代价直接且猛烈——那就是 Token 的剧烈燃烧。好在我手上还有“无周限”的 Token 套餐，可以继续高频度试错，探索 ob-harness 与「GOAL 与 CRITERIA设定」的工程最佳实践。

> [截图 - Subagent 复活截图]

---
### 摘要
本文实录了 Goal-Driven 开发范式与 ob-harness 引擎深度结合的实战效果。以“全自动更换 OpenBMC 固件 WebUI Logo”为例，跑通了目标拆解、子节点派发、全局核验到 Git 自动落盘的独立闭环。展现了 AI 在底层基础设施代码自动化改造上的工程潜力。