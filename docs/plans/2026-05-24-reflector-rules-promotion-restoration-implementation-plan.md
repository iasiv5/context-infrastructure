# Reflector Rules Promotion Restoration 实施计划

## 目标

- 将已批准设计 [docs/specs/2026-05-24-reflector-rules-promotion-restoration-design.md](docs/specs/2026-05-24-reflector-rules-promotion-restoration-design.md) 拆成可执行实现步骤。
- 让 reflector 恢复到 [periodic_jobs/ai_heartbeat/src/v0/reflector.py](periodic_jobs/ai_heartbeat/src/v0/reflector.py) 的原始语义：直接把高价值观测晋升到真实 rules 目标文件，并直接对 [contexts/memory/OBSERVATIONS.md](contexts/memory/OBSERVATIONS.md) 做 GC。
- 移除当前围绕 [rules/skills/ai_heartbeat_local_reflections.md](rules/skills/ai_heartbeat_local_reflections.md) 的单一路径 contract，同时保留本地 runner 的触发、审计、回滚和状态记录能力。
- 把“允许新建真实 skill 文档”“skills 类晋升必须联动 [rules/skills/INDEX.md](rules/skills/INDEX.md)”以及“GC 必须可验证”都落实到代码、prompt、SOP 和测试。

## 架构快照

- [periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py) 继续是 reflector 的本地触发器和审计器，但不再持有 `DEFAULT_RULES_PROMOTION_PATH`、`--rules-promotion-path` 或任何单一路径晋升语义。
- reflector 的写面改成两层：
  - 精确内建规则面： [contexts/memory/OBSERVATIONS.md](contexts/memory/OBSERVATIONS.md)、[rules/SOUL.md](rules/SOUL.md)、[rules/USER.md](rules/USER.md)、[rules/COMMUNICATION.md](rules/COMMUNICATION.md)、[rules/WORKSPACE.md](rules/WORKSPACE.md)、[rules/skills/INDEX.md](rules/skills/INDEX.md)、[periodic_jobs/ai_heartbeat/state/heartbeat_reflector_report.md](periodic_jobs/ai_heartbeat/state/heartbeat_reflector_report.md)
  - 动态 skill 面：允许触碰或新建 `rules/skills/*.md` 下的真实 skill 文档，但显式排除 [rules/skills/ai_heartbeat_local_reflections.md](rules/skills/ai_heartbeat_local_reflections.md)
- prompt contract 与 runner validation 必须同构：prompt 要明确真实路由和 INDEX 联动规则，runner 要按同样规则验 touched files。
- 为了让 GC 真正可审计，reflector report 需要从“自然语言摘要”收紧为“摘要 + 可机器读取的 GC section”。本计划采用的具体契约是：report 增加 `## Garbage-Collected Entries` 段，每个 bullet 要么是被移除的完整 observation 行，要么是 `Date: YYYY-MM-DD` 形式的整块删除标识。
- [periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md](periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md) 必须补上“skills 类晋升必须更新 [rules/skills/INDEX.md](rules/skills/INDEX.md)”规则，使 SOP、prompt 和 runner 校验一致。
- 历史设计文档、旧 report 和 `state/claude_runs/` 下的历史快照允许保留旧语义引用；本次计划只修 runtime contract、SOP 和测试，不清洗历史证据。

## 输入工件

- 已批准设计文档：[docs/specs/2026-05-24-reflector-rules-promotion-restoration-design.md](docs/specs/2026-05-24-reflector-rules-promotion-restoration-design.md)
- 当前 runner：[periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py)
- 当前 reflector prompt：[periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md](periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md)
- 当前 SOP：[periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md](periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md)
- 当前 reflector 测试：[periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py)
- 运行命令基线：
  - `.\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests`
  - `.\.venv\Scripts\python.exe -m py_compile periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py periodic_jobs/ai_heartbeat/src/v0/observer.py periodic_jobs/ai_heartbeat/src/v0/reflector.py periodic_jobs/ai_heartbeat/src/v0/heartbeat_status_cli.py`

## 文件结构与职责

