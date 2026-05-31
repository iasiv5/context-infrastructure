# AI Heartbeat Windows Reminder Policy 实施计划

## 目标

- 将已批准设计 [../specs/2026-05-31-ai-heartbeat-windows-reminder-policy-design.md](../specs/2026-05-31-ai-heartbeat-windows-reminder-policy-design.md) 落成当前仓库的 Windows reminder policy 实现。
- 保持 `/ai-heartbeat` 作为唯一执行入口，只调整 SessionStart reminder 层的 policy、spec 和 renderer。
- 把 [../../periodic_jobs/ai_heartbeat/config/reminder_policy.json](../../periodic_jobs/ai_heartbeat/config/reminder_policy.json) 收成单字段 JSON，只保留 `windows_popup_enabled`。
- 让 `windows_popup_enabled=true` 时继续使用现有 modal；`windows_popup_enabled=false` 时改成 8.88 秒自动消失的轻提醒窗，并在点击时复制 `/ai-heartbeat`。
- 保持 [../../periodic_jobs/ai_heartbeat/state/heartbeat_status.json](../../periodic_jobs/ai_heartbeat/state/heartbeat_status.json) 只承载运行态，不把 popup policy 混入本地状态文件。

## 架构快照

- 本次实现只保留一个仓库级 reminder policy 开关：`windows_popup_enabled`。preflight 负责把这个开关翻译成统一 reminder spec，hook 负责按 spec 渲染 modal 或轻提醒窗。
- [../../periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py](../../periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py) 继续负责 due-task 计算，但会删掉对旧多字段 policy 的依赖，改为解析单字段 policy，并输出最小可消费的 spec：`surface`、`message`、`due_tasks`、`target_date`、`recommended_command`。
- [../../.github/hooks/pre-session.ps1](../../.github/hooks/pre-session.ps1) 继续是唯一 Windows renderer：`surface=modal` 时复用现有 WinForms modal；`surface=text` 时显示轻量、非模态、8.88 秒自动消失的小提醒窗，并在点击时复制 `/ai-heartbeat`。
- [../../periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py](../../periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py)、[../../periodic_jobs/ai_heartbeat/src/v0/heartbeat_status_cli.py](../../periodic_jobs/ai_heartbeat/src/v0/heartbeat_status_cli.py) 和 [../../periodic_jobs/ai_heartbeat/state/heartbeat_status.json](../../periodic_jobs/ai_heartbeat/state/heartbeat_status.json) 的 schema 保持不变。
- 用户可见执行边界不变：hook 只提醒，真正处理仍在当前 chat 中运行 `/ai-heartbeat`。

## 输入工件

- 已批准设计文档：[../specs/2026-05-31-ai-heartbeat-windows-reminder-policy-design.md](../specs/2026-05-31-ai-heartbeat-windows-reminder-policy-design.md)
- 当前 preflight 入口：[../../periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py](../../periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py)
- 当前 Windows hook renderer：[../../.github/hooks/pre-session.ps1](../../.github/hooks/pre-session.ps1)
- 当前 preflight 测试：[../../periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py](../../periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py)
- 当前 AI Heartbeat 文档：[../../periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md](../../periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md)、[../../periodic_jobs/ai_heartbeat/docs/PRD.md](../../periodic_jobs/ai_heartbeat/docs/PRD.md)
- 当前仓库入口文档：[../../AGENTS.md](../../AGENTS.md)、[../../README.md](../../README.md)、[../../setup_guide.md](../../setup_guide.md)、[../CRONTAB.md](../CRONTAB.md)
- 编辑约束：AGENTS.md、README.md、setup_guide.md、docs/CRONTAB.md 以及 docs/specs / docs/plans 下的 markdown 在当前环境里按 notebook-backed 文件处理。实现时优先用 notebook-aware 编辑；如果工具再次命中 Windows 0 字节写入 bug，必须在同一步切到 PowerShell UTF-8 fallback，并立即做长度与 read-back 校验。

## 文件结构与职责

- Modify: [../../periodic_jobs/ai_heartbeat/config/reminder_policy.json](../../periodic_jobs/ai_heartbeat/config/reminder_policy.json)
  - 将 policy schema 收成单字段 JSON，只保留 `windows_popup_enabled`。
