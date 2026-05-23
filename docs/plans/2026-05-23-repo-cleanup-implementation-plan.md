# 实施计划：仓库整理 — Copilot 适配后的内容清理

> 设计文档：`docs/specs/2026-05-23-repo-cleanup-design.md`

## 目标

清理 AGENTS.md、README.md、setup_guide.md 中残留的 OpenCode 时代内容，让文档反映当前真实状态（Copilot 为主 + Claude Code 偶尔用）。

## 文件结构与职责

| 文件 | 职责 | 操作 |
|------|------|------|
| `AGENTS.md` | 仓库根路由表，AI session 起点 | 修改 5 处 |
| `README.md` | 面向开源读者的仓库说明 | 修改 3 处 |
| `setup_guide.md` | 配置指引 | 修改 2 处 |
| `CLAUDE.md` | Claude Code 入口转发 | 不动 |
| `.github/copilot-instructions.md` | Copilot 入口转发 | 不动 |

## 任务清单

### Task 1：AGENTS.md — 删除 First time here 行

**位置**：`AGENTS.md` 第 3 行
**改动**：删除 `> **First time here?** Start with \`setup_guide.md\` — it'll walk you through setup in under an hour.`
**验证**：文件中不再包含 "First time here" 字样；相邻行（空行和 `This folder is home.`）保持完好。

---

### Task 2：AGENTS.md — SessionStart Hook 简化措辞

**位置**：`AGENTS.md` → `## SessionStart Hook: AI Heartbeat` 章节下方段落
**当前内容**：
```
AI Heartbeat 的会前选择框和本地执行现在都由 `.github/hooks/pre-session.ps1` 直接处理。

不要在模型侧重复实现 askQuestions、pending 文件消费协议、或额外的会前任务消费逻辑，除非你确认 SessionStart hook 本身失效。
```

**改为**：
```
AI Heartbeat 的会前选择框和本地执行现在都由 `.github/hooks/pre-session.ps1` 直接处理。SessionStart hook 会在新会话开始时自动执行 `heartbeat_preflight.py`，检查 observer / reflector 是否到期并给出提醒。
```

**验证**：段落中不再包含 "不要在模型侧重复实现" 或 "pending 文件消费协议" 字样。

---

### Task 3：AGENTS.md — Skill 速查通用化

**位置**：`AGENTS.md` → `### 常用 Skill 速查` → 并行 Subagent 条目
**当前内容**：
```
- 准备调用 `run_in_background=True` 前，先把这个 skill 读一遍再执行  
- 派出 agent 后等系统通知即可，不需要轮询
```

**改为**：
```
- 准备使用并行 subagent 前，先把这个 skill 读一遍
- 派出 agent 后等系统通知即可，不需要轮询
```

**验证**：段落中不再包含 `run_in_background=True` 字样。

---

### Task 4：AGENTS.md — Sub-agent 模型路由通用化

**位置**：`AGENTS.md` → `## Sub-agent 模型路由`
**当前内容**（整个章节）：
```
## Sub-agent 模型路由

配置文件：`~/.config/opencode/oh-my-opencode.json`

常用路由速查：
- **Gemini 3 Pro**（创意、brainstorm、非常规思路）→ `category="artistry"`
- **Sonnet 4.6**（执行、调研、代码）→ `category="deep"` 或 `category="unspecified-high"`
- **Haiku 4.5**（轻量任务）→ `category="quick"`
- **Opus 4.6**（最难的逻辑/架构）→ `category="ultrabrain"`

创意性工作（brainstorm、文章结构、观点碰撞）默认派一个 Gemini（artistry）在后台跑，和自己的思考并行。用户说「调 Gemini」→ artistry，说「调 Sonnet」→ deep。
```

**改为**：
```
## Sub-agent 模型路由

不同工具有各自的 subagent 机制和模型选择策略。当前主用 GitHub Copilot，偶尔用 Claude Code：

- **GitHub Copilot**：subagent 由 Copilot 自动调度，无需手动配置路由
- **Claude Code**：如需指定模型或并行 subagent，参考自身配置文件

创意性工作（brainstorm、文章结构、观点碰撞）可考虑在后台跑一个独立 agent，与主线程并行推进。
```

**验证**：段落中不再包含 `opencode`、`oh-my-opencode`、`category="artistry"` 等 OpenCode 特有字样。

---

### Task 5：AGENTS.md — Opus 工作模式通用化

**位置**：`AGENTS.md` → `## Opus 工作模式`
**当前内容**（整个章节）：
```
## Opus 工作模式

如果你的模型 ID 包含 `opus`，以下规则生效：

**你的 context window 很宝贵。** Opus 的核心能力是设计、质量把关和写作。调研、写脚本、关键词检索这些事交给 sub-agent。你的两个主要任务：（1）**设计**：拆分问题、设计计划、分配 sub-agent 任务；（2）**写作与质量把关**：最终文本自己写，sub-agent 结果自己验证。写代码、调研、数据处理全部 delegate，写作和质量验证绝不外包。设计任务拆分时默认考虑并行性（`run_in_background=true`）。
```

**改为**：
```
## 高能力模型工作模式

当使用高能力模型（如 Opus、Sonnet 等）时，注意 token 预算的合理分配：

- **设计**：拆分问题、设计计划、分配 sub-agent 任务
- **质量把关与写作**：最终文本自己写，sub-agent 结果自己验证
- **调研和数据处理**：交给 sub-agent 执行

核心原则：把 token 预算集中在只有高能力模型才能做好的事情上，常规执行类工作交给 sub-agent。
```

