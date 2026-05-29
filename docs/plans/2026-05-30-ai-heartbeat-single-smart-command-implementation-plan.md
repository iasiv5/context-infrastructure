# AI Heartbeat Single Smart Command 实施计划

## 目标

- 将已批准设计 [docs/specs/2026-05-30-ai-heartbeat-single-smart-command-design.md](docs/specs/2026-05-30-ai-heartbeat-single-smart-command-design.md) 落成当前仓库的唯一推荐执行路径。
- 保留 [periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py) 和 [periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py) 的提醒与状态语义，同时把执行入口收敛成 /ai-heartbeat。
- 让 SessionStart hook 只做提醒，不再直接拉起本地执行器。
- 对齐活文档和当前运行面，并删除与新方案冲突的旧执行脚本、旧 prompt 模板、旧测试和过期运行时产物。

## 架构快照

- 本次采用“自动提醒 + 手动触发的 fully agentic 执行”路径：hook 继续自动检查 observer / reflector 是否到期，但真正的任务执行只在用户显式运行 /ai-heartbeat 时发生。
- [periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py) 继续负责 due-task 计算、同日提醒去重和 hook dialog spec；新增一个给 /ai-heartbeat 使用的稳定 command-spec 输出，避免 prompt 侧自己重复实现状态判断。
- [.github/prompts/ai-heartbeat.prompt.md](.github/prompts/ai-heartbeat.prompt.md) 成为唯一主命令入口；它读取 command-spec，决定执行 observer、reflector 还是 observer+reflector，并在每个任务结束后自动调用 [periodic_jobs/ai_heartbeat/src/v0/heartbeat_status_cli.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_status_cli.py) 回写 success / failed / skipped。
- [.github/hooks/pre-session.ps1](.github/hooks/pre-session.ps1) 保留提醒 UI，但移除本地 direct-exec 链路，不再引用 [periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py)。
- 历史文档保留原样：docs/specs/ 和 docs/plans/ 下旧日期文件不做归档迁移、不做重写。

## 输入工件

- 已批准设计文档：[docs/specs/2026-05-30-ai-heartbeat-single-smart-command-design.md](docs/specs/2026-05-30-ai-heartbeat-single-smart-command-design.md)
- 当前提醒与状态入口：[periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py)、[periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py)、[periodic_jobs/ai_heartbeat/src/v0/heartbeat_status_cli.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_status_cli.py)
- 当前 hook 挂载面：[.github/hooks/ai-heartbeat.session-start.json](.github/hooks/ai-heartbeat.session-start.json)、[.github/hooks/pre-session.ps1](.github/hooks/pre-session.ps1)
- 当前活文档：[periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md](periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md)、[periodic_jobs/ai_heartbeat/docs/PRD.md](periodic_jobs/ai_heartbeat/docs/PRD.md)、[README.md](README.md)、[setup_guide.md](setup_guide.md)、[docs/CRONTAB.md](docs/CRONTAB.md)、[AGENTS.md](AGENTS.md)
- 当前测试面：[periodic_jobs/ai_heartbeat/tests/test_heartbeat_state.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_state.py)、[periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py)、[periodic_jobs/ai_heartbeat/tests/test_heartbeat_status_cli.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_status_cli.py)、[periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py)、[periodic_jobs/ai_heartbeat/tests/test_observer_reflector_status.py](periodic_jobs/ai_heartbeat/tests/test_observer_reflector_status.py)
- 编辑约束：README.md、setup_guide.md、docs/CRONTAB.md、AGENTS.md 是 notebook-backed markdown。实现时优先用 notebook-aware 编辑；若工具再次命中 Windows 0 字节写入 bug，必须立即切换到 PowerShell UTF-8 fallback，并在同一步完成长度与 read-back 校验。

## 文件结构与职责

- Create: [.github/prompts/ai-heartbeat.prompt.md](.github/prompts/ai-heartbeat.prompt.md)
  - 仓库唯一主命令入口；负责读取 command-spec、处理 override、执行 observer / reflector 语义并自动回写状态。
