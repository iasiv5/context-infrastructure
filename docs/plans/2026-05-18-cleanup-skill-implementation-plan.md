# cleanup Skill 实施计划

## 目标

- 在 [m/plugins/iasi/skills](m/plugins/iasi/skills) 下新增 `cleanup` skill，使其与现有 [m/plugins/iasi/skills/handoff/SKILL.md](m/plugins/iasi/skills/handoff/SKILL.md) 形成“中途交接用 handoff、终态沉淀用 cleanup”的闭环。
- 将已批准设计 [docs/specs/2026-05-18-cleanup-skill-design.md](docs/specs/2026-05-18-cleanup-skill-design.md) 转成可执行的 prompt 资产，并同步插件 README、marketplace README、plugin metadata 与 changelog。
- 交付结果应让 `iasi` 明确呈现为包含 2 个 custom agents、4 个 skills、1 个 command prompt 和 1 条 workspace-wide instruction 的插件。

## 架构快照

- 新增 [m/plugins/iasi/skills/cleanup/SKILL.md](m/plugins/iasi/skills/cleanup/SKILL.md) 作为单文件 skill，实现设计文档中定义的三层分工：`handoff` 管会话连续性，正式工件更新属于正常开发过程，`cleanup` 管终态长期知识沉淀。
- `cleanup` prompt 需要编码四组关键规则：保守触发模型（硬触发 / 软提醒 / 反触发）、资格门、正常 cleanup 流程、强制 cleanup 流程。
- 强制 cleanup 默认仅允许更新仓库内知识载体，不默认写入用户记忆；这条边界必须在 skill 正文中显式写死。
- 发布面同步覆盖 [m/plugins/iasi/README.md](m/plugins/iasi/README.md)、[m/README.md](m/README.md)、[m/plugins/iasi/.github/plugin/plugin.json](m/plugins/iasi/.github/plugin/plugin.json)、[m/.github/plugin/marketplace.json](m/.github/plugin/marketplace.json) 和 [m/plugins/iasi/CHANGELOG.md](m/plugins/iasi/CHANGELOG.md)。
- 版本号默认从 `5.5.0` 升到 `5.6.0`；如果执行时仓库中已存在更高未发布版本，则基于最新版本做一致性递增。

## 输入工件

- 已批准设计文档：[docs/specs/2026-05-18-cleanup-skill-design.md](docs/specs/2026-05-18-cleanup-skill-design.md)
- 邻近实现参考：[m/plugins/iasi/skills/handoff/SKILL.md](m/plugins/iasi/skills/handoff/SKILL.md)
- 当前插件清单文档：[m/plugins/iasi/README.md](m/plugins/iasi/README.md)、[m/README.md](m/README.md)
- 当前发布元数据：[m/plugins/iasi/.github/plugin/plugin.json](m/plugins/iasi/.github/plugin/plugin.json)、[m/.github/plugin/marketplace.json](m/.github/plugin/marketplace.json)
- 当前变更记录：[m/plugins/iasi/CHANGELOG.md](m/plugins/iasi/CHANGELOG.md)

## 文件结构与职责

- Create: [m/plugins/iasi/skills/cleanup/SKILL.md](m/plugins/iasi/skills/cleanup/SKILL.md)
  - 定义 `cleanup` 的 frontmatter、触发描述、核心职责、硬约束、知识层分工、资格门、正常/强制 cleanup 流程、输出摘要与风险提示。
- Modify: [m/plugins/iasi/README.md](m/plugins/iasi/README.md)
  - 更新资产清单、结构树、使用说明和当前边界，将插件中的 skill 数量从 3 调整为 4，并加入 `cleanup` 的定位说明。
- Modify: [m/README.md](m/README.md)
  - 更新 marketplace 总览和验证说明，使其列出 `cleanup` skill。
- Modify: [m/plugins/iasi/.github/plugin/plugin.json](m/plugins/iasi/.github/plugin/plugin.json)
  - 更新 description、keywords 和 version，使 published metadata 反映新增 `cleanup` skill。
- Modify: [m/.github/plugin/marketplace.json](m/.github/plugin/marketplace.json)
  - 更新 `iasi` 插件条目的 description 和 version，保持 marketplace 展示一致。
- Modify: [m/plugins/iasi/CHANGELOG.md](m/plugins/iasi/CHANGELOG.md)
  - 追加新版本条目，记录 `cleanup` skill 新增、README/metadata 同步与版本递增。

编辑约束说明：

