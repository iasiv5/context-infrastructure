# AI Heartbeat Single Smart Command 设计文档

Date: 2026-05-30
Status: Draft
Author: User + AI

## 背景与目标

- 当前 AI Heartbeat 的提醒层已经基本稳定：SessionStart hook 会调用 [periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py)，再由 [periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py) 维护 observer 24 小时、reflector 7 天、同一天只提醒一次这组状态语义。
- 当前真正混乱的是执行层。仓库里先后存在过手动提醒方案、Copilot CLI 方案、Claude Code 本地 runner 方案，以及更早的 OpenCode 触发器方案。结果是：活代码、活文档和实际工作流已经不再同构，维护者很难判断哪条链路才是当前推荐路径。
- 这次要收敛的不是“是否继续 agentic”，而是“把 agentic 放在用户显式触发之后”。自动化层只做逾期审计和会前提醒；真正的 observer / reflector 仍由当前 chat 中的 Agent 自主读文件、判断、写文件，并自动回写 success / failed / skipped。
- 命令入口从多个执行命令收敛成一个主入口，减少用户心智负担。用户平时只记住一个命令；只有在补跑或调试时才使用 force override。

成功标准：

- 主执行入口收敛成一个仓库级自定义命令，命令名为 `/ai-heartbeat`。
- SessionStart hook 继续自动检查 observer / reflector 是否过期，并继续保持同一天只提醒一次。
- `/ai-heartbeat` 默认自行决定执行 observer、reflector，还是先 observer 再 reflector。
- observer 的幂等特性保持不变：同一逻辑日期已存在条目时，任务记为 skipped，而不是重复写入。
- observer / reflector 的 success / failed / skipped 仍自动回写到状态系统，不需要用户手工记账。
- 历史设计与历史实施计划保留原样，不为“对齐当前事实”而重写或删除历史文档。
- 当前事实源文档与当前运行面保持一致，过时脚本、过时测试和过时运行时配置被清理。

## 范围

- 新增单一主命令资产 [`.github/prompts/ai-heartbeat.prompt.md`](.github/prompts/ai-heartbeat.prompt.md) 作为当前仓库的唯一主执行入口。
- 保留并复用 [periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py)、[periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py)、[periodic_jobs/ai_heartbeat/src/v0/heartbeat_status_cli.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_status_cli.py) 这条提醒与状态链。
- 将 SessionStart hook 的职责明确收缩为“提醒”，不再默认承担本地 direct-exec 执行器角色。
- 更新以下活文档，使其与新方案一致：
  - [periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md](periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md)
  - [periodic_jobs/ai_heartbeat/docs/PRD.md](periodic_jobs/ai_heartbeat/docs/PRD.md)
  - [README.md](README.md)
  - [setup_guide.md](setup_guide.md)
  - [docs/CRONTAB.md](docs/CRONTAB.md)
  - [AGENTS.md](AGENTS.md)
- 清理与当前运行面直接冲突、但不属于历史归档的旧脚本、旧测试和旧 prompt 模板。

## 非范围

- 不改写、不删除 [docs/specs](docs/specs) 和 [docs/plans](docs/plans) 下旧日期的历史设计与历史实施计划文档；它们作为真实历史保留。
- 不让 hook 直接启动 `/ai-heartbeat`，也不在 hook 中偷偷执行 observer / reflector。
- 不把 SessionStart 弹窗扩展成新的任务编排器、复制器或通用命令中心。
- 不重新引入以 Claude CLI、Copilot CLI autopilot 或 OpenCode Server 为核心的后台 direct-exec 运行器。
- 不把 `/ai-heartbeat` 泛化成任意任务调度器；它只服务 AI Heartbeat 的 observer / reflector 语义。
- 不在首版中新增第二个用户可见主命令；force override 只是主命令的参数形态，不是独立命令集合。

## 方案比较

### 方案 A：保留当前 hook + 本地 direct-exec 执行器

- 核心思路：继续让 SessionStart hook 在提醒后直接拉起本地执行器，由执行器再调用外部智能层或本地 runner 完成 observer / reflector。
- 优点：自动化程度高，用户点击后就能继续跑完整任务。
- 缺点：
  - 执行链隐藏在 hook 后面，失败面不透明。
  - 背景执行、高权限写入和当前会话上下文脱节，违背“用户显式触发后再 fully agentic”的目标。
  - 需要继续维护 [periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py) 这条已明显偏离目标的执行面。

