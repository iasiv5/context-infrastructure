# AI Heartbeat 跨平台重构迁移实施计划

## 目标

将子仓库 `openbmc-aware-harness` commit `228d27f8` 中的 3 个运行时文件迁移到主仓库，使主仓库获得跨平台 ai-heartbeat 能力。

## 输入工件

- 设计文档：`docs/specs/2026-06-04-migrate-ai-heartbeat-cross-platform-refactor-design.md`
- 源 commit：`openbmc-aware-harness` 仓库的 `228d27f8a13eb01caafdfb483ad8f6eb5656e4ae`

## 架构快照

本次迁移不引入新架构，只是把子仓库已有的"薄壳 + SOP 分离"结构复制到主仓库。迁移后主仓库的 `/ai-heartbeat` 执行路径从"厚文件单入口"变为"薄壳入口 → SOP 合同 → Python 脚本"三层分离。

## 文件结构与职责

- Modify: `.github/prompts/ai-heartbeat.prompt.md`（厚文件 → 薄壳，OS 探测 + SOP 引用）
- Create: `periodic_jobs/ai_heartbeat/docs/AI_HEARTBEAT_SOP.md`（执行合同，单一事实来源）
- Create: `.claude/commands/ai-heartbeat.md`（Claude Code 入口薄壳）

## 任务清单

### Task 1: 从子仓库提取 SOP 文件

- 目标：将 `AI_HEARTBEAT_SOP.md` 从子仓库 git 对象提取到主仓库
- 涉及文件：`periodic_jobs/ai_heartbeat/docs/AI_HEARTBEAT_SOP.md`（新建）
- 验证：文件存在且内容与子仓库 commit 中版本一致

- [ ] Step 1: 确认目标目录存在
- Run: `Test-Path "d:\_context-infrastructure\periodic_jobs\ai_heartbeat\docs"`
- Expected: `True`

- [ ] Step 2: 从子仓库 git 对象提取文件
- Run: `cd d:\_context-infrastructure; git --git-dir=openbmc-aware-harness/.git checkout 228d27f8a13eb01caafdfb483ad8f6eb5656e4ae -- periodic_jobs/ai_heartbeat/docs/AI_HEARTBEAT_SOP.md`
- Expected: 命令成功，无错误输出

- [ ] Step 3: 验证文件已正确写入
- Run: `Get-Item "d:\_context-infrastructure\periodic_jobs\ai_heartbeat\docs\AI_HEARTBEAT_SOP.md" | Select-Object Length`
- Expected: 文件大小约 3500-4000 字节（非零）

### Task 2: 从子仓库提取 Claude Code 入口文件

- 目标：将 `.claude/commands/ai-heartbeat.md` 从子仓库 git 对象提取到主仓库
- 涉及文件：`.claude/commands/ai-heartbeat.md`（新建，目录也会自动创建）
- 验证：文件存在且内容正确

- [ ] Step 1: 从子仓库 git 对象提取文件
- Run: `cd d:\_context-infrastructure; git --git-dir=openbmc-aware-harness/.git checkout 228d27f8a13eb01caafdfb483ad8f6eb5656e4ae -- .claude/commands/ai-heartbeat.md`
- Expected: 命令成功，目录和文件自动创建

- [ ] Step 2: 验证文件已正确写入
- Run: `Get-Item "d:\_context-infrastructure\.claude\commands\ai-heartbeat.md" | Select-Object Length`
- Expected: 文件大小约 500-700 字节（非零）

### Task 3: 覆盖 Copilot prompt 入口文件

- 目标：用子仓库的薄壳版替换主仓库的厚文件版 `ai-heartbeat.prompt.md`
- 涉及文件：`.github/prompts/ai-heartbeat.prompt.md`（修改）
- 验证：文件内容与子仓库 commit 中版本一致

- [ ] Step 1: 确认当前文件状态（前置快照）
- Run: `(Get-FileHash "d:\_context-infrastructure\.github\prompts\ai-heartbeat.prompt.md").Hash`
- Expected: 返回当前厚文件的 hash（记录下来用于对比确认已变化）

- [ ] Step 2: 从子仓库 git 对象提取并覆盖
- Run: `cd d:\_context-infrastructure; git --git-dir=openbmc-aware-harness/.git checkout 228d27f8a13eb01caafdfb483ad8f6eb5656e4ae -- .github/prompts/ai-heartbeat.prompt.md`
- Expected: 命令成功，无错误输出