- [m/plugins/iasi/README.md](m/plugins/iasi/README.md) 和 [m/plugins/iasi/CHANGELOG.md](m/plugins/iasi/CHANGELOG.md) 在当前工具链里可能以 notebook-backed markdown 打开；若文本 patch 失败、出现 notebook 提示或文件被写成 0 字节，执行者要立即切换到 notebook-aware 编辑方式或 PowerShell UTF-8 fallback，并在同一步完成 read-back 验证。
- 当前工作区的 markdown 文件在 Windows 上存在被 `apply_patch` 截断为 0 字节的已知风险。对新增/修改的 markdown，第一次写入后必须立即做文件大小和 read-back 验证。
- 本次不引入额外 `references/` 文件，除非在实现过程中确认 `cleanup` 的固定输出块已经无法在单文件 prompt 中清晰维护；在未出现这个证据前，不做额外拆分。

## 任务清单

### Task 1: 建立 cleanup skill 文件与单文件 prompt 骨架

- 目标：创建 `cleanup` skill 的单文件实现，并把设计文档中的关键边界完整编码进 prompt。
- 涉及文件：[m/plugins/iasi/skills/cleanup/SKILL.md](m/plugins/iasi/skills/cleanup/SKILL.md)
- 验证命令：
  - `Get-Item "m/plugins/iasi/skills/cleanup/SKILL.md" | Select-Object Length,LastWriteTime | Format-List`
  - `Get-Content "m/plugins/iasi/skills/cleanup/SKILL.md" -TotalCount 260`
  - `rg -n "硬触发|软提醒|反触发|资格门|强制 cleanup|用户记忆默认不写|正式工件更新" "m/plugins/iasi/skills/cleanup/SKILL.md"`
- 预期结果：
  - 新文件存在且非空。
  - frontmatter 至少包含 `name: cleanup` 和与设计一致的描述语义。
  - 正文明确区分 `handoff`、正式工件更新和 `cleanup` 三者职责。
  - 正文包含保守触发模型、资格门、正常 cleanup、强制 cleanup 和默认不写用户记忆的约束。
- [ ] Step 1: 创建 [m/plugins/iasi/skills/cleanup/SKILL.md](m/plugins/iasi/skills/cleanup/SKILL.md) 并写入 frontmatter、定位说明和核心原则。
- [ ] Step 2: 按设计文档写入“何时使用 / 不要路由 / 硬约束 / 知识层分工 / 触发模型 / 资格门 / 执行流程 / 强制 cleanup 权限边界”。
- [ ] Step 3: 在 skill 中显式写入“正式工件更新不算 cleanup”和“强制 cleanup 默认不写用户记忆”。
- [ ] Step 4: 第一次写入后立即做文件大小和 read-back 验证；若文件被截断或出现 notebook 提示，立刻在本任务内切换编辑策略并恢复。

### Task 2: 校准 cleanup 与 handoff 的邻接边界

- 目标：确保新增 `cleanup` skill 不会和现有 `handoff` skill 的职责、触发意图和用户话术发生明显重叠。
- 涉及文件：[m/plugins/iasi/skills/cleanup/SKILL.md](m/plugins/iasi/skills/cleanup/SKILL.md)、[m/plugins/iasi/skills/handoff/SKILL.md](m/plugins/iasi/skills/handoff/SKILL.md)
- 验证命令：
  - `rg -n "新开 chat|继续做|handoff|cleanup|交接|长期知识|普通总结" "m/plugins/iasi/skills/cleanup/SKILL.md" "m/plugins/iasi/skills/handoff/SKILL.md"`
  - 如可用，再对 [m/plugins/iasi/skills/cleanup/SKILL.md](m/plugins/iasi/skills/cleanup/SKILL.md) 运行编辑器诊断检查。
- 预期结果：
  - `cleanup` 明确把“新开 chat 接着做”这类请求归为 `handoff` 适用范围。
  - `cleanup` 明确拒绝把普通总结、状态同步和实现中途文档编辑当作 cleanup。
  - 没有出现“handoff 也负责长期沉淀”或“cleanup 也负责中途续接”的冲突表述。
- [ ] Step 1: 对照 [m/plugins/iasi/skills/handoff/SKILL.md](m/plugins/iasi/skills/handoff/SKILL.md) 核对 `cleanup` 的“何时使用 / 不要路由”两节，清掉会和 handoff 抢路由的措辞。
- [ ] Step 2: 在 `cleanup` 中补足反触发语义和风险提示话术，使“继续做”和“最终沉淀”边界可执行。
- [ ] Step 3: 搜索两份 skill，确认没有自相矛盾或职责串位的表述。
- [ ] Step 4: 若本任务发现 `cleanup` 仍依赖额外模板才能清晰表达，再决定是否在后续任务中最小新增 `references/` 文件；若无硬证据，不新增。

