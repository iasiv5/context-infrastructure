# 实施计划：从 iasi_workspace 迁移资料到 _context-infrastructure

- **日期**：2026-05-22
- **设计文档**：docs/specs/2026-05-22-migrate-iasi-workspace-design.md
- **状态**：待执行

---

## 目标

将旧工作区 C:\iasi_workspace 中的 129 个文件（5.45 MB）迁移到本仓库，并更新 WORKSPACE.md 路由表。

## 文件结构与职责

| 操作 | 文件路径 | 职责 |
|------|---------|------|
| 创建 | adhoc_jobs/articles_archive/ | 存放 78 篇旧文章归档 |
| 创建 | adhoc_jobs/scripts_archive/ | 存放 4 个旧 Python 脚本归档 |
| 创建 | adhoc_jobs/webpage/ | 存放 40 个旧网页/PPT 归档 |
| 已存在 | docs/plans/ | 合入 2 份旧计划文档 |
| 已存在 | docs/specs/ | 合入 2 份旧设计文档 |
| 修改 | rules/WORKSPACE.md | 添加归档路由说明 |

## 任务清单

### Task 1: 创建目标目录

**操作**：创建 3 个新目录（docs/plans 已跳过，因为 docs/specs/ 已有文件）

**命令**：
```
New-Item -ItemType Directory -Force -Path 'd:\_context-infrastructure\adhoc_jobs\articles_archive'
New-Item -ItemType Directory -Force -Path 'd:\_context-infrastructure\adhoc_jobs\scripts_archive'
New-Item -ItemType Directory -Force -Path 'd:\_context-infrastructure\adhoc_jobs\webpage'
New-Item -ItemType Directory -Force -Path 'd:\_context-infrastructure\docs\plans'
```

**验证**：4 个目录均存在

---

### Task 2: 拷贝文章归档

**操作**：将 C:\iasi_workspace\articles 下 78 个文件拷贝到 adhoc_jobs/articles_archive/

**命令**：
```
robocopy "C:\iasi_workspace\articles" "d:\_context-infrastructure\adhoc_jobs\articles_archive" /E /XD "__pycache__" ".tmp"
```

**验证**：目标目录文件数为 78（排除 .tmp 和 __pycache__ 后）

---

### Task 3: 拷贝脚本归档

**操作**：将 C:\iasi_workspace\scripts 下 7 个文件拷贝到 adhoc_jobs/scripts_archive/，排除 __pycache__

**命令**：
```
robocopy "C:\iasi_workspace\scripts" "d:\_context-infrastructure\adhoc_jobs\scripts_archive" /E /XD "__pycache__"
```

**验证**：目标目录中 .py 文件和 .md 文件数量与源一致

---

### Task 4: 拷贝网页归档

**操作**：将 C:\iasi_workspace\webpage 下 40 个文件整体拷贝到 adhoc_jobs/webpage/

**命令**：
```
robocopy "C:\iasi_workspace\webpage" "d:\_context-infrastructure\adhoc_jobs\webpage" /E
```

**验证**：目标目录中的 HTML 文件和 PPT 子目录均完整存在

---

### Task 5: 拷贝设计文档

**操作**：将旧工作区的 plans 和 specs 合入本仓库

**命令**：
```
robocopy "C:\iasi_workspace\docs\plans" "d:\_context-infrastructure\docs\plans" /E
robocopy "C:\iasi_workspace\docs\specs" "d:\_context-infrastructure\docs\specs" /E
```

**验证**：docs/plans/ 有 2 个文件，docs/specs/ 有 3 个文件（含本次设计文档）

---

### Task 6: 更新 WORKSPACE.md

**操作**：在 WORKSPACE.md 的快速查询区域添加归档目录的路由说明

**修改内容**：在注释行前添加归档路由条目

**验证**：WORKSPACE.md 中包含 articles_archive 的路由条目

---

### Task 7: 最终验证

**操作**：对比源目录和目标目录的文件数量

**验证**：源与目标文件数量一致

---

## 执行纪律

- 按任务顺序执行，不跳步
- 每完成一个任务，运行该任务的验证命令
- 遇到路径不存在、权限问题或文件数量不符，立即停下报告
- 全部完成后运行 Task 7 最终验证