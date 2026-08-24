# WORKSPACE.md - 目录路由速查

目标：让 AI 每轮 session 都能快速知道"去哪里找/放什么"。**找任何文件前先查这里。**

## 路由规则

### 项目与代码
- 写代码 / 跑脚本 / 一次性项目：`adhoc_jobs/<project>/`
- 工具脚本（邮件、语义搜索、分享报告等）：`tools/`
- 定时任务：`periodic_jobs/`

### 知识与记录
- 通用调研报告：`contexts/survey_sessions/`
- 思考 / 复盘 / 方法论：`contexts/thought_review/`
- 每日日志：`contexts/daily_records/`
- AI 会话归档：`contexts/ai_sessions/<source>/`（使用 ai_session_export 生成；搜索流程见 `rules/skills/ai_session_search_archive.md`）

### 系统与规则
- 可复用技术方案 / Skill：`rules/skills/`
- 核心公理（Axioms）：`rules/axioms/`
- 记忆系统：`contexts/memory/` + `periodic_jobs/ai_heartbeat/`

### 独立子仓（.gitignore 排除跟踪，物理相邻但 git 独立）
- `ob-harness/` → OpenBMC harness 专用仓（自带 heartbeat：`ob-harness/contexts/memory/OBSERVATIONS.md`；主仓 observer 只记指针条目，子仓细节去子仓记忆查）
- `external_skills/` → 外部 skill 本地 clone + overlay（writing-skill、ai-agent-cli-skill 等；overlay 机制见 `rules/skills/bestpractice_external_skill_overlay.md`）
- `m/` → iasi 插件 marketplace 子仓（brainstorming/grilling/writing-plans 等 skill 的上游）

## 命名规则
- 目录和文件名：小写 + 下划线 (snake_case)
- 临时一次性项目：`tmp_<name>/`

## Python 环境
- 根目录 `.venv/` 为工作区级环境，用 `uv pip install` 管理依赖
- 需要隔离时在 `adhoc_jobs/<project>/.venv/` 建独立环境

## 快速查询

<!-- 随着你的项目增长，在这里添加活跃项目的快捷路由 -->
<!-- 格式：- `project-name` → `adhoc_jobs/project_name/` (说明) -->
<!-- 示例：- `weather monitor` / `weather_monitor` → `adhoc_jobs/weather_monitor/`（家庭气象数据采集与告警） -->