# Claude Code Smart Heartbeat 设计文档

Date: 2026-05-24
Status: Draft
Author: User + AI

## 背景与目标

- AI Heartbeat 的 observer（L1 观测）和 reflector（L2 反思）最初是 agentic 架构：Python 触发器只负责发起任务，真正的扫描、判断、写入由外部 Agent 完成。
- 当前默认执行路径已经切到 `periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py`，但其行为是确定性的本地机械扫描：observer 主要按路径分桶，reflector 主要按固定模板做 GC 和规则输出，已经不再具备原版的语义理解能力。
- 当前环境里本地安装了 Claude Code CLI，且支持 `-p/--print`、`--output-format json`、`--model`、`--permission-mode` 等非交互参数，适合作为新的本地智能执行层。
- 这次设计的目标是：尽量贴近原版“Python 只负责触发，智能判断和写文件交给外部 Agent”的模式，把 observer 和 reflector 的智能层从旧的 OpenCode Server 替换为本地 Claude Code。

成功标准：

- SessionStart hook、提醒弹窗、状态文件机制保持不变。
- `heartbeat_local_runner.py` 恢复为触发器角色，不再自己承担 observer / reflector 的核心判断逻辑。
- observer 由 Claude Code 直接更新 `contexts/memory/OBSERVATIONS.md`。
- reflector 由 Claude Code 直接执行 `OBSERVATIONS.md` 的 GC，并允许直接修改 `rules/` 下首版 allowlist 内的目标文件。
- reflector 的风险控制和恢复机制可审计、可回退，但不把系统做成复杂事务引擎。
- 智能路径失败时显式记为 failed，不用当前机械扫描伪装成功。

## 范围

- 修改 `periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py`，把 observer / reflector 的执行改为调用本地 Claude Code CLI。
- 新增独立 prompt 模板文件，分别承载 observer 和 reflector 的任务协议。
- 为 Claude Code 调用增加运行日志、后置验证和失败状态回写。
- 为 reflector 增加基于 git 的临时 checkpoint 恢复机制。
- 保留现有 `heartbeat_preflight.py`、状态文件和 SessionStart hook 的整体入口。

## 非范围

- 不修改 `.github/hooks/pre-session.ps1` 的交互流程和弹窗 UI。
- 不修改 `heartbeat_preflight.py` 的 overdue 判断逻辑。
- 不保留当前机械 observer / reflector 作为自动降级路径。
- 不把 observer / reflector 改造成通用任务调度器。
- 不引入新的长期后台服务。
- 不在首版中为 Claude Code 加入多模型编排、并行 sub-agent 或复杂自定义 settings 注入。

## 方案比较

### 方案 A：继续使用当前本地确定性 runner

- 核心思路：保留当前 `heartbeat_local_runner.py` 的机械扫描、固定模板晋升和本地报告写入逻辑。
- 优点：稳定、可预测、测试面最小。
- 缺点：能力上限过低，observer 不理解内容，reflector 也不做真正的跨条目归纳，已经偏离原版设计目标。

### 方案 B：Claude Code 负责语义分析，Python 负责最终写回

- 核心思路：Claude Code 只输出结构化结果，Python 再根据结果修改 `OBSERVATIONS.md` 和 `rules/`。
- 优点：执行可控，后置校验简单。
- 缺点：仍然保留了较重的中间编排层，Python 需要理解 observer / reflector 的领域格式，整体上不像原版“外部 Agent 直接完成任务”。

### 方案 C：Claude Code 全权执行 observer / reflector，Python 只做触发与审计

- 核心思路：`heartbeat_local_runner.py` 只做幂等检查、Claude CLI 调用、状态记录、日志采集、后置验证与恢复；真正的扫描、分析、写文件由 Claude Code 直接完成。
- 优点：
  - 与原版 observer.py / reflector.py 的职责分配最接近。
  - 能把语义理解、文件探索和规则晋升重新交还给外部 Agent。
  - runner 层保持薄、边界清晰。
- 缺点：
  - reflector 直接修改 `rules/`，风险高于当前受控本地输出。
  - 对 Claude Code CLI 的可靠性、权限模式和后置验证要求更高。

## 推荐方案

