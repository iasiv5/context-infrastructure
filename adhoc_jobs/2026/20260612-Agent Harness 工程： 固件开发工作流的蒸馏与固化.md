```markdown
# Agent Harness 工程：固件开发工作流的蒸馏与固化

> BU6 AI 辅助编程专案 · 第二轮内部技术分享会  
> 2026-06-17 · 武当厅 & Teams  
> 主讲人：Hu.Iasi ｜ TPM

---

## P1 封面

### PPT 主文案

```

Agent Harness 工程：
固件开发工作流的蒸馏与固化

Hu.Iasi ｜ TPM

BU6 AI 辅助编程专案 · 第二轮内部技术分享会
2026-06-17 · 武当厅 & Teams

```

### Speaker Notes

直接翻页。衔接语："先用一页做一个简短的背景衔接。"

---

## P2 从 AI Tool 到 AI Developer，中间缺的是 Harness

### PPT 主文案

```

AI Coding 正在从工具使用，走向任务委派。

模型能写代码，
不代表它能可靠交付。

从"能生成"到"能交付"，中间缺的是 Harness。

```

### Speaker Notes

过去一年，AI Coding 从补全工具走向 Coding Agent。但今天不复习旧定义，也不假设大家听过之前的分享。我们直接从一个工程问题开始：模型已经足够会写代码，为什么在固件开发里仍然不够可靠？答案是：缺 Harness。这场演讲就是要把 Harness 从概念压实为工程动作。

---

## P3 一句话主张

### PPT 主文案

页面正中央，大字：

```

模型会写代码，
Harness 让它按我们的固件流程写对代码。

```

下方小字：

```

模型负责生成；
Harness 负责语境、边界、工具、验证与反馈。

```

### Speaker Notes

这句话是今天整场的核心判断。模型越来越强，但强的是生成能力。固件开发的难点从来不是"写不出代码"，而是"写出来的代码能不能放进我们的仓库、通过我们的验证、符合我们的交付标准"。Harness 做的就是这件事。

---

## P4 裸 Agent 的失败：模型说完成，不等于真的完成

### PPT 主文案

上半部分：

```

Hacker News upvote 实验（IBM · Tejas Kumar）

任务极简：打开链接 → 登录 → 点 upvote
裸 Agent 卡在登录页，
实际操作没有完成，却给出了完成声明。

```

下半部分：

```

在固件开发中，它变成：

1. 不知道自己在哪个项目语境里
2. 不知道哪些规则不能破
3. 不知道怎样才算真的完成

```

底部结论：

```

Harness 的第一价值，不是让 Agent 更聪明；
而是让它更难在错误语境里自信地交付错误结果。

```

### Speaker Notes

这个案例来自 IBM 工程师 Tejas Kumar 的一次公开分享（资料来源：Harnesses in AI, Tejas Kumar, 2025）。换更强的模型、写更细的 prompt，都不一定能解决这类问题。因为问题不在模型能力，而在于 Agent 根本没有 Harness——没有项目规则注入、没有完成标准验证、没有经验持久化机制。去年大家但凡用过 Agent，一定碰到过类似情况：Agent 自称搞定了，你一查发现根本不对。这就是为什么我们要做 Harness 工程。

---

## P5 Coding Agent = LLM + Harness

### PPT 主文案

```

▌ Coding Agent = LLM + Harness

LLM 决定能力上限：
理解、推理、生成。

Harness 决定能力下限：
上下文、工具、规则、流程、验证、反馈、恢复。

```

页面视觉锚点：

```

强模型给上限；好 Harness 保下限。

```
```

▌ Harness 两层结构

Inner Harness — 厂商内置
系统提示词、工具调用、编排流程
用户难以直接干预

Outer Harness — 团队自建 ★
项目规则、领域知识、工作流、验证门禁
BU6 的核心发力点

```

### Speaker Notes

本次演讲直接采用工程定义：Coding Agent = LLM + Harness。Memory、Tools、Rules、Workflow、Validation 都不再是散落的组件，而是 Harness 的组成部分。Claude Code、Cursor、Codex 之所以好用，不全是模型强，更因为外面这层 Harness 做得到位。BU6 的策略很明确：不卷模型，建 Outer Harness。"强模型给上限，好 Harness 保下限"——模型越强，越要把它放进可控的 Harness，否则错误也会被更高质量地包装。

补充一点：这里的 LLM 代表模型能力层，可以是一颗主模型，也可以是多模型协同；重点不是模型数量，而是模型能力必须被 Harness 编排进可靠流程。

（资料来源：20260423 FWC 专案介绍材料 P4-P5）

---

## P6 为什么固件开发特别需要 Firmware-Aware Harness

### PPT 主文案

五张卡片：

```