- Modify: [periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py)
  - 新增 command-spec 输出，调整 hook 提示文案，移除本地 runner 命令指导。
- Test: [periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py)
  - 锁定 reminder-only 输出、/ai-heartbeat 引导文案和 command-spec 行为。
- Modify: [.github/hooks/pre-session.ps1](.github/hooks/pre-session.ps1)
  - 保留提醒 UI，移除 direct-exec 路径与旧任务选项编排。
- Delete: [periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py)
  - 退役旧本地执行器。
- Delete: [periodic_jobs/ai_heartbeat/src/v0/prompts/observer.md](periodic_jobs/ai_heartbeat/src/v0/prompts/observer.md)
  - 删除旧 observer prompt 模板。
- Delete: [periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md](periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md)
  - 删除旧 reflector prompt 模板。
- Delete: [periodic_jobs/ai_heartbeat/src/v0/_legacy_opencode](periodic_jobs/ai_heartbeat/src/v0/_legacy_opencode)
  - 删除更早的 OpenCode 触发器遗留目录。
- Delete: [periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py)
  - 删除与退役执行面绑定的测试。
- Delete: [periodic_jobs/ai_heartbeat/tests/test_observer_reflector_status.py](periodic_jobs/ai_heartbeat/tests/test_observer_reflector_status.py)
  - 删除与退役 observer.py / reflector.py 入口绑定的测试。
- Modify: [.gitignore](.gitignore)
  - 移除 heartbeat_reflector_report.md 和 claude_runs/ 的 ignore 条目；保留 heartbeat_status.json ignore。
- Delete: [periodic_jobs/ai_heartbeat/state/heartbeat_reflector_report.md](periodic_jobs/ai_heartbeat/state/heartbeat_reflector_report.md)
  - 删除已退役的本地 runner 报告产物。
- Modify: [periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md](periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md)
  - 把当前事实源对齐到“提醒层自动、执行层 /ai-heartbeat 显式触发”。
- Modify: [periodic_jobs/ai_heartbeat/docs/PRD.md](periodic_jobs/ai_heartbeat/docs/PRD.md)
  - 更新产品用户故事和执行入口。
- Modify: [AGENTS.md](AGENTS.md)
  - 把 AI Heartbeat 的会前 hook 表述改成“提醒 + 指向 /ai-heartbeat”，不再说“会前选择框和本地执行”。
- Modify: [README.md](README.md)
  - 更新目录树、默认使用方式和主命令说明。
- Modify: [setup_guide.md](setup_guide.md)
  - 把默认手动执行路径从 heartbeat_local_runner.py 改成 /ai-heartbeat。
- Modify: [docs/CRONTAB.md](docs/CRONTAB.md)
  - 把 cron 路径改成服务 /ai-heartbeat 方案的可选增强，而不是旧本地 runner 的直接入口。
- Keep: [periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py)
  - 无需改动状态语义，除非实现中发现 command-spec 输出必须补一个最小 helper。
- Keep: [periodic_jobs/ai_heartbeat/src/v0/heartbeat_status_cli.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_status_cli.py)
  - 继续作为自动状态回写入口，除非实现中发现参数契约缺口。
- Keep: [periodic_jobs/ai_heartbeat/tests/test_heartbeat_state.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_state.py)
- Keep: [periodic_jobs/ai_heartbeat/tests/test_heartbeat_status_cli.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_status_cli.py)

## 任务清单

### Task 1: 把 preflight 收敛成“提醒 + command-spec”合同

- 目标：让 [periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py) 同时服务 SessionStart hook 和 /ai-heartbeat，但不再输出本地 runner 命令。
- 涉及文件：[periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py)、[periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py)
- 验证范围：command-spec 输出、hook dialog spec、hook message、同日去重逻辑

- [ ] Step 1: 先把测试改成新合同，锁定旧行为已经不再成立。
- Change: 在 [periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py) 中新增或改写用例，覆盖以下行为：
  - --command-spec 返回稳定 JSON，包含 due_tasks、target_date 和推荐执行计划，但不写 last_prompted_on
  - run_hook() 和 run_hook_dialog_spec() 仍会写 last_prompted_on
  - hook message 不再出现 heartbeat_local_runner.py
  - hook dialog spec 不再出现“执行 observer / reflector / observer + reflector”这组三选项，而是提醒型 payload + /ai-heartbeat 引导