- 选择方案 C。
- 原因：这次目标不是做一个“比现在稍聪明一点”的本地脚本，而是尽量恢复原版的 agentic 执行模型。方案 C 在架构层面与原版最一致，最符合“Python 只负责触发，智能层负责判断和写入”的设计意图。
- 主要 trade-off：
  - 接受 reflector 直接改 `rules/` 的更高风险，以换取真正的 L2 反思与晋升能力。
  - 放弃机械降级路径，失败就显式失败，不再把“智能层没跑成”伪装成成功。
  - 在 reflector 上引入轻量 git checkpoint，而不是整树文件快照或复杂事务系统。

## 关键边界与组件职责

- `periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py`
  - 新职责：渲染 prompt、调用 Claude Code CLI、采集 stdout/stderr/退出码、执行后置验证、记录状态。
  - 保留职责：observer 幂等检查、任务级 success/failed/skipped 状态回写。
  - 删除职责：本地 observer 分桶分析、本地 reflector 固定规则晋升和受控报告生成。

- `periodic_jobs/ai_heartbeat/src/v0/prompts/observer.md`
  - 承载 observer 的任务协议。
  - 约束 Claude 先读取知识库和相关规则，再扫描、归纳并直接追加写入 `OBSERVATIONS.md`。
  - 明确 observer 不能执行 reflector 职责，不能修改 `rules/`。

- `periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md`
  - 承载 reflector 的任务协议。
  - 约束 Claude 读取 `OBSERVATIONS.md`、提炼晋升规则、执行 GC，并直接修改首版 allowlist 内的 `rules/` 目标文件。
  - 首版不允许创建或修改 allowlist 之外的 `rules/` 文件。
  - 明确要求产出 `heartbeat_reflector_report.md`，列出 touched files、晋升点、GC 摘要和未晋升原因。

- Claude Code CLI
  - 承担 observer / reflector 的实际智能执行。
  - 默认以工作区根目录作为 cwd 调用，依赖默认模式加载根目录 `CLAUDE.md` 与工作区上下文。
  - 使用 `-p` 非交互单次执行，不建立额外的长期会话状态。

- `periodic_jobs/ai_heartbeat/state/claude_runs/`
  - 保存每次 observer / reflector 的运行记录，包括渲染后的 prompt、stdout、stderr、元数据 JSON 和验证结果。
  - 用于失败排障和 prompt 回放。

- `periodic_jobs/ai_heartbeat/state/heartbeat_reflector_report.md`
  - 由 Claude Code 在 reflector 结束时写入。
  - 是本次 reflector 的审计锚点之一，不再由 runner 机械生成。

- Git checkpoint 机制
  - 只服务 reflector，不用于 observer。
  - 用于在 reflector 写坏 `OBSERVATIONS.md` 或目标规则文件时恢复到运行前基线。
  - 优先复用 git 现有能力，而不是引入自定义快照体系。

## Claude Code 调用策略

- 默认使用 Claude Code CLI 的标准模式，不使用 `--bare`。
- 原因：
  - `--bare` 会关闭 `CLAUDE.md` 自动发现，与当前仓库对 Claude Code 的入口约定冲突。
  - 本设计希望尽量贴近正常的 Claude Code agent 会话，而不是手工重建一套完整系统提示。
- 推荐命令形态：
  - `claude -p --output-format json --permission-mode bypassPermissions --dangerously-skip-permissions --model <configured_model>`
  - prompt 文本通过 stdin 传入，而不是把整段 prompt 直接拼进命令行参数。
- 运行 cwd：工作区根目录。
- 首版不依赖 `--append-system-prompt`、`--system-prompt`、`--settings` 或 `--mcp-config` 注入额外上下文；上下文主要来自：
  - 当前工作区根目录
  - 根目录 `CLAUDE.md`
  - prompt 模板中显式要求读取的 `AGENTS.md`、`KNOWLEDGE_BASE.md` 和相关 L3 规则文件
- 如果后续验证表明默认上下文不足，再追加最小必要的 `--add-dir` 或 `--append-system-prompt`。

## 数据流 / 控制流

### Observer

1. SessionStart hook 继续通过 `.github/hooks/pre-session.ps1` 启动 `heartbeat_local_runner.py observer ...`。
2. runner 读取 `OBSERVATIONS.md`，做幂等检查；如果已存在 `Date: <target_date>`，直接记录 skipped 并退出。
3. runner 渲染 observer prompt 到临时文件，并把同一份 prompt 文本作为 `claude -p` 的输入。
4. runner 以工作区根目录为 cwd 调用 Claude Code CLI。
5. Claude 自主执行：读取知识库和规则、扫描最近变动、做语义归纳、直接追加写入 `OBSERVATIONS.md`。
6. Claude 退出后，runner 做后置验证：
  - `OBSERVATIONS.md` 仍可正常读取。
  - `Date: <target_date>` 条目已真实出现。
