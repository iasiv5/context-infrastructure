# AI Heartbeat 手动提醒机制实施计划

> 历史说明：本文记录的是第一阶段实施计划。当前默认执行链路已经收敛到 SessionStart hook + periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py；文中对 observer.py / reflector.py 的引用主要用于保留当时的实施背景。

## 目标

- 将已批准设计 [docs/specs/2026-05-22-ai-heartbeat-manual-reminder-design.md](docs/specs/2026-05-22-ai-heartbeat-manual-reminder-design.md) 落成可执行实现，不再依赖 cron 才能知道 observer 和 reflector 是否逾期。
- 为 AI Heartbeat 引入本地状态持久化、会前检查入口和对 observer / reflector 的状态回写。
- 保持现有 observer 与 reflector 的业务职责不变，只补充状态层、提醒层和最小必要文档更新。
- 交付结果应让执行者能够在当前仓库内完成实现、运行聚焦测试，并把 README / setup guide 中的“必须 cron”表述更新为“cron 可选，手动提醒模式可用”。

## 架构快照

- 新增一个纯 Python 状态模块，统一定义 heartbeat 状态文件 schema、默认值、逾期判断、提醒去重和 success / failed / skipped / prompted 的回写规则。
- 新增一个会前检查脚本，负责读取状态并输出零个、一个或两个提醒项；该脚本既是自动挂载点要调用的入口，也是没有 hook 时的手动兜底入口。
- 现有 [periodic_jobs/ai_heartbeat/src/v0/observer.py](periodic_jobs/ai_heartbeat/src/v0/observer.py) 和 [periodic_jobs/ai_heartbeat/src/v0/reflector.py](periodic_jobs/ai_heartbeat/src/v0/reflector.py) 继续执行原有 L1 / L2 任务，但在 skip / success / failure 这些结果上统一回写状态文件。
- 本次实现增加聚焦测试，优先覆盖纯逻辑层和脚本级状态回写，不碰 OpenCode 业务逻辑本身。
- 用户可见文档同步覆盖 [README.md](README.md)、[setup_guide.md](setup_guide.md) 和 [docs/CRONTAB.md](docs/CRONTAB.md)，让“手动提醒模式”和“cron 可选”对外可见。
- 当前仓库内未发现稳定的 repo-local 会话启动 hook 文件，因此本计划只交付 hook-agnostic 的 preflight 入口；真正的平台级自动挂载不在本计划范围内。

## 输入工件

- 已批准设计文档：[docs/specs/2026-05-22-ai-heartbeat-manual-reminder-design.md](docs/specs/2026-05-22-ai-heartbeat-manual-reminder-design.md)
- 现有执行器：[periodic_jobs/ai_heartbeat/src/v0/observer.py](periodic_jobs/ai_heartbeat/src/v0/observer.py)、[periodic_jobs/ai_heartbeat/src/v0/reflector.py](periodic_jobs/ai_heartbeat/src/v0/reflector.py)
- 现有 OpenCode 客户端：[periodic_jobs/ai_heartbeat/src/v0/opencode_client.py](periodic_jobs/ai_heartbeat/src/v0/opencode_client.py)
- 当前用户文档：[README.md](README.md)、[setup_guide.md](setup_guide.md)、[docs/CRONTAB.md](docs/CRONTAB.md)
- 当前测试约定：[tools/pytest.ini](tools/pytest.ini) 和样例 [periodic_jobs/ai_heartbeat/tests/test_heartbeat_state.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_state.py)

## 文件结构与职责

- Create: [periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py)
  - 定义状态文件路径、默认 schema、读写与备份、逾期判断、提醒去重和状态变更 helper。
- Create: [periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py)
  - 定义会前检查入口，复用 heartbeat_state 的纯逻辑并输出提醒结果。
- Create: [periodic_jobs/ai_heartbeat/tests/test_heartbeat_state.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_state.py)
  - 覆盖默认状态、损坏文件回退、逾期判断、同日提醒去重和状态回写规则。
- Create: [periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py)
  - 覆盖 reminder 收集逻辑、observer / reflector 双提醒、拒绝执行后的 prompted 语义和 CLI 输出。
- Create: [periodic_jobs/ai_heartbeat/tests/test_observer_reflector_status.py](periodic_jobs/ai_heartbeat/tests/test_observer_reflector_status.py)
  - 通过 monkeypatch 覆盖 observer / reflector 的 skip、success、failure 三类状态回写。
- Modify: [periodic_jobs/ai_heartbeat/src/v0/observer.py](periodic_jobs/ai_heartbeat/src/v0/observer.py)
  - 接入 heartbeat_state；保留原幂等性与 OpenCode 调用逻辑。
- Modify: [periodic_jobs/ai_heartbeat/src/v0/reflector.py](periodic_jobs/ai_heartbeat/src/v0/reflector.py)
  - 接入 heartbeat_state；在成功 / 失败路径上回写状态。
