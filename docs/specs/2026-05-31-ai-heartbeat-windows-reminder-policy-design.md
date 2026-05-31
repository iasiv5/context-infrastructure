# AI Heartbeat Windows Reminder Policy 设计文档

Date: 2026-06-01
Status: Draft / 待审批
Author: User + AI

## 背景与目标

- 当前 AI Heartbeat 的执行合同已经稳定：SessionStart hook 只做 reminder，真正的 observer / reflector 执行仍由当前 chat 中显式运行 `/ai-heartbeat` 触发。
- 当前 Windows reminder 路径是 [.github/hooks/pre-session.ps1](../../.github/hooks/pre-session.ps1) 调用 [heartbeat_preflight.py](../../periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py) 生成 dialog spec，再由 WinForms modal 弹窗呈现提醒。
- 新需求不是改执行层，而是把 reminder policy 收成一个简单的仓库级开关：开关打开时，Windows 继续弹出现有 modal；开关关闭时，不再显示 modal，而是显示一个 8.88 秒自动消失的轻提醒窗。
- 用户已明确约束：这个开关是仓库级版本化开关，不是用户本地临时开关；policy 与运行态分离；不再把 stdout 或其他控制台输出视为正式提醒面。
- 用户已明确交互边界：轻提醒窗只负责提醒，默认停留 8.88 秒；用户点击轻提醒窗时，把 `/ai-heartbeat` 复制到剪贴板；轻提醒窗不提供“今天不再提醒”之类的状态写回交互。

成功标准：

- reminder policy 收成一个简单的仓库级开关。
- [periodic_jobs/ai_heartbeat/config/reminder_policy.json](../../periodic_jobs/ai_heartbeat/config/reminder_policy.json) 的 schema 收成单字段 JSON，只保留 `windows_popup_enabled`。
- Windows 弹窗默认继续开启。
- 关闭 Windows 弹窗后，hook 不再弹 modal，而是显示一个 8.88 秒自动消失的轻提醒窗。
- 轻提醒窗点击时复制 `/ai-heartbeat` 到剪贴板。
- [heartbeat_status.json](../../periodic_jobs/ai_heartbeat/state/heartbeat_status.json) 继续只存 observer / reflector 的运行态与提醒去重态，不承载 policy。
- [heartbeat_preflight.py](../../periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py) 继续负责 due-task 计算，并额外输出统一的 reminder spec。
- [.github/hooks/pre-session.ps1](../../.github/hooks/pre-session.ps1) 继续只做 renderer，不自行决定 reminder policy。
- `/ai-heartbeat` 的执行入口、observer / reflector 的状态回写语义、以及 reminder-only 的边界保持不变。

## 范围

- 收紧 reminder policy 配置面，只保留一个仓库级开关 `windows_popup_enabled`。
- 删除旧的多字段 policy 设计，不再保留 `popup_disabled_fallback_surface`、`copy_profile.modal`、`copy_profile.text` 这类配置项。
- 扩展 [heartbeat_preflight.py](../../periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py)，让它在现有 due-task 判断之外，根据 policy 输出统一 reminder spec。
- 更新 [.github/hooks/pre-session.ps1](../../.github/hooks/pre-session.ps1)，使其根据 spec 渲染 `modal` 或 `text` 两种 surface。这里的 `text` 语义改为轻提醒窗，不再代表控制台文本输出。
- 为 `modal` / `text` surface、policy 默认值、policy 异常默认值补齐测试。
- 更新 AI Heartbeat 的活文档，使 reminder policy 与当前行为一致。

## 非范围

- 不修改 `/ai-heartbeat` 的执行入口和执行合同。
- 不改变 [heartbeat_status.json](../../periodic_jobs/ai_heartbeat/state/heartbeat_status.json) 的 schema。
- 不把版本化开关写入 gitignored 的本地状态文件。
- 不在本轮引入 Windows toast、通知中心集成或新的外部依赖。
- 不让 hook 直接执行 observer 或 reflector。
- 不给轻提醒窗增加“今天不再提醒”或其他状态写回交互。
- 不把控制台 stdout 当成正式提醒面。

