# Antigravity CLI 文件式调用

## 元数据

- 类型：API Guide
- 适用场景：用 Antigravity 订阅额度调用 Gemini agent，替代 Gemini API sub-agent；自动化写作、重写、审稿和文件处理
- 命令：`agy`
- 已验证版本：1.1.5（2026-07-21）

## 核心判断

`agy-ide` 是 IDE launcher。它的 `chat` 子命令会把 prompt 送进图形界面，不是 headless agent CLI。

自动化必须使用独立的 Antigravity CLI：`agy`。官方 installer 位于 `https://antigravity.google/cli/install.sh`；按下方初始化流程先下载审阅，再执行。

`agy` 使用 Antigravity 订阅和系统 keyring 登录，不读取 `GEMINI_API_KEY`。本机 CLI 可以复用 Antigravity App / IDE 已有的 Google 登录凭证。

## 首次安装与初始化

每台机器第一次使用前先检查命令是否存在，不要假设已安装：

```bash
if ! command -v agy >/dev/null 2>&1; then
  installer="$(mktemp)"
  curl -fsSL https://antigravity.google/cli/install.sh -o "$installer"
  less "$installer"  # Review the downloaded script before executing it.
  bash "$installer"
  rm -f "$installer"
fi
```

installer URL 会随官方更新而变化。上述“下载后人工审阅”路线只适合可信个人工作站。受管或高安全环境应从 [官方 GitHub Releases](https://github.com/google-antigravity/antigravity-cli/releases) 下载固定版本资产，并在解压或执行前核对该 release 的 GitHub asset metadata 所公布的 SHA-256 digest。组织无法批准对应 release 与 digest 时，不要安装。

安装脚本默认把二进制放在 `~/.local/bin/agy`。如果当前 shell 仍找不到命令，先运行安装器自带的环境配置，再重新打开 shell：

```bash
~/.local/bin/agy install
```

随后完成初始化检查：

```bash
agy --version
agy --help
agy models
```

`agy` 1.1.5 没有独立 `login` 子命令。`agy models` 或首次 `agy --print` 会尝试从系统 keyring 静默取得 Antigravity 凭证。如果机器尚未登录，先在 Antigravity App / IDE 中完成 Google 登录，再重试 `agy models`。不要用 `GEMINI_API_KEY` 兜底，因为那会绕回 API 计费路径，不再是本 skill 要验证的订阅通道。

初始化完成标准：`command -v agy` 返回有效路径，`agy --version` 正常退出，`agy models` 能列出模型。只有三项都通过后，才运行正式文件式任务。

## 文件式调用契约

所有正式调用都使用三个输入输出层：

1. **任务文件**：完整 prompt 先写入 workspace 内的 `tmp/<session>/agy_<task>_prompt.md`。
2. **结果文件**：prompt 要求 agent 把完整成品写入明确路径，例如 `tmp/<session>/agy_<task>_result.md`。
3. **运行记录**：CLI 的 stdout、stderr 和 `--log-file` 分别落盘。stdout 只是 agent 的完成说明，不能替代结果文件。

prompt、结果和运行记录可能包含任务正文、文件路径、账号元数据或模型事件。它们必须放在 git-ignored 的 `tmp/` 中，只用于本地审计；不得 commit、上传或公开分享。仓库应至少忽略 `tmp/`、`*.log`、`.env` 和 `.env.*`，并在需要时仅放行已脱敏的 `.env.example`。

不要把长 prompt 直接塞进命令行。命令行只传一条 driver prompt：读取任务文件并严格执行。

任务文件、参考材料和输出文件都应位于启动目录或其子目录。从只包含本次必要输入的最小 trusted scratch workspace 启动，不要从 home directory、包含大量私有资料的 monorepo 根目录或带 `.env`、凭证、客户数据的目录启动。

`--sandbox` 限制工具行为，但不等于 workspace 内所有文件都不会进入远端模型上下文。正式调用前先检查 scratch workspace，删除或移出与任务无关的 secrets 和私有资料。

## 标准命令

中文写作和 prose QA 默认用 `gemini-3.6-flash-high`（Gemini 3.6 Flash High）：

```bash
agy --print \
  "Read the complete task from /absolute/path/to/agy_task_prompt.md and follow it exactly." \
  --model "gemini-3.6-flash-high" \
  --mode accept-edits \
  --sandbox \
  --dangerously-skip-permissions \
  --print-timeout 10m \
  --log-file "/absolute/path/to/agy_task_events.log" \
  > "/absolute/path/to/agy_task_stdout.txt" \
  2> "/absolute/path/to/agy_task_stderr.txt"
```

`--print` / `-p` 是顶层 flag，不是子命令。AGY 1.1.5 没有 `agy run`，也没有 `--trust`、`--format` 或 `--output-events`。不要套用其他 agent CLI 的调用形状；`agy run ...` 会进入错误的交互路径，在无 TTY 的 subprocess 中可能报 Bubble Tea `/dev/tty` 错误或挂起。事件和诊断只写入 `--log-file`。

AGY 1.1.5 延续了对持久化 `settings.json` policy 的 headless `--print` 支持。permission、file access、sandbox mode、auto-execution 和 artifact review 等持久设置都会影响非交互运行。正式调用前除检查命令行 flags 外，还必须审阅全局与项目级 AGY settings；不要假设 `--print` 是脱离持久配置的纯净执行环境。

调用方还应设置约 610 秒的外层 process timeout。`--print-timeout 10m` 是 AGY 内部等待上限；外层多留约 10 秒用于进程退出和日志落盘。

`--dangerously-skip-permissions` 只允许与 `--sandbox` 同时使用，并且只在上述最小 trusted scratch workspace 中使用。它用于避免非交互模式卡在文件写入确认，不代表允许 agent 扩大任务范围。任务文件必须明确写出唯一输出路径和“不要修改其他文件”。

## 模型与能力检查

每次首次使用或升级后检查：

```bash
agy --version
agy --help
agy models
```

2026-07-21 在 AGY 1.1.5 中验证可用模型包括：

- `gemini-3.6-flash-low`（Gemini 3.6 Flash Low）
- `gemini-3.6-flash-medium`（Gemini 3.6 Flash Medium）
- `gemini-3.6-flash-high`（Gemini 3.6 Flash High）
- `gemini-3.5-flash-low`、`gemini-3.5-flash-medium`、`gemini-3.5-flash-high`
- `gemini-3.1-pro-low`、`gemini-3.1-pro-high`

写作工作流默认 `gemini-3.6-flash-high`。需要更强推理且订阅配额允许时，才显式改用 `gemini-3.1-pro-high`。不要依赖交互式 `/model` 的持久设置；正式调用始终传 `--model`。

AGY 1.1.5 的 print mode 会在模型名无效时返回非零退出码并列出可用模型。不要静默 fallback。

## 进度与卡死判断

AGY 1.1.5 没有 `--json` 或 `--output-format stream-json`。不要编造 JSON mode，也不要把 plain stdout 包装成伪事件流。

当前可观测性来自 `--log-file`。日志每行自带时间戳，能看到：

- `Print mode: starting`
- `silent auth succeeded`
- `streamGenerateContent` 与 `ResponseID`
- `Auto-approving tool confirmation`
- `CLI store manager shutting down`
- `Language server shutting down`

前台同步调用时，等待进程退出后再读结果文件。后台调用时，可以轮询事件日志的最后修改时间和上述事件，判断模型是否仍有活动。

日志启动阶段可能先出现 `You are not logged into Antigravity`，随后再通过 keyring 完成 `silent auth succeeded`。只要进程最终退出成功且结果文件完整，不要把这些预认证日志误判为失败。

完成条件必须同时满足：

1. 进程退出码为 0。
2. 指定结果文件存在且非空。
3. 结果文件包含任务要求的结构和 URL / 数字等硬约束。
4. stdout 有完成说明；stderr 没有未处理错误。

如果进程超时、结果文件缺失或为空，任务失败。不要把 stdout 的摘要当作成品兜底。

## 写作任务模板

External writing 的 Writer 不读取完整 workflow、`COMMUNICATION.md` 或 `bestpractice_external_prose.md`。Main Agent 先把本题要求压缩成 task packet，再让 AGY 只负责完整成文。

Round 2 候选任务文件至少包含：

```markdown
# Task

Read these files completely:
1. `/absolute/path/to/source_contract.md`
2. `/absolute/path/to/writing_brief.md`
3. `/absolute/path/to/voice_contract.md`
4. `/absolute/path/to/content_map.md`

Write the complete result to:
`/absolute/path/to/result.md`

Do not modify any other file.

## Task

- Write one complete external-facing Chinese article from a blank page.
- Use only facts, scenes, causal claims, and boundaries present in `source_contract.md` and `content_map.md`.
- Preserve the thesis, claim strength, numbers, URLs, image references, and immutable terms.
- Follow `voice_contract.md`; do not output an audit, explanation, invariant count, or PASS statement.
- Decide H2 wording and paragraph entrances independently. Do not copy content-map labels or research taxonomy into the article outline.
- Use normal Chinese paragraphs. Do not put every sentence on its own line.
```

`source_contract.md` 应提供不可改词表，列出产品名、模型名、容易误译的术语和必须逐字保留的标签。AGY 实测会主动翻译 `Oracle`、`reset card`、`system of record` 等词；没有词表时容易改变事实口径。

## Fresh Context、并行候选与一次返工

每次不带 `--continue` 或 `--conversation` 的 `agy --print` 都创建新 conversation。External writing 使用三类 AGY 调用：

- **Round 2 parallel candidates**：默认用两个全新 conversation 从同一个 task packet 分别生成 `candidate_a.md` 和 `candidate_b.md`。运行时有多个模型家族时，优先跨家族生成；它们互不读取，也不串行改写。
- **Round 3 blind reader**：对每个候选使用全新 conversation，只读候选正文，输出 `blind_reader_audit_a.md` 或 `blind_reader_audit_b.md`。它不做事实核查或 PASS 判断。
- **Round 4 optional revision**：只有 Main Agent 冷读验收给出 `RETRY_PROSE` 时，才启动一个全新 conversation。它读取选中候选、原始 task packet 和不超过 3-5 项的 `revision_delta.md`，输出完整修订稿。

AGY Writer 不写 QA，也不是 PASS authority。Main Agent 必须直接读取候选正文，用确定性工具核对数字、URL、图片和结构，再对照 source contract 判断事实与 voice。Round 4 最多一次；仍有非 surgical blocker 时回到 Main Agent 的上游工件或向用户报告，不自动启动更多 AGY conversation。

Main Agent 先独立写 `main_cold_read_a.md` 或 `main_cold_read_b.md`，再读取 blind-reader audit 完成 `acceptance_audit.md`。最终 verdict 只能是 `ACCEPT`、`RETRY_PROSE` 或 `RETURN_TO_ROUND_1`。Writer 的 stdout 只证明进程完成，不参与选择或 PASS 判断。

Round 4 的任务文件必须额外读取选中候选和 `revision_delta.md`。`revision_delta.md` 只列 3-5 个最高影响 blocker、原文位置与正确方向，不得重新附加整份 workflow 或 prose taxonomy。Round 4 输出完整修订稿，不输出 QA。

验收通过后，Main Agent 可做有记录的 surgical completion，包括错字、标点、Markdown、专有名词及可由 source contract 唯一确定的单句局部修复。所有修改写入 `completion_edits.md`；不得借此重排结构或整段重写。

每一轮使用独立的 prompt、result、stdout、stderr 和 events 文件。文件名应包含阶段，例如：

- `agy_candidate_a_prompt.md` / `agy_candidate_a_events.log`
- `agy_candidate_b_prompt.md` / `agy_candidate_b_events.log`
- `agy_revision_prompt.md` / `agy_revision_events.log`

## 已知限制

- 没有 JSON / streaming JSON 输出。
- stdout 只在任务结束时提供最终文本或摘要，不适合当主要 artifact。
- 日志是实现细节，适合判断活性，不应作为稳定 API 解析业务结果。
- `agy-ide chat` 不是本 skill 的 fallback。它会打开或复用 GUI 窗口，无法提供可审计的 headless 完成契约。
- AGY 会调用 agent 工具，可能比单次 Gemini API 请求慢。默认 10 分钟 timeout，不为形式上的模型路由无限重试。

## 验证记录

2026-07-14 在 macOS arm64、AGY 1.1.2 上完成 smoke test：

- 从落盘 prompt 读取任务成功。
- 在 sandbox 中写指定结果文件成功。
- stdout 重定向成功，stderr 为空。
- 事件日志包含带时间戳的 auth、模型请求、文件工具和 shutdown 记录。
- 使用 `Gemini 3.5 Flash (High)` 完成约 2,000 字中文 memo 重写并保留全部 17 个 URL。
- 首轮重写暴露出技术术语误译、逐句换行和第一人称回流；加入不可改词表、自然段约束后显著改善。
- 当时曾用全新 AGY conversation 执行独立 prose QA，并成功保留 Top 5 排序、四段结构、两个深挖候选和全部 17 个 URL。后续多次写作表明，Writer 在同一次 completion 中自写自审并不能可靠判定 PASS；现行流程已改为 Main Agent 冷读验收和最多一次 fresh AGY 返工。一次 AGY 重写仍不能视为免检成稿。

2026-07-20 在 macOS arm64、AGY 1.1.4 上复核 CLI interface 与 headless 路径：

- 官方 GitHub latest release 与本机 `agy --version` 均为 1.1.4。
- `agy --help` 确认 headless 入口仍为顶层 `--print` / `-p`，不存在 `run` 子命令或 JSON event flags。
- `agy --print` 可在非 TTY subprocess 中完成调用，并将 stdout、stderr 与 `--log-file` 分别重定向。
- 1.1.4 release 明确修复 headless run 对持久化 `settings.json` policy 的继承；后续升级复核必须同时检查 CLI help 与 release notes，不能只替换版本号。

2026-07-21 在 macOS arm64、AGY 1.1.5 上完成 Gemini 3.6 Flash High smoke test：

- `agy models` 列出 `gemini-3.6-flash-low`、`gemini-3.6-flash-medium` 和 `gemini-3.6-flash-high`。
- 使用 `gemini-3.6-flash-high` 在最小 sandbox workspace 中读取落盘 prompt、写入指定结果文件并回读验证。
- 进程成功退出，结果内容精确，stderr 为空；事件日志确认模型解析为 `Gemini 3.6 Flash (High)`。

## 官方来源

- https://github.com/google-antigravity/antigravity-cli
- https://antigravity.google/product/antigravity-cli
- https://antigravity.google/docs/cli-overview