### 方案 B：单一智能命令 + 可选 force override

- 核心思路：提醒层继续自动工作；用户真要执行时，只运行一个命令 `/ai-heartbeat`。命令内部自行判断当前该跑 observer、该跑 reflector，还是按顺序跑两个。必要时允许 `force observer`、`force reflector`、`force both` 作为 override。
- 优点：
  - 默认体验只有一个命令，心智负担最低。
  - 执行仍然 fully agentic，但前提是用户显式发起。
  - 保留调试与补跑的工程逃生口，不会把系统做死。
  - 与现有状态系统、提醒系统和 observer 幂等语义天然兼容。
- 缺点：
  - 需要改写当前 hook 文案、活文档和运行面清理策略。
  - 主命令 prompt 本身需要承担调度规则说明，不能写得过于含糊。

### 方案 C：三个手动命令并列存在

- 核心思路：分别暴露 observer、reflector、observer+reflector 三个命令，用户按提醒自行判断运行哪一个。
- 优点：实现直观，单个命令职责纯。
- 缺点：
  - 用户要重复做决策，而这些决策其实已经由 preflight 和状态文件算出来了。
  - 提醒面和执行面都会出现“到底现在该运行哪个”的重复认知成本。
  - 与这次“收敛成单一主入口”的目标相违背。

## 推荐方案

- 选择方案 B。
- 原因：这次真正要解决的问题不是“有没有 agentic”，而是“如何把 agentic 放到一个清晰、显式、低心智负担的入口后面”。方案 B 同时满足这三点：
  - 用户只需记住一个主命令。
  - hook 和 preflight 继续承担自动提醒，不偷跑执行。
  - observer / reflector 在用户显式触发后仍保持 fully agentic。
- 命名选择：主命令名固定为 `ai-heartbeat`。
- 命名原因：
  - 与现有目录、状态文件和文档命名完全一致。
  - 比 `anti-context-rot` 更适合作为稳定的工程入口名。
  - `anti-context-rot` 可以出现在命令描述里，作为文案或副标题，而不是主命令名。
- 主要 trade-offs：
  - 接受 hook 不再“一键执行到底”，换来更清晰的权限边界与可理解性。
  - 接受一个带 override 的主命令，而不是三个平级命令，换来更低的默认复杂度。
  - 接受对活文档和运行面做一次显式清理，换来后续维护的单一事实源。

## 关键边界与组件职责

- [`.github/prompts/ai-heartbeat.prompt.md`](.github/prompts/ai-heartbeat.prompt.md)
  - 当前仓库唯一的 AI Heartbeat 主执行入口。
  - 默认行为：读取状态并智能决定执行 observer、reflector 或 observer+reflector。
  - 可选 override：`force observer`、`force reflector`、`force both`。
  - 不是后台运行器，不保存长期状态，不代替 Python 状态模块。

- [.github/hooks/ai-heartbeat.session-start.json](.github/hooks/ai-heartbeat.session-start.json)
  - 保持 SessionStart 挂载点不变。
  - 只负责把会前检查接到 hook 生命周期中。

- [.github/hooks/pre-session.ps1](.github/hooks/pre-session.ps1)
  - 继续负责会前 UI 展示。
  - 新语义是“提醒 + 指向 `/ai-heartbeat`”，而不是“提醒 + 直接执行本地 runner”。
  - 不再承担 observer / reflector 的任务编排与 direct-exec 启动。

- [periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py)
  - 继续负责 due-task 计算、hook dialog spec 生成、同日去重和 `last_prompted_on` 更新。
  - 不承担执行 observer / reflector 的职责。

- [periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py)
  - 继续作为 observer / reflector 的状态事实源。
  - observer 24 小时、reflector 7 天、prompted 去重和 success / failed / skipped 语义保持不变。

- [periodic_jobs/ai_heartbeat/src/v0/heartbeat_status_cli.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_status_cli.py)
  - 继续作为主命令执行后的自动记账入口。
  - success / failed / skipped 均由 Agent 自动调用，不需要用户手动补记。

