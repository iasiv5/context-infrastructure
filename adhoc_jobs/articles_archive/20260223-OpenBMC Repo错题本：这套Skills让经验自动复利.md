# OpenBMC Repo错题本：这套Skills让经验自动复利

> 导读：这是一个关于"如何让踩过的坑变成团队的财富"的故事。

## 开篇：那个被重复踩了三次的坑

想象一下这个场景：
周一，小王一脸沮丧："U-Boot 编译又报 size overflow 了，搞了一上午才发现是 include 文件冲突..."
周三，小李同样沮丧："我也遇到 U-Boot 编译问题了，size overflow..."
周五，小张："那个...U-Boot...size overflow..."
如果你笑不出来，那是因为你也在经历同样的事情。

在嵌入式 Linux 开发的世界里，BitBake 构建系统就像一个脾气古怪的老匠人——你永远不知道下一次编译失败是因为什么神仙原因。更可怕的是，**同样的错误会在不同时间、不同人身上反复上演**。

今天，我们要聊的就是 OpenBMC 仓库里的"防坑神器"——**Lesson Learned Hub + 自动归档 Skill 组合拳**。

## 一、Lesson Learned Hub：团队的"错题本"

如果把研发团队比作一个班级，那么 Lesson Learned Hub 就是班级的**共享错题本**。
但它不是那种随手记几笔的笔记本，而是一个有着严格"学术规范"的知识库：

### 四层信息披露架构——像剥洋葱一样展示知识

| 层级 | 作用 | 就像... |
|------|------|---------|
| **L0 索引层** | 全局检索，秒定位 | 图书馆的检索系统 |
| **L1 指导层** | 规范和质量清单 | 写论文的格式要求 |
| **L2 条目层** | 结构化的经验卡片 | 错题本上的标准格式 |
| **L3 深度层** | 完整调查报告 | 硕士毕业论文 |

**举个例子：**

当你的构建报错 `u-boot.bin too large` 时，不需要在 Teams 里@所有人问"有人遇到过吗"，直接检索 Lesson Learned Hub，可能会发现这样一张"经验卡片"：

```yaml
id: LL-2026-001
title: U-Boot partition overflow due to wrong include resolution
component: meta-iasi/machine-config
tags: [ast2700, flash-layout, u-boot, include-collision]
failure_mode: size-overflow
impact: high
```

三秒钟，你就知道问题根因是"BBPATH 解析顺序导致 include 文件冲突"，以及解决方案是"改用唯一文件名并在那里覆盖 flash layout"。

**这就是知识复用的力量。**

## 二、双模板设计：小病小治，大病大治

Lesson Learned Hub 提供了两种"病历模板"：

### 🩹 快速模板（Quick Lesson）
- 适用场景：单问题、影响有限、修复直接
- 填写时间：10 分钟
- 就像：感冒开个药方，记录症状和用药即可

### 🏥 深度模板（Deep Lesson）
- 适用场景：高影响、跨组件、反复发作、诊断曲折
- 填写内容：完整生命周期（检测→诊断→修复→验证→预防）
- 就像：疑难杂症的病历，要记录完整检查时间线和后续康复计划

### 每种经验都有"身份证"
每条 Lesson 都带有一组丰富的元数据标签：
- **topic**: build / boot / kernel / device-tree / packaging / security / ci / tooling
- **failure_mode**: config-drift / size-overflow / dependency-missing / provider-conflict / regression / flaky
- **impact**: low / medium / high / critical
- **confidence**: hypothesis（猜测）/ validated（已验证）
- **sensitivity**: public（公开）/ internal（内部脱敏）/ confidential（仅保留安全信息）

这意味着你可以像筛选电商商品一样精确检索经验：**"我要找所有关于 kernel 的、影响等级 high 的、已验证的 size-overflow 问题"**。

## 三、自动归档 Skill：让知识沉淀"自动驾驶"

好了，前面介绍的是"知识库"，但真正的魔法在于**怎么把知识放进去**。
要知道，工程师修复完 Bug 后的精神状态通常是：

> "终于搞定了！赶紧 commit，下班！"

让他再花 20 分钟写经验总结？不可能的，这辈子都不可能的。
这就是两个 Skills 登场的时候：

---

### 🤖 Skill #1：Fix Complete Sentinel（修复完成哨兵）

这个 Skill 就像一位贴心的助理，默默观察着你的工作状态：
- 监测终端输出 ✅
- 监测构建/测试状态 ✅
- 监听你的成功欢呼（或确认文本）✅

当它检测到"失败 → 成功"的状态转换时，就会跳出来问一句话：
> **"要不要归档这次经验？"**

就这一句话，不多打扰，也不遗漏时机。

**使用示例：**

```bash
# 自动检测日志中的修复完成信号
.github/skills/fix-complete-sentinel/scripts/detect_fix_complete.py \
  --log build.log --had-failure

# 检测 + 一键归档（默认模式）
.github/skills/fix-complete-sentinel/scripts/next_action_after_detect.py \
  --text "Build completed successfully" \
  --had-failure \
  --title "Kernel 编译优化" \
  --component "meta-iasi/linux" \
  --owner "iasi-team"
```

---

### 🤖 Skill #2：Lesson Archiver（经验归档助手）

如果说 Sentinel 是"时机探测器"，那 Archiver 就是"知识录入员"。
当你确认要归档后，它会：

1. **自动收集上下文**：症状、根因、变更文件、验证证据、相关链接
2. **智能选择模板**：根据问题复杂度推荐 Quick 或 Deep 模板
3. **敏感信息脱敏**：自动按照 sensitivity 策略处理机密内容
4. **一键完成流程**：创建条目 → 验证格式 → 重建索引

