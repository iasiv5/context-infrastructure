# PLAN PRO MAX Agent 实施计划

## 目标

- 将 [m/plugins/iasi/agents/plan-pro-max.agent.md](m/plugins/iasi/agents/plan-pro-max.agent.md) 升级为 design-first 再 planning 的双阶段 agent，同时保持 VS Code 宿主绑定契约不变。
- 同步插件文档、发布元数据和变更记录，使 `iasi` 的 published surface 与仓库内实际资产保持一致。
- 交付结果应让 `iasi` 明确呈现为包含 2 个 custom agents、3 个 skills、1 个 command prompt 和 1 条 workspace instruction 的插件。

## 架构快照

- 保留 [m/plugins/iasi/agents/plan-pro-max.agent.md](m/plugins/iasi/agents/plan-pro-max.agent.md) frontmatter 中与宿主绑定直接相关的字段，包括 `target`、`disable-model-invocation`、`tools`、`agents`、`handoffs` 以及 `/memories/session/plan.md` 的工件约定。
- 允许调整显示层字段，例如 `name`、`description`、`argument-hint`，并整体重写正文提示词，使其吸收 brainstorming 的 design-first 工作流和 Ask Pro Max 风格里的前提审查强度。
- 文档与发布面同步覆盖 [m/plugins/iasi/README.md](m/plugins/iasi/README.md)、[m/README.md](m/README.md)、[m/plugins/iasi/.github/plugin/plugin.json](m/plugins/iasi/.github/plugin/plugin.json)、[m/.github/plugin/marketplace.json](m/.github/plugin/marketplace.json) 和 [m/plugins/iasi/CHANGELOG.md](m/plugins/iasi/CHANGELOG.md)。
- 版本号按一次新增/强化已发布 agent 资产处理，默认升级到 `5.5.0`；如果执行时发现仓库已有新的未发布版本，再基于最新版本做一致性递增。

## 输入工件

- 已批准设计文档：[docs/specs/2026-05-15-plan-pro-max-design.md](docs/specs/2026-05-15-plan-pro-max-design.md)
- 当前目标文件：[m/plugins/iasi/agents/plan-pro-max.agent.md](m/plugins/iasi/agents/plan-pro-max.agent.md)
- 已发现的同步面：[m/plugins/iasi/README.md](m/plugins/iasi/README.md)、[m/README.md](m/README.md)、[m/plugins/iasi/.github/plugin/plugin.json](m/plugins/iasi/.github/plugin/plugin.json)、[m/.github/plugin/marketplace.json](m/.github/plugin/marketplace.json)、[m/plugins/iasi/CHANGELOG.md](m/plugins/iasi/CHANGELOG.md)

## 文件结构与职责

- Modify: [m/plugins/iasi/agents/plan-pro-max.agent.md](m/plugins/iasi/agents/plan-pro-max.agent.md)
  - 保留绑定字段与 handoff 契约。
  - 重写角色定义、硬约束、双阶段工作流、审批门、回退规则与输出规范。
- Modify: [m/plugins/iasi/README.md](m/plugins/iasi/README.md)
  - 更新资产清单、插件结构树、使用方式和边界描述，使其反映 2 个 agents。
- Modify: [m/README.md](m/README.md)
  - 更新 marketplace 总览行和验证说明，使其包含 Plan Pro Max。
- Modify: [m/plugins/iasi/.github/plugin/plugin.json](m/plugins/iasi/.github/plugin/plugin.json)
  - 更新 description、keywords 和 version，使 published metadata 与新 agent surface 对齐。
- Modify: [m/.github/plugin/marketplace.json](m/.github/plugin/marketplace.json)
  - 更新 `iasi` 插件 description 与 version，保持 marketplace 展示一致。
- Modify: [m/plugins/iasi/CHANGELOG.md](m/plugins/iasi/CHANGELOG.md)
  - 追加新版本条目，记录 Plan Pro Max 升级、README/metadata 同步与版本递增。

编辑约束说明：

- [m/plugins/iasi/agents/plan-pro-max.agent.md](m/plugins/iasi/agents/plan-pro-max.agent.md)、[m/plugins/iasi/README.md](m/plugins/iasi/README.md) 和 [m/plugins/iasi/CHANGELOG.md](m/plugins/iasi/CHANGELOG.md) 在当前工具链里可能以 notebook-backed 形式打开；如果文本 patch 失败、出现 notebook 提示或文件被写成 0 字节，执行者要立即切换到 notebook-aware 编辑方式或 PowerShell UTF-8 fallback，并在同一步完成 read-back 验证。
- 本次不新增其他源码文件，也不做和当前目标无关的结构重构。

## 任务清单

### Task 1: 锁定绑定契约与编辑策略

- 目标：在开始改 prompt 之前，明确哪些 frontmatter 字段必须原样保留，哪些显示层和正文可以调整。
- 涉及文件：[m/plugins/iasi/agents/plan-pro-max.agent.md](m/plugins/iasi/agents/plan-pro-max.agent.md)
- 验证命令：
  - Get-Content "m/plugins/iasi/agents/plan-pro-max.agent.md" -TotalCount 40