- Modify: [periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py)
  - 删除单一路径 promotion contract。
  - 实现真实规则面 / 动态 skill 面 allowlist 判定。
  - 收紧 reflector prompt 渲染输入、report 校验、GC 校验和回滚面。
- Modify: [periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md](periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md)
  - 去掉 `rules_promotion_path` 语义。
  - 明确真实规则路由、允许新建 skill、INDEX 联动和 GC report 格式要求。
- Modify: [periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md](periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md)
  - 在 L2 Reflector 规范里补上 skills 类晋升必须同步更新 [rules/skills/INDEX.md](rules/skills/INDEX.md) 的规则。
- Modify: [periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py)
  - 移除所有把 [rules/skills/ai_heartbeat_local_reflections.md](rules/skills/ai_heartbeat_local_reflections.md) 当唯一合法晋升目标的断言。
  - 增加真实 skill / INDEX / GC 契约相关测试。
- Delete: [rules/skills/ai_heartbeat_local_reflections.md](rules/skills/ai_heartbeat_local_reflections.md)
  - 直接删除，不保留迁移说明文件。
- Create: [docs/plans/2026-05-24-reflector-rules-promotion-restoration-implementation-plan.md](docs/plans/2026-05-24-reflector-rules-promotion-restoration-implementation-plan.md)
  - 当前计划文档。

边界说明：

- 不修改 [.github/hooks/pre-session.ps1](.github/hooks/pre-session.ps1)、[periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py) 或 [periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py)，除非实现中出现不可回避阻塞；若出现，先停下修计划。
- 不清洗历史 docs/specs、state report 或 `state/claude_runs/` 里的旧路径引用；本计划只修 runtime contract。

## 任务清单

### Task 1: 去掉单一路径 promotion contract，并锁定新的 prompt / allowlist 契约

- 目标：把 reflector 从 `rules_promotion_path` 单一路径模型切到“真实规则路由 + 动态 skill 面”的契约。
- Files:
  - Modify: [periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py)（`build_parser`、`DEFAULT_RULES_PROMOTION_PATH`、`_resolve_rules_promotion_path`、`_render_reflector_prompt`、`run_reflector_local`）
  - Modify: [periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md](periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md)
  - Test: [periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py)

## Step 1: 写失败测试或失败检查

```text
在 test_heartbeat_local_runner.py 中改写/新增 reflector 合约测试，明确要求：
- 不再依赖 --rules-promotion-path CLI 参数
- 渲染出的 reflector prompt 不再包含 “Rules promotion path:” 或 “Update {rules_promotion_path}”
- allowlist contract 不再包含 rules/skills/ai_heartbeat_local_reflections.md
- prompt 必须包含核心规则路由、允许新建真实 skill、INDEX 联动约束
```

## Step 2: 运行并确认当前失败

- Run: `.\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py -k reflector`
- Expected: reflector 测试因旧的 `rules_promotion_path` / `ai_heartbeat_local_reflections.md` 合约而失败，而不是因为测试本身搭建错误。

## Step 3: 写最小实现

```text
在 heartbeat_local_runner.py 中：
- 删除 DEFAULT_RULES_PROMOTION_PATH、_resolve_rules_promotion_path 和 parser 里的 --rules-promotion-path
- 把 _render_reflector_prompt 改成不接受 rules_promotion_path，并改为注入真实规则路由说明
- 重写 REFLECTOR_ALLOWLIST_RELATIVE_PATHS：保留 OBSERVATIONS、核心 rules、INDEX、report；动态 skill 文档由后续验证函数按路径模式判断

在 prompts/reflector.md 中：
- 删除 Rules promotion path 行
- 删除 Update {rules_promotion_path} only when... 这类单路径语义
- 明确写出真实规则路由、允许新建真实 skill 文档、以及“只要触碰或新建真实 skill 就必须更新 rules/skills/INDEX.md”
```

## Step 4: 运行并确认通过

- Run: `.\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py -k reflector`
- Expected: 新增/改写的 reflector 合约测试通过；失败只会留在尚未实现的 skill / GC 校验部分。
- Run: `.\.venv\Scripts\python.exe -m py_compile periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py`
- Expected: runner 语法检查通过。