- Modify: [../../periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py](../../periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py)
  - 删除旧多字段 policy 解析，改为输出与新开关对应的统一 reminder spec。
- Test: [../../periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py](../../periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py)
  - 锁定单字段 policy、modal / 轻提醒窗 surface 归一化、command-spec 不受影响，以及 hook 轻提醒窗分支的可观察行为。
- Modify: [../../.github/hooks/pre-session.ps1](../../.github/hooks/pre-session.ps1)
  - 保留 modal 渲染；新增轻提醒窗 renderer；移除把 stdout 当正式提醒面的行为。
- Keep: [../../periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py](../../periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py)
  - 不修改 runtime state schema。
- Keep: [../../periodic_jobs/ai_heartbeat/src/v0/heartbeat_status_cli.py](../../periodic_jobs/ai_heartbeat/src/v0/heartbeat_status_cli.py)
  - 不修改状态回写契约。
- Modify: [../../periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md](../../periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md)
  - 写明单字段 policy、popup on/off 行为、轻提醒窗 8.88 秒自动消失与点击复制。
- Modify: [../../periodic_jobs/ai_heartbeat/docs/PRD.md](../../periodic_jobs/ai_heartbeat/docs/PRD.md)
  - 更新产品层行为说明与术语。
- Modify: [../../AGENTS.md](../../AGENTS.md)
  - 在 SessionStart Hook 段落补充“popup 开则 modal，关则 8.88 秒轻提醒窗”。
- Modify: [../../README.md](../../README.md)
  - 在 AI Heartbeat 使用说明中补充单字段 policy 与轻提醒窗行为。
- Modify: [../../setup_guide.md](../../setup_guide.md)
  - 更新 SessionStart hook 提醒行为和 popup 关闭后的表现。
- Modify: [../CRONTAB.md](../CRONTAB.md)
  - 只在提到 workspace hook 的地方补充 popup on/off 的新行为。

## 任务清单

### Task 1: 先锁定单字段 policy 与新 UI 合同的测试面

- 目标：先用测试把新合同钉住，避免后续实现仍然沿用旧的多字段 policy、`tone` 字段和 stdout 文本提醒语义。
- 涉及文件：[../../periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py](../../periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py)
- 验证范围：单字段 policy 解析、默认回退、`surface` 输出、command-spec 不受影响、轻提醒窗分支的可观察行为。

- [ ] Step 1: 改写 preflight 测试中的 policy fixture 和断言，使其只接受单字段 JSON。
- Change: 在 [../../periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py](../../periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py) 中完成以下变更：
  - 所有写入 policy 的 helper 只生成 `{ "windows_popup_enabled": true|false }`
  - 删除对 `popup_disabled_fallback_surface`、`copy_profile`、`tone` 的断言
  - 保留并重写 `surface=modal` / `surface=text` 的断言
  - 保留 `run_command_spec()` 不受 policy 影响的断言
- Run: .\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini ../../periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py -k "policy or surface or command_spec"
- Expected: 当前会失败，失败点集中在代码仍依赖旧 policy schema 或仍输出旧字段。

- [ ] Step 2: 把现有 stdout 端到端测试改成轻提醒窗分支的可观察测试。
- Change: 改写当前的 `test_pre_session_hook_prints_text_reminder_for_text_surface`，不再以 stdout 为主成功信号；改为通过最小测试缝隙验证 `surface=text` 时会进入轻提醒窗分支，并能观察到自动关闭和点击复制行为。
- Run: .\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini ../../periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py -k "pre_session_hook and text_surface" -vv
- Expected: 当前失败，失败点集中在 hook 仍然只做 `Write-Output`，尚无轻提醒窗分支或缺少可验证信号。

### Task 2: 收紧 policy 文件和 preflight 合同

- 目标：让 [../../periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py](../../periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py) 成为单字段 policy 的唯一解释器，并保持 `/ai-heartbeat` 命令契约不变。
- 涉及文件：[../../periodic_jobs/ai_heartbeat/config/reminder_policy.json](../../periodic_jobs/ai_heartbeat/config/reminder_policy.json)、[../../periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py](../../periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py)
- 验证范围：policy 文件只保留一个字段；preflight 正确输出 modal / text；默认值回到 popup on；command-spec 保持稳定。