- 预期结果：
  - 能逐项核对 `target`、`disable-model-invocation`、`tools`、`agents`、`handoffs` 和 `/memories/session/plan.md` 约定。
  - 明确仅允许调整 `name`、`description`、`argument-hint` 与正文提示词。
  - 文件内容非空，且若发生 truncation 已在本任务内切换编辑策略并恢复。
- [ ] Step 1: 读取当前 agent 顶部 frontmatter，记下必须保留的宿主绑定字段。
- [ ] Step 2: 标记允许调整的显示层字段和正文区域。
- [ ] Step 3: 确认实际编辑方式；若文本 patch 不稳定，立即改用 notebook-aware 或 PowerShell UTF-8 fallback。
- [ ] Step 4: 在任何第一次写入后立即 read-back，确认文件非空且绑定字段未丢失。

### Task 2: 重写 PLAN PRO MAX 的正文协议

- 目标：把 agent 从默认 Plan 升级为 design-first + planning 的双阶段高级规划 agent，同时保持不进入实现的边界。
- 涉及文件：[m/plugins/iasi/agents/plan-pro-max.agent.md](m/plugins/iasi/agents/plan-pro-max.agent.md)
- 验证命令：
  - Get-Content "m/plugins/iasi/agents/plan-pro-max.agent.md" -TotalCount 220
  - 如可用，再对该文件运行编辑器诊断检查。
- 预期结果：
  - frontmatter 的宿主绑定字段保持不变。
  - 正文明确包含：规划适配判断、最小探索、one question at a time、2-3 方案比较、最强反方观点、分段设计确认、显式批准门、批准后写 `/memories/session/plan.md`、设计/计划双向回退规则。
  - 正文仍明确禁止实现、补丁和越权写文件。
- [ ] Step 1: 依据设计文档起草新的 prompt 结构，覆盖角色定义、硬约束、证据与反方协议、设计工作流、批准门、计划工作流和 refinement 回退。
- [ ] Step 2: 只修改允许调整的字段和正文，保留宿主绑定字段不变。
- [ ] Step 3: 读回文件，确认双阶段规则、审批门和 `/memories/session/plan.md` 工件约定都在文本中。
- [ ] Step 4: 若有诊断或格式问题，先在同一文件内修正，再继续后续任务。

### Task 3: 同步插件与 marketplace 文档清单

- 目标：让用户可见文档和目录树准确反映 Plan Pro Max 已作为已发布 agent 资产存在。
- 涉及文件：[m/plugins/iasi/README.md](m/plugins/iasi/README.md)、[m/README.md](m/README.md)
- 验证命令：
  - rg -n "plan-pro-max|Plan Pro Max|2 个 custom agent|2 个 custom agents|2 个 agents|2 个 custom agents|2 custom agents" m/plugins/iasi/README.md m/README.md
- 预期结果：
  - 插件 README 的资产列表、结构树、使用说明和边界描述都包含 Plan Pro Max。
  - 根 README 的 marketplace 总览和验证步骤包含 Plan Pro Max。
  - 不再保留“只有 1 个 custom agent”这一类陈旧描述。
- [ ] Step 1: 更新 [m/plugins/iasi/README.md](m/plugins/iasi/README.md) 的资产清单、插件结构树和“当前边界”计数。
- [ ] Step 2: 在 [m/plugins/iasi/README.md](m/plugins/iasi/README.md) 的使用说明中补充 Plan Pro Max 的定位与调用方式。
- [ ] Step 3: 更新 [m/README.md](m/README.md) 的插件概览行和验证说明，使其列出 Ask Pro Max 与 Plan Pro Max。
- [ ] Step 4: 搜索两份 README，确认没有遗漏的旧计数或旧描述。

### Task 4: 同步发布元数据与变更记录

- 目标：保持插件 manifest、marketplace entry 和 changelog 与新增/强化后的 agent surface 一致。
- 涉及文件：[m/plugins/iasi/.github/plugin/plugin.json](m/plugins/iasi/.github/plugin/plugin.json)、[m/.github/plugin/marketplace.json](m/.github/plugin/marketplace.json)、[m/plugins/iasi/CHANGELOG.md](m/plugins/iasi/CHANGELOG.md)
- 验证命令：
  - Get-Content "m/plugins/iasi/.github/plugin/plugin.json" | ConvertFrom-Json | Out-Null
  - Get-Content "m/.github/plugin/marketplace.json" | ConvertFrom-Json | Out-Null
  - rg -n "5\.5\.0|plan-pro-max|Plan Pro Max|two reusable agents|2 个 custom agent|2 custom agents" m/plugins/iasi/.github/plugin/plugin.json m/.github/plugin/marketplace.json m/plugins/iasi/CHANGELOG.md
- 预期结果：
  - 两个 JSON 文件都能成功解析。
  - plugin description 与 marketplace description 明确反映 ask-pro-max + plan-pro-max + 3 skills + 1 command prompt 的 published surface。
  - plugin.json、marketplace.json 和 CHANGELOG 使用同一个新版本号。
