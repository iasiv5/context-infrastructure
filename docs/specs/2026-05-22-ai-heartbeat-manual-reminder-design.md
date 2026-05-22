# AI Heartbeat 手动提醒机制设计文档

> 历史说明：本文保留了最初的设计阶段语境。当前落地实现已把默认执行路径切到 `periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py`，不再以 `observer.py` / `reflector.py` 作为默认 direct-exec 入口。

## 背景与目标

- 现有记忆系统把 observer 和 reflector 设计成外部定时任务，默认依赖 OpenCode Server 和 cron。
- 这套前提对当前使用方式不合适：用户不准备配置长期驻留的定时执行环境，但仍然希望保留 observer 的日级节奏和 reflector 的周级节奏。
- 这次设计要把自动执行改成会话前审计 + 用户确认后执行：每次 AI 会话开始时检查本地状态，若 observer 距离上次成功执行已超过 24 小时，则提醒是否执行；若 reflector 距离上次成功执行已超过 7 天，则提醒是否执行。
- 成功标准：
  - 不依赖 cron 也能稳定知道 observer 和 reflector 是否逾期。
  - 会话开始时默认自动检查，但只做软提醒，不自动执行。
  - 用户确认后，可由 Agent 在当前会话里代执行 observer 或 reflector。
  - 同一天内重复开启多个会话时，逾期提醒不会反复打断。

## 范围

- 为 observer 和 reflector 引入本地状态记录文件，持久化最近成功执行时间和最近提醒时间。
- 增加一个独立的会前检查器，用于读取状态、判断是否逾期、决定是否提醒。
- 保留现有 observer.py 和 reflector.py 作为真正执行任务的入口，只在成功或失败后回写状态。
- 提供两种进入方式：
  - 会话开始时自动检查。
  - 没有可靠会话钩子时，允许用户手动触发同一个检查入口作为兜底。

## 非范围

- 不重新设计 observer 和 reflector 的业务逻辑，不改变它们对 OBSERVATIONS.md 和 rules/ 的职责边界。
- 不恢复或替代 cron，不做新的后台常驻服务。
- 不把提醒系统扩展成通用任务调度器，不支持任意自定义任务。
- 不在首版引入多用户、多工作区共享状态，状态文件仅服务当前仓库。
- 不在首版加入复杂配置界面，24 小时和 7 天阈值按代码常量处理。

## 方案比较

### 方案 A：继续沿用 cron 和 OpenCode Server

- 核心思路：保持当前设计，要求用户配置 observer 和 reflector 的外部定时执行环境。
- 优点：与现有文档和脚本最一致，提醒逻辑最少。
- 缺点：不符合当前约束，用户明确不准备配置这套运行方式。

### 方案 B：从现有产物反推最近执行时间

- 核心思路：通过 OBSERVATIONS.md 的最新日期、rules/ 的修改时间或日志文件时间，推断 observer 和 reflector 是否最近执行过。
- 优点：不新增状态文件。
- 缺点：语义不稳定。文件修改时间无法可靠区分手工编辑、格式整理和真实执行；一旦推断错误，提醒就会失真。

### 方案 C：独立状态文件 + 会前检查 + 用户确认后执行

- 核心思路：为 observer 和 reflector 维护一份本地状态文件；会话开始时读取状态并做新鲜度审计；若逾期则软提醒，用户确认后在当前会话执行任务。
- 优点：
  - 与当前使用方式一致，不依赖后台调度。
  - 判断条件明确，避免从内容文件反推状态带来的歧义。
  - 自动检查和手动兜底可以共用同一套逻辑。
- 缺点：
  - 需要新增一层状态管理代码。
  - 需要为不同 Agent 平台预留会话入口挂载点。

## 推荐方案

- 选择方案 C。
- 原因：它最贴合当前约束，也最符合现有职责边界。observer 和 reflector 继续专注于记忆处理；新机制只补上状态持久化和会前提醒，不重做执行器。
- 主要 trade-off：
  - 首版接受一份额外状态文件，以换取提醒语义的确定性。
  - 自动检查不绑定某个唯一平台实现，而是定义稳定的检查接口，再由具体平台决定如何在会话开始时挂接。

## 关键边界与组件职责

- 状态文件：periodic_jobs/ai_heartbeat/state/heartbeat_status.json
  - 职责：记录 observer 和 reflector 的最近成功时间、最近尝试时间、最近状态、最近错误摘要、最近提醒日期。
  - 该文件是运行时元数据，不属于长期记忆内容，因此不放在 contexts/memory。

- 状态读写模块：建议新增到 periodic_jobs/ai_heartbeat/src/v0 下的共享模块
  - 职责：统一读取和写入 heartbeat_status.json。
  - 需要提供原子写入，避免中途失败产生半写文件。
  - 只负责状态持久化，不负责逾期判断。

- 会前检查器
  - 职责：读取状态文件，按当前时间判断 observer 是否超过 24 小时、reflector 是否超过 7 天，并结合最近提醒日期做去重。
  - 输出：零个、一个或两个提醒项。
  - 它只做审计和提醒，不直接执行 observer 或 reflector。

- 现有执行器：periodic_jobs/ai_heartbeat/src/v0/observer.py 和 periodic_jobs/ai_heartbeat/src/v0/reflector.py
  - 职责：继续执行现有 L1 和 L2 任务。
  - 新职责：任务结束后回写状态文件。
  - 规则：只有成功完成时才推进 last_success_at；失败只更新 last_attempt_at、last_status 和 last_error。

