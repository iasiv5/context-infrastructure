# ob-harness V1.0 发布：OpenBMC 固件开发工作台

做 OpenBMC 开发，环境搭建一直是手工活：从克隆主仓库、选 machine、source setup，到拉子仓库、配 externalsrc，每换一台机器就得重来一遍。ob-harness 把这一整串收进一个 `ob` 命令，再给整个仓库配上一套 AI Agent 能直接读懂的上下文框架。V1.0 今天发布。

## 发布说明

ob-harness 是一个 OpenBMC 固件开发工作台。`ob` CLI 把环境初始化、镜像构建和工作区状态收成三条命令：

- `ob init` —— 初始化某个 machine 的开发环境，一条命令跑完从克隆到 externalsrc 注入
- `ob build` —— 选一个已初始化的 machine，跑 bitbake 出镜像
- `ob status` —— 看工作区现在是什么状态

`ob` 不带参数会进入交互菜单，带参数则直接执行，习惯点菜单和习惯敲命令的都照顾到。刚上手 OpenBMC 的话，特别推荐先从菜单模式试起，交互体验专门做了增强。

除了 CLI，仓库本身还内置了一套 AI Agent 上下文框架：把规则、记忆、技能栈结构化进仓库，让 Agent 每次启动自动加载，而不是靠人手动喂 prompt。用 Claude Code 或 GitHub Copilot 打开仓库，session 一启动，Agent 就会自动读取项目规则（身份、沟通风格、目录路由、技能索引），带着上下文做判断，而不是凭 LLM 的通用经验去猜你的代码库长什么样。遇到「这事怎么做」，它先查技能索引再动手；产出的设计文档和实施计划，自动归档到 `docs/`，事后可查。

固件开发要的环境、依赖、调试路径，和 Agent 协作要的上下文，从此共用同一套结构。

## 推荐起手式：左手 Agent，右手 Terminal

ob-harness 支持三种用法。

第一种，全程待在 Agent 输入框里，用自然语言指挥它替你跑初始化、编译、排错。

第二种，全程待在 VS Code 的 Terminal 里，敲 `./ob`，用脚本初始化环境、编译 machine。

不过 V1.0 阶段我最推荐第三种：左手 Agent，右手 Terminal，两边共享同一份上下文。Agent 提的问题、给的输出，你在 Terminal 里敲的命令、系统返回的报错，彼此都在同一个视野里。这样你不用再把一长串编译错误手动贴给 Agent，Agent 也不用隔着一层去猜你的环境现在是什么状态。上下文一旦接上，人和 Agent 才算真正在同一个现场协作。

（配图：左侧 Agent 对话、右侧 Terminal 的协作截图）

## 未来展望

第一，`ob` 会持续补齐 OB 开发的关键功能。已经排进计划的就有两个：`ob dev <recipe>` 把 devtool 的 modify / reset 流程整合进来，`ob start-qemu <machine>` 自动拉起 QEMU 模拟环境。再往后接入测试自动化，Agent 就能自己跑完「开发 → 验证」这条回路，把功能开发和验证连成一体。

第二，新的 OpenBMC 固件开发经验，用 skill 固化下来。每攒够一条能复用的，就沉淀成 `bestpractice_xx` 或 `workflow_xx`，方便以后调用和更新。

第三，自带的 Agent Skill 会继续扩充。V1.0 目前只带两组 slash-command skill：

- 增强版 `/brainstorming`：用于问题探索、需求澄清和脑暴；
- 增强版 `/writing-plans`：承接脑暴后的设计结论，拆成适合 Agent 分阶段执行的编程任务。

两组都源自 obra/superpowers，做了中文化和面向 Copilot 的增强。后面会继续收集好用的 Agent Skill，比如我最近在大量测试 Matt Pocock 的 `/grill-me` 升级版 `/grill-with-docs`，它能把 LLM 的洞察力拉高一个台阶，还能无缝衔接现有的 `/brainstorming` 和 `/writing-plans`。

> P.S. ob-harness V1.0 到目前为止的功能规划、设计定稿和落地执行，大半都靠上面这三个 skill 协助完成（`docs/specs/` 下的 11 份设计文档、`docs/plans/` 下的 12 份实施计划，就是这套流程跑出来的产物）。代码部分，100% AI-made。

如果你对 OpenBMC 开发感兴趣，也经常使用 GitHub Copilot 或 Claude Code，欢迎试用：https://github.com/iasiv5/ob-harness

---

摘要：ob-harness V1.0 正式发布。`ob` 一条命令覆盖 OpenBMC 的环境初始化（init）、镜像构建（build）和工作区状态（status）；仓库还内置一套 AI Agent 上下文框架，Claude Code 或 GitHub Copilot 打开即用。最推荐的用法是左手 Agent、右手 Terminal，两边共享同一份上下文。这套工具自己的设计和实现，大半由它自带的 skill 协助完成，代码 100% AI-made。