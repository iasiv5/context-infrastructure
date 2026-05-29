# 实施计划：openbmc-aware-harness 种子态迁移与第一轮收敛

- **日期**：2026-05-29
- **设计文档**：docs/specs/2026-05-29-openbmc-aware-harness-design.md
- **状态**：待执行

---

## 目标

在 openbmc-aware-harness 内落出第一版可工作的 OpenBMC 专用 context 仓库骨架，执行“先高保真种子迁移，再做第一轮收敛”的路线。

这份计划只覆盖第一版落仓工作，不覆盖后续功能扩展、periodic_jobs 回归或 tools 体系重建。

## 架构快照

- **总体策略**：先把启动链路、rules、关键 docs 和 OBSERVATIONS 迁移到 openbmc-aware-harness，再逐步把核心 rules 和入口文档收敛为 OpenBMC 语境。
- **边界约束**：第一版不引入 periodic_jobs，不整体迁移 tools，不搬运历史 specs 和 plans 内容；只保留空的 adhoc_jobs 作为未来临时任务落点。
- **验证原则**：先做静态一致性校验，再做一次真实 Copilot 启动 smoke run，确认新仓会带路且不串回父仓库。

## 输入工件

- 已批准设计：docs/specs/2026-05-29-openbmc-aware-harness-design.md
- 用户补充约束：第一版排除 periodic_jobs 与 tools；docs 只直迁 docs/SKILL_ECOSYSTEM.md；contexts 只直迁 contexts/memory/OBSERVATIONS.md；adhoc_jobs 先保留空目录。

## 文件结构与职责

| 操作 | 文件路径 | 职责 |
|------|---------|------|
| 创建 | openbmc-aware-harness/.github/ | 放置 GitHub Copilot 入口文件 |
| 创建 | openbmc-aware-harness/.github/copilot-instructions.md | 把会话入口导向目标仓自己的 AGENTS.md |
| 创建 | openbmc-aware-harness/AGENTS.md | 目标仓的根路由与启动读取入口 |
| 创建 | openbmc-aware-harness/CLAUDE.md | 兼容 Claude 类入口，继续转发到 AGENTS.md |
| 创建 | openbmc-aware-harness/README.md | 目标仓公开说明与定位 |
| 创建 | openbmc-aware-harness/setup_guide.md | 目标仓初始化与上手路径 |
| 创建 | openbmc-aware-harness/rules/ | 第一版最关键知识资产的完整种子拷贝 |
| 修改 | openbmc-aware-harness/rules/SOUL.md | 保留教义主体，改成 OpenBMC 工程助手语境 |
| 修改 | openbmc-aware-harness/rules/USER.md | 去掉 iasi 私人画像，改成 OpenBMC 团队共享对象 |
| 修改 | openbmc-aware-harness/rules/WORKSPACE.md | 改为 OpenBMC 仓内目录路由，不再引用父仓个人资产 |
| 修改 | openbmc-aware-harness/rules/COMMUNICATION.md | 仅保留与 OpenBMC 协作仍相关的表达规范 |
| 修改 | openbmc-aware-harness/rules/skills/INDEX.md | 收敛成第一版仍保留的 OpenBMC 相关技能索引 |
| 创建 | openbmc-aware-harness/docs/SKILL_ECOSYSTEM.md | 保留技能生态说明入口 |
| 创建 | openbmc-aware-harness/docs/specs/.gitkeep | 为后续设计文档保留空目录 |
| 创建 | openbmc-aware-harness/docs/plans/.gitkeep | 为后续计划文档保留空目录 |
| 创建 | openbmc-aware-harness/docs/working.md | 记录 rules 与入口文件的逐文件审视台账 |
| 创建 | openbmc-aware-harness/contexts/memory/OBSERVATIONS.md | 保留共享观察入口 |
| 创建 | openbmc-aware-harness/adhoc_jobs/.gitkeep | 为一次性调试与验证任务保留空目录 |
| 保持不变 | openbmc-aware-harness/LICENSE | 维持目标仓当前许可证文件 |

## 任务清单

### Task 1: 建立基线与停机条件

**目标**：确认目标仓当前状态、分支和缺失项，避免在错误分支或错误基线上开工。

