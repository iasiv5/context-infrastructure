# Crontab 配置指南

本文档描述 context infrastructure 系统所需的定时任务。

如果你只想使用 AI Heartbeat 的手动提醒模式，先运行 `python periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py` 即可；这份文档只覆盖仍然选择 cron 或其他系统级调度的场景。workspace 内建 SessionStart hook 会按单字段 reminder policy 决定 Windows modal 或 8.88 秒轻提醒窗。

---

## 时间线总览

```raw
3:05 AM   → Situation Awareness: 每日摘要 + 摄像头缓存刷新
4:00 AM   → Session Sync: 导出 AI session 归档
6:30 AM   → WeChat DB Parser: 导出每日消息为 CSV（如适用）
7:00 AM   → Daily Briefing: 生成个人晨报 → Email
8:00 AM   → AI Heartbeat Observer: 扫描文件变动，提取观察写入 OBSERVATIONS.md
Every 2m  → Situation Awareness: 快照采集（交通/摄像头/警报）
Every 12h → Situation Awareness: 风力预警检查
Weekly    → AI Heartbeat Reflector: 合并/提升/清理记忆
Daily     → Crontab Monitor: 健康审计，发现异常则发告警邮件
```

---

## 核心任务说明

### AI Heartbeat Due Check（每日 / 每周）

定时检查 observer / reflector 是否到期，并把结果写入日志或接入你自己的提醒系统。这一步只做审计和提醒，不直接执行 observer / reflector；真正处理仍在当前 chat 中运行 `/ai-heartbeat`。如果你同时启用了 workspace 自带的 SessionStart hook，它会按仓库 policy 决定 Windows modal 或 8.88 秒轻提醒窗；cron 本身仍只负责审计和日志。

- **脚本**：`periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py`
- **依赖**：本地 Python 环境、workspace 文件读写权限
- **建议时间**：每日 8:00 AM（observer 审计）与每周日 9:00 AM（reflector 审计）

### Crontab Monitor（每日）

自主审计所有 crontab 任务的健康状态，发现异常时发送告警邮件。

- **脚本**：`periodic_jobs/ai_heartbeat/src/v0/jobs/crontab_monitor.py`
- **依赖**：已配置的 AI backend、Gmail（`GMAIL_USERNAME` / `GMAIL_APP_PASSWORD`）
- **建议时间**：每日 9:00 AM

### AI News Survey（每日/每周）
```cron
# ── 时区说明 ──────────────────────────────────────────────
# 以下时间均为本地时间。如需指定时区，在 crontab 顶部添加：
# TZ=America/Los_Angeles

# AI Heartbeat Observer Due Check — 每日 8:00 AM
# 如果日志提示 observer 已到期，请在当前 chat 中运行 /ai-heartbeat
0 8 * * * cd /path/to/your/workspace && /path/to/your/workspace/.venv/bin/python periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py >> /tmp/heartbeat_observer_check.log 2>&1

# AI Heartbeat Reflector Due Check — 每周日 9:00 AM
# 如果日志提示 reflector 已到期，请在当前 chat 中运行 /ai-heartbeat
0 9 * * 0 cd /path/to/your/workspace && /path/to/your/workspace/.venv/bin/python periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py >> /tmp/heartbeat_reflector_check.log 2>&1

# Crontab Monitor — 每日 9:00 AM
0 9 * * * cd /path/to/your/workspace && /path/to/your/workspace/.venv/bin/python periodic_jobs/ai_heartbeat/src/v0/jobs/crontab_monitor.py >> /tmp/crontab_monitor.log 2>&1

# AI News Survey 日报 — 每日 8:00 AM（发个人邮件）
0 8 * * * cd /path/to/your/workspace && /path/to/your/workspace/.venv/bin/python periodic_jobs/ai_heartbeat/src/v0/jobs/ai_news_survey.py --mode daily >> /tmp/ai_news_survey.log 2>&1

# AI News Survey 周报 — 每周一 8:00 AM（发布到 Kit 订阅者）
0 8 * * 1 cd /path/to/your/workspace && /path/to/your/workspace/.venv/bin/python periodic_jobs/ai_heartbeat/src/v0/jobs/ai_news_survey.py --mode weekly --publish-to-kit >> /tmp/ai_news_weekly.log 2>&1
```

---

## 注意事项

1. **路径替换**：所有 `/path/to/your/workspace` 必须替换为你的实际绝对路径。
2. **虚拟环境**：脚本依赖 `.venv` 中的 Python 包，确保先运行 `uv pip install -r requirements.txt`（如有）。
3. **环境变量**：cron 环境不会自动加载 `.env`，建议在脚本中显式加载，或在 crontab 中用 `env $(cat .env | xargs)` 注入。
4. **时区**：macOS cron 默认使用系统时区；Linux 服务器建议在 crontab 顶部显式设置 `TZ=`。
5. **日志**：示例中日志写入 `/tmp/`，生产环境建议改为持久化路径（如 `logs/` 目录）。
6. **依赖顺序**：Observer 依赖当天的文件变动，建议在 daily briefing 和 news survey 之后运行（8:30 AM 以后）。
