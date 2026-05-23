# Copilot CLI Smart Heartbeat Design

Date: 2026-05-23
Status: Approved
Author: User + AI

## Background & Goal

AI Heartbeat 的 observer（L1 观测）和 reflector（L2 反思）任务最初设计为 agentic 架构：Python 触发器发送 prompt 给远程 OpenCode Server，由 LLM agent 自主完成文件分析、模式识别和写入。由于 OpenCode Server 在当前环境中不可用，heartbeat_local_runner.py 用纯 Python 机械扫描替代了智能层，代价是：

- Observer 只做基于目录路径的硬编码分桶（🔴🟡🟢），不理解文件内容
- Reflector 只输出固定模板规则，不做真正的跨条目分析和规则晋升

**Goal**: 利用本地安装的 GitHub Copilot CLI (`copilot -p`) 引入智能处理，恢复 agentic 能力，同时保持与现有 hook 流程的兼容。

## Scope

### In Scope
- 改造 heartbeat_local_runner.py，在不改变 pre-session.ps1 和 hook 配置的前提下，用 copilot -p 替代机械扫描
- 创建外部 prompt 模板文件（observer.md / reflector.md）
- 保留机械扫描作为降级路径
- 归档旧脚本到 legacy/ 目录

### Out of Scope
- 修改 pre-session.ps1 或 hook 配置
- 修改 heartbeat_preflight.py 或 heartbeat_state.py
- 修改弹窗 UI 或状态管理逻辑
- 创建新的 Python 脚本文件

## Design Decisions

### D1: 改造现有 runner.py（不新增脚本）

**选择**: 修改 heartbeat_local_runner.py，不创建新的 Python 入口。

**理由**:
- pre-session.ps1 的 Start-HeartbeatLocalExecution 已硬编码调用 heartbeat_local_runner.py
- 不改 pre-session.ps1 意味着零风险不影响 hook 流程
- runner.py 已有完整的参数解析和状态回写逻辑

### D2: 完全 Agentic（与原版一致）

**选择**: copilot agent 自主完成所有工作（读文件、分析、写入），Python 端只做触发和状态记录。

**理由**:
- 与原版 observer.py / reflector.py 的策略一致
- 机械扫描层的硬编码判断天花板太低，无法替代真正的语义理解
- copilot CLI 的 --allow-all 模式天然支持自主执行

### D3: 外部 .md 文件管理 Prompt

**选择**: prompt 模板存放在 prompts/observer.md 和 prompts/reflector.md。

**理由**:
- Prompt 需要频繁迭代，不应每次都改 Python 代码
- .md 格式方便在 VS Code 中直接编辑和预览
- 可复用现有 PROMPT_TEMPLATE 的结构，适配 copilot CLI 环境

### D4: copilot CLI 作为智能层

**选择**: `copilot -p "<prompt>" --allow-all -s -C <workspace_root>`

**理由**:
- 非交互模式（-p），跑完即退出，适合后台任务
- 在新 terminal 窗口中执行（Start-Process），不影响当前 VS Code 中的 Copilot 会话
- -s 静默输出，只返回 agent 响应
- --allow-all 给予完整文件系统权限（等同于原版 OpenCode-Builder agent 的权限）

### D5: 降级到机械扫描

**选择**: 当 copilot CLI 不可用时，降级到现有的机械扫描逻辑。

**理由**:
- 防止 copilot 未登录、未安装或网络不通时整个 heartbeat 系统挂掉
- 机械扫描虽然笨，但作为传感器仍然有价值（至少能记录哪些文件变了）
- 降级是渐进式的，不需要人工干预

### D6: 旧脚本归档到 legacy/

**选择**: 将 observer.py、reflector.py、opencode_client.py 移动到 legacy/ 子目录。

**理由**:
- 保留历史参考价值（prompt 模板、agentic 设计思路）
- 不在主目录中造成困惑（用户可能误以为需要维护两套）

## Architecture

### Execution Flow