**涉及文件**：openbmc-aware-harness/

**命令**：

```raw
git -C "d:\_context-infrastructure\openbmc-aware-harness" status --short --branch
Get-ChildItem "d:\_context-infrastructure\openbmc-aware-harness" -Force
Test-Path "d:\_context-infrastructure\openbmc-aware-harness\AGENTS.md"
Test-Path "d:\_context-infrastructure\openbmc-aware-harness\rules\SOUL.md"
Test-Path "d:\_context-infrastructure\openbmc-aware-harness\periodic_jobs"
Test-Path "d:\_context-infrastructure\openbmc-aware-harness\tools"
```

**验证**：

- 当前分支和工作树状态已经明确。
- AGENTS.md 和 rules/SOUL.md 在执行前应当不存在。
- periodic_jobs 和 tools 在目标仓中应当不存在。
- 如果当前分支是 main 或 master，且用户没有明确同意直接在该分支实现，先停下确认。

---

### Task 2: 创建第一版目录骨架与可追踪空目录

**目标**：先把第一版确定需要的目录骨架搭起来，并让空目录能被 Git 跟踪。

**涉及文件**：

- openbmc-aware-harness/.github/
- openbmc-aware-harness/docs/specs/.gitkeep
- openbmc-aware-harness/docs/plans/.gitkeep
- openbmc-aware-harness/adhoc_jobs/.gitkeep

**命令**：

```raw
New-Item -ItemType Directory -Force -Path "d:\_context-infrastructure\openbmc-aware-harness\.github"
New-Item -ItemType Directory -Force -Path "d:\_context-infrastructure\openbmc-aware-harness\docs"
New-Item -ItemType Directory -Force -Path "d:\_context-infrastructure\openbmc-aware-harness\docs\specs"
New-Item -ItemType Directory -Force -Path "d:\_context-infrastructure\openbmc-aware-harness\docs\plans"
New-Item -ItemType Directory -Force -Path "d:\_context-infrastructure\openbmc-aware-harness\contexts"
New-Item -ItemType Directory -Force -Path "d:\_context-infrastructure\openbmc-aware-harness\contexts\memory"
New-Item -ItemType Directory -Force -Path "d:\_context-infrastructure\openbmc-aware-harness\adhoc_jobs"
New-Item -ItemType File -Force -Path "d:\_context-infrastructure\openbmc-aware-harness\docs\specs\.gitkeep"
New-Item -ItemType File -Force -Path "d:\_context-infrastructure\openbmc-aware-harness\docs\plans\.gitkeep"
New-Item -ItemType File -Force -Path "d:\_context-infrastructure\openbmc-aware-harness\adhoc_jobs\.gitkeep"
```

**验证**：

```raw
Get-ChildItem "d:\_context-infrastructure\openbmc-aware-harness" -Force
Test-Path "d:\_context-infrastructure\openbmc-aware-harness\docs\specs\.gitkeep"
Test-Path "d:\_context-infrastructure\openbmc-aware-harness\docs\plans\.gitkeep"
Test-Path "d:\_context-infrastructure\openbmc-aware-harness\adhoc_jobs\.gitkeep"
```

预期结果：上面三个 .gitkeep 全为 True，且没有顺手创建出 periodic_jobs 或 tools。

---

### Task 3: 复制入口文件、共享文档和 OBSERVATIONS

**目标**：先把启动链路和关键共享文档带进目标仓，保证第一版有可运行入口。

**涉及文件**：

- openbmc-aware-harness/AGENTS.md
- openbmc-aware-harness/CLAUDE.md
- openbmc-aware-harness/.github/copilot-instructions.md
- openbmc-aware-harness/README.md
- openbmc-aware-harness/setup_guide.md
- openbmc-aware-harness/docs/SKILL_ECOSYSTEM.md
- openbmc-aware-harness/contexts/memory/OBSERVATIONS.md

**命令**：