- [ ] Step 3: 验证文件已被替换
- Run: `(Get-FileHash "d:\_context-infrastructure\.github\prompts\ai-heartbeat.prompt.md").Hash`
- Expected: hash 值与 Step 1 不同，确认文件内容确实变了

### Task 4: 交叉验证三个文件的完整性

- 目标：确认主仓库中的 3 个文件与子仓库 `228d27f8` 中的对应文件二进制一致
- 涉及文件：上述 3 个文件
- 验证：三个 `fc /b` 对比全部输出"no differences encountered"

- [ ] Step 1: 对比 SOP 文件
- Run: `cmd /c "fc /b `"d:\_context-infrastructure\openbmc-aware-harness\periodic_jobs\ai_heartbeat\docs\AI_HEARTBEAT_SOP.md`" `"d:\_context-infrastructure\periodic_jobs\ai_heartbeat\docs\AI_HEARTBEAT_SOP.md`""`
- Expected: `FC: no differences encountered`

- [ ] Step 2: 对比 Claude Code 入口文件
- Run: `cmd /c "fc /b `"d:\_context-infrastructure\openbmc-aware-harness\.claude\commands\ai-heartbeat.md`" `"d:\_context-infrastructure\.claude\commands\ai-heartbeat.md`""`
- Expected: `FC: no differences encountered`

- [ ] Step 3: 对比 Copilot prompt 文件
- Run: `cmd /c "fc /b `"d:\_context-infrastructure\openbmc-aware-harness\.github\prompts\ai-heartbeat.prompt.md`" `"d:\_context-infrastructure\.github\prompts\ai-heartbeat.prompt.md`""`
- Expected: `FC: no differences encountered`

### Task 5: 运行现有测试确认无回归

- 目标：确认迁移没有破坏主仓库现有的 Python 测试
- 涉及文件：`periodic_jobs/ai_heartbeat/tests/` 下 3 个测试文件
- 验证：pytest 全部通过

- [ ] Step 1: 运行 ai-heartbeat 相关测试
- Run: `cd d:\_context-infrastructure; .\.venv\Scripts\python.exe -m pytest periodic_jobs/ai_heartbeat/tests/ -v`
- Expected: 所有测试通过，无 failures

### Task 6: 提交变更

- 目标：将 3 个迁移文件和设计文档/实施计划一起提交
- 涉及文件：上述 3 个文件 + 设计文档 + 实施计划
- 验证：`git status` 干净，commit 存在

- [ ] Step 1: 检查工作区状态
- Run: `cd d:\_context-infrastructure; git status`
- Expected: 看到 3 个 modified/new 文件 + 设计文档 + 实施计划

- [ ] Step 2: 暂存并提交
- Run: `cd d:\_context-infrastructure; git add .github/prompts/ai-heartbeat.prompt.md periodic_jobs/ai_heartbeat/docs/AI_HEARTBEAT_SOP.md .claude/commands/ai-heartbeat.md docs/specs/2026-06-04-migrate-ai-heartbeat-cross-platform-refactor-design.md docs/plans/2026-06-04-migrate-ai-heartbeat-cross-platform-refactor-implementation-plan.md; git commit -m "refactor(ai-heartbeat): 跨平台 prompt 入口与执行合同抽离 (migrated from openbmc-aware-harness 228d27f8)"`
- Expected: commit 成功

- [ ] Step 3: 确认提交
- Run: `cd d:\_context-infrastructure; git log --oneline -1`
- Expected: 显示新的 commit

## 最终验证

迁移完成后执行以下收口验证：

1. `git diff HEAD~1 --stat` 确认只改了预期的 5 个文件（3 个运行时 + 设计文档 + 实施计划）
2. 逐文件 `fc /b` 确认 3 个运行时文件与子仓库版本一致
3. `pytest` 确认无回归
4. 在 VS Code 中运行 `/ai-heartbeat` 确认 Copilot 入口能正常触发 OS 探测和 SOP 引用

## 执行纪律

- 按 Task 1-6 顺序执行
- 每个 Task 完成后再进入下一个
- 如果任一 Step 的实际输出与预期不符，立即停下并排查原因
- Task 6 的 commit 包含跨仓库来源信息（子仓库名 + commit hash），便于未来追溯