- Modify: [README.md](README.md)
  - 更新 AI Heartbeat 介绍和目录树文案，去掉“必须 cron”的唯一表述，补上手动提醒模式。
- Modify: [setup_guide.md](setup_guide.md)
  - 将 Step 3 调整为“手动提醒模式为默认路径，cron 为可选增强路径”。
- Modify: [docs/CRONTAB.md](docs/CRONTAB.md)
  - 在 cron 文档的入口处补一条边界说明：本页只服务于仍想使用外部定时任务的用户。
- Runtime output: `periodic_jobs/ai_heartbeat/state/heartbeat_status.json`
  - 首次运行时自动创建；不手工维护，不把它当成长期记忆内容。

编辑约束说明：

- [setup_guide.md](setup_guide.md) 是 notebook-backed markdown。若普通文本编辑没有落盘，执行者必须立即改用 notebook-aware 编辑方式或 PowerShell UTF-8 fallback，并在同一步完成 read-back 验证。
- 当前 Windows 工具链对 markdown 新增 / 改写存在被写成 0 字节的风险。对新增或改动的 markdown 文件，第一次写入后必须立即做文件长度和 read-back 验证。
- 新测试文件应沿用 [periodic_jobs/ai_heartbeat/tests/test_heartbeat_state.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_state.py) 的导入方式，通过 `importlib.util.spec_from_file_location` 直接按路径加载模块，避免把 `periodic_jobs/ai_heartbeat/src/v0` 强行改造成 package。

## 任务清单

### Task 1: 建立状态层与纯逻辑测试

- 目标：先把状态文件 schema、读写与逾期判断做成可单测的纯逻辑层。
- 涉及文件：[periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py)、[periodic_jobs/ai_heartbeat/tests/test_heartbeat_state.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_state.py)
- 验证命令：
  - `python -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests/test_heartbeat_state.py`
  - `python -m py_compile periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py`
- 预期结果：
  - 默认状态与设计文档中的 JSON schema 一致。
  - observer 的 24 小时阈值、reflector 的 7 天阈值、同日提醒去重和损坏文件备份都被测试覆盖。
  - 状态模块可以在不存在状态文件时完成初始化，并能在同一接口里记录 prompted / success / failed / skipped。
- [ ] Step 1: 创建 [periodic_jobs/ai_heartbeat/tests/test_heartbeat_state.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_state.py)，先写失败测试，覆盖默认 schema、逾期判断、同日去重和损坏文件回退。
- [ ] Step 2: 运行 `python -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests/test_heartbeat_state.py`，确认当前失败，失败点集中在缺失的状态模块或未实现的行为。
- [ ] Step 3: 创建 [periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py)，实现状态路径解析、目录创建、原子写入、损坏文件备份、逾期判断和状态回写 helper。
- [ ] Step 4: 重新运行 `python -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests/test_heartbeat_state.py` 与 `python -m py_compile periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py`，确认测试通过且无语法错误。

### Task 2: 实现会前检查入口与提醒输出

- 目标：把状态层包装成一个可手动调用的会前检查脚本，并用聚焦测试锁住 reminder 语义。
- 涉及文件：[periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py)、[periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py)
- 验证命令：
  - `python -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py`
  - `python -m py_compile periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py`
  - `python periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py --help`
- 预期结果：
  - 会前检查入口可在没有状态文件时正常初始化并给出提醒判断。
  - observer 与 reflector 可以分别提醒，也可以在同一次检查中同时提醒。
  - “用户本次拒绝执行”路径只更新 prompted 日期，不被记成一次 attempt。
  - CLI 至少提供一个稳定的手动入口，供没有自动 hook 的场景调用。
  - 本任务不猜测具体平台 hook 文件；若后续确认存在稳定挂点，再用单独实现切片接入。
- [ ] Step 1: 创建 [periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py)，先写失败测试，覆盖无状态文件、双提醒、已提醒去重和拒绝执行路径。
- [ ] Step 2: 运行 `python -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py`，确认当前失败来自缺失的 preflight 入口或提醒逻辑。
- [ ] Step 3: 创建 [periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py)，实现 reminder 收集函数、最小 CLI 和人工可读输出。
- [ ] Step 4: 重新运行 `python -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py`、`python -m py_compile periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py` 与 `python periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py --help`，确认脚本可用且测试通过。

### Task 3: 将 observer / reflector 接到状态层

