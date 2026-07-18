# Workflow Watchdog - 后台任务巡检

## 适用场景

派出长时间运行的 workflow、后台 agent 或批量 sub-agent 任务之后。这类子进程偶尔会"鬼打墙"：卡在某个循环或重试里，长时间不产出结果。不要在原地死等。

## 做法

派出任务后，设一个 reasonable 的巡检 wake-up，默认约 30 分钟（1800s）。Claude Code harness 用 `ScheduleWakeup`；其他 harness 用对应的定时机制（如 Process Launcher 的延时执行，见 `rules/skills/process_launcher.md`）。

醒来后检查任务状态，分两种情况处理：

1. **真实在忙**：有新输出、agent 在持续产出。不管它，继续等或再设一次 wake-up。
2. **鬼打墙卡住**：长时间无进展、同一步骤反复重试。把它 kill 掉（Claude Code 用 `TaskStop`），用已有的部分结果推进，或换方法重做。

"真忙 vs 卡住"的判断自己做，不用问用户。这和 `rules/SOUL.md` 的自主执行契约一致：巡检和 kill 属于技术编排决策，自己推到底。

## 来源

实践反馈：跑 workflow 时子进程卡住，AI 死等浪费了整段时间。教训是把"派出后设巡检"变成默认动作，而非出问题后的补救。