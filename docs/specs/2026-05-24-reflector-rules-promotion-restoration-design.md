# Reflector Rules Promotion Restoration 设计文档

Date: 2026-05-24
Status: Draft
Author: User + AI

## 背景与目标

- `periodic_jobs/ai_heartbeat/src/v0/reflector.py` 的原始语义是：reflector 读取 `contexts/memory/OBSERVATIONS.md`，把高价值观测按职责边界直接晋升到 `rules/` 下的真实目标文件，同时对 `OBSERVATIONS.md` 执行垃圾回收。
- 当前本地执行路径已经切到 `periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py`，但默认晋升口被收敛为单一文件 `rules/skills/ai_heartbeat_local_reflections.md`。这降低了运行风险，但已经偏离原始 reflector 的职责分配。
- 当前 `rules/skills/ai_heartbeat_local_reflections.md` 既不是真正的通用 skill 文档，也不在 `rules/skills/INDEX.md` 中登记，导致它占用了 skill 命名空间，却没有满足 skill 的可发现性和完整性要求。
- 这次设计的目标是：严格恢复原始 reflector.py 的精神，让 reflector 直接把规则晋升到真实规则面，同时保留当前本地 runner 的审计、回滚和状态记录能力。

成功标准：

- reflector 继续直接重写 `contexts/memory/OBSERVATIONS.md` 做 GC。
- reflector 不再把 `rules/skills/ai_heartbeat_local_reflections.md` 作为正式规则存储目标。
- reflector 将高价值规则直接写入真实规则文件：`rules/SOUL.md`、`rules/USER.md`、`rules/COMMUNICATION.md`、`rules/WORKSPACE.md`，以及真实 skill 文档；当现有 skill 没有合适承载位时，允许新建真实 skill 文档。
- 任何 skills 类晋升，只要触碰或新建真实 skill 文档，就必须同次更新 `rules/skills/INDEX.md`。
- `heartbeat_local_runner.py` 回到“触发器 + 审计器”角色，不再持有单一 promotion path 的设计中心。
- reflector 的失败仍然可回滚，且不会影响 allowlist 之外的用户未提交工作。

## 范围

- 修改 `periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py`，移除单一 `rules_promotion_path` 的中心设计。
- 修改 `periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md`，把晋升路由改成真实规则面路由约束。
- 修改 `periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md`，显式补充“skills 类晋升必须更新 `rules/skills/INDEX.md`”规则。
- 调整 reflector allowlist，使其覆盖真实规则目标文件、真实 skill 文档和 `rules/skills/INDEX.md`。
- 修改 reflector 的后置校验逻辑，使其校验真实规则面、skill 索引联动和 `OBSERVATIONS.md` 的 GC 结果。
- 调整现有测试，使其不再假设 `rules/skills/ai_heartbeat_local_reflections.md` 是唯一合法晋升目标。
- 清理或退役 `rules/skills/ai_heartbeat_local_reflections.md` 的正式职责。

## 非范围

- 不修改 observer 的职责边界或运行模式。
- 不修改 `.github/hooks/pre-session.ps1` 的入口交互和本地执行流程。
- 不引入新的长期状态数据库、审批工作流或人工审核队列。
- 不把 reflector 扩展成通用文档整理器或多阶段知识发布系统。
- 不在本次设计中重构整个 `rules/skills/` 体系。

## 方案比较

### 方案 A：保留 local_reflections 作为正式晋升目标

- 核心思路：沿用当前 `rules/skills/ai_heartbeat_local_reflections.md` 作为唯一规则晋升口，只增强说明和索引。
- 优点：实现最小，当前测试和回滚逻辑改动最少。
- 缺点：
  - 与原始 `reflector.py` 的真实规则晋升语义不一致。
  - 继续把 skill 命名空间用于非正式 skill 文档。
  - 即便补上 `INDEX.md`，也会把一个受控运行产物伪装成通用 skill。

### 方案 B：取消 local_reflections，直接晋升到真实规则面