7. 验证通过，记录 success；否则记录 failed，并保留运行日志。

### Reflector

1. SessionStart hook 继续通过 `.github/hooks/pre-session.ps1` 启动 `heartbeat_local_runner.py reflector ...`。
2. runner 识别 reflector 允许触碰的 tracked 文件集合；首版固定为以下 allowlist：
  - `contexts/memory/OBSERVATIONS.md`
  - `rules/SOUL.md`
  - `rules/USER.md`
  - `rules/COMMUNICATION.md`
  - `rules/WORKSPACE.md`
  - `rules/skills/ai_heartbeat_local_reflections.md`
3. runner 检查这组文件的 git 状态：
  - 如果触面 clean，直接以当前 `HEAD` 作为恢复基线。
  - 如果触面 dirty，先创建临时 git checkpoint，保存 reflector 运行前状态。
4. runner 渲染 reflector prompt，并调用 Claude Code CLI。
5. Claude 自主执行：读取 `OBSERVATIONS.md`、提炼晋升规则、修改对应 `rules/` 文件、做 GC、写 `heartbeat_reflector_report.md`。
6. Claude 退出后，runner 做后置验证：
  - `OBSERVATIONS.md` 和被修改过的规则文件仍可正常读取。
  - `heartbeat_reflector_report.md` 存在且包含本次 target date。
  - report 中列出了 touched files。
  - report 中列出的 touched files 是 allowlist 的子集，且每一行都应是裸 repo-relative path。
7. 验证通过：
  - 记录 success。
  - 若存在临时 git checkpoint，则删除该临时恢复锚点。
8. 验证失败或 Claude 执行失败：
  - 若存在临时 git checkpoint，则仅恢复 reflector 触面文件。
  - 若触面 clean 且基线来自 `HEAD`，则从 `HEAD` 恢复 reflector 触面文件。
  - 记录 failed，并保留完整运行日志。

## 2026-05-24 实施根因链与修复点

- 本轮真实 dry run 暴露出的第一条根因链不是 Claude 本身不会写文件，而是 prompt 中混入了绝对 Windows 路径和 8.3 短路径，触发了 Claude CLI 的 suspicious Windows path 审批门槛。
- 对应修复已经落在 runner：observer 和 reflector prompt 改为 repo-relative path，运行 cwd 固定为工作区根目录，同时在 prompt 前缀里明确禁止把路径改写回绝对 Windows 路径或 8.3 短路径。
- 第二条根因链来自 CLI 调用方式。早期实现把整段 prompt 作为 `-p <prompt>` argv 传入；当前实现改成保留 `-p`，但通过 stdin 传 prompt，避免 Windows 下超长命令行和转义噪声继续污染调用链。
- 第三条根因链来自权限旗标语义。`--allow-dangerously-skip-permissions` 只表示允许启用 bypass，不等于真的跳过权限；当前实现已经固定为 `--dangerously-skip-permissions`。
- 第四条根因链来自 reflector allowlist。`heartbeat_reflector_report.md` 是合法输出，但最初没有进入运行时 allowlist，导致 reflector 写出 report 后又被 runner 判成越界修改。当前实现会把运行时 `report_path` 自动并入 allowlist。
- 第五条根因链来自 report 格式。Claude 在 `## Touched Files` 下自然写出了“路径 + 说明”的 bullet；当前实现做了两层处理：一方面收紧 prompt，要求 touched-file 行固定写成裸 repo-relative path；另一方面保留解析兜底，兼容历史 report 里的反引号和尾注说明。
- 第六条根因链来自失败回滚。reflector 失败时，旧逻辑会对所有 allowlist 路径统一做 `git checkout <baseline> -- <path>`；一旦 report 文件是本次新生成且不在 baseline 里，回滚阶段本身就会再失败。当前实现已经改为：存在于 baseline 的路径走 checkout，只在本次运行里生成、且 baseline 中不存在的路径直接删除。
- 当前 dry-run 验证结果已经满足设计目标：observer 与 reflector 都能在非交互模式下完成，reflector report 能稳定生成，状态文件也会正确写回 success。
- 当前对 reflector report 的明确约束是：`## Touched Files` 下每个 bullet 只允许写裸 repo-relative path，格式固定为 `- path/to/file.ext`，不加反引号，不加解释，不在同一行追加原因说明。

