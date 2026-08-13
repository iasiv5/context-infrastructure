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
3. **prose lint CLI 已安装**：直接跑 `external-prose-lint path/to/article.md` 或 `python -m writing_skill.external_prose_lint_cli path/to/article.md`
4. **不要读主仓 `rules/skills/` 下那 5 个桩**——它们只是转发链接，没有内容

## 更新方式

```powershell
# 上游有更新时
cd external_skills/writing-skill
git pull           # 拉上游最新
pip install -e .   # 重装（如果 src/ 有变化）
```

## 与 main 同步的关系

- main 上的 stub 文件 = **main 独占**，iasi 0 改动 → 合并 main 时零冲突
- 本 overlay 文件 + `external_skills/` clone = **iasi 专属**，main 看不到
- 两条线互不干扰