- 核心思路：reflector 直接把规则写到真实目标文件；`OBSERVATIONS.md` 继续做 GC；runner 只负责触发、审计、回滚和状态记录。
- 优点：
  - 与原始 `reflector.py` 的职责划分最一致。
  - 规则最终落点与实际消费位置一致，不再引入中间汇总层。
  - `rules/skills/INDEX.md` 的索引语义恢复完整。
- 缺点：
  - allowlist 和后置校验会比当前单一路径更复杂。
  - 真实 skill 文档的创建、修改和索引联动需要更严格的验证。

### 方案 C：保留 local_reflections 作为 staging 层，再异步晋升到真实规则面

- 核心思路：reflector 先写 `local_reflections`，后续再由其他流程把其中内容搬运到真实规则文件。
- 优点：安全缓冲层更明显。
- 缺点：
  - 引入额外状态和第二条晋升链路。
  - 让规则真实落点与 reflector 完成时刻解耦，偏离原始设计。
  - 本次需求并未要求 staging 层，属于额外复杂度。

## 推荐方案

- 选择方案 B。
- 原因：本次目标是“严格按原始 reflector.py 的精神还原 reflector 机制”，而不是给当前本地实现做局部修补。方案 B 在语义上最直接，且不会继续在 `rules/skills/` 下维持一个不完整的伪 skill 产物。
- 主要 trade-offs：
  - 接受多目标 allowlist 和测试面扩大的复杂度，以换取规则晋升语义的正确性。
  - 接受 reflector 直接触碰真实规则文件的更高风险，以换取与原始设计一致的职责边界。
  - 放弃 staging 层的缓冲，要求 prompt 约束、校验和回滚机制更严格。

## 关键边界与组件职责

- `periodic_jobs/ai_heartbeat/src/v0/reflector.py`
  - 作为原始语义锚点：reflector 负责规则晋升和 `OBSERVATIONS.md` 的 GC。
  - 不需要恢复为实际执行入口，但其职责边界应被当前本地实现重新对齐。

- `periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py`
  - 保留职责：触发 reflector、记录状态、写运行日志、做后置验证、做失败回滚。
  - 删除职责：以单一路径 `rules_promotion_path` 约束 reflector 的正式落盘位置。
  - 新职责：验证真实规则面 touched files 是否完整、合法且在 allowlist 内。

- `periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md`
  - 明确 reflector 的真实路由规则，而不是单一路径输出。
  - 约束规则落点：
    - Agent 身份与核心价值观 → `rules/SOUL.md`
    - 用户画像与人生哲学 → `rules/USER.md`
    - 沟通风格 → `rules/COMMUNICATION.md`
    - 目录路由 → `rules/WORKSPACE.md`
    - 技术方法论、工作流、最佳实践 → 真实 skill 文档
  - 当现有 skill 没有合适承载位时，允许新建真实 skill 文档。
  - 只要触碰或新建真实 skill 文档，就必须同次更新 `rules/skills/INDEX.md`。

- `periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md`
  - 必须显式包含“skills 类晋升必须更新 `rules/skills/INDEX.md`”规则，使 SOP 与 runner 校验保持一致。

- `contexts/memory/OBSERVATIONS.md`
  - 始终是 reflector 的 GC 面。
  - reflector 声称完成晋升和 GC 后，runner 必须验证对应条目已被删除或收敛。

- `rules/skills/INDEX.md`
  - 是真实 skill 的索引入口。
  - 不再允许出现“触碰或新建真实 skill，但不更新索引”的不完整晋升。

- `periodic_jobs/ai_heartbeat/state/heartbeat_reflector_report.md`
  - 继续作为 reflector 的审计产物。
  - 负责记录 touched files、晋升摘要和 GC 摘要。
  - 不承担规则持久化职责。

- `rules/skills/ai_heartbeat_local_reflections.md`
  - 退役为正式晋升目标。
  - 直接删除，不保留迁移说明文件，也不再纳入 reflector 正式写入路径。

## 数据流 / 控制流

