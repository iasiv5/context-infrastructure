# Setup Guide: Context Infrastructure

这是 AI 引导的配置指南。按步骤操作，每步完成后立刻能感受到差异。

---

## Step 1：填写身份文件（必填，5 分钟）

**价值**：完成这一步，AI 的行为立刻个性化。这是 ROI 最高的一步。

### 1a. 填写 USER.md

打开 `rules/USER.md`，用自己的信息替换模板内容。

至少填写这几项：
- **称呼**：你希望 AI 怎么叫你
- **时区**：避免时间混乱
- **背景**：你是谁、你做什么
- **技术兴趣**：越具体越好
- **会让你烦的**：帮 AI 避开你讨厌的沟通方式

**验证**：填好后，在 AI 对话里问「介绍一下你对我的了解」，看 AI 是否能准确描述你。

### 1b. 自定义 SOUL.md（可选但推荐）

打开 `rules/SOUL.md`，调整 AI 的核心行为基调。

默认内容已经是通用的良好基础（直接、有观点、不说废话）。如果你有特殊需求，在「氛围」和「核心真理」部分添加你的偏好。

---

## Step 2：探索和扩展 Skills（推荐，15 分钟）

**价值**：理解 skill 的格式，开始积累自己的可复用工作流。

### 2a. 浏览现有 Skills

打开 `rules/skills/INDEX.md`，快速扫描已有的 skill 分类：

- **BestPractice 类**：立刻可用，与你的工具和项目无关
- **Workflow 类**：调研、幻灯片制作、认知画像提取等，需要理解后适配
- **API Guide 类**：⚙️ 标记的需要配置，✅ 标记的可直接用

### 2b. 创建你的第一个 Skill

找一件你经常做的事（调用某个 API、处理某类数据、执行某个工作流），用以下格式创建 `rules/skills/<category>_<name>.md`：

```markdown
# Skill: 名称

## When to Use
什么情况下触发这个 skill

## Prerequisites  
需要什么工具/配置

## 步骤
1. 步骤一
2. 步骤二

## 示例
具体的命令或代码
```

将新 skill 添加到 `rules/skills/INDEX.md` 对应分类。

### 2c. 安装外部 public skill repo

`rules/skills/` 里的内容是 starter set，不需要把所有能力都复制进来。需要更完整的能力时，先看 [`docs/SKILL_ECOSYSTEM.md`](docs/SKILL_ECOSYSTEM.md)。那里列出了一组独立维护的 public skill repo，例如 Tavily、Google Docs、Outlook、Resend、OpenCode、Process Launcher、PPTX、Typefully 和 Stripe。

安装时，把目标 repo URL 交给你的 AI agent，让它从当前 workspace 的 `AGENTS.md` / `WORKSPACE.md` 出发，只暴露一个 root skill。通用技术 contract 留在 public repo；联系人 alias、本地路径、endpoint、token 和业务上下文留在本地 overlay。

### 2d. 关于 Axioms（公理）

`rules/axioms/` 包含 43 条从真实经历中蒸馏的决策原则。这些代表原作者的视角和认知模式，对你有**参考价值**，但不能替代你自己的公理。

建议：
- 先浏览 `rules/axioms/INDEX.md` 了解分类和核心含义
- 遇到共鸣的公理，标注下来
- 未来从你自己的项目经历中积累你的公理（参考同类格式）

---

## Step 3：配置记忆系统（可选，20-30 分钟）

**价值**：让 AI 积累你的工作经验，但不强依赖后台定时任务。

### 3a. 理解三层架构

```raw
L3（全局约束）: rules/ 下所有文件 → 每次 session 被动加载
L1/L2（动态记忆）: contexts/memory/OBSERVATIONS.md → agent 主动检索
```

L3 你已经配置好了（Step 1）。L1/L2 现在有两种运行方式：

1. **手动提醒模式（默认推荐）**：每次会话前检查 observer / reflector 是否过期，再在当前 chat 中运行 `/ai-heartbeat`。
2. **Cron 增强模式（可选）**：如果你愿意配置后台定时审计，再接入系统级调度。

### 3b. 手动提醒模式（默认）

`periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py` 会读取本地状态文件，判断 observer 是否超过 24 小时、reflector 是否超过 7 天，并给出提醒。真正执行 observer / reflector 的统一入口是当前 chat 中的 `/ai-heartbeat`。

先确认这两个入口都能正常响应：
1. `python periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py --help`
2. 确认 `.github/prompts/ai-heartbeat.prompt.md` 已存在，并能在 chat 中作为 `/ai-heartbeat` 使用