- [periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md](periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md)
  - 继续描述 observer / reflector 的目标、边界和记忆分层哲学。
  - 需要从“外部触发器 / 本地 runner / direct file execution”表述，收敛到“提醒层自动、执行层由 `/ai-heartbeat` 显式触发”。

- [periodic_jobs/ai_heartbeat/docs/PRD.md](periodic_jobs/ai_heartbeat/docs/PRD.md)
  - 继续描述产品愿景、价值主张和高层业务流。
  - 需要把当前用户故事中的执行入口改成“hook 提醒 + 用户在 chat 中运行 `/ai-heartbeat`”。

- 活文档对齐面
  - [README.md](README.md)、[setup_guide.md](setup_guide.md)、[docs/CRONTAB.md](docs/CRONTAB.md)、[AGENTS.md](AGENTS.md) 必须与新方案同步。
  - 这些文档是当前事实源，不允许继续保留 `heartbeat_local_runner.py` 为主路径的说法。

- 历史文档边界
  - [docs/specs](docs/specs) 和 [docs/plans](docs/plans) 下旧日期文件全部保留，不因新方案而重写、移动或删除。
  - 它们不是当前事实源，而是演化历史。

- 退役运行面
  - 以下内容在新方案下应被视为退役对象：
    - [periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py)
    - [periodic_jobs/ai_heartbeat/src/v0/prompts/observer.md](periodic_jobs/ai_heartbeat/src/v0/prompts/observer.md)
    - [periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md](periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md)
    - [periodic_jobs/ai_heartbeat/src/v0/_legacy_opencode](periodic_jobs/ai_heartbeat/src/v0/_legacy_opencode)
    - [periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py)
    - [periodic_jobs/ai_heartbeat/tests/test_observer_reflector_status.py](periodic_jobs/ai_heartbeat/tests/test_observer_reflector_status.py)
  - 以下 ignored runtime output 不再作为方案内正式产物：
    - `periodic_jobs/ai_heartbeat/state/heartbeat_reflector_report.md`
    - `periodic_jobs/ai_heartbeat/state/claude_runs/`

## 数据流 / 控制流

### 会前提醒路径

1. SessionStart hook 继续通过 [.github/hooks/ai-heartbeat.session-start.json](.github/hooks/ai-heartbeat.session-start.json) 调用 [.github/hooks/pre-session.ps1](.github/hooks/pre-session.ps1)。
2. hook 调用 [periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_preflight.py) 生成当前 due-task 信息。
3. `heartbeat_preflight.py` 基于 [periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py) 判断：
   - observer 是否超过 24 小时。
   - reflector 是否超过 7 天。
   - 今天是否已经提醒过。
4. 若本次需要提醒，hook 弹窗只展示：
   - 当前过期项是 observer、reflector，还是两者都过期。
   - 推荐在当前 chat 中运行 `/ai-heartbeat`。
5. 弹窗本身不负责选择运行 observer 还是 reflector，也不直接执行任何本地 runner。

### 主命令默认路径

1. 用户在当前 chat 中运行 `/ai-heartbeat`。
2. 命令首先读取：
   - [AGENTS.md](AGENTS.md)
   - [periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md](periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md)
   - [periodic_jobs/ai_heartbeat/docs/PRD.md](periodic_jobs/ai_heartbeat/docs/PRD.md)
   - 必要的 `rules/` 约束
   - [periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_state.py) 对应的状态文件
3. 命令解析是否带有 override：
   - 无 override：按当前 due-task 状态选择执行计划。
   - `force observer`：无视 due 状态，只执行 observer。
   - `force reflector`：无视 due 状态，只执行 reflector。
   - `force both`：无视 due 状态，按 observer 后 reflector 的顺序执行。
4. 无 override 时的默认决策表：
   - 只有 observer 过期：执行 observer。
   - 只有 reflector 过期：执行 reflector。
   - 两者都过期：先 observer，再在 observer 成功或 skipped 后执行 reflector。
   - 两者都不过期：给出“当前无需执行”的说明，并退出，不改状态。

### observer 执行路径

1. observer 先读取 [contexts/memory/OBSERVATIONS.md](contexts/memory/OBSERVATIONS.md)。
2. 若当前逻辑日期的 `Date: YYYY-MM-DD` 条目已存在：
   - 不再追加写入。
   - 自动调用 [periodic_jobs/ai_heartbeat/src/v0/heartbeat_status_cli.py](periodic_jobs/ai_heartbeat/src/v0/heartbeat_status_cli.py) 记录 skipped。