## 方案比较

### 方案 A：保留当前 stdout 文本提醒

- 核心思路：继续沿用现有 `surface=text` 分支，只通过 `Write-Output` 输出提醒文本。
- 优点：实现最短，不新增 UI 代码。
- 缺点：
  - 在当前 SessionStart command hook 宿主里，stdout 不是稳定可见的用户界面。
  - 实际效果等同于“算出来了提醒，但用户未必看到”。
  - 不满足“关掉 popup 后仍然要有真正可见提醒面”的目标。

### 方案 B：非模态轻提醒窗

- 核心思路：保留当前 PowerShell + WinForms 技术栈；当 `windows_popup_enabled=false` 时，不弹 modal，而是显示一个轻量、非模态、8.88 秒自动消失的小提醒窗。
- 优点：
  - 不引入新依赖。
  - 在当前 hook 宿主里有稳定的可见性。
  - 保持低侵入，同时比 stdout 更符合“提醒”语义。
  - 点击后复制 `/ai-heartbeat`，足够轻量，不会把 reminder 层做成第二套交互系统。
- 缺点：
  - 它不是 Windows 通知中心原生通知。
  - 需要在现有 WinForms 渲染代码旁边新增一条轻提醒窗分支。

### 方案 C：Windows 原生通知中心提醒

- 核心思路：当 `windows_popup_enabled=false` 时，不用 WinForms，而是调用 Windows 原生通知 API，把提醒投递到通知中心。
- 优点：更贴近系统原生提醒体验。
- 缺点：
  - 在当前 PowerShell command hook 宿主下，兼容性与可验证性都更复杂。
  - 需要额外处理 app identity、宿主上下文与可靠性问题。
  - 超出“本轮保持简单设计”的约束。

## 推荐方案

- 选择方案 B。
- 原因：这次需求的关键不是“做出最原生的 Windows 通知”，而是“在不加新依赖的前提下，让 policy 关闭 popup 后仍然有一个真正可见、低侵入的提醒面”。方案 B 在当前仓库边界内最稳，也最符合用户明确给出的约束。
- 主要 trade-offs：
  - 接受轻提醒窗不是原生通知中心，换来更稳的实现边界和更低的验证成本。
  - 接受轻提醒窗只做提醒与点击复制，不做状态写回，换来更简单清晰的 reminder 语义。
  - 接受 policy 只保留一个简单开关，换来更低的配置复杂度。

## 关键边界与组件职责

- [periodic_jobs/ai_heartbeat/config/reminder_policy.json](../../periodic_jobs/ai_heartbeat/config/reminder_policy.json)
  - 仓库级版本化 policy。
  - 最终 schema 只保留一个字段：`windows_popup_enabled`。
  - 目标形状固定为：

```json
{
  "windows_popup_enabled": true
}
```

  - `true` 表示继续使用现有 modal。
  - `false` 表示改为 8.88 秒自动消失的轻提醒窗。
  - 不再保留 `popup_disabled_fallback_surface`、`copy_profile` 等旧字段。
  - 不存 runtime state，不存 prompted 结果，不承载时长以外的本地偏好。

- [heartbeat_status.json](../../periodic_jobs/ai_heartbeat/state/heartbeat_status.json)
  - 继续只存 observer / reflector 的 success、failed、skipped、last_prompted_on。
  - 不新增 popup toggle 语义。

- [heartbeat_preflight.py](../../periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py)
  - 继续负责 due-task 计算。
  - 读取 policy 并输出统一 reminder spec。
  - `windows_popup_enabled=true` 时输出 `surface=modal`。
  - `windows_popup_enabled=false` 时输出 `surface=text`。这里的 `text` 代表轻提醒窗，不代表 stdout。
  - spec 至少包含 `surface`、`message`、`due_tasks`、`target_date`、`recommended_command`。