如果你在 GitHub Copilot 里启用了 hooks，这个 workspace 已自带 `.github/hooks/ai-heartbeat.session-start.json`；它会在 SessionStart 时调用 `.github/hooks/pre-session.ps1`，后者内部执行 `heartbeat_preflight.py --hook-dialog-spec`。Windows 默认弹窗提醒；若仓库 policy 关闭弹窗，则显示一个 8.88 秒自动消失的轻提醒窗，点击后复制 `/ai-heartbeat`，仍建议你在当前 chat 中运行 `/ai-heartbeat`。默认 policy 位于 `periodic_jobs/ai_heartbeat/config/reminder_policy.json`。

### 3c. 默认执行入口

默认推荐使用 `/ai-heartbeat` 做显式执行。hook 只负责提醒，不直接执行 observer / reflector。
```bash
# 查看当前是否需要执行 observer / reflector
python periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py

# 查看 machine-readable 决策结果
python periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py --command-spec
```

在当前 chat 中运行主命令：

- `/ai-heartbeat`
- `/ai-heartbeat force observer`
- `/ai-heartbeat force reflector`
- `/ai-heartbeat force both`


### 3e. 可选：配置 Cron

如果你希望把手动提醒模式升级为系统级定时审计或提醒集成，再去看 `docs/CRONTAB.md`。真正的 observer / reflector 仍建议在当前 chat 中通过 `/ai-heartbeat` 执行。这一步不是必需的。

### 3f. 验证

先跑一次会前检查，再在当前 chat 中试一次主命令：

```bash
python periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py
```

然后在当前 chat 中运行 `/ai-heartbeat`，确认它能根据当前状态做出默认决策；如需覆盖默认决策，再试一次 `force observer`、`force reflector` 或 `force both`。


查看 `periodic_jobs/ai_heartbeat/state/heartbeat_status.json` 是否已创建，并确认命令输出能说明 observer / reflector 的当前状态。

如果你决定继续走后台调度，再去参考 `docs/CRONTAB.md`；如果不配 cron，手动提醒模式已经可以工作。

---

## Step 4：扩展 Tier 2 组件（按需，30-60 分钟）

以下组件独立工作，按需配置，不配不影响核心功能。

### 语义搜索（⚙️）

当你的 `contexts/` 目录积累了足够多内容后，语义搜索让你能按意思而非关键词检索历史记录。

**需要**：LLM Studio（本地）或 OpenAI API key  
**配置**：参见 `rules/skills/semantic_search.md`

### 分享报告到 Web（⚙️）

将调研报告转为 HTML 并发布到你自己的服务器。

**需要**：一台有 SSH 访问权限的服务器  
**配置**：参见 `rules/skills/share_report.md`，替换 `<your-domain>` 和 `<your-server>`

### 发送邮件通知（⚙️）

让 AI 完成任务后发邮件通知你。

**需要**：Gmail App Password  
**配置**：参见 `rules/skills/send_email.md`

---

## 何时你会感受到系统的价值

**填好 USER.md 后（立刻）**：AI 的回答更有针对性，不再是泛化的通用答复。

**使用 2-3 周后**：`contexts/` 目录里开始积累你的工作记录，AI 可以引用上下文。

**运行 1-2 个月记忆系统后**：observer 开始识别你的工作模式，reflector 把高价值经验晋升为 skill 或 axiom。

**积累 6+ 个月后**：系统开始真正了解你的判断逻辑和决策模式，你会发现 AI 给出的建议越来越接近你自己会做的决定。

---

## 常见问题

**Q：axioms 能直接用吗？**  
A：可以用来理解系统的结构，但核心内容代表原作者的视角。你的 axioms 需要从你自己的经历中提炼。参考 `rules/skills/workflow_cognitive_profile_extraction.md` 了解提炼方法。

**Q：skills 能直接用吗？**  
A：✅ 标记的可以直接用。⚙️ 标记的需要替换配置（endpoint、API key、域名等）。BestPractice 类基本都可以直接用。更完整的工具型能力放在独立 public repo 里，见 [`docs/SKILL_ECOSYSTEM.md`](docs/SKILL_ECOSYSTEM.md)。

**Q：`/ai-heartbeat` 需要什么依赖？**  
A：需要本地 Python 环境、workspace 文件读写权限，以及 `.github/prompts/ai-heartbeat.prompt.md`、`heartbeat_preflight.py`、`heartbeat_status_cli.py` 这条提醒与状态链可用。

**Q：旧兼容入口还能用吗？**  
A：当前方案不再保留这些兼容入口。默认且唯一的执行路径是当前 chat 中的 `/ai-heartbeat`。

---

## 下一步

系统搭好后，真正的积累才刚开始。关键是持续使用：把你的工作放在这个 workspace 里，让 AI 参与每天的工作。随着时间推移，系统会越来越懂你。
