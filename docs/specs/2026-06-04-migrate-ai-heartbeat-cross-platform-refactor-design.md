# AI Heartbeat 跨平台重构迁移设计文档

## 背景与目标

子仓库 `openbmc-aware-harness` 在 commit `228d27f8` 中将 `ai-heartbeat.prompt.md` 从"厚文件"重构为"薄壳 + SOP 分离"架构。主要改动：

- 将完整的 observer/reflector 执行合同从 prompt 文件抽离到独立的 `AI_HEARTBEAT_SOP.md`
- 将硬编码的 Windows PowerShell 路径替换为 OS 探测逻辑（`<PYTHON>` 占位符）
- 新增 `.claude/commands/ai-heartbeat.md` 作为 Claude Code 入口
- 两个平台入口（Copilot / Claude Code）共享同一份 SOP，消除平台耦合和内容重复

主仓库的 `ai-heartbeat.prompt.md` 仍是重构前的旧版厚文件（硬编码 `.\.venv\Scripts\python.exe`，无 OS 探测，无 SOP 分离）。

**目标：** 将这次重构的运行时文件迁移到主仓库，使主仓库获得跨平台能力。

**成功标准：** 迁移后主仓库的 `/ai-heartbeat` 在 Windows 和 Linux 上都能正常工作，Copilot 和 Claude Code 两个入口共享同一份执行合同。

## 范围

迁移以下 3 个文件：

| # | 操作 | 文件 | 说明 |
|---|---|---|---|
| 1 | 修改 | `.github/prompts/ai-heartbeat.prompt.md` | 厚文件（~100 行）→ 薄壳（~22 行），OS 探测 + SOP 引用 |
| 2 | 新增 | `periodic_jobs/ai_heartbeat/docs/AI_HEARTBEAT_SOP.md` | 执行合同单一事实来源（~117 行） |
| 3 | 新增 | `.claude/commands/ai-heartbeat.md` | Claude Code 的 `/ai-heartbeat` 入口薄壳（~19 行） |

## 非范围

- 设计文档和实施计划（子仓库中的 `docs/specs/002-*` 和 `docs/plans/003-*`）不搬入主仓库
- Python 脚本（`heartbeat_preflight.py`、`heartbeat_status_cli.py`、`heartbeat_state.py`）— 已验证两边完全一致，无需迁移
- Hooks（`pre-session.ps1`、`ai-heartbeat.session-start.json`）— 已验证两边完全一致
- 测试文件 — 已验证两边完全一致
- 配置文件（`reminder_policy.json`、`KNOWLEDGE_BASE.md`、`PRD.md`）— 两边有仓库特定的差异，各自独立演进，不需要同步
- 建立自动同步机制（未来可考虑，但不在此范围内）

## 方案比较

### 方案 A：手动逐文件复制

把子仓库 commit 中的 3 个文件手动复制到主仓库对应路径。

优点：简单、可控。

缺点：两个仓库之间没有同步机制，未来再改需再次手动搬运。

### 方案 B：git format-patch + git am

从子仓库导出 commit 为 patch 文件，在主仓库用 `git am` 应用。

优点：保留原始 commit message 和 author 信息。

缺点：patch 包含 5 个文件（含 2 份设计/计划文档不需要的文件），需要手动 edit hunk 剔除；路径不对齐时处理冲突麻烦。

### 方案 C：git checkout 从子仓库提取指定文件

在主仓库里用 `git --git-dir=openbmc-aware-harness/.git checkout 228d27f -- <file>` 从子仓库的 git 对象提取指定文件。

优点：精确（只拿 3 个文件）、干净（不经过 patch）、可复现。

缺点：需要逐个文件执行命令。

## 推荐方案

**方案 C**。精确拿取、不引入不需要的文件、命令可复现。方案 A 等价但靠人工复制更容易出错；方案 B 引入不需要的设计文档且处理繁琐。

主要 trade-off：搬运后两仓库各自拥有一份独立的 SOP，没有自动同步机制。未来改动需手动对齐。

## 关键边界与组件职责

### 迁移前架构

```raw
ai-heartbeat.prompt.md (厚文件，~100 行)
├── YAML frontmatter
├── 启动约束
├── 输入解释
├── 决策输入（硬编码 .\.venv\Scripts\python.exe）
├── 默认决策表
├── observer 合同
├── reflector 合同
└── 输出要求
```

单一入口，所有内容内联，Windows 路径硬编码。

### 迁移后架构

