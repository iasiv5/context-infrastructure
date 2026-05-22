# OPSX 流程说明（基于 OpenSpec v1.2.0）

## 1. 文档目的

本说明用于解释 `opsx` 在 OpenSpec v1.2.0 下的标准工作流、每个阶段的职责边界、常用命令与落地顺序，便于团队统一使用方式。

`opsx` 不是一个单命令，而是 4 个动作组成的端到端流程：

1. `opsx:explore`（探索）
2. `opsx:propose`（提案）
3. `opsx:apply`（实施）
4. `opsx:archive`（归档）

---

## 2. 一图看懂整体流程

```text
Idea / Problem
    |
    v
/opsx:explore
(澄清问题、查代码、评估方案；不实现业务代码)
    |
    | 需求与范围明确后
    v
/opsx:propose
(创建 change，生成 proposal/design/specs/tasks)
    |
    | artifacts 达到 apply-ready
    v
/opsx:apply
(按 tasks 实施代码并勾选任务)
    |
    | 任务完成
    v
/opsx:archive
(可选同步 specs，归档到 archive 目录)
```

---

## 3. 基础命令与目录约定

### 3.1 初始化与状态检查

```bash
openspec init
openspec list --json
openspec status --change "<change-name>" --json
```

### 3.2 典型目录结构（spec-driven）

- `openspec/changes/<change-name>/proposal.md`
- `openspec/changes/<change-name>/design.md`
- `openspec/changes/<change-name>/specs/<capability>/spec.md`
- `openspec/changes/<change-name>/tasks.md`

归档后路径：

- `openspec/changes/archive/YYYY-MM-DD-<change-name>/`

---

## 4. 各阶段详细说明

## 4.1 `opsx:explore`（探索阶段）

### 目标

- 讨论问题、澄清范围、比较方案、识别风险。
- 产出是“共识与方向”，不是代码实现。

### 可做

- 阅读代码与架构。
- 调研现有 change（如果存在）。
- 用 ASCII 图说明数据流、模块关系、方案对比。
- 在用户同意时，补充/更新 OpenSpec artifacts（记录思考结果）。

### 禁止

- 不写业务实现代码。
- 不自动进入 apply。

### 常用命令

```bash
openspec list --json
```

---

## 4.2 `opsx:propose`（提案阶段）

### 目标

把“想法”变成“可执行 change”，并达到 apply-ready。

### 标准步骤

1. 明确 change 名（kebab-case）或根据需求描述推导名称。
2. 创建 change 目录：

```bash
openspec new change "<name>"
```

3. 读取 artifact 依赖图：

```bash
openspec status --change "<name>" --json
```

4. 按依赖顺序生成 artifacts：

```bash
openspec instructions proposal --change "<name>" --json
openspec instructions design --change "<name>" --json
openspec instructions specs --change "<name>" --json
openspec instructions tasks --change "<name>" --json
```

5. 每生成一个 artifact 后重新检查 status，直到 `applyRequires` 全部 `done`。

### 关键原则

- 严格按 `instructions` 返回的 `template` 与 `instruction` 写内容。
- `context`/`rules` 是约束，不应原样复制进产物文件。

---

## 4.3 `opsx:apply`（实施阶段）

### 目标

按任务清单落地代码，持续更新 `tasks.md` 进度。

### 标准步骤

1. 选择 change。
2. 获取 schema 与当前状态：

```bash
openspec status --change "<name>" --json
```

3. 获取 apply 指令：

```bash
openspec instructions apply --change "<name>" --json
```

4. 读取 `contextFiles`（通常包含 proposal/specs/design/tasks）。
5. 逐项完成 pending task，并把 `- [ ]` 改为 `- [x]`。

### apply 常见状态分支

- `blocked`：前置 artifacts 缺失，需先补齐。
- `all_done`：任务全部完成，可进入归档。
- 其他状态：继续实施。

### 实施守则

- 变更最小化，严格按任务范围推进。
- 遇到不清晰任务、设计冲突或阻塞，暂停并反馈。

---

## 4.4 `opsx:archive`（归档阶段）

### 目标

把完成的 change 移入归档，形成可追溯历史。

### 标准步骤

1. 选择 change（应明确选择，不建议猜测）。
2. 检查 artifact 完成度：

```bash
openspec status --change "<name>" --json
```

3. 检查 `tasks.md` 是否还有 `- [ ]`。
4. 若存在 delta specs，评估是否同步主 specs。
5. 执行归档：

```bash
mkdir -p openspec/changes/archive
mv openspec/changes/<name> openspec/changes/archive/YYYY-MM-DD-<name>
```

### 注意点

- 有未完成项时可提示风险并由用户确认是否继续。
- 归档目录已存在同名目标时应报错并改用其他方案。

---

## 5. 阶段关系与常见误区

### 5.1 `explore` 不会自动调用 `propose`

- `explore` 负责探索和澄清。
- `propose` 是明确触发的提案动作。
- 只有用户确认后，才进入提案生成。

### 5.2 不是强制线性，但推荐主路径

理论上可以在 change 生命周期内交错操作（例如 apply 途中回改 artifacts），但团队协作建议主路径：

1. 先 explore
2. 再 propose
3. 再 apply
4. 最后 archive

### 5.3 `tasks.md` 是实施真相源

- 实施阶段以 `tasks.md` 为执行清单。
- 完成即勾选，保持进度可见、可审计。

---

## 6. 建议的团队实践

1. 每个 change 只解决一类明确问题，避免超范围。
2. `proposal` 写清动机与影响，`design` 写清取舍，`specs` 写可测试要求。
3. PR 评审时同时检查代码与 `tasks.md` 是否一致。
4. 归档前确认：功能完成、测试通过、文档同步。


[2026-02-28]