**使用示例：**

```bash
# 创建经验条目
.github/skills/lesson-archiver/scripts/create_lesson.py \
  --type quick \
  --title "U-Boot 启动失败问题" \
  --component "meta-iasi/u-boot" \
  --owner "iasi-team"

# 完整归档流程（验证 + 索引更新）
.github/skills/lesson-archiver/scripts/archive-after-fix.sh \
  docs/lessons/entries/LL-2025-001.md
```

**最重要的是：整个流程可以在一句话确认后自动完成。**

工程师只需要说"要归档"，剩下的都交给 Skill。从"修复完成"到"经验入库"，全程无缝衔接。

## 四、安全红线：给知识库加把锁

当然，知识库不能成为泄密渠道。系统内置了三级安全防护：

| 级别 | 说明 | 处理方式 |
|------|------|----------|
| 🟢 **Public** | 公开可分享 | 完整记录所有细节 |
| 🟡 **Internal** | 内部使用 | 脱敏敏感值和拓扑信息 |
| 🔴 **Confidential** | 机密 | 仅保留摘要、影响、决策和安全修复步骤 |

**绝对禁止入库存储的内容**：密钥、令牌、私钥、客户标识符、内部基础设施凭证。

安全是底线，便捷是体验，两者缺一不可。

## 五、实战：一句话完成经验归档

现在，让我们看看真实的自动化流程是什么样的。

### 场景：你刚修复了一个 U-Boot 编译问题

**9:00 AM** — 构建失败，终端一片红色
```
ERROR: u-boot-1_2023.10-r0 do_generate_static: u-boot.bin too large
```

**10:30 AM** — 经过排查，你发现是 `BBPATH` 解析顺序导致的 include 文件冲突，修改后重新构建...

**10:35 AM** — 构建成功！终端变绿 ✅

此时，**Fix Complete Sentinel** 已经默默检测到了状态转换（fail → pass），自动弹出提示：

```
🔍 Fix Complete Sentinel 检测到修复完成信号
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
构建状态：失败 → 成功
变更文件：meta-iasi/conf/machine/iasi-2700.conf
相关日志：u-boot.bin size overflow → resolved

要不要归档这次经验？（是/否）
```

**你只需要回复一个字："是"**

然后见证自动化流程的魔力：

| 时间 | 发生了什么 | 你的操作 |
|------|-----------|---------|
| 0s | Lesson Archiver 自动收集上下文 | 等待 |
| 3s | 创建经验条目草稿 | 等待 |
| 5s | 询问：影响等级？（low/medium/high/critical） | 回复：high |
| 8s | 询问：适用范围？ | 回复：machine=iasi-2700 |
| 12s | 自动验证 YAML 格式 | 等待 |
| 15s | 自动重建索引 | 等待 |
| 18s | 提示归档完成，显示文件路径 | 完成！|

**最终输出：**
```
✅ 经验归档完成！
📄 文件：docs/lessons/entries/LL-2025-042.md
🏷️ 标签：u-boot, size-overflow, include-collision, ast2700
🎯 状态：已验证，已索引

下次有人遇到类似问题，可以直接检索到这条经验。
```

**全程耗时：18 秒，你只需要说两次话：**
1. "是"（确认归档）
2. "high"（影响等级）

### 这就是自动化的力量

没有记忆复杂的脚本路径，没有手动复制模板，没有担心格式错误。

系统在你修复成功的**黄金时刻**自动出现，用最少的交互完成最完整的归档。

> 💡 **进阶提示**：对于历史问题的批量归档，或自动检测未覆盖的场景，你也可以手动调用底层脚本。但日常工作中，让 Sentinel （监控修复完成的哨兵）自动检测才是这套系统的最佳打开方式。

## 六、知识复利：让经验像滚雪球

想象一下这个画面：

- 第一个月：10 条经验 → 新人遇到问题时能查到解决方案
- 第六个月：50 条经验 → 形成完整的故障模式图谱
- 第十二个月：100+ 条经验 → 面试候选人时可以直接展示团队的工程深度

这就是**知识复利效应**。

每一条被归档的 Bug，都在为团队的未来投资。

## 结语：让错误有价值

最后，送给大家一句话：

> "聪明的工程师从自己的错误中学习，智慧的工程师让整个团队从自己的错误中学习。"

Lesson Learned Hub + 自动归档 Skill，就是让这种"智慧学习"成为可能的工具。

下次当你修复完一个棘手的 Bug，不妨花 5 分钟把它归档——也许下个月，它就会帮某个同事少熬一个通宵。

## 互动话题

你们团队现在是怎么让AI使用复用技术经验的？来评论区交流一下吧！
---

## 文章摘要（100字以内）

OpenBMC 仓库的 Lesson Learned Hub 是一套防"重复踩坑"的经验管理系统。配合 Fix Complete Sentinel 和 Lesson Archiver 两个自动归档 Skill，工程师只需在修复完成后确认"要不要归档"，即可一键完成经验录入。让每次 Bug 修复都成为团队的知识资产，实现知识复利。

## 配图建议

1. **封面图**：工程师面对电脑，旁边有一个"错题本"图标，体现"把错误变成知识"的主题
2. **第1部分后**：四层架构示意图（金字塔或洋葱图）
3. **第3部分后**：两个 Skill 协作流程图（时间线风格：Bug → 修复 → Sentinel检测 → Archiver归档 → 知识库）
4. **第5部分后**：5步法流程图（带时间标注：5分钟）
5. **第6部分后**：知识复利曲线图（雪球越滚越大）