- [.github/hooks/pre-session.ps1](../../.github/hooks/pre-session.ps1)
  - 继续只做 Windows reminder 渲染。
  - `surface=modal` 时复用现有 WinForms modal 流程。
  - `surface=text` 时渲染轻量、非模态、8.88 秒自动消失的小提醒窗。
  - 用户点击轻提醒窗时，把 `/ai-heartbeat` 写入剪贴板。
  - 不在轻提醒窗路径写 `last_prompted_on`，也不提供 `今天不再提醒`。

- `/ai-heartbeat`
  - 执行入口与状态回写语义不变。
  - 不感知 popup 开关，也不承担 reminder policy 解析。

## 数据流 / 控制流

### SessionStart 提醒路径

1. SessionStart hook 继续通过 [.github/hooks/ai-heartbeat.session-start.json](../../.github/hooks/ai-heartbeat.session-start.json) 调用 [.github/hooks/pre-session.ps1](../../.github/hooks/pre-session.ps1)。
2. hook 调用 [heartbeat_preflight.py](../../periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py) 生成 reminder spec。
3. preflight 同时读取：
   - [heartbeat_status.json](../../periodic_jobs/ai_heartbeat/state/heartbeat_status.json) 中的 runtime state。
   - `periodic_jobs/ai_heartbeat/config/reminder_policy.json` 中的 reminder policy。
4. preflight 先按现有逻辑判断 observer / reflector 是否 due，再根据 policy 归一化出本次 reminder surface：
   - popup 开启：`surface=modal`。
   - popup 关闭：`surface=text`。
5. hook 根据 spec 渲染提醒；提醒内容仍然指向“如需处理，请在当前 chat 中运行 `/ai-heartbeat`”。

### Modal 路径

1. hook 继续显示当前 WinForms 对话框。
2. 保留现有两步语义：`知道了` 不改状态，`今天不再提醒` 才写 prompted 去重。
3. modal 本身仍不直接执行 observer 或 reflector。

### 轻提醒窗路径

1. hook 显示一个轻量、非模态、8.88 秒自动消失的小提醒窗。
2. 小提醒窗默认展示标题与 gentle reminder 文案。
3. 小提醒窗不显示按钮。
4. 用户点击小提醒窗时，把 `/ai-heartbeat` 复制到剪贴板，然后窗口关闭。
5. 轻提醒窗不写 `last_prompted_on`，也不执行任务。

## 错误处理与回退

- policy 文件缺失、损坏或字段非法
  - 处理：回到仓库默认值，即 `windows_popup_enabled=true`。
  - 原则：policy 解析错误时，不额外引入第二套配置决策。

- modal 或轻提醒窗渲染失败
  - 处理：脚本稳定退出。
  - 原则：本轮设计不再追加第三种提醒面。

- 无任务 due
  - 处理：不输出 reminder，不改状态。

## 测试策略

- Python 单测：
  - policy 读取成功时，preflight 能正确产出 `modal` 或 `text` surface。
  - policy 缺失或损坏时，preflight 能回到默认 policy。
  - popup 开关只影响 hook reminder spec，不影响 `/ai-heartbeat` command spec。
  - `surface=text` 路径不修改 prompted 状态。
  - policy schema 收紧后，只有单字段 JSON 仍能被正确解析。

- Hook 验证：
  - 保留 [.github/hooks/pre-session.ps1](../../.github/hooks/pre-session.ps1) 的语法校验。
  - 新增 `surface=text` 的 smoke check，确认会进入轻提醒窗分支而不是 modal 分支。
  - 新增轻提醒窗自动关闭验证，确认默认停留约 8.88 秒后退出。
  - 新增点击行为验证，确认点击轻提醒窗后 `/ai-heartbeat` 被复制到剪贴板。

## 未决事项

- 当前没有未决事项；这份设计可以直接进入单份实施计划。