- Run: .\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py
- Expected: 当前测试失败，失败点集中在缺少 --command-spec、旧 runner 命令仍在输出、dialog spec 仍暴露旧执行选项。

- [ ] Step 2: 在 preflight 中实现新的命令侧合同，并同步收缩 hook 文案。
- Change: 修改 [periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py)，完成以下最小实现：
  - 新增 --command-spec CLI 模式，输出稳定 JSON，供 /ai-heartbeat 读取
  - 移除 _local_runner_command() 及其在 hook message 中的展示职责
  - 把 build_dialog_spec() 和 build_hook_message() 改成提醒型合同，明确推荐 /ai-heartbeat
  - 保持 run_hook() / run_hook_dialog_spec() 继续负责 last_prompted_on 去重更新
- [ ] Step 3: 重新运行聚焦验证并确认通过。
- Run: .\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py
- Expected: preflight 测试全部通过。
- Run: .\.venv\Scripts\python.exe -m py_compile periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py
- Expected: 无语法错误。
- Run: .\.venv\Scripts\python.exe periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py --help
- Expected: --command-spec 和 --hook-dialog-spec 都出现在帮助输出中。

### Task 2: 把 SessionStart hook 改成纯提醒 UI

- 目标：让 [.github/hooks/pre-session.ps1](.github/hooks/pre-session.ps1) 不再根据用户选择直接启动本地 runner，而是只展示提醒并退出。
- 涉及文件：[.github/hooks/pre-session.ps1](.github/hooks/pre-session.ps1)
- 验证范围：语法正确、旧 direct-exec 链路已移除、hook 仍读取 --hook-dialog-spec

- [ ] Step 1: 先锁定当前脚本里仍然存在的 direct-exec 锚点。
- Run: Select-String -Path ".github/hooks/pre-session.ps1" -Pattern "heartbeat_local_runner.py|Start-HeartbeatLocalExecution|Start-HeartbeatSelectionExecution|run_observer|run_reflector|run_observer_and_reflector"
- Expected: 当前会返回命中，证明 hook 仍绑定旧执行链路。

- [ ] Step 2: 把 hook 改成 reminder-only，并收缩不再使用的 helper。
- Change: 修改 [.github/hooks/pre-session.ps1](.github/hooks/pre-session.ps1)，完成以下最小改动：
  - 删除或移除引用 heartbeat_local_runner.py 的 direct-exec helper
  - 调整 dialog 消费逻辑，使其只展示提醒和推荐命令 /ai-heartbeat
  - 关闭“用户在弹窗里决定 observer / reflector 执行顺序”的旧职责
- [ ] Step 3: 运行语法与静态回归检查。
- Run: pwsh -NoProfile -Command "$null = [System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path '.github/hooks/pre-session.ps1'), [ref]$null, [ref]$null)"
- Expected: 解析通过，无 PowerShell 语法错误。
- Run: Select-String -Path ".github/hooks/pre-session.ps1" -Pattern "heartbeat_local_runner.py|Start-HeartbeatLocalExecution|Start-HeartbeatSelectionExecution"
- Expected: 无命中。
- Run: Select-String -Path ".github/hooks/pre-session.ps1" -Pattern "hook-dialog-spec|Show-HeartbeatDialog"
- Expected: 仍存在 hook dialog 读取与 UI 展示路径。

### Task 3: 创建 /ai-heartbeat 主命令 prompt

- 目标：新增 [.github/prompts/ai-heartbeat.prompt.md](.github/prompts/ai-heartbeat.prompt.md)，把默认路径、override 语义、observer 幂等和自动状态回写写成可执行合同。
- 涉及文件：[.github/prompts/ai-heartbeat.prompt.md](.github/prompts/ai-heartbeat.prompt.md)
- 验证范围：frontmatter、默认决策表、override 语义、状态回写指令、observer 幂等指令

