# 设计文档：仓库整理 — Copilot 适配后的内容清理

## 背景与目标

仓库已完成 GitHub Copilot 适配改造（`copilot-instructions.md` → `AGENTS.md` 单一规则源头），但 AGENTS.md 和 README.md 中仍残留 OpenCode 时代的内容描述，需要清理和更新。

**目标**：让所有面向读者的文档反映当前真实状态（Copilot 为主 + Claude Code 偶尔用），去掉已失效的工具特有描述。

## 范围

### 在范围内
1. AGENTS.md — 删除过时内容，OpenCode 特有章节改为通用描述
2. README.md — 更新工具列表、目录结构说明，反映 Copilot 适配
3. setup_guide.md — 同步检查，更新 OpenCode 相关措辞
4. CLAUDE.md — 保留不动（已确认）
5. `.github/copilot-instructions.md` — 检查是否需要同步

### 不在范围
- `m/` 目录的 README 和插件内容
- `rules/` 下的具体规则文件
- `periodic_jobs/` 的代码逻辑

## 方案比较

### 方案 A：逐文件最小化改动（推荐）
- 只改不准确的内容，不-change-没有问题的段落
- 风险低，改动可追溯

### 方案 B：统一重写
- 按当前工具栈重新组织文案
- 风险较高，容易遗漏原有好内容

**推荐方案 A**：最安全，改动精确可控。

## 关键改动清单

### AGENTS.md

| 改动 | 当前内容 | 改为 | 理由 |
|------|---------|------|------|
| 第 3 行 | `> **First time here?** Start with setup_guide.md...` | 删除 | 对所有读者无用（setup_guide.md 已在 README 里被推荐） |
| Sub-agent 模型路由 | OpenCode 配置路径 + category 映射 | 通用描述：各工具有自己的 subagent 机制 | OpenCode 概念不适用于 Copilot/Claude Code |
| Opus 工作模式 | `run_in_background=true` 等参数 + Opus 专属 | 通用原则：高能力模型集中 token 做设计/写作/质量把关 | 参数是 OpenCode 专属的 |
| Skill 速查 | `run_in_background=True` 参数名 | 去掉参数名，只保留语义描述 | 参数名不通用 |
| SessionStart Hook | 不要在模型侧重复实现 askQuestions... 警告 | 简化为中性描述 | Copilot 环境下这个警告不相关 |

### README.md

| 改动 | 当前内容 | 改为 |
|------|---------|------|
| Quick Start 工具列表 | `Claude Code / OpenCode / Cursor` | `GitHub Copilot / Claude Code / Cursor` |
| 目录结构 | 缺少 `copilot-instructions.md` 和 `CLAUDE.md` 说明 | 补充这两项的说明 |
| 可复用层描述 | 未提 Copilot hooks 入口 | 补充简短说明 |

### setup_guide.md

| 改动 | 当前内容 | 改为 |
|------|---------|------|
| Step 3c | 保留旧版 OpenCode 触发器 措辞 | 更新为中性描述 |
| 工具提及 | 偶尔出现 OpenCode 假定 | 同步更新 |

## 未决事项

- 是否需要在 AGENTS.md 里保留一个简短的版本历史或适配说明段落来记录从 OpenCode 到 Copilot 的迁移？（建议不加，保持简洁）