- 会话入口挂载层
  - 职责：在每次会话开始时调用会前检查器。
  - 设计要求：挂载层是可替换的。若当前平台支持 pre-session hook，则自动调用；若不支持，则退化为显式命令入口。
  - 该层不保存业务状态，避免平台耦合。

## 状态文件格式

首版采用 JSON，原因是机器可读性强、实现简单、人工排查时也足够直观。建议结构如下：

```json
{
  "version": 1,
  "observer": {
    "last_success_at": null,
    "last_attempt_at": null,
    "last_status": "never",
    "last_target_date": null,
    "last_error": null,
    "last_prompted_on": null
  },
  "reflector": {
    "last_success_at": null,
    "last_attempt_at": null,
    "last_status": "never",
    "last_target_date": null,
    "last_error": null,
    "last_prompted_on": null
  }
}
```

字段解释：

- last_success_at：最近一次成功执行完成时间，使用带时区的 ISO 时间戳。
- last_attempt_at：最近一次尝试执行时间，无论成功或失败都更新。
- last_status：never、success、failed、skipped 之一。skipped 仅用于脚本已被显式调用、但因幂等性检查等原因无需继续执行而退出；用户在提醒阶段拒绝执行，不计为 skipped。
- last_target_date：本次执行对应的逻辑日期。observer 主要使用它，reflector 可记录运行日。
- last_error：最近一次失败的简短摘要。成功后清空。
- last_prompted_on：最近一次因为逾期而向用户发出提醒的本地日期，用于同日去重。

## 数据流 / 控制流

- 开发中的正常路径：
  1. 会话开始时，挂载层调用会前检查器。
  2. 会前检查器读取 heartbeat_status.json；若文件不存在，则初始化为 never 状态。
  3. 会前检查器按以下规则判断：
     - observer：若 last_success_at 为空，或距离当前时间超过 24 小时，则视为逾期。
     - reflector：若 last_success_at 为空，或距离当前时间超过 7 天，则视为逾期。
  4. 若任务逾期，且 last_prompted_on 不是今天，则生成软提醒；若今天已提醒过，则本次静默跳过提醒。
  5. 用户看到提醒后明确确认是否执行。若用户本次拒绝执行，仅更新 last_prompted_on，不更新 last_attempt_at、last_status 或 last_success_at。
  6. 若用户确认，则 Agent 在当前会话中执行 observer.py 或 reflector.py。
  7. 执行结束后，状态读写模块回写结果：
     - 成功：更新 last_success_at、last_attempt_at、last_status，清空 last_error，并把 last_prompted_on 清空。
     - 失败：更新 last_attempt_at、last_status、last_error，不修改 last_success_at。

- 手动兜底路径：
  1. 若平台没有可靠会话开始钩子，用户可显式调用同一个会前检查入口。
  2. 后续提醒、确认、执行和状态更新逻辑与正常路径完全一致。

- 提醒文案要求：
  - 提醒属于软提醒，不自动执行。
  - 提醒内容应包含任务名称、距离上次成功执行的时间跨度，以及明确确认入口。
  - 提醒文案不应把失败尝试伪装成最新成功时间。

## 错误处理与回退

- 状态文件不存在
  - 处理：首次运行时自动初始化为 never 状态。
  - 效果：observer 和 reflector 都会进入逾期判断，并在去重规则允许时提醒一次。

- 状态文件损坏或 JSON 解析失败
  - 处理：不要默默覆盖原文件。先将损坏文件重命名为带时间戳的备份，再重新初始化默认状态文件。
  - 效果：避免静默丢失排障线索。

- observer 或 reflector 执行失败
  - 处理：记录 last_attempt_at、last_status=failed 和 last_error；保持 last_success_at 不变。
  - 效果：下次检查仍会继续提醒，不会因为失败尝试而掩盖逾期状态。

- 同一天多次新开会话
  - 处理：利用 last_prompted_on 做日级去重。
  - 效果：自动检查每次都做，但同一天只提醒一次，直到成功执行为止。

- 没有自动挂载点
  - 处理：保留显式手动检查入口作为兜底。
  - 效果：自动体验退化，但核心逻辑仍可用。

## 测试策略

- 纯逻辑测试
  - 验证逾期判断：从未执行、刚执行、超过 24 小时、超过 7 天等边界情况。
  - 验证提醒去重：同一天重复会话不重复提醒，跨天后恢复提醒。

- 状态持久化测试
  - 验证成功写回：success 会更新 last_success_at 并清空 last_error。
  - 验证失败写回：failed 不会推进 last_success_at。
  - 验证损坏文件回退：解析失败时会先备份再重建。

- 集成级冒烟测试
  - 模拟会话开始，检查 overdue observer 和 overdue reflector 的提醒内容是否正确。
  - 模拟用户确认后执行 observer 或 reflector，检查状态文件是否按预期变化。
  - 模拟没有自动挂载点的场景，检查手动入口是否复用同一套逻辑。

## 未决事项

- 当前无阻塞性未决事项。
- 实施计划阶段只需要在具体平台上选定一个会话开始挂载点；如果挂载点不稳定，首版直接走手动检查入口即可，不影响本设计成立。