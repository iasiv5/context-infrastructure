# 外部写作 Skill 本地 overlay 路由（iasi 专属）

> 这个文件是 **iasi 专属的**，不属于上游 main 同步范围。main 上的 5 个写作 skill 文件（`workflow_external_writing.md` 等）在 PR #86 之后已经是转发桩，只指向 GitHub。AI agent 不会自动 fetch GitHub URL，所以读桩文件拿不到任何操作流程。
>
> 本文件告诉 AI：**写公众号 / 外部分析文章前，去读本地 clone 的完整 skill 内容。**

## 完整 skill 内容位置

本地 clone：`external_skills/writing-skill/`（独立 git repo，不进主仓 `.gitignore`）。

| skill 文件 | 完整内容在 | 用途 |
|---|---|---|
| 外部写作工作流 | `external_skills/writing-skill/skills/workflow_external_writing.md` | 公众号 / 外部分析文章操作主干 |
| 内部写作工作流 | `external_skills/writing-skill/skills/workflow_internal_writing.md` | 内部 memo / 决策文档 |
| prose 诊断词汇表 | `external_skills/writing-skill/skills/bestpractice_external_prose.md` | Manager 查阅（不进 Writer 上下文） |
| Thesis Catalog | `external_skills/writing-skill/skills/reference_writing_thesis_catalog.md` | L1-L8 启发性分析视角 |
| Prose Lint CLI | `external_skills/writing-skill/skills/external_prose_lint.md` | CLI 用法 |
| **Root 路由** | `external_skills/writing-skill/skills/writing_workflows.md` | 入口，路由 internal vs external |

## AI agent 行为规则

写公众号或外部分析文章时：

1. **先读 root 路由**：`external_skills/writing-skill/skills/writing_workflows.md`
2. **按它路由到 external writing workflow**：读 `external_skills/writing-skill/skills/workflow_external_writing.md` 的完整内容
3. **prose lint CLI**：调用命令见下文「本机运行契约」（旧文「CLI 已安装」指 Windows 工作机，Linux 服务器上未安装，勿直接跑 `external-prose-lint`）。
4. **不要读主仓 `rules/skills/` 下那 5 个桩**——它们只是转发链接，没有内容

## 更新方式

```powershell
# 上游有更新时
cd external_skills/writing-skill
git pull           # 拉上游最新
pip install -e .   # 重装（如果 src/ 有变化）
```

## 本机运行契约（iasi 专属，2026-11-08 实测）

Linux 服务器上 Antigravity CLI（gemini-4-argon-high）与 voice-lora 服务不存在（它们只在工作机上）。缺席时按以下降级执行：

- **写手与冷读**：用调用方 harness 的 fresh-context sub-agent（同一模型档位也可，隔离靠会话）；voice rewrite 由写手 prompt 里的文风硬约束替代。
- **密度门降级**：≤1 处/千字在降级管线上不可达（2026-11-08 实测 8 稿 7 读，下限 ≈2.8 处/千字）。放行线改为：冷读 SHIP + 定性门全过（口吻、thesis 复述、进入理由、数字回收）+ 密度 ≤3 处/千字且连续两轮稳定。要破 1 处/千字，回工作机跑 Antigravity + voice-lora 全链路。
- **源材料落盘**：「读取输入」一步的完成标准是源材料已存为 `draft-*.md` 文件。分享链接（如微信录音笔 share_token）易失效，源材料不能只活在对话上下文里。
- **lint 调用**（宿主 python3 无 pip、ensurepip 被禁，勿走 pip install；PYTHONPATH 直跑已验证）：

```bash
PYTHONPATH=external_skills/writing-skill/src python3 -m writing_skill.external_prose_lint_cli <文章路径>
```

## 与 main 同步的关系

- main 上的 stub 文件 = **main 独占**，iasi 0 改动 → 合并 main 时零冲突
- 本 overlay 文件 + `external_skills/` clone = **iasi 专属**，main 看不到
- 两条线互不干扰