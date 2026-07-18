# Skill: Delayed Execution (延时执行)

用于在一段时间后执行任务。这个 starter skill 只保留轻量 fallback；如果任务需要持久化、重启恢复、日志查询、取消、或提交 AI agent 工作，请安装 `docs/SKILL_ECOSYSTEM.md` 里的 public repos。

## When to Use

- 需要在一段时间后执行一个简单命令
- 当前 workspace 尚未安装更完整的 process manager
- 任务丢失风险可接受

## 推荐路径

优先安装并使用 ecosystem 里的专用能力：

- `process-launcher`: durable one-shot schedule、进程日志、取消、重启恢复
- `opencode_skill`: OpenCode `submit` / `submit --dry-run` / batch submission

对于需要 AI 判断的延时任务，正确组合是：先用 `opencode_skill submit --dry-run` 预检提交链路，再用 `process-launcher` 在未来时间触发真实 `opencode_skill submit`。不要在本 starter skill 里维护私有 OpenCode endpoint、模型、agent 或本地路径。

## 轻量 Fallback：sleep + nohup

只适合低风险、短期、可丢失的命令行任务。

```bash
# 语法：nohup bash -c 'sleep <秒数> && <命令>' > /tmp/delayed_task.log 2>&1 &
nohup bash -c 'sleep 3600 && /path/to/script.sh' > /tmp/delayed_task.log 2>&1 &
disown
```

## 时间换算

| 时间 | 秒数 |
|------|------|
| 1 分钟 | 60 |
| 5 分钟 | 300 |
| 10 分钟 | 600 |
| 30 分钟 | 1800 |
| 1 小时 | 3600 |
| 2 小时 | 7200 |
| 24 小时 | 86400 |

## 查看与取消

```bash
# 检查任务是否在运行
ps aux | grep "sleep" | grep -v grep

# 查看日志
tail -f /tmp/delayed_task.log

# 取消任务
kill <PID>
```

## Safety Rules

- 优先使用 `process-launcher`，除非任务确实低风险且可丢失。
- 延时执行前先跑目标命令的 dry-run / check / preview 模式；没有预检能力时明确告知风险。
- 所有 fallback 任务都必须重定向日志。
- 不要把真实 API key、私有 endpoint、联系人、模型偏好或本机路径写进 public starter skill。