### Task 3: 同步插件与 marketplace 文档清单

- 目标：让用户可见文档准确反映 `cleanup` skill 已成为插件 published surface 的一部分。
- 涉及文件：[m/plugins/iasi/README.md](m/plugins/iasi/README.md)、[m/README.md](m/README.md)
- 验证命令：
  - `rg -n "cleanup|4 个 skill|4 个 skills|四个 skill|brainstorming|handoff|writing-plans" "m/plugins/iasi/README.md" "m/README.md"`
  - `rg -n "3 个 skill|three published skills|three reusable skills" "m/plugins/iasi/README.md" "m/README.md"`
- 预期结果：
  - 插件 README 的资产列表、结构树、使用方式和当前边界都包含 `cleanup`。
  - marketplace README 的插件总览和验证步骤包含 `cleanup`。
  - 不再残留“3 个 skill / three reusable skills”这一类旧计数描述。
- [ ] Step 1: 更新 [m/plugins/iasi/README.md](m/plugins/iasi/README.md) 的资产清单、技能说明、结构树和当前边界计数。
- [ ] Step 2: 在 [m/plugins/iasi/README.md](m/plugins/iasi/README.md) 的使用方式中补充 `/cleanup` 调用和其与 `handoff` 的分工说明。
- [ ] Step 3: 更新 [m/README.md](m/README.md) 的插件包含内容和验证列表，使其列出 `cleanup`。
- [ ] Step 4: 搜索两份 README，清理残留的旧 skill 计数或缺失的 `cleanup` 引用。

### Task 4: 同步发布元数据与变更记录

- 目标：让 plugin manifest、marketplace entry 和 changelog 与新增 `cleanup` skill 的 published surface 一致。
- 涉及文件：[m/plugins/iasi/.github/plugin/plugin.json](m/plugins/iasi/.github/plugin/plugin.json)、[m/.github/plugin/marketplace.json](m/.github/plugin/marketplace.json)、[m/plugins/iasi/CHANGELOG.md](m/plugins/iasi/CHANGELOG.md)
- 验证命令：
  - `Get-Content "m/plugins/iasi/.github/plugin/plugin.json" | ConvertFrom-Json | Out-Null`
  - `Get-Content "m/.github/plugin/marketplace.json" | ConvertFrom-Json | Out-Null`
  - `rg -n "5\.6\.0|cleanup|four reusable skills|4 个 skill|4 个 skills" "m/plugins/iasi/.github/plugin/plugin.json" "m/.github/plugin/marketplace.json" "m/plugins/iasi/CHANGELOG.md"`
- 预期结果：
  - 两个 JSON 文件都能成功解析。
  - `plugin.json` 与 `marketplace.json` 的 description 和 version 一致反映新增 `cleanup` skill 后的 published surface。
  - changelog 追加了对应版本条目，并说明新增 `cleanup` 以及 README/metadata 同步。
- [ ] Step 1: 确认版本号递增策略，默认将插件版本从 `5.5.0` 提升到 `5.6.0`。
- [ ] Step 2: 更新 [m/plugins/iasi/.github/plugin/plugin.json](m/plugins/iasi/.github/plugin/plugin.json) 的 description、keywords 和 version，使其反映 4 个 skills。
- [ ] Step 3: 更新 [m/.github/plugin/marketplace.json](m/.github/plugin/marketplace.json) 中 `iasi` 条目的 description 和 version。
- [ ] Step 4: 在 [m/plugins/iasi/CHANGELOG.md](m/plugins/iasi/CHANGELOG.md) 追加新版本条目，记录 `cleanup` skill 新增与文档/元数据同步。
- [ ] Step 5: 解析两个 JSON 并核对版本一致性；若任一解析失败，先在本任务内修复。

### Task 5: 做一次收口验证与发布面审计

