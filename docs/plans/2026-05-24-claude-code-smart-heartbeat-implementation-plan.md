# Claude Code Smart Heartbeat 实施计划

## 目标

- 将已批准设计 [docs/specs/2026-05-24-claude-code-smart-heartbeat-design.md](docs/specs/2026-05-24-claude-code-smart-heartbeat-design.md) 落成可执行实现。
- 把 [periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py) 从当前机械 observer / reflector 执行器改造成 Claude Code 驱动的触发器。
- 为 observer / reflector 引入已提交的 prompt 模板、运行日志、后置验证和 reflector 专用 git checkpoint 恢复机制。
- 保持现有 SessionStart hook、preflight、状态文件和任务入口不变，不在本次计划中改动 `.github/hooks/pre-session.ps1` 或 `heartbeat_preflight.py`。

## 架构快照

- `heartbeat_local_runner.py` 保留参数解析、路径解析、状态回写和任务分发职责，但移除本地机械扫描与固定模板晋升逻辑，改为围绕 Claude Code CLI 组织 observer / reflector 执行。
- observer 与 reflector 共享一套 Claude CLI 调用基础设施：prompt 模板加载、prompt 渲染、stdout / stderr / 元数据落盘、退出码检查和最小结果验证。
- observer 仍保持 append-only 语义：Claude 直接更新 [contexts/memory/OBSERVATIONS.md](contexts/memory/OBSERVATIONS.md)，runner 只在结束后验证 target date 条目是否存在。
- reflector 改为 Claude 直接执行 GC 和规则写入；runner 只负责 allowlist 约束、git 基线选择、失败恢复和 report 校验。
- prompt 模板存放在 `periodic_jobs/ai_heartbeat/src/v0/prompts/`，作为实现的一部分提交到仓库；运行期副本和 Claude 执行日志写到 `periodic_jobs/ai_heartbeat/state/claude_runs/`，并通过 `.gitignore` 忽略。

## 输入工件

- 已批准设计文档：[docs/specs/2026-05-24-claude-code-smart-heartbeat-design.md](docs/specs/2026-05-24-claude-code-smart-heartbeat-design.md)
- 当前执行器：[periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py)
- 当前 observer / reflector prompt 源材料：[periodic_jobs/ai_heartbeat/src/v0/observer.py](periodic_jobs/ai_heartbeat/src/v0/observer.py)、[periodic_jobs/ai_heartbeat/src/v0/reflector.py](periodic_jobs/ai_heartbeat/src/v0/reflector.py)
- 当前 local runner 测试：[periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py)
- 当前状态 / preflight 约束：[periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py)、[periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py)
- 当前运行时忽略规则：[.gitignore](.gitignore)

## 文件结构与职责

- Modify: [periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py)
  - 用 Claude CLI 触发 observer / reflector，替换当前机械实现。
  - 增加 prompt 加载 / 渲染、运行日志、observer 后置验证、reflector allowlist 校验、git 基线与恢复逻辑。
- Create: [periodic_jobs/ai_heartbeat/src/v0/prompts/observer.md](periodic_jobs/ai_heartbeat/src/v0/prompts/observer.md)
  - observer 的正式任务协议，来源于原版 observer prompt，并适配 Claude Code CLI。
- Create: [periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md](periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md)
  - reflector 的正式任务协议，来源于原版 reflector prompt，并收紧到首版 allowlist。
- Modify: [periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py)
  - 把当前机械 runner 断言替换成 Claude 驱动路径的单元测试和恢复测试。
- Modify: [.gitignore](.gitignore)
  - 忽略 `periodic_jobs/ai_heartbeat/state/claude_runs/` 运行日志目录。
- Runtime output: `periodic_jobs/ai_heartbeat/state/claude_runs/`
  - 保存每次 observer / reflector 的 prompt 副本、stdout、stderr 和元数据 JSON；不纳入版本控制。

编辑约束说明：