- [ ] Step 1: 把 policy 文件收成单字段 JSON。
- Change: 修改 [../../periodic_jobs/ai_heartbeat/config/reminder_policy.json](../../periodic_jobs/ai_heartbeat/config/reminder_policy.json)，目标形状固定为：
  - `{ "windows_popup_enabled": true }`
  - 或 `{ "windows_popup_enabled": false }`
  - 删除 `popup_disabled_fallback_surface`、`copy_profile` 等旧字段
- Run: .\.venv\Scripts\python.exe -c "import json, pathlib; p=pathlib.Path(r'periodic_jobs/ai_heartbeat/config/reminder_policy.json'); print(json.loads(p.read_text(encoding='utf-8')))"
- Expected: 成功解析，且打印结果只包含 `windows_popup_enabled`。

- [ ] Step 2: 简化 preflight 的 policy 读取与 reminder spec。
- Change: 修改 [../../periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py](../../periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py)，完成以下最小实现：
  - 只解析 `windows_popup_enabled`
  - policy 缺失、损坏或字段非法时回到内置默认值 `windows_popup_enabled=true`
  - `windows_popup_enabled=true` 时输出 `surface=modal`
  - `windows_popup_enabled=false` 时输出 `surface=text`
  - 输出保留 `surface`、`message`、`due_tasks`、`target_date`、`recommended_command`，不要再依赖 `tone`
  - 保持 `--command-spec` 输出契约不变
- Run: .\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini ../../periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py
- Expected: preflight 测试通过，且与 policy schema 收紧后的断言一致。
- Run: .\.venv\Scripts\python.exe -m py_compile ../../periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py
- Expected: 无语法错误。
- Run: .\.venv\Scripts\python.exe ../../periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py --hook-dialog-spec --state-path ../../periodic_jobs/ai_heartbeat/state/heartbeat_status.json
- Expected: 输出为非空 JSON，包含 `surface` 字段，且不需要旧 `copy_profile` 字段才能工作。

### Task 3: 把 hook 的 `surface=text` 改成轻提醒窗

- 目标：让 [../../.github/hooks/pre-session.ps1](../../.github/hooks/pre-session.ps1) 从“modal 或 stdout”变成“modal 或轻提醒窗”，并给自动化验证留下最小可观察面。
- 涉及文件：[../../.github/hooks/pre-session.ps1](../../.github/hooks/pre-session.ps1)、[../../periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py](../../periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py)
- 验证范围：modal 路径保留；`surface=text` 进入轻提醒窗；轻提醒窗 8.88 秒自动关闭；点击复制 `/ai-heartbeat`；不写 `last_prompted_on`。

- [ ] Step 1: 为轻提醒窗实现准备最小测试缝隙。
- Change: 在 [../../.github/hooks/pre-session.ps1](../../.github/hooks/pre-session.ps1) 中加入只服务验证的最小观测点，使自动化测试能判断：
  - 轻提醒窗分支被调用
  - 自动关闭事件发生
  - 点击复制动作发生
  - 该观测点不能改变默认用户行为，也不能变成新的正式配置面
- Run: Select-String -Path ".github/hooks/pre-session.ps1" -Pattern "Show-HeartbeatDialog|Write-Output|Clipboard|Timer|surface|text"
- Expected: 当前仍能看到旧的 stdout 文本提醒路径，尚无轻提醒窗实现和点击复制锚点。

- [ ] Step 2: 实现轻提醒窗 renderer，并保留 modal 语义。
- Change: 修改 [../../.github/hooks/pre-session.ps1](../../.github/hooks/pre-session.ps1)，完成以下最小实现：
  - 保留现有 `Show-HeartbeatDialog` modal 路径
  - 新增轻量、非模态、8.88 秒自动消失的小提醒窗函数
  - `surface=text` 时调用轻提醒窗，而不是 `Write-Output`
  - 轻提醒窗点击时把 `/ai-heartbeat` 写入剪贴板，然后关闭窗口
  - 轻提醒窗不显示按钮，不写 `last_prompted_on`，不提供 `今天不再提醒`
  - modal 路径仍然是唯一会触发 `--mark-prompted` 的交互路径