- [ ] Step 1: 先确认主命令资产当前不存在。
- Run: Test-Path ".github/prompts/ai-heartbeat.prompt.md"
- Expected: 返回 False。

- [ ] Step 2: 创建主命令 prompt，并把执行合同写死。
- Change: 创建 [.github/prompts/ai-heartbeat.prompt.md](.github/prompts/ai-heartbeat.prompt.md)，至少覆盖以下内容：
  - frontmatter 中的命令名与描述
  - 先读取 [AGENTS.md](AGENTS.md)、[periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md](periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md)、[periodic_jobs/ai_heartbeat/docs/PRD.md](periodic_jobs/ai_heartbeat/docs/PRD.md)
  - 通过 heartbeat_preflight.py --command-spec 读取 due-task 状态
  - 默认决策表：observer only / reflector only / both / none
  - override：force observer、force reflector、force both
  - observer 先检查 [contexts/memory/OBSERVATIONS.md](contexts/memory/OBSERVATIONS.md) 当天 Date: 条目，已有则调用 heartbeat_status_cli.py --status skipped
  - observer / reflector 成功或失败后自动调用 heartbeat_status_cli.py
- [ ] Step 3: 运行 prompt 资产存在性和关键语义检查。
- Run: Get-Item ".github/prompts/ai-heartbeat.prompt.md" | Select-Object FullName,Length | Format-List
- Expected: 文件存在，且 Length 大于 0。
- Run: Select-String -Path ".github/prompts/ai-heartbeat.prompt.md" -Pattern "name:|ai-heartbeat|force observer|force reflector|force both|heartbeat_preflight.py|heartbeat_status_cli.py|OBSERVATIONS.md"
- Expected: 关键锚点全部命中。

### Task 4: 删除旧执行面与旧测试，并清理 ignore/runtime 残留

- 目标：把新方案明确退役的本地 runner、旧 prompt、旧 OpenCode 触发器、旧测试和旧运行时产物从当前运行面移除。
- 涉及文件：[periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py)、[periodic_jobs/ai_heartbeat/src/v0/prompts/observer.md](periodic_jobs/ai_heartbeat/src/v0/prompts/observer.md)、[periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md](periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md)、[periodic_jobs/ai_heartbeat/src/v0/_legacy_opencode](periodic_jobs/ai_heartbeat/src/v0/_legacy_opencode)、[periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py)、[periodic_jobs/ai_heartbeat/tests/test_observer_reflector_status.py](periodic_jobs/ai_heartbeat/tests/test_observer_reflector_status.py)、[periodic_jobs/ai_heartbeat/state/heartbeat_reflector_report.md](periodic_jobs/ai_heartbeat/state/heartbeat_reflector_report.md)、[.gitignore](.gitignore)
- 验证范围：旧文件已删除、.gitignore 已移除旧忽略项、当前目录树不再出现旧执行面

- [ ] Step 1: 先确认这些旧入口和旧测试当前仍然存在。
- Run: Get-ChildItem "periodic_jobs/ai_heartbeat/src/v0" -Name
- Expected: 当前输出包含 heartbeat_local_runner.py、prompts、_legacy_opencode。
- Run: Get-ChildItem "periodic_jobs/ai_heartbeat/tests" -Name
- Expected: 当前输出包含 test_heartbeat_local_runner.py 和 test_observer_reflector_status.py。

- [ ] Step 2: 删除旧执行面与旧测试，并同步收缩 ignore/runtime 残留。
- Change: 删除以下内容：
  - [periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py)
  - [periodic_jobs/ai_heartbeat/src/v0/prompts/observer.md](periodic_jobs/ai_heartbeat/src/v0/prompts/observer.md)
  - [periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md](periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md)
  - [periodic_jobs/ai_heartbeat/src/v0/_legacy_opencode](periodic_jobs/ai_heartbeat/src/v0/_legacy_opencode)
  - [periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py)
  - [periodic_jobs/ai_heartbeat/tests/test_observer_reflector_status.py](periodic_jobs/ai_heartbeat/tests/test_observer_reflector_status.py)
  - [periodic_jobs/ai_heartbeat/state/heartbeat_reflector_report.md](periodic_jobs/ai_heartbeat/state/heartbeat_reflector_report.md)
  - 本地 periodic_jobs/ai_heartbeat/state/claude_runs/（若存在）
  - .gitignore 中 heartbeat_reflector_report.md 和 claude_runs/ 的 ignore 行