```raw
Copy-Item "d:\_context-infrastructure\AGENTS.md" "d:\_context-infrastructure\openbmc-aware-harness\AGENTS.md" -Force
Copy-Item "d:\_context-infrastructure\CLAUDE.md" "d:\_context-infrastructure\openbmc-aware-harness\CLAUDE.md" -Force
Copy-Item "d:\_context-infrastructure\.github\copilot-instructions.md" "d:\_context-infrastructure\openbmc-aware-harness\.github\copilot-instructions.md" -Force
Copy-Item "d:\_context-infrastructure\README.md" "d:\_context-infrastructure\openbmc-aware-harness\README.md" -Force
Copy-Item "d:\_context-infrastructure\setup_guide.md" "d:\_context-infrastructure\openbmc-aware-harness\setup_guide.md" -Force
Copy-Item "d:\_context-infrastructure\docs\SKILL_ECOSYSTEM.md" "d:\_context-infrastructure\openbmc-aware-harness\docs\SKILL_ECOSYSTEM.md" -Force
Copy-Item "d:\_context-infrastructure\contexts\memory\OBSERVATIONS.md" "d:\_context-infrastructure\openbmc-aware-harness\contexts\memory\OBSERVATIONS.md" -Force
```

**验证**：

```raw
Get-Item "d:\_context-infrastructure\openbmc-aware-harness\AGENTS.md", "d:\_context-infrastructure\openbmc-aware-harness\CLAUDE.md", "d:\_context-infrastructure\openbmc-aware-harness\.github\copilot-instructions.md", "d:\_context-infrastructure\openbmc-aware-harness\README.md", "d:\_context-infrastructure\openbmc-aware-harness\setup_guide.md", "d:\_context-infrastructure\openbmc-aware-harness\docs\SKILL_ECOSYSTEM.md", "d:\_context-infrastructure\openbmc-aware-harness\contexts\memory\OBSERVATIONS.md" | Select-Object FullName, Length
```

预期结果：所有文件长度都大于 0。

---

### Task 4: 复制完整 rules 树并形成种子态快照

**目标**：把最关键的知识资产整体带进目标仓，先保证原始教义完整落地，再进入逐文件审视。

