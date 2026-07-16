# AI 写固件：demo 丝滑，上线就翻车？ob-harness 在固件圈把六大支柱跑通  （未发表）

阿里云开发者公众号前几天那篇《数据研发 Multi-Agent 架构的 Harness 工程实践》在 AI 圈刷了屏。作者曹亚龙把这套工程范式浓缩成一句话：LLM 负责理解和创意，Harness 负责约束和验证。文章把它分成三层（身份、执行、进化）和六大支柱（Identity、Orchestration、Context、Gate、Recovery、Evolution），讲得相当系统。

样本全来自数据研发场景。同样的问题换到固件工程师手里会是什么样？我维护的 ob-harness 试着回答了一下。它是面向 OpenBMC 的开发工作台，开源在 GitHub 上。这篇不讲怎么装，重点讲它怎么把六大支柱翻译成固件工程师能跑的命令。

## 一、OpenBMC 交给 AI，第一道坎是哪几条

OpenBMC 这种系统级软件，源码动辄上 GB，构建依赖 Yocto 的 bitbake，一次完整镜像要跑几小时。新人 clone 仓库之后，光是配齐 Python 依赖、下载好 SoC 对应的 QEMU、按 machine 正确绑定源码，就要折腾一两天。把这样的开发环境丢给 AI Agent，遇到的事故和数仓场景其实同病根，只是漂移点换了地方：

- 跳过环境前置检查直接敲 bitbake，等编译跑一半才发现 machine 选择错了；
- 自作主张改编译参数，把另一个项目的 local.conf 串到这台 machine；
- machine 名拿不准就自己随便挑一个现成的；
- 改一行代码，AI 搞不清楚如何用 patch 的方式让临时生效的代码永久落盘到具体的 recipe；
- 编译报错堆栈太长，Agent 抓不到根因，最后一句"编译失败"扔给你，原因去日志里捞。

每条背后都是同一件事：临时口头说的约束、环境依赖、硬件拓扑，在对话窗口里被压缩漂移掉了。"这台 AST2600 用的哪条 defconfig""machine 名只能从这几个枚举值里选"，二十分钟前讲过，二十分钟后 Agent 就可能忘。LLM 自身扛不住长程约束，固件场景对长程约束的依赖又不比数仓少。把抗约束这件事从模型里搬出来，交给一套确定性的工程框架托住，这是 Harness Engineering 的核心命题，也是 ob-harness 想做的事。

## 二、ob-harness 长什么样：一条命令 + 一套上下文

ob-harness 有两个入口。用 Claude Code 或 GitHub Copilot 打开仓库，直接描述需求就行，例如"初始化 romulus 的开发环境""bitbake 报错帮我查""在 QEMU 里启动 romulus"。不想用 Agent 时，`ob` 这条 Shell 命令可以独立跑，不烧 token，不需要 Agent 介入，适合确定性重复操作或想省钱的时候。两个入口的底座是同一套：`ob` 这条命令本身，加上它周围的上下文框架（AGENTS.md、Skill 索引、axioms、ADR）。

双入口是固件场景特有的判断。数仓几乎全部跑在云端，token 成本是运营问题。固件场景里，编译卡在性能受限的本地编译机上，跑一个镜像就要几小时，全程挂着烧 token 的 Agent 是需要掂量的。token 富余时尽管差遣 Agent，紧张时多用 ob CLI，碰到脏活再召唤 Agent，奢俭由人。

## 三、从 Identity 到 Context：前三根支柱怎么落到命令行里

身份、编排、上下文这一组，ob-harness 全用 Markdown 和 Shell 脚本实现。

**Identity：固件场景里要写得更狠**。AGENTS.md 告诉打开仓库的 Coding Agent：你是 OpenBMC 开发助手，工作根目录是这里，遇到"怎么做 X"时先查技能索引再动手，而不是凭猜测。下面更细的 Skill 各自带输入、流程、约束，比如"设计 OpenBMC 新功能""用 QEMU 验证 BMC 改动""排查构建失败"。规则按三档放：硬红线写在最显眼位置（环境动作必须走 ob 前门、不能跳过用户审查）；中等重要的历史教训随项目演进积累（通过 `/ai-heartbeat` 自检晋升）；操作规则按需加载。这套分层和数仓场景的三层金字塔思路完全一致，只是具体红线换了内容。