1. SessionStart hook 继续通过现有入口调用 `heartbeat_local_runner.py reflector ...`。
2. runner 准备 reflector 运行上下文，但不再传入单一 `rules_promotion_path` 作为正式目标。
3. reflector prompt 明确真实规则路由、skill 索引联动约束和 `OBSERVATIONS.md` GC 义务。
4. reflector 读取 `periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md`、`contexts/memory/OBSERVATIONS.md` 及相关 L3 规则文件。
5. reflector 按职责边界把高价值内容直接落到真实规则文件；若现有 skill 没有合适承载位，则允许新建真实 skill；只要触碰或新建真实 skill，则同次更新 `rules/skills/INDEX.md`。
6. reflector 重写 `contexts/memory/OBSERVATIONS.md`，删除已晋升条目和过期低优先级条目。
7. reflector 写 `periodic_jobs/ai_heartbeat/state/heartbeat_reflector_report.md`，列出 touched files、晋升摘要和 GC 摘要。
8. runner 执行后置审计：
  - touched files 必须全在 allowlist 内。
  - 每个 touched file 必须真实存在且可读。
  - 若 touched files 包含真实 skill 文档，则必须同时包含 `rules/skills/INDEX.md`。
  - `contexts/memory/OBSERVATIONS.md` 必须完成与 report 一致的 GC。
  - 若存在越界修改或校验失败，则恢复 allowlist 触面。
9. 成功时记录 success；失败时记录 failed，并保留完整运行日志。

## 错误处理与回退

- **reflector 运行前 allowlist 触面干净**：直接以 `HEAD` 为恢复基线，不额外创建 checkpoint。
- **reflector 运行前 allowlist 触面已有未提交改动**：创建临时 git checkpoint，恢复基线指向 checkpoint，而不是更早的 `HEAD`。
- **reflector 执行失败**：恢复 allowlist 触面内文件，不影响 allowlist 之外的未提交工作。
- **report 缺少 target date**：视为失败并回滚。
- **report 缺少 touched files**：视为失败并回滚。
- **report 提到 allowlist 之外文件**：视为失败并回滚。
- **report 提到不存在文件**：视为失败并回滚。
- **触碰或新建真实 skill 但未更新 `rules/skills/INDEX.md`**：视为不完整晋升并回滚。
- **report 声称 GC 完成，但 `OBSERVATIONS.md` 仍残留已晋升条目**：视为校验失败并回滚。
- **reflector 成功**：删除临时 checkpoint，并记录 success。

## 测试策略

- 重写 `periodic_jobs/ai_heartbeat/tests/test_heartbeat_local_runner.py` 中对 `rules/skills/ai_heartbeat_local_reflections.md` 作为唯一晋升目标的假设。
- 成功路径测试：覆盖 reflector 同时触碰 `contexts/memory/OBSERVATIONS.md` 与真实规则文件的场景。
- skills 路径测试：覆盖 reflector 修改已有真实 skill 文档或新建真实 skill 文档，并同步更新 `rules/skills/INDEX.md` 的场景。
- 失败路径测试：覆盖以下情况：
  - report 缺 target date
  - report 提到非 allowlist 文件
  - 触碰或新建真实 skill 但未同步更新 `rules/skills/INDEX.md`
  - report 声称 GC 完成但 `contexts/memory/OBSERVATIONS.md` 仍残留已晋升条目
- 回滚测试：保留 clean surface 和 dirty surface 两类 checkpoint 语义验证，只把 allowlist 样本换成真实规则面。
- prompt 合约测试：验证 reflector prompt 不再把单一路径 promotion file 当作正式规则出口，而是明确真实路由和 INDEX 联动约束。
- 文档对齐检查：确保 `periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md` 已显式包含 skills 类晋升必须更新 `rules/skills/INDEX.md` 的规则。

## 已确认决策

- 首版允许 reflector 在现有 skill 没有合适承载位时新建真实 skill 文档。
- `rules/skills/ai_heartbeat_local_reflections.md` 直接删除，不保留迁移说明文件。
- 需要在 `periodic_jobs/ai_heartbeat/docs/KNOWLEDGE_BASE.md` 中显式补充“skills 类晋升必须更新 `rules/skills/INDEX.md`”这条规则，使 SOP 与实现校验完全一致。