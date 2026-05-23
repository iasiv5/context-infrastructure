# Memory Observations

这是三层记忆系统的动态记忆日志。observer 会把当天观测追加到这里；reflector 会回看这里的近期内容，清理低价值项，并据此产出规则晋升与报告。默认触发方式是 `.github/hooks/pre-session.ps1` 调用 `periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py`。

## 格式说明

每个日期条目格式如下：

```raw
Date: YYYY-MM-DD

🔴 High: [方法论/约束] 描述
🟡 Medium: [项目状态/决策] 描述
🟢 Low: [任务流水] 描述
```

### 优先级定义

- **🔴 High**：跨项目通用的经验教训、硬性约束、影响系统架构的重大决策。永久保留，候选晋升为 axiom 或 skill。
- **🟡 Medium**：活跃项目的关键进展、技术决策背景、未来几周仍需参考的信息。
- **🟢 Low**：日常任务流水、瞬时 debug 记录、临时上下文。定期垃圾回收。

## 如何加载记忆

不要全文加载这个文件（可能很大）。按需检索：

```bash
# 搜索特定主题
grep -n "关键词" contexts/memory/OBSERVATIONS.md

# 搜索最近 N 天
grep -A 20 "Date: $(date -v-7d +%Y-%m-%d)" contexts/memory/OBSERVATIONS.md
```

或使用语义搜索（`rules/skills/semantic_search.md`）做跨日期语义检索。

---

<!-- 以下是记录区域，由 AI Heartbeat 本地执行器追加与整理 -->

Date: 2026-05-22

🔴 High: Local observer scan detected rule-surface changes in AGENTS.md, docs/plans/2026-05-22-ai-heartbeat-manual-reminder-implementation-plan.md, docs/specs/2026-05-22-ai-heartbeat-manual-reminder-design.md, rules/WORKSPACE.md, docs/specs/2026-05-22-migrate-iasi-workspace-design.md, docs/plans/2026-05-22-migrate-iasi-workspace-implementation-plan.md, ... (+80).
🟡 Medium: Local observer scan detected active workspace changes in periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py, periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py, periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py, periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py, periodic_jobs/ai_heartbeat/tests/test_heartbeat_status_cli.py, periodic_jobs/ai_heartbeat/src/v0/heartbeat_status_cli.py, ... (+63).
🟢 Low: Local observer scan detected routine workspace churn in .github/hooks/pre-session.ps1, .gitignore, .github/hooks/ai-heartbeat.session-start.json, pyrightconfig.json, contexts/thought_review/.gitkeep, contexts/survey_sessions/.gitkeep, ... (+11).

Date: 2026-05-23

🔴 High: Local observer scan detected rule-surface changes in AGENTS.md, rules/skills/ai_heartbeat_local_reflections.md, docs/plans/2026-05-22-ai-heartbeat-manual-reminder-implementation-plan.md, docs/specs/2026-05-22-ai-heartbeat-manual-reminder-design.md, rules/skills/INDEX.md, rules/WORKSPACE.md, ... (+79).
🟡 Medium: Local observer scan detected active workspace changes in README.md, periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py, periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py, docs/CRONTAB.md, setup_guide.md, periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py, ... (+63).
🟢 Low: Local observer scan detected routine workspace churn in .github/copilot-instructions.md, .github/hooks/pre-session.ps1, .gitignore, CLAUDE.md, .github/hooks/ai-heartbeat.session-start.json, pyrightconfig.json, ... (+13).