- 目标：在不跑仓库级构建的前提下，确认新增 skill、文档和发布面描述彼此一致，且所有被修改的 markdown/json 文件都未被截断。
- 涉及文件：[m/plugins/iasi/skills/cleanup/SKILL.md](m/plugins/iasi/skills/cleanup/SKILL.md)、[m/plugins/iasi/README.md](m/plugins/iasi/README.md)、[m/README.md](m/README.md)、[m/plugins/iasi/.github/plugin/plugin.json](m/plugins/iasi/.github/plugin/plugin.json)、[m/.github/plugin/marketplace.json](m/.github/plugin/marketplace.json)、[m/plugins/iasi/CHANGELOG.md](m/plugins/iasi/CHANGELOG.md)
- 验证命令：
  - `rg -n "cleanup|4 个 skill|four reusable skills|5\.6\.0" "m/plugins/iasi/skills/cleanup/SKILL.md" "m/plugins/iasi/README.md" "m/README.md" "m/plugins/iasi/.github/plugin/plugin.json" "m/.github/plugin/marketplace.json" "m/plugins/iasi/CHANGELOG.md"`
  - `rg -n "3 个 skill|three reusable skills" "m/plugins/iasi/README.md" "m/README.md" "m/plugins/iasi/.github/plugin/plugin.json" "m/.github/plugin/marketplace.json"`
  - `Get-Item "m/plugins/iasi/skills/cleanup/SKILL.md","m/plugins/iasi/README.md","m/plugins/iasi/CHANGELOG.md" | Select-Object Name,Length | Format-Table -AutoSize`
  - 如可用，对上述文件运行编辑器 diagnostics 检查。
- 预期结果：
  - 不再存在旧的 3-skill 文案。
  - 所有 markdown 文件都非空，且 skill/README/changelog 的描述与 metadata 版本一致。
  - 手动查看时，`cleanup` 的定位清晰，不与 `handoff`、`brainstorming` 或 `writing-plans` 混淆。
- [ ] Step 1: 搜索所有已改文件，清掉残留的旧 skill 计数和遗漏的 `cleanup` surface 描述。
- [ ] Step 2: 检查被改动的 markdown 文件长度，防止 0 字节或异常截断漏过。
- [ ] Step 3: 对已改文件做一次 diagnostics 检查；如有本次引入的问题，立即在当前任务内修复。
- [ ] Step 4: 输出最终修改摘要，明确新增了哪些资产、同步了哪些发布面、保留了哪些既有边界。

## 执行纪律

- 开始实现前，先批判性复查本计划；如果发现文件范围、版本号或验证命令与仓库现实不符，先修计划再动手。
- 严格按任务顺序执行，不要把 skill prompt 编写、README 同步和 metadata 递增混成一个不可验证的大步骤。
- 每个任务完成后都运行该任务定义的验证；验证失败时，先在当前任务内修复，不要跳到后面的任务碰运气。
- 对新增或修改的 markdown 文件，第一次写入后必须立即做文件大小和 read-back 验证；一旦出现 0 字节或 notebook-backed 编辑问题，立刻停在当前任务修复。
- 如果当前就在 `main` 或 `master`，且用户没有明确同意，开始实现前先确认。
- 全部任务完成后，再做收口验证并输出修改摘要。

## 最终验证

- 读取 [m/plugins/iasi/skills/cleanup/SKILL.md](m/plugins/iasi/skills/cleanup/SKILL.md) 前 260 行，人工核对 frontmatter、触发模型、资格门、正常/强制 cleanup 流程和“用户记忆默认不写”约束均已落盘。
- 运行以下 JSON 解析检查：
  - `Get-Content "m/plugins/iasi/.github/plugin/plugin.json" | ConvertFrom-Json | Out-Null`
  - `Get-Content "m/.github/plugin/marketplace.json" | ConvertFrom-Json | Out-Null`
- 运行以下搜索审计：
  - `rg -n "cleanup|5\.6\.0|4 个 skill|four reusable skills" "m/plugins/iasi/skills/cleanup/SKILL.md" "m/plugins/iasi/README.md" "m/README.md" "m/plugins/iasi/.github/plugin/plugin.json" "m/.github/plugin/marketplace.json" "m/plugins/iasi/CHANGELOG.md"`
  - `rg -n "3 个 skill|three reusable skills" "m/plugins/iasi/README.md" "m/README.md" "m/plugins/iasi/.github/plugin/plugin.json" "m/.github/plugin/marketplace.json"`
- 运行文件长度检查：
  - `Get-Item "m/plugins/iasi/skills/cleanup/SKILL.md","m/plugins/iasi/README.md","m/plugins/iasi/CHANGELOG.md" | Select-Object Name,Length | Format-Table -AutoSize`
- 如编辑器 diagnostics 可用，再对所有已修改文件运行一次 diagnostics 检查。
- 手动结果预期：插件 README、marketplace README、plugin metadata、marketplace metadata 与 changelog 一致反映 `cleanup` 已成为已发布的第四个 skill；其定位明确是终态长期知识沉淀，而不是中途续接或普通总结。