- 目标：在不改变 observer / reflector 核心职责的前提下，把 skip / success / failure 结果统一写回状态文件。
- 涉及文件：[periodic_jobs/ai_heartbeat/src/v0/observer.py](periodic_jobs/ai_heartbeat/src/v0/observer.py)、[periodic_jobs/ai_heartbeat/src/v0/reflector.py](periodic_jobs/ai_heartbeat/src/v0/reflector.py)、[periodic_jobs/ai_heartbeat/tests/test_observer_reflector_status.py](periodic_jobs/ai_heartbeat/tests/test_observer_reflector_status.py)
- 验证命令：
  - `python -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests/test_observer_reflector_status.py`
  - `python -m py_compile periodic_jobs/ai_heartbeat/src/v0/observer.py periodic_jobs/ai_heartbeat/src/v0/reflector.py`
  - `python periodic_jobs/ai_heartbeat/src/v0/observer.py --help`
  - `python periodic_jobs/ai_heartbeat/src/v0/reflector.py --help`
- 预期结果：
  - observer 在幂等性 skip 时记录 skipped 和目标日期，但不伪造 success。
  - observer / reflector 在成功后写入 last_success_at 并清空 last_error、last_prompted_on。
  - observer / reflector 在失败后只写 attempt / failed / last_error，不推进 last_success_at。
  - 脚本仍保持原来的 CLI 入口和参数形态。
- [ ] Step 1: 创建 [periodic_jobs/ai_heartbeat/tests/test_observer_reflector_status.py](periodic_jobs/ai_heartbeat/tests/test_observer_reflector_status.py)，先写失败测试，monkeypatch OpenCodeClient 与状态路径，覆盖 observer skip、observer success、reflector success 和 failure 路径。
- [ ] Step 2: 运行 `python -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests/test_observer_reflector_status.py`，确认当前失败反映的正是缺失的状态接线。
- [ ] Step 3: 修改 [periodic_jobs/ai_heartbeat/src/v0/observer.py](periodic_jobs/ai_heartbeat/src/v0/observer.py) 与 [periodic_jobs/ai_heartbeat/src/v0/reflector.py](periodic_jobs/ai_heartbeat/src/v0/reflector.py)，只补状态回写和最小必要的 helper 提取，不重写 OpenCode 业务逻辑。
- [ ] Step 4: 重新运行 `python -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests/test_observer_reflector_status.py`、`python -m py_compile periodic_jobs/ai_heartbeat/src/v0/observer.py periodic_jobs/ai_heartbeat/src/v0/reflector.py`、`python periodic_jobs/ai_heartbeat/src/v0/observer.py --help` 和 `python periodic_jobs/ai_heartbeat/src/v0/reflector.py --help`，确认脚本接口未回归。

### Task 4: 更新用户文档，把手动提醒模式公开化

- 目标：让新机制在仓库主文档和 setup guide 中可发现，并把“cron 是唯一方式”的旧表述改成“cron 可选”。
- 涉及文件：[README.md](README.md)、[setup_guide.md](setup_guide.md)、[docs/CRONTAB.md](docs/CRONTAB.md)
- 验证命令：
  - `rg -n "手动提醒|会前检查|cron 可选|heartbeat_preflight|heartbeat_status" README.md setup_guide.md docs/CRONTAB.md`
  - `rg -n "L1/L2 需要设置 cron 自动运行|observer.py      # 每日观察脚本（需配置 cron）|reflector.py     # 每周反思脚本（需配置 cron）" README.md setup_guide.md docs/CRONTAB.md`
  - `Get-Item README.md,setup_guide.md,docs/CRONTAB.md | Select-Object Name,Length | Format-Table -AutoSize`
  - 对 [setup_guide.md](setup_guide.md) 做一次 read-back，确认 Step 3 的新文案真实落盘。
- 预期结果：
  - README 清楚说明 AI Heartbeat 现在支持手动提醒模式，cron 仅是可选增强。
  - setup guide 的 Step 3 以手动提醒模式为默认路径，cron 改为可选章节。
  - docs/CRONTAB 明确自己只服务于仍要外部调度的用户，不再暗示它是唯一入口。
  - 所有改动后的 markdown 文件都非空，尤其是 notebook-backed 的 setup_guide 没有写丢。
- [ ] Step 1: 更新 [README.md](README.md) 中 AI Heartbeat 的目录树和使用说明，把 observer / reflector 从“需配置 cron”改成“可手动触发，cron 可选”。
- [ ] Step 2: 更新 [setup_guide.md](setup_guide.md) 的 Step 3，将手动提醒模式写成默认路径，并新增手动检查 / 手动执行示例；保留 cron 作为可选增强路径。
- [ ] Step 3: 更新 [docs/CRONTAB.md](docs/CRONTAB.md) 的文档开头或说明段，明确它只覆盖选择 cron 的用户。
- [ ] Step 4: 立即运行 `rg` 搜索、文件长度检查和 [setup_guide.md](setup_guide.md) 的 read-back 验证；若 notebook 编辑没有真实落盘，在本任务内切换编辑策略并修复。