- [ ] Step 1: 确定版本号递增策略，默认将插件版本从 5.4.0 提升到 5.5.0。
- [ ] Step 2: 更新 [m/plugins/iasi/.github/plugin/plugin.json](m/plugins/iasi/.github/plugin/plugin.json) 的 description、keywords 和 version。
- [ ] Step 3: 更新 [m/.github/plugin/marketplace.json](m/.github/plugin/marketplace.json) 中 `iasi` 条目的 description 和 version。
- [ ] Step 4: 在 [m/plugins/iasi/CHANGELOG.md](m/plugins/iasi/CHANGELOG.md) 中追加新版本条目，记录 agent 升级和文档/元数据同步。
- [ ] Step 5: 解析两个 JSON 并核对版本一致性；若任一文件解析失败，先修复再继续。

### Task 5: 做一次收口验证与发布面审计

- 目标：在不跑仓库级构建的前提下，确认实现结果在 prompt、文档和发布面上自洽且无明显遗漏。
- 涉及文件：[m/plugins/iasi/agents/plan-pro-max.agent.md](m/plugins/iasi/agents/plan-pro-max.agent.md)、[m/plugins/iasi/README.md](m/plugins/iasi/README.md)、[m/README.md](m/README.md)、[m/plugins/iasi/.github/plugin/plugin.json](m/plugins/iasi/.github/plugin/plugin.json)、[m/.github/plugin/marketplace.json](m/.github/plugin/marketplace.json)、[m/plugins/iasi/CHANGELOG.md](m/plugins/iasi/CHANGELOG.md)
- 验证命令：
  - rg -n "one custom agent|1 个 custom agent|ask-pro-max, three reusable skills, and one reusable command prompt" m/plugins/iasi/README.md m/README.md m/plugins/iasi/.github/plugin/plugin.json m/.github/plugin/marketplace.json
  - 如可用，对上述 6 个文件运行编辑器诊断检查。
  - 手动 smoke：重新打开插件说明或 Copilot 选择器，确认 Plan Pro Max 的展示名称与定位文案合理。
- 预期结果：
  - 不再存在“只有一个 agent”的陈旧文案。
  - 所有被触及文件内容非空、路径和命名一致。
  - 手动查看时，Plan Pro Max 的定位清晰可见，不与 Ask Pro Max 混淆。
- [ ] Step 1: 搜索所有已改文件，清掉仍然残留的旧清单文案。
- [ ] Step 2: 对已改文件做一次诊断检查；如有本次引入的错误，立即修复。
- [ ] Step 3: 做一次最小手动 smoke，确认文案和资产命名对用户可理解。
- [ ] Step 4: 输出最终修改摘要，说明保持了哪些绑定字段不变，以及同步了哪些发布面文件。

## 执行纪律

- 开始实现前，先批判性复查本计划；如果发现版本号、文件范围或验证命令与仓库现实不符，先修计划再动手。
- 严格按任务顺序执行；不要把 prompt 改写、文档同步和发布面同步混成一个不可验证的大步骤。
- 每个任务完成后都运行该任务定义的验证；如果验证失败，先在当前任务内修复，不要跳到后面的任务碰运气。
- 遇到 notebook-backed 文档、0 字节文件、frontmatter 误改或 JSON 解析失败时，立即停在当前任务并修复，不要带着损坏状态继续。
- 如果当前就在 `main` 或 `master`，且用户没有明确同意，开始实现前先确认。
- 全部任务完成后，再做收口验证并输出变更摘要。

## 最终验证

- 读取 [m/plugins/iasi/agents/plan-pro-max.agent.md](m/plugins/iasi/agents/plan-pro-max.agent.md) 前 200 行，人工核对 frontmatter 绑定字段未变、正文出现 design-first 双阶段协议。
- 运行以下 JSON 解析检查：
  - Get-Content "m/plugins/iasi/.github/plugin/plugin.json" | ConvertFrom-Json | Out-Null
  - Get-Content "m/.github/plugin/marketplace.json" | ConvertFrom-Json | Out-Null
- 运行以下搜索审计：
  - rg -n "plan-pro-max|Plan Pro Max|5\.5\.0" m/plugins/iasi/agents/plan-pro-max.agent.md m/plugins/iasi/README.md m/README.md m/plugins/iasi/.github/plugin/plugin.json m/.github/plugin/marketplace.json m/plugins/iasi/CHANGELOG.md
  - rg -n "one custom agent|1 个 custom agent|ask-pro-max, three reusable skills, and one reusable command prompt" m/plugins/iasi/README.md m/README.md m/plugins/iasi/.github/plugin/plugin.json m/.github/plugin/marketplace.json
- 如编辑器诊断可用，再对所有已修改文件运行一次 diagnostics 检查。
- 手动结果预期：插件文档、marketplace 文案和 agent 文件都一致指向 Plan Pro Max 已成为 published agent surface 的一部分。