- 新增的 prompt 模板是 Markdown 文件。创建后必须立即做文件长度和 read-back 验证，避免当前 Windows 工具链把 Markdown 写成 0 字节。
- 本计划不修改 [periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py)、[periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py) 和 [.github/hooks/pre-session.ps1](.github/hooks/pre-session.ps1)；如果执行过程中发现必须改这三处，先停下来修计划。
- reflector 的写面必须始终局限在设计文档定义的 allowlist；不要在实现时临时扩大到更多 `rules/skills/` 文件。

## 任务清单

### Task 1: 建立 Claude observer happy path 和 prompt 模板

- 目标：先把 observer 的成功路径从机械分桶切到 Claude Code 执行，并把 prompt 模板正式落盘。
- 涉及文件：[periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py)、[periodic_jobs/ai_heartbeat/src/v0/prompts/observer.md](periodic_jobs/ai_heartbeat/src/v0/prompts/observer.md)、[periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py)
- 验证命令：
  - `.\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py -k observer`
  - `.\.venv\Scripts\python.exe -m py_compile periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py`
  - `Get-Item periodic_jobs/ai_heartbeat/src/v0/prompts/observer.md | Format-List Length | Out-String`
- 预期结果：
  - observer prompt 模板真实存在且非空。
  - runner 在 observer 成功路径上会调用 Claude CLI，而不是 `_iter_recent_files` / `_build_observer_lines` 这类机械逻辑。
  - 当 Claude 执行成功且 `OBSERVATIONS.md` 出现 target date 条目时，状态被记为 success。
- [ ] Step 1: 在 [periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py) 中新增 observer-focused 失败测试，覆盖 prompt 模板加载、Claude CLI 调用和 target date 后置验证；保留现有 skip 语义断言。
- [ ] Step 2: 运行 `.\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py -k observer`，确认当前失败来自缺失的 Claude observer 路径，而不是测试搭建错误。
- [ ] Step 3: 创建 [periodic_jobs/ai_heartbeat/src/v0/prompts/observer.md](periodic_jobs/ai_heartbeat/src/v0/prompts/observer.md)，并在 [periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py) 中实现 observer 所需的最小 helper：prompt 路径解析、模板读取 / 渲染、Claude CLI 调用、observer 结果验证。
- [ ] Step 4: 立即检查 `observer.md` 的文件长度并做 read-back，确认没有 0 字节写入问题。
- [ ] Step 5: 重新运行 `.\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py -k observer` 和 `.\.venv\Scripts\python.exe -m py_compile periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py`，确认 observer happy path 通过。

### Task 2: 锁住 observer 的失败语义和运行日志

- 目标：在 observer 路径上补齐“不降级、显式失败、保留运行证据”的语义。
- 涉及文件：[periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py)、[periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py)、[.gitignore](.gitignore)
- 验证命令：
  - `.\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py -k "observer and (fail or error or artifact)"`
  - `rg -n "claude_runs" .gitignore`
  - `rg -n "_build_observer_lines|Local observer scan detected" periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py`
- 预期结果：
  - Claude CLI 不存在、退出码非 0、JSON 不可解析、或 target date 未写入时，observer 都记为 failed。
  - 失败时会在 `state/claude_runs/` 下保留 prompt / stdout / stderr / 元数据，而不是静默丢失。
  - `.gitignore` 已忽略 `periodic_jobs/ai_heartbeat/state/claude_runs/`。
  - runner 中不再保留 observer 的机械分桶实现。
- [ ] Step 1: 在 [periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py) 中新增 observer 失败测试，覆盖 CLI 缺失、非 0 退出、无效 JSON 和后置验证失败场景，并断言失败时会写出运行日志目录。
- [ ] Step 2: 运行 `.\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py -k "observer and (fail or error or artifact)"`，确认当前失败点集中在缺失的日志与失败处理语义。
- [ ] Step 3: 修改 [periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py) 与 [.gitignore](.gitignore)，实现 `claude_runs/` 运行日志落盘、observer 失败状态记录，以及“失败不降级到机械扫描”的行为；同时删除已无用的 observer 机械 helper。
- [ ] Step 4: 重新运行 `.\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py -k "observer and (fail or error or artifact)"`，再用 `rg -n "claude_runs" .gitignore` 和 `rg -n "_build_observer_lines|Local observer scan detected" periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py` 确认运行日志规则和 observer 机械路径都已对齐。