① 平台差异重
同一功能在不同平台 / 客户 / 分支上的实现路径可能不同。

② 仓库规则深
不懂 OneTree / layer / recipe / machine 规则，就会按社区习惯写错。

③ 开发环境重
OpenBMC 环境初始化、依赖解析、构建链路本身就是工程复杂度。

④ 验证链路长
模型说 done，不等于 build pass / boot pass / smoke pass。

⑤ 质量门禁硬
固件交付不是代码完成，而是证据充分、风险可控。

```

底部收束：

```

通用 Agent 看到的是互联网共识；
Firmware-Aware Harness 要补回项目真实语境。

```

### Speaker Notes

举几个具体例子：同一个 BMC 功能，在 Grace C2、Vera C2、GB300 上的实现路径可能完全不同。BIOS 跨 Intel/AMD/NVIDIA 三大平台，模块接口差异巨大。OneTree BMC 有严格的 recipe/layer/machine 覆盖关系和 Single Source Policy。OpenBMC 环境初始化涉及主仓库克隆、bitbake 初始化、依赖解析、lockfile 生成、bare mirror 缓存填充——一次 build 可能几十分钟到几小时。客户交付有明确的 Definition of Done：Build Pass、Smoke Test Pass、Known Issues 清单、Release Notes。这些壁垒决定了：固件开发不能用通用 Harness，必须用 Firmware-Aware Harness。

对测试团队来说，不需要关心每个 recipe 或 layer 的细节，只需要理解：这些规则决定了代码能不能正确进入目标平台、目标分支和目标交付路径。

（资料来源：20260423 FWC 专案介绍材料；ob-harness v1.0 Release Notes）

---

## P7 蒸馏：把隐性工程判断变成 Agent 可消费资产

### PPT 主文案

左侧——蒸馏四步：

```

观察真实工作流
↓
抽取可复用判断
↓
封装为 Agent 可消费载体
↓
真实任务验证迭代

```

右侧——什么值得蒸馏？

```

高频 / 高风险 / 高隐性 / 高复用 / 高验证

```

底部判断：

```

蒸馏的不只是知识，
而是可复用的工程判断。

```

### Speaker Notes

蒸馏不是"把老工程师的经验写成文档"那么简单。真正的蒸馏还要把开发操作入口本身 Harness 化——不只是告诉 Agent 规则是什么，还要让它有能力操作环境、触发构建、检查状态。具体来说，蒸馏的对象包括开发入口、检查点、验证路径、失败处理方式等。

右边五个词是筛选标准：不是所有东西都要沉淀。高频出现、犯错代价高、新人或 Agent 不容易自然知道、沉淀一次多人可用、能通过 checklist 或 review 判断执行效果——满足这些条件的经验，才值得投入蒸馏。否则就会变成 Agent 不读、人也不维护的死文档。

---

## P8 固化：从个人 Prompt 到团队默认路径

### PPT 主文案

顶部核心判断：

```

蒸馏解决经验从哪里来；
固化解决经验如何不丢、如何复用、如何进入默认流程。

```

四层阶梯（辅助信息，视觉缩小）：

```

L1 个人可复用
Prompt / 本地 Skill / 个人配置

L2 项目可继承
AGENTS.md / README / repo rules

L3 工作台化
CLI / workspace / status / build / memory

L4 流程门禁化
CI / AI PR Review / release checklist

```

页面主视觉，放大：

```

没有默认触发，就不叫固化；
没有验证闭环，就不叫工程。

```

### Speaker Notes

L1 经验随人走，人一离开就没了。L2 经验随项目走，新人 clone 仓库就能获得 AGENTS.md 和 README——已经比 L1 好很多。L3 是工作台化，Agent 不只能读规则，还能操作环境、触发构建、检查状态。L4 是门禁化，流程强制执行，不依赖个人自觉。BU6 的目标：关键经验至少到达 L3，核心质量规则到达 L4。

关于 AGENTS.md 有四句原则：少写背景多写边界、少写知识多写禁区、少写愿望多写检查、少写一次性说明多写可复用规则。200 行以内，每一行对应一次事故或教训，随模型升级频繁瘦身，防止旧约束压制新能力。

（资料来源：20260513 双周例会材料 P6-P7）

---

## P9 失败模式 → Harness 对策

### PPT 主文案

```