3. 若当日条目不存在：
   - Agent 按 Knowledge Base 与 PRD 定义的 observer 语义扫描、过滤、归纳并写入 [contexts/memory/OBSERVATIONS.md](contexts/memory/OBSERVATIONS.md)。
   - 写入完成后自动记录 success。
4. 若 observer 失败：
   - 自动记录 failed。
   - 若本次计划原本是 observer+reflector，则 reflector 不再继续执行。

### reflector 执行路径

1. reflector 读取 [contexts/memory/OBSERVATIONS.md](contexts/memory/OBSERVATIONS.md) 与相关规则面。
2. Agent 按 Knowledge Base 与 PRD 定义的 reflector 语义执行晋升与 GC。
3. 完成后自动记录 success；失败时自动记录 failed。
4. 若本次计划是 observer+reflector，只有 observer 成功或 skipped 时，reflector 才会被执行。

## 错误处理与回退

- 会前提醒失败
  - 处理：提醒失败不应触发隐式执行。hook 最多降级为不提醒，用户仍可手动运行 `/ai-heartbeat`。

- 当前无任务到期且用户未指定 override
  - 处理：命令直接说明当前 observer / reflector 都不需要执行，并退出。
  - 状态：不写 success，不写 failed，不改变 `last_prompted_on`。

- observer 已有当天条目
  - 处理：记 skipped，不重复写入。
  - 语义：这是显式执行后的幂等退出，不是 failure，也不是 success 伪装。

- observer 失败
  - 处理：自动记录 failed。
  - 回退：若本次原本计划 observer+reflector，则停止，不进入 reflector。

- reflector 失败
  - 处理：自动记录 failed。
  - 回退：本次命令到此结束，不尝试额外补救动作。

- 状态回写失败
  - 处理：视为任务失败，而不是 silent success。
  - 原因：用户已明确要求 success / failed 自动回写；状态系统写不进去时，不应假设任务完整成功。

- 旧 ignored runtime outputs 仍留在本地目录
  - 处理：它们不再作为新方案的正式产物。实现阶段可安全删除本地残留，但不需要把这件事包装成历史文档迁移。

## 测试策略

- 保留并继续使用：
  - [periodic_jobs/ai_heartbeat/tests/test_heartbeat_state.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_state.py)
  - [periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_preflight.py)
  - [periodic_jobs/ai_heartbeat/tests/test_heartbeat_status_cli.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_status_cli.py)

- 删除并停止维护：
  - [periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py](periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py)
  - [periodic_jobs/ai_heartbeat/tests/test_observer_reflector_status.py](periodic_jobs/ai_heartbeat/tests/test_observer_reflector_status.py)
  - 原因：它们绑定的都是被本设计退役的执行面。

- 新方案需要验证的核心行为：
  - SessionStart 仍能正确提醒 observer / reflector 到期状态，并维持同日去重。
  - `/ai-heartbeat` 在四种默认状态下能做出正确决策：observer only、reflector only、both、none。
  - `force observer`、`force reflector`、`force both` 能覆盖默认决策。
  - observer 的幂等性保持不变：同日已有条目时，记 skipped。
  - observer+reflector 联合执行时，observer failed 会阻断 reflector；observer skipped 则允许 reflector 继续。
  - success / failed / skipped 都会自动回写状态。
  - 活文档中的主路径不再提到 `heartbeat_local_runner.py`、旧的 `observer.py` / `reflector.py` 兼容入口或 Claude local runner。

- 验证层级：
  - Python 纯逻辑测试：状态、preflight、status CLI。
  - prompt 行为冒烟测试：人工执行 `/ai-heartbeat` 和 force override，检查任务决策与状态回写。
  - 文档审计：只检查活文档，不要求历史 spec / plan 文档对齐当前方案。

## 未决事项

- 当前无阻塞性未决事项。
- 本设计已明确写死以下边界：
  - 主命令名固定为 `ai-heartbeat`。
  - 历史 spec / plan 文档保留原样。
  - hook 只提醒，不执行。
  - 主执行入口只有一个，force 只是参数，不是第二套命令面。