**涉及文件**：openbmc-aware-harness/rules/**

**命令**：

```raw
Copy-Item "d:\_context-infrastructure\rules\*" "d:\_context-infrastructure\openbmc-aware-harness\rules" -Recurse -Force
```

**验证**：

```raw
Test-Path "d:\_context-infrastructure\openbmc-aware-harness\rules\SOUL.md"
Test-Path "d:\_context-infrastructure\openbmc-aware-harness\rules\USER.md"
Test-Path "d:\_context-infrastructure\openbmc-aware-harness\rules\WORKSPACE.md"
Test-Path "d:\_context-infrastructure\openbmc-aware-harness\rules\COMMUNICATION.md"
Test-Path "d:\_context-infrastructure\openbmc-aware-harness\rules\skills\INDEX.md"
Get-ChildItem "d:\_context-infrastructure\openbmc-aware-harness\rules" -Recurse -File | Measure-Object
```

预期结果：5 个核心文件均存在，且 rules 文件总数大于 5。

**可选 checkpoint commit**：在这一任务完成后，可以提交一次“seed context skeleton”快照，便于后续收敛阶段做 diff。

---

### Task 5: 建立启动关键文件的审视台账

**目标**：先把所有启动关键文件的处置结论写成一张表，避免边改边忘。

**涉及文件**：

- openbmc-aware-harness/docs/working.md
- openbmc-aware-harness/AGENTS.md
- openbmc-aware-harness/.github/copilot-instructions.md
- openbmc-aware-harness/rules/SOUL.md
- openbmc-aware-harness/rules/USER.md
- openbmc-aware-harness/rules/WORKSPACE.md
- openbmc-aware-harness/rules/COMMUNICATION.md
- openbmc-aware-harness/rules/skills/INDEX.md

**修改内容**：

- 在 openbmc-aware-harness/docs/working.md 建一张台账表，至少包含 4 列：文件路径、处置结论、理由、后续动作。
- 先覆盖 7 个启动关键文件：AGENTS.md、.github/copilot-instructions.md、rules/SOUL.md、rules/USER.md、rules/WORKSPACE.md、rules/COMMUNICATION.md、rules/skills/INDEX.md。
- 处置结论只允许写成“原样保留”“局部改写”“暂不保留”三种之一。

**验证**：

```raw
Select-String -Path "d:\_context-infrastructure\openbmc-aware-harness\docs\working.md" -Pattern "AGENTS.md|copilot-instructions.md|rules/SOUL.md|rules/USER.md|rules/WORKSPACE.md|rules/COMMUNICATION.md|rules/skills/INDEX.md"
```

预期结果：7 个启动关键文件都能在台账里找到且只出现一次。

---

### Task 6: 扩展审视到剩余 rules 子树

**目标**：把 rules 下剩余文件逐个归类，不让后续收敛工作留盲区。

**涉及文件**：

- openbmc-aware-harness/rules/axioms/**
- openbmc-aware-harness/rules/skills/**
- openbmc-aware-harness/docs/working.md

**修改内容**：

- 继续在 openbmc-aware-harness/docs/working.md 中追加剩余 rules 文件的处置结果。
- 对每个文件写明保留、局部改写或暂不保留的理由。
- 对会影响第一版启动链路或 OpenBMC 语境的文件，明确标记为“本轮必须处理”。

**验证**：

```raw
$root = Resolve-Path "d:\_context-infrastructure\openbmc-aware-harness"
$ledger = Get-Content "$($root.Path)\docs\working.md" -Raw
Get-ChildItem "$($root.Path)\rules" -Recurse -File | ForEach-Object {
  $relative = $_.FullName.Substring($root.Path.Length + 1).Replace('\\','/')
  if (-not $ledger.Contains($relative)) {
    Write-Output "MISSING $relative"
  }
}
```

预期结果：没有任何输出；只要出现 MISSING，就说明还有 rules 文件没被纳入台账。

---

### Task 7: 第一轮 OpenBMC 化修改核心 rules

**目标**：在保留原始教义主体的前提下，把最关键的 rules 改成 OpenBMC 团队共享仓语境。

**涉及文件**：

- openbmc-aware-harness/rules/SOUL.md
- openbmc-aware-harness/rules/USER.md
- openbmc-aware-harness/rules/WORKSPACE.md
- openbmc-aware-harness/rules/COMMUNICATION.md
- openbmc-aware-harness/rules/skills/INDEX.md

**修改内容**：

- rules/USER.md：去掉 iasi 私人画像，改成 OpenBMC 固件开发者或团队共享用户画像。
- rules/WORKSPACE.md：把目录路由改成 openbmc-aware-harness 内部结构，不再引用父仓的文章归档、增长分析或个人知识目录。
- rules/skills/INDEX.md：收敛成第一版仍保留且与 OpenBMC 开发相关的 skill 索引。
- rules/SOUL.md 与 rules/COMMUNICATION.md：保留普适教义和表达原则，仅改掉与当前目标冲突的部分。

**验证**：

```raw
Select-String -Path "d:\_context-infrastructure\openbmc-aware-harness\rules\USER.md", "d:\_context-infrastructure\openbmc-aware-harness\rules\WORKSPACE.md", "d:\_context-infrastructure\openbmc-aware-harness\rules\skills\INDEX.md" -Pattern "OpenBMC|BMC|firmware"
Select-String -Path "d:\_context-infrastructure\openbmc-aware-harness\rules\USER.md", "d:\_context-infrastructure\openbmc-aware-harness\rules\WORKSPACE.md", "d:\_context-infrastructure\openbmc-aware-harness\rules\skills\INDEX.md" -Pattern "iasi|公众号|Typefully|GA4|kit_metrics|periodic_jobs|ai_heartbeat"
```

预期结果：第一条命令能命中 OpenBMC 相关表述；第二条命令不应再命中与父仓个人运营或已排除能力相关的表述。

---

### Task 8: 修订入口文件并清除陈旧引用

**目标**：让目标仓入口文件与真实结构对齐，不再误导 agent 读到父仓路径或已排除能力。

**涉及文件**：

- openbmc-aware-harness/AGENTS.md
- openbmc-aware-harness/.github/copilot-instructions.md
- openbmc-aware-harness/CLAUDE.md
- openbmc-aware-harness/README.md
- openbmc-aware-harness/setup_guide.md

**修改内容**：

- AGENTS.md：保留启动读取机制，但把说明改成目标仓自己的目录和能力边界。
- .github/copilot-instructions.md：继续强制先读目标仓 AGENTS.md，不再引用父仓状态。
- CLAUDE.md：继续做最小转发，不引入额外规则。
- README.md 与 setup_guide.md：删除 periodic_jobs、tools 和父仓运营资产相关描述，改成 OpenBMC 专用 context 仓定位。

**验证**：

```raw
Select-String -Path "d:\_context-infrastructure\openbmc-aware-harness\AGENTS.md", "d:\_context-infrastructure\openbmc-aware-harness\.github\copilot-instructions.md", "d:\_context-infrastructure\openbmc-aware-harness\CLAUDE.md", "d:\_context-infrastructure\openbmc-aware-harness\README.md", "d:\_context-infrastructure\openbmc-aware-harness\setup_guide.md" -Pattern "periodic_jobs|ai_heartbeat|tools/|Typefully|GA4|share_report|d:\\_context-infrastructure|\.\./"
Select-String -Path "d:\_context-infrastructure\openbmc-aware-harness\AGENTS.md" -Pattern "rules/SOUL.md|rules/USER.md|rules/WORKSPACE.md|rules/COMMUNICATION.md|rules/skills/INDEX.md"
```

预期结果：第一条命令无输出；第二条命令能命中 5 个启动读取目标。

**可选 checkpoint commit**：在这一任务完成后，可以提交一次“retarget core docs and rules”快照，作为第一轮收敛完成点。

---

### Task 9: 做硬一致性校验与真实 smoke run

**目标**：确认第一版仓库已经具备自洽的启动链路和正确的能力边界。

**涉及文件**：整个 openbmc-aware-harness 仓库

**命令**：

```raw
$root = "d:\_context-infrastructure\openbmc-aware-harness"
$required = @(
  "AGENTS.md",
  "CLAUDE.md",
  ".github/copilot-instructions.md",
  "README.md",
  "setup_guide.md",
  "rules/SOUL.md",
  "rules/USER.md",
  "rules/WORKSPACE.md",
  "rules/COMMUNICATION.md",
  "rules/skills/INDEX.md",
  "docs/SKILL_ECOSYSTEM.md",
  "docs/specs/.gitkeep",
  "docs/plans/.gitkeep",
  "docs/working.md",
  "contexts/memory/OBSERVATIONS.md",
  "adhoc_jobs/.gitkeep"
)
$required | ForEach-Object {
  [PSCustomObject]@{
    Path = $_
    Exists = Test-Path (Join-Path $root $_)
  }
}
Test-Path "$root\periodic_jobs"
Test-Path "$root\tools"
git -C "$root" status --short
```

**手动 smoke run**：

- 用 openbmc-aware-harness 作为当前工作区根目录，打开一个新的 GitHub Copilot 会话。
- 观察启动时是否先读取目标仓的 AGENTS.md 和 5 个核心 rules 文件。
- 在新会话里发一个最小问题，例如“当前仓库的启动读取链是什么？”，确认回答基于目标仓而不是父仓。

**验证**：

- 上述 required 清单全部为 Exists = True。
- periodic_jobs 和 tools 的检测结果都为 False。
- git status 只包含预期文件改动。
- 手动 smoke run 中不再出现父仓路径泄漏或已排除能力的引用。

---

## 执行纪律

- 开始实现前，先批判性复查整份计划；如果发现缺项、矛盾、命名不一致或验证命令无效，先修计划。
- 按任务顺序执行，不要无声跳步、合并步或改变任务目标。
- 每完成一个任务，都运行该任务定义的验证。
- 遇到阻塞、重复失败或计划与仓库现实不符，立即停下来说明，不要猜。
- 如果当前就在 main 或 master，且用户没有明确同意，开始实现前先确认。
- 全部任务完成后，运行最终验证并输出修改摘要。

## 最终验证

1. 运行 Task 9 的静态清单检查，确认第一版所需文件全部在位，且 periodic_jobs 与 tools 没有误入目标仓。
2. 运行 Task 9 的 git status 检查，确认只包含计划内文件变动。
3. 做一次新的 GitHub Copilot 会话 smoke run，确认启动读取链已经完全切换到 openbmc-aware-harness。
4. 输出一份简短执行摘要，至少包含：新增文件、修改文件、未纳入第一版的能力，以及后续可选扩展项。