- [ ] Step 3: 运行清理回归检查。
- Run: Test-Path "periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py"; Test-Path "periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py"; Test-Path "periodic_jobs/ai_heartbeat/tests/test_observer_reflector_status.py"; Test-Path "periodic_jobs/ai_heartbeat/state/heartbeat_reflector_report.md"
- Expected: 全部返回 False。
- Run: Select-String -Path ".gitignore" -Pattern "heartbeat_reflector_report.md|claude_runs"
- Expected: 无命中。
- Run: Get-ChildItem "periodic_jobs/ai_heartbeat/src/v0" -Name
- Expected: 不再包含 heartbeat_local_runner.py、prompts、_legacy_opencode。

### Task 5: 对齐 AI Heartbeat 的事实源文档

- 目标：让 [periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md](periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md) 和 [periodic_jobs/ai_heartbeat/docs/PRD.md](periodic_jobs/ai_heartbeat/docs/PRD.md) 不再描述旧的 OpenCode / local runner 执行面，而是描述当前的提醒层与主命令模型。
- 涉及文件：[periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md](periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md)、[periodic_jobs/ai_heartbeat/docs/PRD.md](periodic_jobs/ai_heartbeat/docs/PRD.md)
- 验证范围：旧 runtime 名称与旧 direct-exec 描述已移除，新主路径已写清

- [ ] Step 1: 先锁定文档里当前仍绑定旧方案的段落。
- Run: Select-String -Path "periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md","periodic_jobs/ai_heartbeat/docs/PRD.md" -Pattern "OpenCode-Builder|OpenCode Server|create_session|send_message|本地执行器|heartbeat_local_runner.py|Claude CLI|copilot CLI"
- Expected: 当前会返回命中，说明事实源仍混有旧运行面叙述。

- [ ] Step 2: 按已批准设计重写事实源，不改 observer / reflector 的核心职责。
- Change: 修改 [periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md](periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md) 和 [periodic_jobs/ai_heartbeat/docs/PRD.md](periodic_jobs/ai_heartbeat/docs/PRD.md)，至少完成以下对齐：
  - 明确 hook 只负责自动提醒
  - 明确 /ai-heartbeat 是当前唯一主执行入口
  - observer / reflector 继续保留 L1 / L2 语义
  - success / failed / skipped 继续回写状态系统
  - 历史 spec / plan 保留原样，不纳入当前事实源
- [ ] Step 3: 运行术语审计和长度检查。
- Run: Select-String -Path "periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md","periodic_jobs/ai_heartbeat/docs/PRD.md" -Pattern "heartbeat_local_runner.py|OpenCode-Builder|OpenCode Server|Claude CLI|copilot CLI"
- Expected: 无命中。
- Run: Get-Item "periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md","periodic_jobs/ai_heartbeat/docs/PRD.md" | Select-Object Name,Length | Format-Table -AutoSize
- Expected: 两个文件都非空，Length 明显大于 0。

### Task 6: 对齐面向仓库使用者的活文档与说明入口

- 目标：让 [AGENTS.md](AGENTS.md)、[README.md](README.md)、[setup_guide.md](setup_guide.md)、[docs/CRONTAB.md](docs/CRONTAB.md) 的默认路径全部收敛到“hook 提醒 + /ai-heartbeat 显式触发”。
- 涉及文件：[AGENTS.md](AGENTS.md)、[README.md](README.md)、[setup_guide.md](setup_guide.md)、[docs/CRONTAB.md](docs/CRONTAB.md)
- 验证范围：旧 runner/compat 说法已删除，notebook-backed 文档真实落盘

- [ ] Step 1: 先确认这些活文档里还存在旧执行入口与兼容说法。
- Run: Select-String -Path "AGENTS.md","README.md","setup_guide.md","docs/CRONTAB.md" -Pattern "heartbeat_local_runner.py|observer.py|reflector.py|Claude CLI|claude_runs|heartbeat_reflector_report|按到期状态提醒并触发|本地执行器"
- Expected: 当前会有命中。

