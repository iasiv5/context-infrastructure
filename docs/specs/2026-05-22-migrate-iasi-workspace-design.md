# 设计文档：从 iasi_workspace 迁移资料到 _context-infrastructure

- **日期**：2026-05-22
- **状态**：待审批

---

## 1. 背景与目标

用户在 C:\iasi_workspace 有一个旧工作区，积累了大量公众号文章、Python 脚本、网页/PPT 和设计文档。现在需要将这些历史内容迁移到当前活跃工作区 d:\_context-infrastructure，并让未来的日常工作（写文章、写脚本、做调研、存资料）也在本仓库进行。

## 2. 范围

### 2.1 迁移范围

| 源目录 | 内容 | 目标位置 |
|--------|------|---------|
| C:\iasi_workspace\articles\* | 80+ 篇公众号文章（.md / .docx） | adhoc_jobs\articles_archive\ |
| C:\iasi_workspace\scripts\* | 4 个 Python CLI + README | adhoc_jobs\scripts_archive\ |
| C:\iasi_workspace\webpage\* | 静态 HTML 页面 + 演讲 PPT 目录 | adhoc_jobs\webpage\ |
| C:\iasi_workspace\docs\plans\* | 2 份实施计划 | docs\plans\ |
| C:\iasi_workspace\docs\specs\* | 2 份设计文档 | docs\specs\ |

### 2.2 不迁移（保留在旧工作区）

- claws/ -- Claude Code agent 配置，不在新工作区使用
- m/plugins/iasi/ -- VS Code 插件配置，已在全局 agent-plugins 目录生效
- logs/ -- 历史运行日志，不需要留存
- autotrade/ -- 一次性产物，无长期价值
- .claude/, .github/, .venv/ -- 旧工作区基础设施配置

## 3. 方案说明

### 核心原则

- 归档优先：旧内容统一放 adhoc_jobs/ 下的归档子目录，不对活跃目录造成干扰
- 保持原样：文件名、内部目录结构不做改动，直接平移
- 未来衔接：新的文章创作、脚本开发、调研成果按 WORKSPACE.md 现有路由规则走

## 4. 执行方式

使用 robocopy 完成迁移（自动排除 __pycache__ 等目录）：

`powershell
# 1. 创建目标目录
New-Item -ItemType Directory -Force -Path 'd:\_context-infrastructure\adhoc_jobs\articles_archive'
New-Item -ItemType Directory -Force -Path 'd:\_context-infrastructure\adhoc_jobs\scripts_archive'
New-Item -ItemType Directory -Force -Path 'd:\_context-infrastructure\adhoc_jobs\webpage'
New-Item -ItemType Directory -Force -Path 'd:\_context-infrastructure\docs\plans'
New-Item -ItemType Directory -Force -Path 'd:\_context-infrastructure\docs\specs'

# 2. 拷贝文章
robocopy 'C:\iasi_workspace\articles' 'd:\_context-infrastructure\adhoc_jobs\articles_archive' /E /XD '__pycache__' '.tmp'

# 3. 拷贝脚本（排除 __pycache__）
robocopy 'C:\iasi_workspace\scripts' 'd:\_context-infrastructure\adhoc_jobs\scripts_archive' /E /XD '__pycache__'

# 4. 拷贝网页
robocopy 'C:\iasi_workspace\webpage' 'd:\_context-infrastructure\adhoc_jobs\webpage' /E

# 5. 拷贝设计文档
robocopy 'C:\iasi_workspace\docs\plans' 'd:\_context-infrastructure\docs\plans' /E
robocopy 'C:\iasi_workspace\docs\specs' 'd:\_context-infrastructure\docs\specs' /E
`

## 5. 迁移后需更新

- WORKSPACE.md：添加归档目录的路由说明
- .gitignore（如需要）：排除 __pycache__/ 目录

## 6. 验证策略

- 迁移后对比源目录和目标目录的文件数量，验证完整性
- 抽检关键文件的可读性
- 确认目标目录结构符合设计

## 7. 未决事项

- 无

## 8. 文件扫描结果

| 板块 | 文件数 | 总大小 | 最大文件 |
|------|--------|--------|---------|
| articles | 78 | 3.47 MB | 0.56 MB (.docx) |
| scripts | 7 | 0.09 MB | 0.03 MB (.py) |
| webpage | 40 | 1.85 MB | 0.52 MB (.png) |
| docs | 4 | 0.04 MB | 0.01 MB (.md) |
| **合计** | **129** | **5.45 MB** | 无过大文件 |

根目录下的 GIF (4.27 MB) 和 MP4 (1.25 MB) 不迁移。