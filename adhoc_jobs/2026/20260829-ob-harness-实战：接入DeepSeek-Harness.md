# 把 ob-harness 接入 DeepSeek Harness，我只用了 9 条符号链接

8 月中旬 DeepSeek 开源 Harness（DSH）后，解析文章已经刷屏。聊它“是什么”的够多了，今天我们来聊点贴近工程的：**一个已经沉淀了大量 AI 资产（Skills）的项目，无缝接入一个新 Harness 的入场费有多贵？**

`ob-harness` 给出的答案是：**9 条符号链接，4 个 Markdown 文件，两个 commit，一小时收口。**

本文将复盘这次接入的全过程。为节省时间，先放出核心结论——跨 Harness 迁移 AI 资产的**三原则**：
1. **单一物理来源**：Skill 实体只存一份。
2. **最小桥接**：为新 Harness 逐条建立软链接。
3. **入口解耦**：不同平台的命令入口互不引用。

---

## 背景：双平台的好日子到头了

此前，ob-harness 的仓库级 Skill 实体一直安居在 `.claude/skills/` 目录下。无论是 Claude Code 还是 GitHub Copilot 都能直接读取。

但 DSH 出现后，现状被打破了：它不认 `.claude/` 目录，通用的 `.agent/` 目录 Claude Code 又不认。

摆在面前的似乎只有两条路：要么把所有 Skill 复制进 `.dsh/skills/`，从此忍受双份维护和必然的逻辑漂移；要么把实体挪到中立目录，给所有平台架设桥接，维护成本直接翻倍。

既然都不想选，只能先扒一扒 DSH 的 Skill 发现机制。

## 摸底：DSH 如何发现 Skill？

翻阅 DSH 源码的 `dsh-skill-filesystem` 模块，其发现机制可以浓缩为一张优先级（Rank）表。同名 Skill 排名越小优先级越高：

| Rank | 来源 | 路径 |
|---|---|---|
| 100 | project-dsh | `<git root>/.dsh/skills/` |
| 200 | project-agents | `<git root>/.agents/skills/` |
| 400 | user-dsh | `~/.dsh/skills/` |
| 500 | user-agents | `~/.agents/skills/` |

适配的核心基于三个机制：
1. `<git root>` 从会话工作目录向上寻找 `.git` 解析，DSH 确实不看 `.claude/`。
2. DSH 接受两种 Skill 形态：内含 `SKILL.md` 的文件夹，或带 Frontmatter 的独立 `.md` 文件（键名仅支持 kebab-case）。
3. **DSH 会跟随符号链接（软链）**，且文件 Watcher 实时生效，修改无需重启。

第三点直接给了破局思路：实体不动，给 DSH 铺一层软链当桥就行。

## 适配实录：从翻车到收敛

### 第一版：想省事，翻了车

最开始想一劳永逸，直接对整个目录建软链：`.dsh/skills -> .claude/skills`。

实测表明，DSH 会遍历目录下的每一个文件。`.claude/skills/` 里的文档（如 `ATTRIBUTIONS.md`）全被误当成 Skill 候选去解析，直接刷了一屏的 Warning。

> [截图：整目录链接产生的 warn 噪音]

教训很直接：**整包软链会引入无关文件导致报错，桥必须逐条搭建。**

### 第二版：9 条链接 + 4 个入口

收敛后的方案分为两类。

**第一类**，针对 9 个常规 Skill（如 brainstorming、grilling 等），逐条建立相对符号链接：
```sh
ln -sfn ../../.claude/skills/<name> .dsh/skills/<name>
```

**第二类**，针对 4 个斜杠命令（如 `/goal-driven`），直接做成三入口的独立 Markdown 文件，分别放在 `.claude/commands/`、`.github/prompts/` 和 `.dsh/skills/`。因为在 DSH 里，命令即 Skill，`/name` 就是调用入口。

> [截图：.dsh/skills 目录 tree，9 条链接 + 4 个 md]
> [截图：DSH 会话里 13 个条目全部可见]
> [截图：/goal-driven 在 DSH 的输入框菜单里跑起来]

最后一张截图印证了方案的成功：此前实战内置的 `/goal-driven` 命令，如今无需重构，原样出现在了第三家 Harness 的菜单里。

### 陷阱实录

过程中踩过的坑，挑三个最痛的：

1. **Frontmatter 键名严格校验**：如果写了驼峰命名（如 `disableModelInvocation`），DSH 会直接拒收整个文件。文件悄悄失效，比报错更难排查。
2. **Rank 覆盖制造假故障**：`~/.agents/skills` 里如果装着同名 Skill，项目版（Rank 100）会永远压过用户版（Rank 500）。排查行为异常时，先想 Rank 覆盖，再看文件内容。
3. **入口耦合差点连坐**：早期 DSH 入口文件写成了去读 `.claude/commands/`，导致 DSH 的命脉拴在了 Claude Code 上。修正后严格遵守“互不引用”，底线是删掉任何一家 Harness 的入口，另外两家必须照常工作。

## 收口：把坑变成 Know-how

这次适配最终沉淀为一条最佳实践（Best Practice）：
1. **单一物理来源**：Skill 实体只在 `.claude/skills/` 维护。
2. **最小桥接**：新增第 10 个 Skill，只需加一条 `ln -sfn` 软链给 DSH。
3. **入口解耦**：多平台的命令入口互不引用。

踩过的坑不能白踩。落进 Harness 沉淀为规则后，它们就会变成下个会话的安全护栏。

当然，方案还有一丝不完美：`/goal-driven` 的提示词模板目前是内联副本，两处代码已经出现了 15 行的逻辑漂移。正确的做法是提取一份中立声明供三方引用，这点已经记入 Know-how，下不为例。

## 彩蛋：顺手给 DSH 写套皮肤

工具接入流顺了，自然想折腾点花样。在深入理解了 DSH 机制后，我顺手为 DSH Web 写了个皮肤插件 [dsh-skins](https://github.com/iasiv5/skins)：默认换上 OpenBMC 主题，支持明暗双态，且能一键还原。

一条命令即可安装：
```sh
dsh plugin --profile web add github:iasiv5/skins#main
```

> [截图：DSH Web 换上 OpenBMC 皮肤，亮暗两态]

接入新生态最优雅的姿势莫过于此：**先用极简成本将其溶入现有工作流，再用一个插件反哺它的生态。**

## 后记

ob-harness 坚持 Build in Public。本次适配仅产生两个 Commit：[f8815ae](https://github.com/iasiv5/ob-harness/commit/f8815aec0f1c28e73881ddc5f887c7313cd3be94) 完成软链和三入口桥接，[364c94e](https://github.com/iasiv5/ob-harness/commit/364c94eed0b7890e13d06adc44a0258ebc1ebca2) 将经验固化为 Know-how。

模型正在商品化，Harness 正在春笋化。Claude Code、Copilot、DSH……明年一定还会有新的平台，每家的接入格式也一定会有所差异。但只要你保持一份 Harness-agnostic（与平台解耦）的 AI 资产，不管搬来多少新邻居，你要做的，不过是再敲一行 `ln -sfn`。

---

**内容摘要**

DeepSeek Harness 开源，本文实录 ob-harness 的极简接入全过程：深扒源码摸清 Skill 发现机制，解决软链翻车与 Rank 覆盖等隐蔽陷阱，最终通过“9 条软链 + 4 个独立入口”完成资产无缝迁移。文末附赠自研 DSH Web OpenBMC 皮肤插件。