# Antigravity CLI 文件式调用

## 元数据

- 类型：API Guide
- 适用场景：用 Antigravity 订阅额度调用 Gemini agent，自动化完成写作、重写、审稿和文件处理
- 命令：`agy`
- 已验证版本：1.1.2（2026-07-14）

## 核心判断

`agy-ide` 是 IDE launcher。它的 `chat` 子命令会把 prompt 送进图形界面，不是 headless agent CLI。自动化必须使用独立的 Antigravity CLI：`agy`。

## 首次安装与初始化

每台机器第一次使用前先检查命令是否存在：

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

安装脚本默认把二进制放在 `~/.local/bin/agy`。如果当前 shell 仍找不到命令，运行安装器自带的环境配置，再重新打开 shell：

```bash
~/.local/bin/agy install
```

随后完成初始化检查：

```bash
agy --version
agy --help
agy models
```

`agy` 1.1.2 没有独立的 `login` 子命令。`agy models` 或首次 `agy --print` 会尝试从系统 keyring 静默取得 Antigravity 凭证。如果机器尚未登录，先在 Antigravity App 或 IDE 中完成 Google 登录，再重试 `agy models`。

`agy` 使用 Antigravity 订阅和系统 keyring 登录，不读取 `GEMINI_API_KEY`。不要用 API key 兜底，否则会绕回 API 计费路径，不再是本 skill 要验证的订阅通道。

初始化完成标准：`command -v agy` 返回有效路径，`agy --version` 正常退出，`agy models` 能列出模型。三项都通过后，才运行正式任务。

## 文件式调用契约

所有正式调用都使用三层文件：

1. **任务文件**：完整 prompt 写入 workspace 内的 `tmp/<session>/agy_<task>_prompt.md`。
2. **结果文件**：prompt 要求 agent 把完整成品写入明确路径，例如 `tmp/<session>/agy_<task>_result.md`。
3. **运行记录**：CLI 的 stdout、stderr 和 `--log-file` 分别落盘。stdout 只是完成说明，不能替代结果文件。

prompt、结果和运行记录可能包含任务正文、文件路径、账号元数据或模型事件。它们必须放在 git-ignored 的 `tmp/` 中，只用于本地审计；不得 commit、上传或公开分享。仓库应至少忽略 `tmp/`、`*.log`、`.env` 和 `.env.*`，并在需要时仅放行已脱敏的 `.env.example`。

不要把长 prompt 直接塞进命令行。命令行只传一条 driver prompt，要求读取任务文件并严格执行。任务文件、参考材料和输出文件都应位于启动目录或其子目录。

从只包含本次必要输入的最小 trusted scratch workspace 启动，不要从 home directory、包含大量私有资料的 monorepo 根目录或带 `.env`、凭证、客户数据的目录启动。`--sandbox` 限制工具行为，但不等于 workspace 内所有文件都不会进入远端模型上下文。正式调用前先检查 scratch workspace，删除或移出与任务无关的 secrets 和私有资料。

## 标准命令

中文写作和 prose QA 默认使用 `Gemini 3.5 Flash (High)`：

```bash
agy --print \
  "Read the complete task from /absolute/path/to/agy_task_prompt.md and follow it exactly." \
  --model "Gemini 3.5 Flash (High)" \
  --mode accept-edits \
  --sandbox \
  --dangerously-skip-permissions \
  --print-timeout 10m \
  --log-file "/absolute/path/to/agy_task_events.log" \
  > "/absolute/path/to/agy_task_stdout.txt" \
  2> "/absolute/path/to/agy_task_stderr.txt"
```

调用方还应设置约 610 秒的外层 process timeout。`--print-timeout 10m` 是 AGY 内部等待上限；外层多留约 10 秒供进程退出和日志落盘。

`--dangerously-skip-permissions` 只允许与 `--sandbox` 同时使用，并且只在上述最小 trusted scratch workspace 中使用。任务文件必须写明一个输出路径，或逐项列出一组有限输出路径，并明确“不要修改列表之外的文件”。

## 模型与可观测性

每次首次使用或升级后运行 `agy --version`、`agy --help` 和 `agy models`。已验证的模型包括：

- `Gemini 3.5 Flash (Low)`
- `Gemini 3.5 Flash (Medium)`
- `Gemini 3.5 Flash (High)`
- `Gemini 3.1 Pro (Low)`
- `Gemini 3.1 Pro (High)`

正式调用始终显式传 `--model`，不要依赖交互式 `/model` 的持久设置。模型名无效时应视为失败，不要静默 fallback。

AGY 1.1.2 没有 `--json` 或 streaming JSON 输出。当前可观测性来自 `--log-file`。日志中的 `Print mode: starting`、`silent auth succeeded`、`streamGenerateContent`、tool confirmation 和 shutdown 事件可以帮助判断进程活性。日志启动阶段可能先出现未登录提示，随后再通过 keyring 完成 silent auth；应以最终退出状态和结果文件为准。

完成条件必须同时满足：

1. 进程退出码为 0。
2. 所有指定结果文件存在且非空。
3. 结果文件满足任务要求的结构、数字、URL 等硬约束。
4. stdout 有完成说明，stderr 没有未处理错误。

进程超时、任一结果文件缺失或为空时，任务失败。不得把 stdout 摘要当作成品兜底。

## 写作任务约束

任务文件至少应明确：需要完整读取的 brief、草稿和文风规则；一个结果路径或逐项列出的有限结果路径；禁止修改列表之外的文件；必须保留的 thesis、事实、数字、URL、图片、H2 顺序和术语。

写作 brief 应附“不可改词表”，列出产品名、模型名、API 名、代码标识符、易误译术语和必须逐字保留的标签。中文正文使用自然段。短句是一种倾向，不得把每句话单独换行。

## Fresh Conversations

每次不带 `--continue` 或 `--conversation` 的 `agy --print` 都创建新 conversation。多轮写作的 IC-1、IC-2、IC-3 应分别调用一次新的 `agy --print`。所有 prompt、草稿、校准材料、审查报告和日志都放在 gitignored 的 `tmp/<session_slug>/` 下：

- IC-1 只读 brief，写结构稿。
- IC-2 读 brief、结构稿和同渠道文风校准材料，从空白页面完整重写。
- IC-3 读 brief、IC-2 成品、校准材料和文风规则，独立审稿并写 `article_qa.md` 与 `prose_qa.md`。
- 主线程随后完成 Manager Voice Pass，写 `article_final.md` 与 `voice_audit.md`。这一步不属于 AGY conversation。

每轮使用独立的 prompt、result、stdout、stderr 和 events 文件，例如 `agy_ic1_prompt.md`、`agy_ic1_result.md`、`agy_ic1_stdout.txt`、`agy_ic1_stderr.txt`、`agy_ic1_events.log`。

## 已知限制

- 没有 JSON 或 streaming JSON 输出。
- stdout 不适合作为主要 artifact。
- 事件日志属于实现细节，只用于判断活性，不应作为稳定业务 API。
- `agy-ide chat` 会打开或复用 GUI，不能作为 headless fallback。
- AGY 会调用 agent 工具，可能比单次 API 请求慢。默认 10 分钟 timeout，不无限重试。

## 官方来源

- https://github.com/google-antigravity/antigravity-cli
- https://antigravity.google/product/antigravity-cli
- https://antigravity.google/docs/cli-overview
