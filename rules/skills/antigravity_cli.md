# Antigravity CLI 文件式调用

## 元数据

- 类型：API Guide
- 适用场景：用 Antigravity 订阅额度调用 Gemini agent，替代 Gemini API sub-agent；自动化写作、重写、审稿和文件处理
- 命令：`agy`
- 已验证版本：1.1.2（2026-07-14）

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

`agy` 1.1.2 没有独立 `login` 子命令。`agy models` 或首次 `agy --print` 会尝试从系统 keyring 静默取得 Antigravity 凭证。如果机器尚未登录，先在 Antigravity App / IDE 中完成 Google 登录，再重试 `agy models`。不要用 `GEMINI_API_KEY` 兜底，因为那会绕回 API 计费路径，不再是本 skill 要验证的订阅通道。

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

中文写作和 prose QA 默认用 `Gemini 3.5 Flash (High)`：

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

调用方还应设置约 610 秒的外层 process timeout。`--print-timeout 10m` 是 AGY 内部等待上限；外层多留约 10 秒用于进程退出和日志落盘。

`--dangerously-skip-permissions` 只允许与 `--sandbox` 同时使用，并且只在上述最小 trusted scratch workspace 中使用。它用于避免非交互模式卡在文件写入确认，不代表允许 agent 扩大任务范围。任务文件必须明确写出唯一输出路径和“不要修改其他文件”。

## 模型与能力检查

每次首次使用或升级后检查：

```bash
agy --version
agy --help
agy models
```

已验证可用模型包括：

- `Gemini 3.5 Flash (Low)`
- `Gemini 3.5 Flash (Medium)`
- `Gemini 3.5 Flash (High)`
- `Gemini 3.1 Pro (Low)`
- `Gemini 3.1 Pro (High)`

写作工作流默认 `Gemini 3.5 Flash (High)`。需要更强推理且订阅配额允许时，才显式改用 `Gemini 3.1 Pro (High)`。不要依赖交互式 `/model` 的持久设置；正式调用始终传 `--model`。

AGY 1.1.2 的 print mode 会在模型名无效时返回非零退出码并列出可用模型。不要静默 fallback。

## 进度与卡死判断

AGY 1.1.2 没有 `--json` 或 `--output-format stream-json`。不要编造 JSON mode，也不要把 plain stdout 包装成伪事件流。

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

任务文件至少包含：

```markdown
# Task

Read these files completely:
1. `/absolute/path/to/writing_brief.md`
2. `/absolute/path/to/source_draft.md`
3. `/absolute/path/to/COMMUNICATION.md`
4. `/absolute/path/to/bestpractice_external_prose.md`

Write the complete result to:
`/absolute/path/to/result.md`

Do not modify any other file.

## Hard invariants

- Preserve the thesis, facts, numbers, URLs, image references, and H2 order.
- Preserve product names and project-specific terms exactly as listed below.
- Do not translate identifiers such as `reset card`, model names, API names, or code symbols.
- Use normal Chinese paragraphs. Do not put every sentence on its own line.
- Short sentences are a tendency, not a reason to create telegraph prose.
- Read the output once after writing and verify every invariant.
```

写作 brief 应提供一份“不可改词表”，列出产品名、模型名、容易误译的术语和必须逐字保留的标签。AGY 实测会主动翻译 `Oracle`、`reset card`、`system of record` 等词；没有词表时容易改变事实口径。

## Fresh Context 与多轮写作

每次不带 `--continue` 或 `--conversation` 的 `agy --print` 都创建新 conversation。外部写作的 IC-1、IC-2、IC-3 应分别调用一次新的 `agy --print`，不要复用 conversation：

- IC-1 只读 brief，写结构稿。
- IC-2 读 brief + 结构稿 + 3-5 篇同渠道已发布成稿校准样本，完整重写。prompt 必须说明只继承结构稿的 claim、证据、URL、数字与 H2 顺序，不继承原句和段落入口；按 brief 的 Voice Route 从空白页面重写。目标是“懂技术的人向聪明朋友自然介绍自己的发现”，同时避开教材声和表演式口语两个极端。
- IC-3 读 brief + IC-2 成品 + IC-2 使用的正向样本与双端负例 + 文风规则，先做整篇声线判定。若开头、多个 H2 入口和结尾仍像课程讲义，必须整篇重写 prose，不能只换词；随后检查是否为亲切感擅自加入比喻、俚语、绝对化结论或 source pack 没有的新事实。输出 `article_qa.md` 候选稿，不把自己的 prose 直接视为最终稿。

IC-3 完成后，主线程按 `workflow_external_writing.md` 执行 Manager Voice Pass：读取 `article_qa.md`，写 `article_final.md` 和带真实前后对照的 `translationese_audit.md`。这一步不再调用 AGY；最终 prose 责任由主线程保留。

每一轮使用独立的 prompt、result、stdout、stderr 和 events 文件。文件名应包含阶段，例如：

- `agy_ic1_prompt.md` / `agy_ic1_events.log`
- `agy_ic2_prompt.md` / `agy_ic2_events.log`
- `agy_ic3_prompt.md` / `agy_ic3_events.log`

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
- 用全新 AGY conversation 完成独立 prose QA，保留 Top 5 排序、四段结构、两个深挖候选和全部 17 个 URL，并修正夸大表述与术语漂移。因此 external-facing 成品仍默认保留独立 IC-3，不能把一次 AGY 重写视为免检成稿。

## 官方来源

- https://github.com/google-antigravity/antigravity-cli
- https://antigravity.google/product/antigravity-cli
- https://antigravity.google/docs/cli-overview