**Orchestration：ob 这条命令本身就是编排**。看子命令清单就能看明白整个 OpenBMC 开发节奏：`ob init [machine]` 一口气下源码、装依赖、绑定工作区；`ob build` 构建镜像（省略 machine 进交互菜单，带 machine 一步直构可脚本化）；`ob status` 查工作区状态、源码绑定、残留产物；`ob start-qemu` / `ob stop-qemu` 起 / 停 QEMU 实例。每条命令背后都是一段原本要人记下的流程，现在固化成脚本。`ob init` 不止 clone 源码，还会检测平台、解析 machine 的 SoC 型号和对应 QEMU binary、按需配 DL_DIR 和 SSTATE_DIR、刷新 SSH known_hosts、检测残留 PID。所谓"前置依赖自动完成、不问用户不等确认"，在 ob 里被翻译成"源码下载、SoC 识别、缓存配置、health check 全部动手时自动跑"。

**Context：固件项目对加载控制更敏感**。固件项目无关文档太多，一次性塞进上下文代价极高，一个不经意的 Find 可能扫到几 GB 编译产物。ob-harness 用三条机制对抗：项目级目录路由文件（WORKSPACE.md）拦住全盘搜索；Skill 拆成核心层 + 详情层，碰到具体子情景（join 规范、新 machine 初始化规范等）才读对应详情，实在判断不了才回退到全部；设计文档、实施计划、ADR 全部写到 `docs/` 下的 Markdown 文件，下次 Agent 启动按需读取这些文件而不是上一轮的对话历史。文件驱动的原则被延伸到了 Agent 与工具之间，`ob build` 的编译日志、`ob start-qemu` 的串口记录都是文件路径，Agent 读哪个自己决定。

## 四、退出码 3：固件场景独有的恢复信号

Gate 这一支柱固件场景最难落地。数仓的 Gate 主要是格式检查 + SQL 语法校验 + 阶段评审 checklist，相对好自动化。固件场景下，验证一次要么跑几小时编译，要么起 QEMU 或实体 BMC，成本高出一截。ob-harness 在常规四层测试（protocol / unit / orchestration / integration）+ `ob_check.sh` 一站式自检 + GitHub Actions CI 之外，多加了一根特别 CLI 场景才设计得出的暗支柱：退出码契约。

`ob` 把所有子命令的退出码统一成四档：0 成功（或良性无操作）、1 失败或用法错误、2 用户取消不算失败、3 前置缺失（比如 machine 没 init 就想 build）。第三档是关键，它附一句修复提示行（缺啥就提示去补啥），让 Agent 看到这一档时归于"去补前置再重试"，而不是"报错停下"。

数仓场景不需要这根支柱，因为数仓 Agent 主要靠对话协议做状态，不靠 shell 退出码。但固件这种 CLI 主导的场景里它特别昂贵：少了它，Agent 遇到前置缺失会当成硬失败，要么放弃要么瞎编，要么反复发起同样会失败的调用；有了它，Agent 能稳定回退到自己补前置再重试，等于提供了一条 Agent 端的自动恢复机制。整套设计的意义，V1.2 的 release 标题一句话就说完了：**让 ob 成为 agent 可信赖的可靠前门**。

代码评审上，Codex / Claude 生成的代码进 `ob` 仓库前必须过独立 CI 与 ob_check，并通过 code-review Skill 自查。生成者不能既当运动员又当裁判，这一原则在 ob-harness 里被延伸到 Agent 与校验机制的关系上，必须有自动门禁和外部 review 双保险。

## 五、几小时编译不能白跑：固件自带的 Recovery 与 Evolution

**Recovery：固件场景对状态持久化的渴求更直接**。几小时编译跑挂了从头再来，是噩梦级体验。ob 的对策是结构化的工作区状态文件：`ob status` 背后记录哪台 machine 已 init、源码绑定到哪、有没有构建过的镜像、有没有正在跑的 QEMU 实例。任意时刻中止，下次启动读这份文件几秒内就能回到上次断点，不用重跑已完成步骤。`ob start-qemu` 还会按串口 socket 和启动用户过滤 PID，避免多人共用编译机时误杀别人正在跑的 BMC 实例，顺带自动清理陈旧 SSH host key。

**Evolution：ob-harness 本身就是验证样本**。它就是用 AI Coding 做出来的项目，每一次工程改进都是"把错误工程化"的真实案例。机制有两条。