```raw
.github/prompts/ai-heartbeat.prompt.md (薄壳，~22 行)  <- Copilot 入口
├── YAML frontmatter
├── OS 探测（python -> .venv fallback）
└── 读取 periodic_jobs/ai_heartbeat/docs/AI_HEARTBEAT_SOP.md

.claude/commands/ai-heartbeat.md (薄壳，~19 行)  <- Claude Code 入口
├── OS 探测（同上）
└── 读取 periodic_jobs/ai_heartbeat/docs/AI_HEARTBEAT_SOP.md

periodic_jobs/ai_heartbeat/docs/AI_HEARTBEAT_SOP.md (合同，~117 行)  <- 单一事实来源
├── 启动约束（读取 AGENTS.md / KNOWLEDGE_BASE.md / PRD.md）
├── 输入解释
├── 决策输入（<PYTHON> 占位符）
├── 默认决策表 + override
├── observer 合同
├── reflector 合同
├── 写入工具注释
└── 输出要求
```

两个入口薄壳职责相同：OS 探测 -> 确定 `<PYTHON>` -> 引导 agent 读取 SOP -> 替换占位符 -> 完整执行。

## 数据流 / 控制流

```raw
用户触发 /ai-heartbeat
       |
  平台入口薄壳
       |
  OS 探测 -> 确定 <PYTHON>
       |
  读取 AI_HEARTBEAT_SOP.md
       |
  读取 AGENTS.md / KNOWLEDGE_BASE.md / PRD.md
       |
  执行 <PYTHON> heartbeat_preflight.py --command-spec
       |
  根据 recommended_action 决定执行路径
       |
  observer / reflector 执行
       |
  heartbeat_status_cli.py 记账
```

## 错误处理与回退

| 场景 | 处理策略 |
|---|---|
| prompt 文件覆盖后内容丢失 | 已验证：主仓库当前版本与子仓库 refactor 前的版本二进制一致，无丢失风险 |
| SOP 引用的路径在主仓库不存在 | 已验证：SOP 引用的全部路径在主仓库全部存在 |
| `<PYTHON>` 探测失败（两个路径都不可用） | SOP 入口薄壳已处理：停止并提示用户确保 Python 可用 |
| `.claude/` 目录在主仓库不存在 | 由 git 自动创建，不涉及 `.gitignore` 排除 |
| observer 对 OBSERVATIONS.md 的写入静默失败 | SOP 中已包含写入验证和 heredoc 回退策略 |

## 风险分析

### 已验证无风险

| 检查项 | 验证方法 | 结果 |
|---|---|---|
| prompt 文件前驱一致性 | `fc /b` 二进制对比主仓库 vs 子仓库 refactor 前版本 | 完全一致 |
| Python 脚本一致性 | `fc /b` 对比 3 个脚本 | 完全一致 |
| Hooks 一致性 | `fc /b` 对比 | 完全一致 |
| 测试文件一致性 | `fc /b` 对比 3 个测试 | 完全一致 |
| SOP 路径兼容性 | `Test-Path` 验证全部引用路径 | 全部存在 |
| KNOWLEDGE_BASE.md 语义完整性 | grep 验证 observer/reflector 关键语义 | 包含全部必要定义 |

### 需注意的差异（不影响功能）

| 文件 | 差异 | 原因 | 影响 |
|---|---|---|---|
| `reminder_policy.json` | 子仓库 `false`，主仓库 `true` | 仓库特定偏好 | 无。不涉及 SOP 执行路径 |
| `KNOWLEDGE_BASE.md` | 内容有差异 | 各自独立演进 | 无。主仓库版本包含全部必要语义 |
| `PRD.md` | 内容有差异 | 各自独立演进 | 无。同上 |

### 长期维护风险

- **缺乏自动同步机制**：未来任一仓库修改 SOP 或入口文件，另一仓库不会自动收到更新。需要在 commit message 或 CHANGELOG 中标注跨仓库影响。
- **代码块 language hint 变化**：新 SOP 把 ` ```powershell ` 改为 ` ```text `，如果有外部工具依赖 language hint 解析代码块，行为会改变。对 Copilot/Claude Code agent 无影响。

## 测试策略

### 手动验证步骤

迁移完成、commit 前执行以下验证：

1. **文件完整性**：逐一确认 3 个文件内容与子仓库 `228d27f8` 中的版本一致
2. **Copilot 入口**：在 VS Code 中运行 `/ai-heartbeat`，确认 OS 探测正常、SOP 被正确引用
3. **跨平台探测**：分别在 Windows（`.venv\Scripts\python.exe`）和 Linux（系统 `python`）下确认 OS 探测逻辑命中正确路径

### 持续验证

- 现有测试（`test_heartbeat_preflight.py`、`test_heartbeat_status_cli.py`、`test_heartbeat_state.py`）不受影响，可在主仓库直接运行 `pytest` 确认

## 已决事项

- **两仓库自动同步机制**：不需要。子仓库和主仓库各自独立演进，SOP 修改时通过 commit message 标注跨仓库影响即可。