## Git checkpoint 设计

- 该机制是“临时恢复锚点”，不是在当前分支上长期留下一个普通开发 commit。
- 只在 reflector 使用；observer 不使用 checkpoint。
- 只覆盖 reflector 的 allowlist 触面，不覆盖整个仓库，也不扫描嵌套子仓库。
- 如果 reflector 运行前触面已经干净，直接把当前 `HEAD` 当成恢复基线，不强制生成额外 checkpoint。
- 如果 reflector 运行前触面存在未提交修改，则创建临时 git checkpoint，确保恢复到 reflector 运行前那一刻，而不是恢复到更早的 `HEAD`。
- reflector 成功后，checkpoint 应被清理，不作为长期历史保留。
- reflector 失败后，恢复动作只针对触面文件，不影响用户在其他路径下的未提交工作。

## 错误处理与回退

### Claude CLI 不存在或不可执行

- 处理：直接记 failed。
- 记录：写入运行日志，明确错误为 CLI 不可用。
- 不回退到机械扫描。

### Claude CLI 超时

- 处理：直接记 failed。
- 记录：保留 prompt、stdout/stderr、超时信息。
- reflector 若已建立基线，则恢复触面文件。

### Claude 退出码非 0

- 处理：直接记 failed。
- reflector 若已建立基线，则恢复触面文件。

### `--output-format json` 无法解析

- 处理：直接记 failed。
- 原因：说明 CLI 返回结果不符合预期，不应继续假定任务成功。

### Observer 后置验证失败

- 处理：记 failed。
- 标准：未生成 target date 条目、或 `OBSERVATIONS.md` 变为不可读。

### Reflector 后置验证失败

- 处理：记 failed，并恢复 reflector 触面文件。
- 标准：report 缺失、未写入 target date、`OBSERVATIONS.md` 不可读、或被 report 标记为 touched 的规则文件不可读。

### Reflector 修改了 allowlist 之外的文件

- 处理：记 failed，并恢复 reflector 触面文件。
- 原因：首版 reflector 的写面是固定集合；任何越界写入都视为协议违例。

### Git checkpoint 创建失败

- 处理：reflector 直接失败，不执行 Claude。
- 原因：该任务允许直接改 `rules/`，没有恢复锚点时不应继续。

### 运行日志写入失败

- 处理：任务失败。
- 原因：日志与 prompt 回放是本设计的审计基线之一，首版不接受 silent loss。

## 测试策略

### 单元测试

- 验证 prompt 渲染和路径注入逻辑。
- 验证 observer 幂等检查和 success / skipped / failed 状态回写。
- 验证 reflector 触面识别、git clean / dirty 两种基线选择逻辑。
- 验证失败时的恢复命令只覆盖 reflector 触面文件。

### CLI 适配测试

- 验证 `claude -p ... --output-format json` 在当前工作区可正常运行。
- 验证 cwd 设置为工作区根目录时，Claude 能读取 `CLAUDE.md` 并访问目标文件。
- 验证通过 stdin 传入 prompt 时，CLI 返回仍能稳定解析为 JSON。
- 验证 `--permission-mode bypassPermissions --dangerously-skip-permissions` 下 observer / reflector 可以非交互完成文件改动。

### 行为测试

- Observer 成功路径：运行一次 observer，确认 `OBSERVATIONS.md` 新增语义条目，而不是当前机械路径桶。
- Observer 幂等路径：同一日期重复运行 observer，确认第二次为 skipped。
- Reflector 成功路径：运行 reflector，确认 `heartbeat_reflector_report.md` 更新，并能真实修改 `rules/` 或明确说明无可晋升项。
- Reflector 失败恢复路径：人为构造 Claude 执行失败或后置验证失败，确认触面文件从 git 基线恢复。

### 审计测试

- 每次运行都应生成 prompt 副本、stdout、stderr 和元数据记录。
- report 中必须列出 touched files，便于后续人工使用 git 做复核。
- report 中的 touched files 必须是 reflector allowlist 的子集，且采用裸 repo-relative path 格式。

## 未决事项

- 需要在实施阶段确认 Claude Code CLI 返回 JSON 的稳定字段结构，并据此定义最小解析逻辑。
- 首版 reflector 的 allowlist 已固定；是否扩展到更多 `rules/skills/` 文件，留待后续版本再讨论。
- 需要在实施阶段决定临时 git checkpoint 的具体命名与清理方式，但不改变本设计确定的恢复语义。