`
pre-session.ps1 (unchanged)
  → WinForms dialog → user selects task
    → Start-HeartbeatLocalExecution (unchanged)
      → Start-Process new terminal
        → python heartbeat_local_runner.py observer [args]

Inside heartbeat_local_runner.py:

run_observer_local():
  1. Idempotency check (read OBSERVATIONS.md, check Date: xxx)
     → exists → persist_skipped → return
  2. Check copilot CLI availability
     → not available → fallback to mechanical scan
  3. Load prompts/observer.md template
  4. Render template (replace {target_date}, {workspace_root}, etc.)
  5. subprocess.run([
       "copilot", "-p", rendered_prompt,
       "--allow-all", "-s",
       "-C", workspace_root
     ], timeout=600)
     → exit code 0 → persist_success
     → exit code != 0 or timeout → fallback to mechanical scan
                                    persist_failure with error

run_reflector_local():
  Same structure, different prompt template.
`

### Fallback Chain

`
copilot CLI available?
  ├─ Yes → copilot -p (smart path)
  │        ├─ Success → persist_success
  │        └─ Fail/Timeout → mechanical scan → persist_success(degraded)
  └─ No → mechanical scan directly → persist_success(degraded)
`

### Key Behavior: Degraded Status

当智能路径失败、降级到机械扫描时，状态记录为 **success (degraded)**：
- last_status 设为 "success"（任务确实完成了）
- last_error 记录降级原因（如 "copilot CLI timeout, fell back to mechanical scan"）
- 这样下一轮 preflight 不会因为 failed 而反复重试，但降级事件可追溯

### File Changes

`
Modified:
  periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py
    + _is_copilot_cli_available() -> bool
    + _load_prompt_template(task_name) -> str
    + _render_prompt(template, **kwargs) -> str
    + _run_copilot_cli(prompt, workspace_root, timeout) -> CompletedProcess
    ~ run_observer_local(): smart path with mechanical fallback
    ~ run_reflector_local(): smart path with mechanical fallback
    (existing mechanical code retained as fallback)

New:
  periodic_jobs/ai_heartbeat/src/v0/prompts/observer.md
    - Observer prompt template (based on observer.py PROMPT_TEMPLATE)
    - Variables: {target_date}, {workspace_root}, {observations_path}
  
  periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md
    - Reflector prompt template (based on reflector.py PROMPT_TEMPLATE)
    - Variables: {target_date}, {workspace_root}, {observations_path}, {report_path}, {rules_promotion_path}

Moved (archive):
  periodic_jobs/ai_heartbeat/src/v0/legacy/
    ← observer.py
    ← reflector.py  
    ← opencode_client.py
`

## Observer Prompt Design

Based on original observer.py PROMPT_TEMPLATE, adapted for copilot CLI:

``markdown
# L1 Observer Task

## Target Date
{target_date}

## Workspace Root
{workspace_root}

## Observations File
{observations_path}

## Instructions

You are an L1 Observer for a personal knowledge infrastructure workspace. Your job is to scan recent file changes and produce a concise, semantically meaningful observation entry.

### Idempotency Constraint
Before writing, read {observations_path} and check if an entry with Date: {target_date} already exists. If so, output "Entry for {target_date} already exists, skipping" and exit.

### Scan Scope
Scan {workspace_root} for files modified in the last 7 days. Exclude: .git, .venv, __pycache__, .pytest_cache, node_modules, and periodic_jobs/ai_heartbeat/state/.

### Analysis Method
For each modified file:
1. Read the file content (or at least the first 50 lines for large files)
2. Understand WHAT changed and WHY it matters
3. Classify by impact:
   - 🔴 High: Changes to rules/, AGENTS.md, docs/specs/, docs/plans/ — these define the system's behavior
   - 🟡 Medium: Changes to periodic_jobs/, docs/, tools/, m/, README.md — active workspace activity
   - 🟢 Low: Routine changes (scripts, configs, archives)

### Output Format
Write a new entry to {observations_path} using this exact format:

    Date: {target_date}
    
    🔴 High: <natural language description of what changed and why it matters>
    🔴 High: <another observation if applicable>
    🟡 Medium: <description>
    🟢 Low: <summary of routine changes>

### Quality Requirements
- Each observation should be a natural language sentence describing the change's significance, not just a file path
- Group related file changes into single observations where appropriate
- Maximum 6 file paths per observation line
- If no significant changes found: 🟢 Low: No significant workspace changes detected.