- [ ] Step 2: 更新活文档，并严格按 notebook-backed 约束做落盘验证。
- Change: 修改以下文件：
  - [AGENTS.md](AGENTS.md)：把“会前选择框和本地执行”改成“会前提醒 + /ai-heartbeat”
  - [README.md](README.md)：更新目录树、主路径说明和 AI Heartbeat 使用方式
  - [setup_guide.md](setup_guide.md)：把默认执行路径改成 /ai-heartbeat，保留 cron 作为可选增强
  - [docs/CRONTAB.md](docs/CRONTAB.md)：让 cron 场景服务新方案，而不是旧 local runner
- [ ] Step 3: 立即做术语审计、长度检查和 read-back，防止 notebook-backed 文档空写。
- Run: Select-String -Path "AGENTS.md","README.md","setup_guide.md","docs/CRONTAB.md" -Pattern "heartbeat_local_runner.py|observer.py|reflector.py|Claude CLI|claude_runs|heartbeat_reflector_report|按到期状态提醒并触发|本地执行器"
- Expected: 无命中。
- Run: Select-String -Path "AGENTS.md","README.md","setup_guide.md","docs/CRONTAB.md" -Pattern "ai-heartbeat|heartbeat_preflight.py|SessionStart|cron|observer|reflector"
- Expected: 新主路径与核心概念命中齐全。
- Run: Get-Item "AGENTS.md","README.md","setup_guide.md","docs/CRONTAB.md" | Select-Object Name,Length | Format-Table -AutoSize
- Expected: 四个文件都非空，Length 明显大于 0。
- Run: Get-Content "setup_guide.md" -TotalCount 40
- Expected: 能直接读回新的 Step 3 / AI Heartbeat 说明，不是旧 runner 文案，也不是空文件。

### Task 7: 做一次收口验证，只保留新执行面

- 目标：确认提醒层、状态层、主命令资产、活文档和清理结果已经彼此对齐，不再残留旧执行面作为当前事实。
- 涉及文件：[periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py)、[periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py)、[periodic_jobs/ai_heartbeat/src/v0/heartbeat_status_cli.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_status_cli.py)、[.github/prompts/ai-heartbeat.prompt.md](.github/prompts/ai-heartbeat.prompt.md)、[.github/hooks/pre-session.ps1](.github/hooks/pre-session.ps1)、[periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md](periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md)、[periodic_jobs/ai_heartbeat/docs/PRD.md](periodic_jobs/ai_heartbeat/docs/PRD.md)、[AGENTS.md](AGENTS.md)、[README.md](README.md)、[setup_guide.md](setup_guide.md)、[docs/CRONTAB.md](docs/CRONTAB.md)
- 验证范围：保留测试通过、脚本语法通过、旧执行面已退出、活文档与新路径一致

- [ ] Step 1: 运行保留测试集。
- Run: .\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests/test_heartbeat_state.py periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py periodic_jobs/ai_heartbeat/tests/test_heartbeat_status_cli.py
- Expected: 三个保留测试文件全部通过。

- [ ] Step 2: 运行保留 Python 脚本语法检查。
- Run: .\.venv\Scripts\python.exe -m py_compile periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py periodic_jobs/ai_heartbeat/src/v0/heartbeat_status_cli.py
- Expected: 无语法错误。

- [ ] Step 3: 运行 hook 解析与活文档术语审计。
- Run: pwsh -NoProfile -Command "$null = [System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path '.github/hooks/pre-session.ps1'), [ref]$null, [ref]$null)"
- Expected: 解析通过。
- Run: Select-String -Path ".github/hooks/pre-session.ps1","periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py",".github/prompts/ai-heartbeat.prompt.md","periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md","periodic_jobs/ai_heartbeat/docs/PRD.md","AGENTS.md","README.md","setup_guide.md","docs/CRONTAB.md" -Pattern "heartbeat_local_runner.py|observer.py|reflector.py|OpenCode-Builder|OpenCode Server|Claude CLI|claude_runs|heartbeat_reflector_report"
- Expected: 无命中。