### Task 3: 建立 reflector Claude happy path、report 校验和 allowlist 约束

- 目标：把 reflector 从当前固定模板 GC / 晋升逻辑切到 Claude Code 执行，并锁住首版 allowlist 写面。
- 涉及文件：[periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py)、[periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md](periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md)、[periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py)
- 验证命令：
  - `.\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py -k reflector`
  - `.\.venv\Scripts\python.exe -m py_compile periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py`
  - `Get-Item periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md | Format-List Length | Out-String`
  - `rg -n "_build_reflection_rules|controlled local-reflector output|Local Reflector Report" periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py`
- 预期结果：
  - reflector prompt 模板真实存在且非空。
  - Claude 成功路径上，runner 校验 report 存在、包含 target date，且 touched files 全在 allowlist 内。
  - 旧的本地固定规则生成与固定 report 写入逻辑已从 runner 中移除。
- [ ] Step 1: 在 [periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py) 中新增 reflector 成功路径失败测试，覆盖 prompt 模板加载、report/date 校验、touched files allowlist 校验和 success 状态回写。
- [ ] Step 2: 运行 `.\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py -k reflector`，确认失败信号来自当前 reflector 仍是机械实现。
- [ ] Step 3: 创建 [periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md](periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md)，并修改 [periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py) 以实现 reflector 的 Claude happy path、固定 allowlist 和 report 校验；同时移除 `_prune_observations`、`_build_reflection_rules`、`_write_rules_promotions`、`_write_reflector_report` 等机械 reflector 逻辑。
- [ ] Step 4: 立即检查 `reflector.md` 的文件长度并做 read-back，确认模板没有写丢。
- [ ] Step 5: 重新运行 `.\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py -k reflector`、`.\.venv\Scripts\python.exe -m py_compile periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py`，以及 `rg -n "_build_reflection_rules|controlled local-reflector output|Local Reflector Report" periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py`，确认 reflector 已完全切换到 Claude 路径。

### Task 4: 实现 reflector 的 git 基线选择、checkpoint 和失败恢复

- 目标：把设计里约定的 clean HEAD / dirty checkpoint 两种恢复语义落到代码里，并通过聚焦测试锁住失败恢复边界。
- 涉及文件：[periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py)、[periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py)
- 验证命令：
  - `.\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py -k "reflector and (checkpoint or restore or git)"`
  - `.\.venv\Scripts\python.exe -m py_compile periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py`
- 预期结果：
  - reflector 触面 clean 时直接把当前 HEAD 当恢复基线。
  - reflector 触面 dirty 时会创建临时 git checkpoint。
  - Claude 执行失败、report 校验失败或越界写入 allowlist 之外文件时，只恢复 reflector allowlist 触面。
  - 成功路径会清理临时 checkpoint，不留下长期历史污染。
- [ ] Step 1: 在 [periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py) 中新增 reflector 的 git 失败测试，覆盖 clean 基线、dirty checkpoint、失败恢复和越界写入检测。
- [ ] Step 2: 运行 `.\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py -k "reflector and (checkpoint or restore or git)"`，确认当前失败集中在缺失的 git 基线与恢复逻辑。
- [ ] Step 3: 修改 [periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py)，实现 reflector allowlist 的 git 状态检查、临时 checkpoint、失败恢复、成功清理和越界写入判定。
- [ ] Step 4: 重新运行 `.\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py -k "reflector and (checkpoint or restore or git)"` 与 `.\.venv\Scripts\python.exe -m py_compile periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py`，确认恢复逻辑稳定且无语法错误。

### Task 5: 做一次 heartbeat 级收口验证