## Step 5: 可选 checkpoint commit

- Run: `git add periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py && git commit -m "Refactor reflector promotion contract"`
- Expected: 如需切分风险，生成一个只包含 contract 迁移的 checkpoint commit；如果用户不希望提交，则跳过。

### Task 2: 实现动态 skill allowlist、INDEX 联动校验，并删除 local_reflections 文件

- 目标：让 reflector 既能合法触碰已有真实 skill，也能新建真实 skill，同时把 INDEX 联动和 local_reflections 退役落实到代码与测试。
- Files:
  - Modify: [periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py)（reflector touched-file 校验和 allowlist 判定相关函数）
  - Modify: [periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py)
  - Delete: [rules/skills/ai_heartbeat_local_reflections.md](rules/skills/ai_heartbeat_local_reflections.md)

## Step 1: 写失败测试或失败检查

```text
在 test_heartbeat_local_runner.py 中新增/改写测试，覆盖：
- report 触碰已有真实 skill 文档 + rules/skills/INDEX.md 时成功
- report 触碰新建真实 skill 文档 + rules/skills/INDEX.md 时成功
- report 触碰或新建真实 skill 文档但未包含 rules/skills/INDEX.md 时失败
- report 触碰 rules/skills/ai_heartbeat_local_reflections.md 时失败
```

## Step 2: 运行并确认当前失败

- Run: `.\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py -k "reflector and (allowlist or skill or index)"`
- Expected: 当前实现无法区分真实 skill 和 retired 文件，也不会强制 INDEX 联动，因此测试失败。

## Step 3: 写最小实现

```text
在 heartbeat_local_runner.py 中实现一个明确的 reflector path policy：
- 精确允许：contexts/memory/OBSERVATIONS.md、rules/SOUL.md、rules/USER.md、rules/COMMUNICATION.md、rules/WORKSPACE.md、rules/skills/INDEX.md、periodic_jobs/ai_heartbeat/state/heartbeat_reflector_report.md
- 动态允许：rules/skills/*.md 下的真实 skill 文档
- 明确拒绝：rules/skills/ai_heartbeat_local_reflections.md
- 对 touched files 增加 INDEX coupling 校验：只要 touched files 里有任一真实 skill 文档，就必须同时包含 rules/skills/INDEX.md

然后从仓库中删除 rules/skills/ai_heartbeat_local_reflections.md
```

## Step 4: 运行并确认通过

- Run: `.\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py -k "reflector and (allowlist or skill or index)"`
- Expected: skill / INDEX / retired-file 相关 reflector 测试全部通过。
- Run: `rg -n "ai_heartbeat_local_reflections.md" periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md`
- Expected: runtime code、prompt、tests、SOP 中不再残留该路径引用。
- Run: `Test-Path rules/skills/ai_heartbeat_local_reflections.md`
- Expected: 输出 `False`。

## Step 5: 可选 checkpoint commit

- Run: `git add periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py rules/skills && git commit -m "Retire local reflector output file"`
- Expected: 如需切分风险，生成一个只包含动态 skill allowlist 与文件删除的 checkpoint commit；否则跳过。

### Task 3: 把 GC 摘要收紧为可机器验证的 report 契约

- 目标：让 runner 能根据 report 里的 GC section 真实验证 OBSERVATIONS 已完成删除，而不是只验证文件可读。
- Files:
  - Modify: [periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md](periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md)
  - Modify: [periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py)（reflector 运行前快照、GC section 解析、GC 校验）
  - Modify: [periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py)

## Step 1: 写失败测试或失败检查

```text
在 test_heartbeat_local_runner.py 中新增/改写测试，要求：
- report 必须包含 `## Garbage-Collected Entries`
- 每个 bullet 要么是完整 observation 行，要么是 `Date: YYYY-MM-DD`
- 若 report 声称某个条目或日期块已被 GC，但 OBSERVATIONS 里仍保留该内容，则 reflector 失败并回滚
```

## Step 2: 运行并确认当前失败

- Run: `.\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py -k "reflector and (garbage or gc or observations)"`
- Expected: 当前实现因没有 GC section parser 和 pre-run / post-run 比较逻辑而失败。

## Step 3: 写最小实现

```text
在 heartbeat_local_runner.py 中：
- 在 reflector 运行前抓取 OBSERVATIONS 的原始文本快照
- 新增 GC section 解析 helper，用于读取 `## Garbage-Collected Entries`
- 校验规则：
  - bullet 为完整 observation 行时，该行在 post-run OBSERVATIONS 中必须消失
  - bullet 为 `Date: YYYY-MM-DD` 时，该日期块在 post-run OBSERVATIONS 中必须整体消失
