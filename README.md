# Context Infrastructure — Reference Implementation

> English version: [https://github.com/grapeot/context-infrastructure-en](https://github.com/grapeot/context-infrastructure-en)
>
> 背景阅读：[为什么AI只会说正确的废话，以及怎么把它逼出舒适区](https://yage.ai/context-infrastructure.html)

这是一个运行了一年的 context infrastructure 系统的完整结构。主要价值是作为 reference implementation，让你看到系统长什么样、数据如何流动、记忆如何积累。

**核心定位**：这不是开箱即用的工具，而是一个可以参考的蓝图。Clone 下来后，你可以立刻体验「有 context vs 没有 context」的差异。但要让 AI 真正变成你自己的，需要从头采集你的行为数据——没有捷径。

---

## Quick Start（5 分钟）

```bash
git clone https://github.com/grapeot/context-infrastructure
cd context-infrastructure
# 用 VS Code（需安装 GitHub Copilot 扩展）、Claude Code、OpenCode 或 Cursor 打开这个目录
```

然后：打开 [`rules/USER.md`](rules/USER.md)，填写你的基本信息。这是 ROI 最高的一步，完成后 AI 的行为立刻个性化。

详细步骤见 [`setup_guide.md`](setup_guide.md)。

如果你想把它扩展成更完整的工作系统，可以看 [`docs/SKILL_ECOSYSTEM.md`](docs/SKILL_ECOSYSTEM.md)。那里列了一组可单独安装的 public skill repo，例如 Web 搜索、Google Docs、Google Maps、邮件/newsletter、OpenCode、PPTX、社交媒体、支付分析、家庭网络分析和本地 process launcher。`context-infrastructure` 保持轻量；完整能力通过独立 repo 按需安装。

---

## 目录结构

```raw
context-infrastructure/
├── AGENTS.md                    # 根路由表（AI 每次 session 的起点）
├── setup_guide.md               # 配置指引
├── .env.example                 # 环境变量模板
├── CLAUDE.md                    # Claude Code 入口（转发到 AGENTS.md）
├── .github/
│   ├── copilot-instructions.md  # GitHub Copilot 入口（转发到 AGENTS.md）
│   ├── prompts/
│   │   └── ai-heartbeat.prompt.md # AI Heartbeat 主执行命令
│   └── hooks/
│       ├── ai-heartbeat.session-start.json # GitHub Copilot SessionStart 注册文件
│       └── pre-session.ps1      # GitHub Copilot 会话前 hook（调用 heartbeat_preflight）
│
├── docs/
│   ├── CRONTAB.md               # 定时任务配置指南（时间线 + 示例 crontab）
│   └── SKILL_ECOSYSTEM.md       # 可单独安装的 public skill repo 目录
│
├── rules/
│   ├── SOUL.md                  # AI 的身份和行为基调（模板）
│   ├── USER.md                  # 你的偏好和背景（模板）
│   ├── COMMUNICATION.md         # 沟通风格指南（可直接用）
│   ├── WORKSPACE.md             # 目录路由索引
│   ├── axioms/                  # 43 条决策公理（展示层）
│   └── skills/                  # 25+ 个可复用 skill（展示层）
│
├── contexts/
│   ├── memory/
│   │   └── OBSERVATIONS.md      # observer 追加观测、reflector 回看的动态记忆日志
│   ├── survey_sessions/         # 调研报告存放目录
│   ├── daily_records/           # 日常记录存放目录
│   └── thought_review/          # 思考复盘存放目录
│
├── periodic_jobs/
│   └── ai_heartbeat/
│       ├── config/
│       │   └── reminder_policy.json # Windows reminder policy（single-field popup toggle）
│       ├── docs/
│       │   ├── PRD.md           # 记忆系统设计文档
│       │   └── KNOWLEDGE_BASE.md # 观察和反思的 SOP
│       ├── state/
│       │   └── heartbeat_status.json # observer / reflector 的本地状态
│       └── src/v0/
│           ├── heartbeat_preflight.py   # 会话前检查与提醒入口
│           ├── heartbeat_state.py       # observer / reflector 的状态事实源
│           ├── heartbeat_status_cli.py  # success / failed / skipped 自动记账
│           └── jobs/                    # 可选周期任务
│
├── tools/
│   ├── semantic_search/         # 语义搜索（Tier 2）
│   └── share_report/            # 报告发布（Tier 2）
│
└── adhoc_jobs/                  # 按需任务存放目录
```

---

## 三层结构

**展示层（可以参考，不能复制）**：[`rules/axioms/`](rules/axioms/) 和 [`rules/skills/`](rules/skills/) 包含了这个系统积累一年的内容。43 条公理是从具体经历中蒸馏出来的，skills 是从真实项目中总结的。这些代表原作者的视角，对你有参考价值，但不能替代你自己积累的认知。

**可复用层（直接用）**：[`rules/SOUL.md`](rules/SOUL.md)、[`rules/USER.md`](rules/USER.md) 是模板，填写即可使用。GitHub Copilot 用户通过 [`.github/copilot-instructions.md`](.github/copilot-instructions.md) 自动加载 [AGENTS.md](AGENTS.md)；Claude Code 用户通过 [CLAUDE.md](CLAUDE.md) 加载同一套入口。[`rules/COMMUNICATION.md`](rules/COMMUNICATION.md) 是通用的沟通风格指南，大多数人可以直接采用。[`periodic_jobs/ai_heartbeat/`](periodic_jobs/ai_heartbeat/) 提供了记忆系统的实现代码。

默认可用的是 hook 提醒 + `/ai-heartbeat` 显式执行模式：SessionStart hook 或手动运行 [`periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py`](periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py) 检查 observer / reflector 是否逾期；真正处理时，在当前 chat 中运行 `/ai-heartbeat`。observer 负责把当天观测追加到 [`contexts/memory/OBSERVATIONS.md`](contexts/memory/OBSERVATIONS.md)，reflector 负责回看这些观测、清理低价值项，并晋升长期规则。如果你在 GitHub Copilot 里启用了 hooks，这个 workspace 已自带 [`.github/hooks/ai-heartbeat.session-start.json`](.github/hooks/ai-heartbeat.session-start.json)，会在 SessionStart 时调用 [`.github/hooks/pre-session.ps1`](.github/hooks/pre-session.ps1) 并给出提醒。Windows 默认弹窗提醒；若仓库 policy 关闭弹窗，则显示一个 8.88 秒自动消失的轻提醒窗，点击后复制 `/ai-heartbeat`。默认 policy 位于 [`periodic_jobs/ai_heartbeat/config/reminder_policy.json`](periodic_jobs/ai_heartbeat/config/reminder_policy.json)。如果你想做系统级定时审计，再参考 [`docs/CRONTAB.md`](docs/CRONTAB.md)。

**不可复用层**：公理的具体内容、skill 背后的具体经验。理解它们的结构和形成方式，然后从你自己的数据中积累。

---

## License

MIT