- 目标：确认本次切片没有破坏现有 preflight / state / status CLI 约束，并把 runner、prompt、测试和 ignore 规则收口到一个可执行状态。
- 涉及文件：[periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py)、[periodic_jobs/ai_heartbeat/src/v0/prompts/observer.md](periodic_jobs/ai_heartbeat/src/v0/prompts/observer.md)、[periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md](periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md)、[periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py)、[.gitignore](.gitignore)
- 验证命令：
  - `.\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests`
  - `.\.venv\Scripts\python.exe -m py_compile periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py periodic_jobs/ai_heartbeat/src/v0/observer.py periodic_jobs/ai_heartbeat/src/v0/reflector.py periodic_jobs/ai_heartbeat/src/v0/heartbeat_status_cli.py`
  - `rg -n "claude_runs|heartbeat_reflector_report.md|heartbeat_status.json" .gitignore`
  - `Get-Item periodic_jobs/ai_heartbeat/src/v0/prompts/observer.md,periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md | Select-Object Name,Length | Format-Table -AutoSize`
- 预期结果：
  - heartbeat 目录下现有测试全部通过。
  - 受影响 Python 文件语法检查通过。
  - `.gitignore` 同时覆盖 `heartbeat_status.json`、`heartbeat_reflector_report.md` 和 `claude_runs/`。
  - 两个 prompt 模板都非空，且 runner 已是 Claude 驱动实现。
- [ ] Step 1: 运行 `.\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests`，确认没有遗漏旧测试回归。
- [ ] Step 2: 运行完整 py_compile 命令，确认 state / preflight / runner / observer / reflector / status_cli 全部可编译。
- [ ] Step 3: 用 `rg` 和 `Get-Item` 检查 ignore 规则与 prompt 模板长度；若发现模板为空或忽略规则不全，在当前任务内修复后再继续。
- [ ] Step 4: 输出最终修改摘要，明确本次已经切到 Claude Code 智能路径、reflector 首版写面受 allowlist 约束、且失败不会再降级到机械扫描。

## 执行纪律

- 开始实现前，先批判性复查本计划；如果发现设计文档、现有文件结构或验证命令与仓库现实不符，先修计划再动手。
- 严格按任务顺序执行，不要把 observer、reflector、git 恢复和最终回归合成一个不可验证的大补丁。
- 每完成一个任务，都运行该任务定义的验证；验证失败时，先在当前任务内修复，不要跳步。
- 新增测试优先使用失败测试或失败检查驱动；确实不适合严格 TDD 的地方，也要先定义“改动前缺什么”和“改动后如何证明已生效”。
- 新建 Markdown prompt 文件后，必须立刻做文件长度和 read-back 验证；一旦出现 0 字节或内容缺失，停在当前任务内修复。
- 如果当前就在 `main` 或 `master`，且用户没有明确同意，开始实现前先确认。
- 遇到必须改动 [periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py)、[periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py) 或 [.github/hooks/pre-session.ps1](.github/hooks/pre-session.ps1) 才能继续的情况，立即停下来说明，不要默改范围。
- 全部任务完成后，再做最终验证并输出修改摘要。

## 最终验证

- 运行完整 heartbeat 测试集：
  - `.\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests`
- 运行完整语法检查：
  - `.\.venv\Scripts\python.exe -m py_compile periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py periodic_jobs/ai_heartbeat/src/v0/observer.py periodic_jobs/ai_heartbeat/src/v0/reflector.py periodic_jobs/ai_heartbeat/src/v0/heartbeat_status_cli.py`
- 运行关键 grep 审计：
  - `rg -n "claude_runs|heartbeat_reflector_report.md|heartbeat_status.json" .gitignore`
  - `rg -n "Local observer scan detected|controlled local-reflector output|_build_reflection_rules|_build_observer_lines" periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py`
- 运行 prompt 文件长度检查：
  - `Get-Item periodic_jobs/ai_heartbeat/src/v0/prompts/observer.md,periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md | Select-Object Name,Length | Format-Table -AutoSize`
- 手动结果预期：
  - local runner 已变成 Claude Code 驱动的触发器。
  - observer 成功时会写入 target date 条目，失败时显式记 failed 并保留运行日志。
  - reflector 成功时会写 report，失败时按 allowlist 和 git 基线恢复。
  - 本次实现没有再偷偷保留机械 fallback。