BU6 在 AI Coding 推进中反复暴露出的典型问题：

```

| 失败模式 | 本质问题 | Harness 对策 | BU6 落点 |
|---------|---------|------------|---------|
| 按社区习惯写，不符合项目规则 | 不懂项目语境 | 项目规则注入 | AGENTS.md |
| 每次重新摸代码，效率低且易遗漏 | 经验没留下来 | 模块知识沉淀 | README / Skill |
| 聊着聊着就开发，需求设计验证断裂 | 流程没约束 | 规格驱动开发 | S.D.D |
| 会建议修改，但无法进入验证 | 缺执行入口 | 开发工作台封装 | ob-harness |
| 说 done 但没有证据 | 缺完成标准 | 自动化质量门禁 | AI PR Review / CI |

### Speaker Notes

这张表不是穷举，而是我们过去九个月在 BIOS 和 BMC 团队推进 AI Coding 过程中最频繁碰到的五类问题。每一类都有对应的 Harness 对策和落地点。后面四位同事的案例，本质上都是在解决这张表中的某一行或某几行。比如 Wiki 的 BIOS Setup Layout 审查对应第一行和第五行，Mars 的字节需求全流程开发对应第三行，Essie 的发布包校验对应第五行。

（资料来源：20260423 FWC 专案介绍材料 P7-P11）

---

## P10 BU6 固件开发 Harness 闭环

### PPT 主文案

闭环流程图：

```

需求进入
↓
结构化理解         S.D.D / Proposal / Design / Task
↓
项目语境注入        AGENTS.md / README / Domain Rules
↓
开发工作台执行       CLI / workspace / build environment
↓
质量验证           Build / Review / CI / Checklist
↓
经验沉淀           Prompt → Skill → Rule → Script
↓
资产分发           Plugin / Repo Template / Team Standard
↓
下一次任务默认继承 ←────────────────────────────┘

```

右侧四个标签：

```

🔵 蒸馏 → 经验沉淀
🟢 固化 → 资产分发 + 默认继承
🔴 质量赋能 → 质量验证
⭐ 组织复利 → 下一次任务默认继承

```

图旁注释：

```

工程师负责判断、抽取、审核与决策；
Harness 负责让这些判断进入默认流程。

```

### Speaker Notes

这张图是今天整场的总图。蒸馏发生在经验沉淀环节，固化发生在资产分发和默认继承环节，质量赋能发生在验证门禁环节。最关键的是最后一步——下一次任务默认继承。如果经验只沉淀了但没有进入下一次任务的默认路径，那蒸馏就白做了。这个闭环转一圈，团队的 Harness 就厚一层。

注意图旁那句话：Harness 不是替代工程师，而是放大工程判断。蒸馏靠人，固化靠工程，验证靠闭环。

闭环图里有一个节点叫"开发工作台执行"——这不是 PPT 概念，我们已经在建了。下一页花两分钟讲。

---

## P11 从 Prompt 到工作台：ob-harness 作为 OpenBMC Harness 样板工程

### PPT 主文案

上半部分——经验资产升级路径：

```

Prompt
↓
Skill / AGENTS.md
↓
CLI / Workspace               ← ob-harness
↓
Build / Run / Validation Harness
↓
Team Standard / CI Gate

```

右侧标注：

```

Prompt 是草稿纸，不是最终工程资产。

```

下半部分——ob-harness 四象限：

| **Context** | **Workspace** |
|:---|:---|
| rules / skills / memory | source / docs / plans |
| **Execution** | **Feedback** |
| init / build / status / start-qemu* | logs / observations / rules |

三阶段演进（一行）：

```

✅ Context Harness → ✅ Build Harness → 🔧 Run & Validation Harness

```

页面脚注：

```

* start-qemu：developing
  当前定位：样板工程，持续演进中