- [ ] Step 4: 检查当前目录树与关键文件长度。
- Run: Get-ChildItem "periodic_jobs/ai_heartbeat/src/v0" -Name; Get-ChildItem "periodic_jobs/ai_heartbeat/tests" -Name
- Expected: 目录树只剩新方案保留的脚本与测试，不再包含 runner、旧 prompts、_legacy_opencode 和旧测试文件。
- Run: Get-Item ".github/prompts/ai-heartbeat.prompt.md","periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md","periodic_jobs/ai_heartbeat/docs/PRD.md","AGENTS.md","README.md","setup_guide.md","docs/CRONTAB.md" | Select-Object Name,Length | Format-Table -AutoSize
- Expected: 所有关键文件都非空，长度合理。

## 执行纪律

- 开始实现前，先批判性复查整份计划；如果发现命名、路径、删除范围或验证命令与仓库现实不符，先修计划再动手。
- 严格按任务顺序执行，不要把“preflight 合同改造”“hook 提醒收缩”“主命令创建”“旧执行面清理”“活文档对齐”合成一个不可验证的大提交。
- 每完成一个任务，都运行该任务定义的验证；验证失败时，先在当前任务里修复，不要跳到后续任务。
- 对 notebook-backed markdown 文件，第一次写入后必须立即做长度检查和 read-back；一旦再次命中 0 字节落盘，立即切换到 PowerShell UTF-8 fallback 并在同一步修复。
- 删除脚本和测试前，先确认它们只绑定退役执行面；不要误删仍被保留状态链依赖的文件。
- 如果当前就在 main 或 master，且用户没有明确同意，开始实现前先确认。
- 全部任务完成后，先跑最终验证，再输出修改摘要；不要在未通过最终验证时宣称迁移完成。

## 最终验证

- 运行保留测试：
  - .\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests/test_heartbeat_state.py periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py periodic_jobs/ai_heartbeat/tests/test_heartbeat_status_cli.py
- 运行保留 Python 语法检查：
  - .\.venv\Scripts\python.exe -m py_compile periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py periodic_jobs/ai_heartbeat/src/v0/heartbeat_status_cli.py
- 运行 hook 解析：
  - pwsh -NoProfile -Command "$null = [System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path '.github/hooks/pre-session.ps1'), [ref]$null, [ref]$null)"
- 运行旧执行面术语审计：
  - Select-String -Path ".github/hooks/pre-session.ps1","periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py",".github/prompts/ai-heartbeat.prompt.md","periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md","periodic_jobs/ai_heartbeat/docs/PRD.md","AGENTS.md","README.md","setup_guide.md","docs/CRONTAB.md" -Pattern "heartbeat_local_runner.py|observer.py|reflector.py|OpenCode-Builder|OpenCode Server|Claude CLI|claude_runs|heartbeat_reflector_report"
- 运行目录树与长度检查：
  - Get-ChildItem "periodic_jobs/ai_heartbeat/src/v0" -Name; Get-ChildItem "periodic_jobs/ai_heartbeat/tests" -Name
  - Get-Item ".github/prompts/ai-heartbeat.prompt.md","periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md","periodic_jobs/ai_heartbeat/docs/PRD.md","AGENTS.md","README.md","setup_guide.md","docs/CRONTAB.md" | Select-Object Name,Length | Format-Table -AutoSize
- 预期结果：
  - 保留测试通过。
  - 关键 Python 脚本无语法错误。
  - hook 已退回提醒职责，不再直接执行任务。
  - /ai-heartbeat 成为唯一主入口。
  - 旧执行面、旧测试和旧运行时产物已从当前运行面退出。
  - 活文档全部与新方案一致，且没有 notebook-backed 空写问题。

## 审阅 Checkpoint

- 实施计划保存后，先由用户审阅。
- 用户批准前，不进入实现。
- 审阅通过后，下一步应由普通编码 agent 或人工按本计划执行，而不是在当前 planning 流程里直接切进编码。