- Run: pwsh -NoProfile -Command "$null = [System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path '.github/hooks/pre-session.ps1'), [ref]$null, [ref]$null)"
- Expected: 解析通过，无 PowerShell 语法错误。
- Run: Select-String -Path ".github/hooks/pre-session.ps1" -Pattern "Clipboard|Set-Text|SetText|surface|modal|text|Timer|FormBorderStyle|TopMost"
- Expected: 能命中新轻提醒窗的 UI 与点击复制锚点，同时保留 modal 分支。

- [ ] Step 3: 让端到端测试覆盖轻提醒窗行为。
- Change: 更新 [../../periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py](../../periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py) 中的 hook 端到端用例，使其通过 fake preflight payload + 最小观测点验证：
  - `surface=text` 时进入轻提醒窗分支
  - 默认约 8.88 秒后关闭
  - 点击事件会复制 `/ai-heartbeat`
- Run: .\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini ../../periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py -k "pre_session_hook and text_surface" -vv
- Expected: 新的 hook 端到端用例通过，且不再依赖 stdout 文本输出。

### Task 4: 对齐 AI Heartbeat 自身文档与仓库入口文档

- 目标：让文档全部反映“单字段 policy + popup on/off 两种 surface + 8.88 秒轻提醒窗”的已批准设计。
- 涉及文件：[../../periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md](../../periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md)、[../../periodic_jobs/ai_heartbeat/docs/PRD.md](../../periodic_jobs/ai_heartbeat/docs/PRD.md)、[../../AGENTS.md](../../AGENTS.md)、[../../README.md](../../README.md)、[../../setup_guide.md](../../setup_guide.md)、[../CRONTAB.md](../CRONTAB.md)
- 验证范围：文档不再提旧多字段 policy、text fallback、copy profile；改成单字段 policy 和轻提醒窗语义。

- [ ] Step 1: 先锁定文档中所有旧术语命中。
- Run: Select-String -Path "periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md","periodic_jobs/ai_heartbeat/docs/PRD.md","AGENTS.md","README.md","setup_guide.md","docs/CRONTAB.md" -Pattern "popup_disabled_fallback_surface|copy_profile|gentle|fallback|text reminder|stdout"
- Expected: 当前会命中旧设计术语，证明这些文档仍需更新。

- [ ] Step 2: 只补与新提醒行为直接相关的说明。
- Change: 修改以下文件：
  - [../../periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md](../../periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md)：写明单字段 policy、popup on/off、轻提醒窗 8.88 秒自动消失与点击复制
  - [../../periodic_jobs/ai_heartbeat/docs/PRD.md](../../periodic_jobs/ai_heartbeat/docs/PRD.md)：更新产品行为与术语
  - [../../AGENTS.md](../../AGENTS.md)、[../../README.md](../../README.md)、[../../setup_guide.md](../../setup_guide.md)、[../CRONTAB.md](../CRONTAB.md)：只补 popup on/off 的用户可见行为，不展开实现细节
- Run: Select-String -Path "periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md","periodic_jobs/ai_heartbeat/docs/PRD.md","AGENTS.md","README.md","setup_guide.md","docs/CRONTAB.md" -Pattern "windows_popup_enabled|轻提醒窗|8.88 秒|复制 /ai-heartbeat|popup|modal"
- Expected: 新行为术语命中齐全，旧多字段术语不再是主表述。
- Run: Get-Item "periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md","periodic_jobs/ai_heartbeat/docs/PRD.md","AGENTS.md","README.md","setup_guide.md","docs/CRONTAB.md" | Select-Object Name,Length | Format-Table -AutoSize
- Expected: 所有文档都非空；若任一 notebook-backed 文件长度异常，先修复落盘再继续。

### Task 5: 做收口验证，确认新 policy 没有破坏现有执行边界

- 目标：确认 policy 文件、preflight、hook renderer、测试和文档已经对齐，且 `/ai-heartbeat`、runtime state、status CLI 的既有边界没有被误改。
- 涉及文件：[../../periodic_jobs/ai_heartbeat/config/reminder_policy.json](../../periodic_jobs/ai_heartbeat/config/reminder_policy.json)、[../../periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py](../../periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py)、[../../periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py](../../periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py)、[../../.github/hooks/pre-session.ps1](../../.github/hooks/pre-session.ps1)、[../../periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md](../../periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md)、[../../periodic_jobs/ai_heartbeat/docs/PRD.md](../../periodic_jobs/ai_heartbeat/docs/PRD.md)、[../../AGENTS.md](../../AGENTS.md)、[../../README.md](../../README.md)、[../../setup_guide.md](../../setup_guide.md)、[../CRONTAB.md](../CRONTAB.md)
- 验证范围：聚焦测试通过、Python 语法通过、PowerShell 解析通过、policy 只剩单字段、旧执行边界未被污染。