**验证**：段落中不再包含 `run_in_background=true` 字样；章节标题从 "Opus 工作模式" 变为 "高能力模型工作模式"。

---

### Task 6：README.md — Quick Start 工具列表更新

**位置**：`README.md` → Quick Start 代码块
**当前内容**：
```
# 用 Claude Code / OpenCode / Cursor 打开这个目录
```

**改为**：
```
# 用 GitHub Copilot / Claude Code / Cursor 打开这个目录
```

**验证**：文件中不再包含 "OpenCode" 字样（在这个位置）。

---

### Task 7：README.md — 目录结构补充

**位置**：`README.md` → 目录结构代码块
**当前内容**：
```
├── .github/
│   └── hooks/
│       ├── ai-heartbeat.session-start.json # GitHub Copilot SessionStart 注册文件
│       └── pre-session.ps1      # GitHub Copilot 会话前 hook（调用 heartbeat_preflight）
```

**改为**：
```
├── CLAUDE.md                    # Claude Code 入口（转发到 AGENTS.md）
├── .github/
│   ├── copilot-instructions.md  # GitHub Copilot 入口（转发到 AGENTS.md）
│   └── hooks/
│       ├── ai-heartbeat.session-start.json # GitHub Copilot SessionStart 注册文件
│       └── pre-session.ps1      # GitHub Copilot 会话前 hook（调用 heartbeat_preflight）
```

**验证**：目录结构中包含 `copilot-instructions.md` 和 `CLAUDE.md` 的说明行。

---

### Task 8：README.md — 可复用层补充 Copilot hooks 说明

**位置**：`README.md` → `**可复用层（直接用）**：` 段落
**当前内容**中提到 GitHub Copilot hooks 的部分：
```
如果你在 GitHub Copilot 里启用了 hooks，这个 workspace 已自带 `.github/hooks/ai-heartbeat.session-start.json`，会在 SessionStart 时调用 `.github/hooks/pre-session.ps1`；
```

这段已经在描述 Copilot 了，但缺少入口文件的说明。在 `快速开始` 段落后、`如果你在 GitHub Copilot` 之前，补充入口说明。

**改为**（在「填写即可使用。」之后插入一句）：
```
GitHub Copilot 用户通过 `.github/copilot-instructions.md` 自动加载 `AGENTS.md`；Claude Code 用户通过根目录 `CLAUDE.md` 加载。
```

**验证**：可复用层段落中包含 `copilot-instructions.md` 和 `CLAUDE.md` 的提及。

---

### Task 9：setup_guide.md — Step 3c 更新

**位置**：`setup_guide.md` → `### 3c. 可选：保留旧版 OpenCode 触发器`
**当前内容**：
```
### 3c. 可选：保留旧版 OpenCode 触发器

默认推荐使用 `heartbeat_local_runner.py` 做本地 direct-exec。只有在你明确要兼容旧版 OpenCode 流程时，才需要继续保留 `observer.py` / `reflector.py` 及其相关依赖。
```

**改为**：
```
### 3c. 兼容性说明

默认推荐使用 `heartbeat_local_runner.py` 做本地 direct-exec。`observer.py` / `reflector.py` 保留在目录中作为兼容参考，日常使用不需要关注。
```

**验证**：标题不再包含 "旧版 OpenCode" 字样。

---

### Task 10：setup_guide.md — FAQ 中 OpenCode 引用更新

**位置**：`setup_guide.md` → 常见问题 Q&A → observer.py / reflector.py 问题
**当前内容**：
```
**Q：observer.py / reflector.py 还能用吗？**  
A：可以，但它们现在属于旧版 OpenCode 触发器，主要用于兼容或迁移，不再是默认推荐路径。
```

**改为**：
```
**Q：observer.py / reflector.py 还能用吗？**  
A：保留在目录中作为兼容参考，默认推荐使用 `heartbeat_local_runner.py`。
```

**验证**：回答中不再包含 "旧版 OpenCode 触发器" 字样。

---

## 执行纪律

1. 按任务顺序执行，不要跳步或合并步
2. 每完成一个任务，运行该任务的验证检查
3. 遇到仓库实际情况与计划不符时，立即停下说明，不要猜
4. 全部完成后运行最终验证

## 最终验证

完成所有任务后，执行以下检查：

1. **全文搜索 `OpenCode`**：在 `AGENTS.md`、`README.md`、`setup_guide.md` 中搜索 "OpenCode"，确认仅在合理的上下文（如历史说明）中出现，不再有工具假定或配置引用
2. **全文搜索 `run_in_background`**：确认三个文件中不再包含此参数
3. **全文搜索 `opencode`**（不区分大小写）：确认不再引用 `oh-my-opencode.json` 或 `~/.config/opencode/`
4. **全文搜索 `copilot-instructions.md`**：确认 README.md 中有对应的目录结构说明
5. **通读 AGENTS.md**：确认整体连贯，没有因删除/替换导致的段落断裂或悬空引用
6. **通读 README.md**：确认目录结构与实际文件一致，工具列表准确

最终验证命令：
```powershell
Select-String -Path "AGENTS.md","README.md","setup_guide.md" -Pattern "OpenCode|opencode|oh-my-opencode|run_in_background" -CaseSensitive:$false
```
预期结果：返回的匹配应为零或仅在 setup_guide.md 兼容性说明中出现的 `observer.py` / `reflector.py` 上下文里，不应出现工具假定或配置引用。