### Task 5: 做一次收口验证与实现交接检查

- 目标：在不做仓库级大范围构建的前提下，确认 Python 逻辑、脚本入口和用户文档已经彼此对齐，可交给后续编码执行流程继续推进或收尾。
- 涉及文件：[periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py)、[periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py)、[periodic_jobs/ai_heartbeat/src/v0/observer.py](periodic_jobs/ai_heartbeat/src/v0/observer.py)、[periodic_jobs/ai_heartbeat/src/v0/reflector.py](periodic_jobs/ai_heartbeat/src/v0/reflector.py)、[periodic_jobs/ai_heartbeat/tests/test_heartbeat_state.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_state.py)、[periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py)、[periodic_jobs/ai_heartbeat/tests/test_observer_reflector_status.py](periodic_jobs/ai_heartbeat/tests/test_observer_reflector_status.py)、[README.md](README.md)、[setup_guide.md](setup_guide.md)、[docs/CRONTAB.md](docs/CRONTAB.md)
- 验证命令：
  - `python -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests`
  - `python -m py_compile periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py periodic_jobs/ai_heartbeat/src/v0/observer.py periodic_jobs/ai_heartbeat/src/v0/reflector.py`
  - `rg -n "手动提醒|会前检查|cron 可选|heartbeat_preflight|heartbeat_status" README.md setup_guide.md docs/CRONTAB.md periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py`
  - `Get-Item README.md,setup_guide.md,docs/CRONTAB.md,periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py,periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py | Select-Object Name,Length | Format-Table -AutoSize`
  - 如编辑器 diagnostics 可用，再对上述 Python 与 markdown 文件做一次 diagnostics 检查。
- 预期结果：
  - 所有 heartbeat 新增测试通过。
  - 四个 Python 脚本语法检查通过。
  - 用户文档、脚本入口和状态文件命名一致，不再互相矛盾。
  - 没有 0 字节或异常截断的 markdown / Python 文件。
- [ ] Step 1: 运行 heartbeat 目录下全部新增测试，确认没有遗漏单测文件或路径错误。
- [ ] Step 2: 运行全部 Python 语法检查，确认新增模块和被修改脚本都可编译。
- [ ] Step 3: 搜索用户文档与脚本文件，确认 `heartbeat_preflight`、`heartbeat_status`、`cron 可选` 等关键术语已经对齐。
- [ ] Step 4: 检查所有关键文件长度并查看 diagnostics；若发现本次引入的问题，在当前任务内修复后再收口。
- [ ] Step 5: 输出最终修改摘要，明确新增了哪些模块、哪些测试、哪些文档入口被更新，以及仍保留的边界是“observer / reflector 仍依赖手动确认后执行，而不是自动执行”。

## 执行纪律

- 开始实现前，先批判性复查本计划；如果发现文件路径、测试命令或文档范围与仓库现实不符，先修计划再动手。
- 严格按任务顺序执行，不要把状态层、脚本接线和文档改动合成一个不可验证的大步骤。
- 每完成一个任务，都运行该任务定义的验证；验证失败时，先在当前任务内修复，不要跳步。
- 新增测试必须先写失败检查，再写最小实现；不适合 TDD 的脚本入口任务，也要先定义当前缺失行为，再补实现。
- 对新增或修改的 markdown 文件，第一次写入后必须立即做文件长度和 read-back 验证；一旦出现 0 字节或 notebook-backed 编辑失效，立刻停在当前任务修复。
- 如果当前就在 `main` 或 `master`，且用户没有明确同意，开始实现前先确认。
- 全部任务完成后，再做收口验证并输出修改摘要。

## 最终验证

- 运行完整测试集：
  - `python -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests`
- 运行完整语法检查：
  - `python -m py_compile periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py periodic_jobs/ai_heartbeat/src/v0/observer.py periodic_jobs/ai_heartbeat/src/v0/reflector.py`
- 运行关键术语审计：
  - `rg -n "手动提醒|会前检查|cron 可选|heartbeat_preflight|heartbeat_status" README.md setup_guide.md docs/CRONTAB.md periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py`
  - `rg -n "L1/L2 需要设置 cron 自动运行|需配置 cron" README.md setup_guide.md`
- 运行关键文件长度检查：
  - `Get-Item README.md,setup_guide.md,docs/CRONTAB.md,periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py,periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py | Select-Object Name,Length | Format-Table -AutoSize`
- 如编辑器 diagnostics 可用，再对所有新增 / 修改文件运行一次 diagnostics 检查。
- 手动结果预期：状态模块和 preflight 入口存在并可调用；observer / reflector 会按 skip / success / failure 更新状态文件；README、setup guide 和 CRONTAB 文档不再把 cron 写成唯一入口，同时保留“cron 仍可选”的事实边界。