- [ ] Step 1: 运行 preflight 聚焦测试。
- Run: .\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py
- Expected: 全部通过。

- [ ] Step 2: 运行相关 Python 语法检查。
- Run: .\.venv\Scripts\python.exe -m py_compile periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py periodic_jobs/ai_heartbeat/src/v0/heartbeat_status_cli.py
- Expected: 无语法错误。

- [ ] Step 3: 运行 hook 解析与关键术语审计。
- Run: pwsh -NoProfile -Command "$null = [System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path '.github/hooks/pre-session.ps1'), [ref]$null, [ref]$null)"
- Expected: 解析通过。
- Run: Select-String -Path ".github/hooks/pre-session.ps1","periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py","periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py","periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md","periodic_jobs/ai_heartbeat/docs/PRD.md","AGENTS.md","README.md","setup_guide.md","docs/CRONTAB.md" -Pattern "heartbeat_local_runner.py|run_observer_and_reflector|OpenCode-Builder|OpenCode Server"
- Expected: 无命中。

- [ ] Step 4: 检查 policy 文件和关键文档落盘状态。
- Run: .\.venv\Scripts\python.exe -c "import json, pathlib; p=pathlib.Path(r'periodic_jobs/ai_heartbeat/config/reminder_policy.json'); data=json.loads(p.read_text(encoding='utf-8')); print(sorted(data.keys()))"
- Expected: 只打印 `['windows_popup_enabled']`。
- Run: Get-Item "periodic_jobs/ai_heartbeat/config/reminder_policy.json","periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py",".github/hooks/pre-session.ps1","AGENTS.md","README.md","setup_guide.md","docs/CRONTAB.md" | Select-Object Name,Length | Format-Table -AutoSize
- Expected: 所有关键文件都非空。

## 执行纪律

- 开始实现前，先批判性复查整份计划；如果发现缺项、矛盾、命名不一致或验证命令无效，先修计划。
- 按任务顺序执行，不要无声跳步、合并步或改变任务目标。
- 每完成一个任务，都运行该任务定义的验证。
- 遇到阻塞、重复失败或计划与仓库现实不符，立即停下来说明，不要猜。
- 如果当前就在 `main` 或 `master`，且用户没有明确同意，开始实现前先确认。
- 对 notebook-backed markdown，任何编辑后都必须做长度检查和 read-back；一旦再次出现 0 字节写入，立即切换到 PowerShell UTF-8 fallback。
- 全部任务完成后，运行最终验证并输出修改摘要。

## 最终验证

- Run: .\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py
- Expected: Windows reminder policy 相关测试全部通过。
- Run: .\.venv\Scripts\python.exe -m py_compile periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py periodic_jobs/ai_heartbeat/src/v0/heartbeat_status_cli.py
- Expected: 无语法错误。
- Run: pwsh -NoProfile -Command "$null = [System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path '.github/hooks/pre-session.ps1'), [ref]$null, [ref]$null)"
- Expected: PowerShell hook 解析通过。
- Run: .\.venv\Scripts\python.exe -c "import json, pathlib; p=pathlib.Path(r'periodic_jobs/ai_heartbeat/config/reminder_policy.json'); data=json.loads(p.read_text(encoding='utf-8')); print(sorted(data.keys()))"
- Expected: 只剩 `windows_popup_enabled`。
- Run: Select-String -Path "periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py",".github/hooks/pre-session.ps1","periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py","periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md","periodic_jobs/ai_heartbeat/docs/PRD.md","AGENTS.md","README.md","setup_guide.md","docs/CRONTAB.md" -Pattern "windows_popup_enabled|surface|/ai-heartbeat|轻提醒窗|8.88 秒|剪贴板"
- Expected: 新行为术语命中齐全。