- 若 report 缺少 GC section 或校验失败，则 reflector 失败并触发回滚

在 prompts/reflector.md 中：
- 把 GC 摘要要求改成 `## Garbage-Collected Entries` 明确格式
- 保留自然语言 walkthrough，但不得代替该 section
```

## Step 4: 运行并确认通过

- Run: `.\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py -k "reflector and (garbage or gc or observations)"`
- Expected: GC 契约相关测试通过，错误场景会稳定失败并触发回滚。
- Run: `.\.venv\Scripts\python.exe -m py_compile periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py`
- Expected: runner 语法检查通过。

## Step 5: 可选 checkpoint commit

- Run: `git add periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py && git commit -m "Make reflector GC report machine-verifiable"`
- Expected: 如需切分风险，生成一个只包含 GC 契约收紧的 checkpoint commit；否则跳过。

### Task 4: 对齐 SOP，并收口 reflector 文档契约

- 目标：让 [periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md](periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md) 与 prompt / runner 的 skill 晋升规则一致，避免后续执行者读到冲突语义。
- Files:
  - Modify: [periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md](periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md)
  - Modify: [periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md](periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md)（如果需要补充与 SOP 对齐的措辞）
  - Test: [periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py)（如有直接断言 prompt / KB wording）

## Step 1: 写失败测试或失败检查

```text
先做文档前置检查：
- KNOWLEDGE_BASE 的 4.2 Reflector 段当前没有显式写出“skills 类晋升必须更新 rules/skills/INDEX.md”
- prompt / runner 已经依赖该规则，因此 SOP 目前落后于实现契约
```

## Step 2: 运行并确认当前失败

- Run: `rg -n "rules/skills/INDEX.md" periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md`
- Expected: 当前没有命中，证明 SOP 尚未覆盖该规则。

## Step 3: 写最小实现

```text
修改 KNOWLEDGE_BASE 的 4.2 Reflector 规范，明确补上一条：
- 当晋升目标落在 rules/skills/ 下的真实 skill 文档时，必须同步更新 rules/skills/INDEX.md