### Scope Constraint
This is an L1 Observer task ONLY. Do NOT modify any files under rules/. Do NOT perform L2 Reflector work (no rule promotion, no garbage collection).
``

## Reflector Prompt Design

Based on original reflector.py PROMPT_TEMPLATE, adapted for copilot CLI:

``markdown
# L2 Reflector Task

## Target Date
{target_date}

## Workspace Root
{workspace_root}

## Observations File
{observations_path}

## Report File
{report_path}

## Rules Promotion File
{rules_promotion_path}

## Instructions

You are an L2 Reflector for a personal knowledge infrastructure workspace. Your job is to review observations, distill operational rules, and clean up stale entries.

### Step 1: Read and Analyze
Read {observations_path} completely. Focus on 🔴 High and 🟡 Medium entries from the last 14 days.

### Step 2: Rule Promotion
Identify patterns that are:
- Cross-project applicable
- Verified across multiple observations
- Have clear actionable scope

Promote to the appropriate target file:
- rules/SOUL.md: Agent identity and core values
- rules/USER.md: User profile and philosophy
- rules/COMMUNICATION.md: Communication style (communication only, not technical knowledge)
- rules/WORKSPACE.md: Directory routing
- rules/skills/: Technical methodology, workflows, best practices

Write promoted rules to {rules_promotion_path} using this format:

    # AI Heartbeat Local Reflections
    
    Last Updated: {target_date}
    
    ## Promoted Rules
    - <rule 1>
    - <rule 2>
    ...

### Step 3: Garbage Collection
Rewrite {observations_path}:
- Remove entries that have been fully promoted to rules
- Remove 🟢 Low entries older than 30 days
- Keep all 🔴 and 🟡 entries from the last 14 days
- Keep entries that contain unresolved insights

### Promotion Threshold
Only promote rules that meet ALL criteria:
- Cross-project generalizable
- Verified (appeared in multiple observations or confirmed by manual review)
- Has a clear applicable scenario
- Not already present in the target file

### Output
After completing all steps, write a brief summary report to {report_path}.

### Scope Constraint
This is an L2 Reflector task. Focus on rule promotion and GC. Do NOT start new L1 Observer observations.
``

## Error Handling

| Scenario | Detection | Response | Status Record |
|----------|-----------|----------|---------------|
| copilot CLI not installed | shutil.which("copilot") is None | Fallback to mechanical scan | success (degraded) |
| copilot CLI not logged in | Subprocess exits non-zero quickly | Fallback to mechanical scan | success (degraded) |
| copilot execution timeout | subprocess.run(..., timeout=600) raises TimeoutExpired | Fallback to mechanical scan | success (degraded) |
| copilot execution fails | Exit code != 0 | Fallback to mechanical scan | success (degraded) |
| Prompt template missing | FileNotFoundError on prompts/*.md | Log error, fallback to mechanical scan | success (degraded) |
| OBSERVATIONS.md has today's entry | Idempotency check | Skip entirely | skipped |

## Testing Strategy

1. **Smart path**: Run heartbeat_local_runner.py observer --target-date <test-date> → verify copilot CLI is invoked and OBSERVATIONS.md gets a semantic entry (not just file paths)
2. **Fallback path**: Set PATH to exclude copilot → verify mechanical scan runs and produces the same output as before
3. **Idempotency**: Run observer twice with same date → second run outputs "Entry already exists, skipping"
4. **Terminal isolation**: Verify the new terminal window (started by Start-Process in pre-session.ps1) runs independently and does not inject output into the current VS Code Copilot session
5. **Reflector end-to-end**: Run reflector after observer → verify rules promotion and GC happen via copilot CLI
6. **Degraded status**: Verify that fallback scenarios correctly record success + degradation note in heartbeat_status.json

## Open Items

- [ ] Determine appropriate subprocess timeout (proposed: 600s/10min for observer, 900s/15min for reflector)
- [ ] Decide if copilot CLI stdout should be captured to a log file under periodic_jobs/ai_heartbeat/state/ for debugging
- [ ] Consider adding --model parameter support (e.g., --model gpt-5.2) — deferred to post-MVP
- [ ] Consider adding --effort level configuration (default: medium) — deferred to post-MVP