```

### Speaker Notes

前面讲的是蒸馏和固化的方法论。这一页给一个工程落点。

ob-harness 不是一个 Prompt，也不是一个单点 Skill，而是面向 OpenBMC 的 Harness 样板工程。它把 Context、Workspace、Execution、Feedback 放进同一个工作台，让 Agent 不只读规则，也能逐步进入构建、运行和反馈闭环。

start-qemu 的意义也不是多一个 QEMU 命令，而是让这个工作台从 Build Harness 走向 Run & Validation Harness。

但我要强调：ob-harness 不是今天的第五个案例。它的角色，是未来承载、分发、验证团队经验的样板工作台。

（资料来源：ob-harness public README / AGENTS.md / v1.0 Release Notes）

---

## P12 后四个案例的听众指南

### PPT 主文案

顶部引导语：

```

接下来的四个案例，
请不要只理解成"某个同事用 AI 做了一个功能"。

请带着三个问题去听：

① 这个案例从人工经验里蒸馏了什么？
② 它固化到了什么载体或流程？
③ 它让下一次类似任务少掉了哪类风险？

```

案例导览表：

| 案例 | 不只是在做什么 | 建议观察点 | 可能固化载体 |
|------|-----------|---------|---------|
| BIOS Setup Layout 文档质量审查 | 不只是让 AI 看文档 | 审查经验如何变成检查规则 | Review Checklist / Skill |
| CBS 配置自动化 | 不只是自动改配置 | 重复配置路径如何规则化 | Script / Validation Rule |
| 字节需求全流程开发 | 不只是 Agent 写代码 | 需求到验证如何结构化 | S.D.D Workflow |
| BMC 发布包智能校验 | 不只是检查发布包 | 人工 checklist 如何自动化 | Release Validation Skill |

底部收束：

```

请不要只听"AI 做了什么"，
更要听"经验沉淀到了哪里"。

```

### Speaker Notes

我不评价每个案例做得怎么样——那是大家听完之后自己判断的。我只给一个视角：每个案例的真正价值，不在于用了什么 AI 功能，而在于它把哪段人工经验蒸馏出来了、固化到了什么地方、让下一次任务少了什么风险。带着这三个问题去听，你会发现这四个案例不是零散的 AI 技巧，而是固件开发工作流被工程化、资产化、质量化的过程。这些案例蒸馏出来的经验，未来也可以逐步纳入统一的 Harness 工作台中承载和分发。

---

## P13 总结：错一次，沉淀一次；沉淀一次，团队复利一次

### PPT 主文案

```

固件质量不能只靠人的记忆和责任心。

Harness 的意义，
是把质量经验写进默认路径。

错一次，不只是修这次输出；
而是修下一次不再犯的机制。

```

页面正中央，大字：

```

错一次，沉淀一次；
沉淀一次，团队复利一次。

```

### Speaker Notes

这次活动是字节 & IEC 质量文化共建。所以我用质量的语言来收束：固件质量的终极保障，不是某个人特别仔细，而是系统默认不让错误通过。错一次，要沉淀成规则、Skill、CLI、验证入口或门禁，让同类错误下一次更难发生。Harness 的目的不是炫技，而是把 Agent 从"好玩的工具"变成"可托付的工作流组件"。

好，我的开场到这里。接下来请 Wiki 上台，给大家分享第一个案例。

---

## 结构总览

| 页码 | 标题 | 核心任务 | 时长 |
|------|------|---------|------|
| P1 | 封面 | — | — |
| P2 | 从 AI Tool 到 AI Developer，中间缺的是 Harness | 背景衔接 | 1 min |
| P3 | 一句话主张 | 锚定全场判断 | 1 min |
| P4 | 裸 Agent 的失败 | 建立直觉 | 3 min |
| P5 | Coding Agent = LLM + Harness | 新定义 + Inner/Outer | 3 min |
| P6 | 为什么固件开发特别需要 Harness | 五张卡片 | 3 min |
| P7 | 蒸馏 | 四步 + 筛选标准 | 3 min |
| P8 | 固化 | 四层阶梯 + 金句 | 3 min |
| P9 | 失败模式 → Harness 对策 | 五行映射 | 3 min |
| P10 | BU6 Harness 闭环 | 结构总结图 | 2 min |
| P11 | ob-harness 样板工程 | 只讲结构和演进 | 2 min |
| P12 | 后四个案例听众指南 | 引导视角 | 2 min |
| P13 | 总结 | 质量文化收束 | 1 min |
| | | **总计** | **~27 min** |
```