如果 prompt 中的措辞与此不一致，同步调整 reflector prompt，使 SOP、prompt、runner 三者完全对齐
```

## Step 4: 运行并确认通过

- Run: `rg -n "rules/skills/INDEX.md" periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md`
- Expected: KNOWLEDGE_BASE 和 reflector prompt 都能命中 INDEX 联动规则。
- Run: `.\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py -k reflector`
- Expected: reflector 契约测试仍通过，没有因文案对齐引入回归。

## Step 5: 可选 checkpoint commit

- Run: `git add periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md && git commit -m "Align reflector SOP with index update rule"`
- Expected: 如需切分风险，生成一个只包含 SOP / prompt 对齐的 checkpoint commit；否则跳过。

### Task 5: 跑完整 reflector 回归与 heartbeat 收口验证

- 目标：确认这次变更没有破坏现有 observer / preflight / state 约束，并把 reflector 改动收口成一个可执行切片。
- Files:
  - Modify: [periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py)（仅在回归中发现剩余缺口时）
  - Modify: [periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md](periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md)（仅在回归中发现剩余缺口时）
  - Modify: [periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md](periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md)（仅在回归中发现剩余缺口时）
  - Test: [periodic_jobs/ai_heartbeat/tests](periodic_jobs/ai_heartbeat/tests)

## Step 1: 写失败测试或失败检查

```text
收口前先明确最终通过条件：
- reflector 相关测试全部通过
- heartbeat 目录完整测试集通过
- 相关 Python 文件 py_compile 通过
- runtime code / prompt / tests / SOP 中不再残留 rules_promotion_path 或 ai_heartbeat_local_reflections.md
- rules/skills/ai_heartbeat_local_reflections.md 已不存在
```

## Step 2: 运行并确认当前失败

- Run: `.\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests`
- Expected: 如果前四个任务还有遗漏，这一步会暴露剩余 reflector 回归或契约不一致点。

## Step 3: 写最小实现

```text
只修本轮回归暴露的剩余缺口，不顺手做设计之外的重构。
若需要改动 observer、preflight、state 或 hook 才能继续，先停下来修计划，不要直接扩范围。
```

## Step 4: 运行并确认通过

- Run: `.\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests`
- Expected: heartbeat 测试集通过。
- Run: `.\.venv\Scripts\python.exe -m py_compile periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py periodic_jobs/ai_heartbeat/src/v0/observer.py periodic_jobs/ai_heartbeat/src/v0/reflector.py periodic_jobs/ai_heartbeat/src/v0/heartbeat_status_cli.py`
- Expected: 相关 Python 文件语法检查通过。
- Run: `rg -n "rules-promotion-path|DEFAULT_RULES_PROMOTION_PATH|ai_heartbeat_local_reflections.md" periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md`
- Expected: 上述 runtime code / prompt / tests / SOP 范围内不再命中旧 contract。
- Run: `Test-Path rules/skills/ai_heartbeat_local_reflections.md`
- Expected: 输出 `False`。

## Step 5: 可选 checkpoint commit

- Run: `git add periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py rules/skills && git commit -m "Restore direct reflector promotion semantics"`
- Expected: 如用户允许提交，生成最终 checkpoint commit；否则跳过。

## 执行纪律

- 开始实现前，先批判性复查整份计划；如果发现设计要求、命令、路径或符号名与仓库现实不符，先修计划。
- 严格按任务顺序执行，不要把 contract 迁移、skill allowlist、GC 契约、SOP 对齐和最终回归合并成一个大补丁。
- 每完成一个任务，都运行该任务定义的验证；验证失败先在当前任务内修复，不要跳步。
- 不要把 docs/specs、历史 report 或 `state/claude_runs/` 里的旧路径引用当成当前任务的清理对象；本计划只修 runtime contract。
- 遇到必须扩展到 observer、preflight、state 或 hook 才能继续的阻塞，立即停下来说明，不要猜。
- 如果当前就在 `main` 或 `master`，且用户没有明确同意，开始实现前先确认。
- 全部任务完成后，运行最终验证并输出修改摘要。

## 最终验证

- 运行 reflector 聚焦测试：
  - `.\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py -k reflector`
- 运行 heartbeat 完整测试集：
  - `.\.venv\Scripts\python.exe -m pytest -c tools/pytest.ini periodic_jobs/ai_heartbeat/tests`
- 运行完整语法检查：
  - `.\.venv\Scripts\python.exe -m py_compile periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py periodic_jobs/ai_heartbeat/src/v0/observer.py periodic_jobs/ai_heartbeat/src/v0/reflector.py periodic_jobs/ai_heartbeat/src/v0/heartbeat_status_cli.py`
- 运行旧 contract 清理检查：
  - `rg -n "rules-promotion-path|DEFAULT_RULES_PROMOTION_PATH|ai_heartbeat_local_reflections.md" periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md`
- 运行 INDEX 规则覆盖检查：
  - `rg -n "rules/skills/INDEX.md" periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py`
- 运行 retired file 检查：
  - `Test-Path rules/skills/ai_heartbeat_local_reflections.md`
- 手动结果预期：
  - local runner 已不再把 reflector 绑定到单一路径 promotion file。
  - reflector 可以触碰已有真实 skill，也可以在无合适承载位时新建真实 skill，但任何这类写入都必须联动 [rules/skills/INDEX.md](rules/skills/INDEX.md)。
  - reflector report 包含可机器校验的 GC section，runner 会据此验证 OBSERVATIONS 的实际删除结果。
  - [rules/skills/ai_heartbeat_local_reflections.md](rules/skills/ai_heartbeat_local_reflections.md) 已从 runtime contract 和仓库文件中退场。