第一条，`/ai-heartbeat` 周期自检。它会定期触发 agent 对整个仓库做观测和反思，把当下发现的问题写进 structured 的 observation 文件；同一问题反复出现，会被晋升成规则或公理写回 `rules/axioms/`，下次 Agent 启动自动加载。仓库里能看到 "docs(memory): ai-heartbeat 2026-07-12 观测写入 + 规则晋升" 这种 commit message，就是这一循环跑完一圈留下的痕迹。

第二条，ADR 制度化。每当有重要设计取舍，就写一份 ADR（架构决策记录）落到仓库里，命名编号追踪。ADR-0003 立住了"所有 OpenBMC 环境动作统一走 ob 这个前门"的约定；ADR-0006 是 QEMU launch profile 抽取的决策；ADR-0007 是 SoC 识别逻辑收敛到单一入口。下次 Agent 看到这段代码时，能读到当初为什么这么设计，而不是拍脑袋自圆其说。

整个项目形成一条闭环：AI 犯错，工程化为门禁 / Skill / ADR，下次自动加载。V1.0 → V1.1 → V1.2 三个 release notes 完整记录了这一过程。

## 六、个人项目，敢不敢对标大厂方案

最常见的质疑很直接：ob-harness 是个人项目，贡献者一两人，跟生产级 Multi-Agent 系统不在一个量级，凭什么值得读。

垂直领域的公开样本本来就稀缺。OpenBMC、bitbake、Yocto 这种重型固件场景下，AI Coding 的实践分享零零散散，ob-harness 把六大支柱在这种场景里逐一落到可跑的机制上，对固件、嵌入式、基础软件领域的工程师是直接能借鉴的。Harness 概念本身就广，小到 `CLAUDE.md`，大到整套 Agent 系统，都算 Harness 工程理念的不同形态。判据不是规模，是机制齐全度。一个小仓库把六大支柱全跑通，反而比大规模系统更透明，更适合当学习样本。再加上固件场景的独有约束（几小时编译、本地编译机、token 预算紧张、CLI 主导、退出码契约），这些是数仓方案覆盖不到的盲区，ob-harness 在每一根支柱上都给了对应方案。

另一种质疑更尖锐：给 Agent 上这么多规矩，是不是反而限制了它的能力。其实恰恰相反。固件这种长任务、高约束、高风险的场景里，给 Agent 一套可信赖的机制，恰恰是它真正能进入生产流程的前提。可预测了才有信用，有信用了才敢把几小时编译、关键网络接口、线上 BMC 交给它。

Harness Engineering 未来要么成为 AI 时代的 DevOps 标准学科，要么被更强的模型吸收成过渡性补丁。两种走向 ob-harness 都准备着，做法是每一根支柱都尽量模块化、可独立移除：`ob` 是普通 Shell 脚本随时可换；AGENTS.md 是 Markdown 换一家 Agent 读；Skill 是纯文本描述能本地跑能跨平台分；ADR 是可版本化的决策记录不需要 AI 工具也能读。即便未来模型内化了流程编排、上下文管理、自我校验的能力，沉淀下来的工程经验也不会浪费。它们就是 Markdown、Shell 脚本、ADR 记录，换个底座继续用。

---

如果你在自己的领域里也撞上"AI demo 丝滑、生产流程不敢用"的问题，阿里那篇六大支柱提供了一份完整的 checklist，ob-harness 提供一份可读的小型参考实现。

仓库地址：https://github.com/iasiv5/ob-harness

致谢 context-infrastructure 项目（鸭哥 grapeot）的架构启发，以及前面提到的阿里文章给本文提供了理论锚点。

---

**摘要**：阿里那篇《数据研发 Multi-Agent 架构的 Harness 工程实践》给出了完整的 Harness 工程理论框架（身份 / 执行 / 进化三层 + Identity / Orchestration / Context / Gate / Recovery / Evolution 六大支柱），但落地样本全在数仓领域。本文把开源的 OpenBMC 开发工作台 ob-harness 作为一份固件领域的镜像，逐一对照六大支柱在垂直工程领域的具体形态：ob CLI 把编排物理化为命令；AGENTS.md + Skill + axioms 把身份分层落实；渐进式 Context 管理对抗固件项目庞大的无关信息；四层测试与退出码契约构成固件场景独特的 Gate；`ob status` 和 QEMU PID 管理提供固件长任务必备的 Recovery；`/ai-heartbeat` 与 ADR 制度跑通 Evolution 飞轮。结论：Harness Engineering 是跨场景范式，垂直领域也能完整跑通，大小不是决定因素，机制是否齐全才是。