# 严重分叉上游跟踪策略

## 元数据

- **类型**: BestPractice
- **适用场景**: 跟踪一个已经与本地分支严重双向分叉（双向各领先数十提交以上）的上游分支；同步 main 增量到长期维护的 fork（如个人/团队定制分支）
- **创建日期**: 2026-07-20
- **来源**: iasi 跟踪 main 的实战（merge commit b1b4a50，33 文件自动合并 + 13 文件冲突）

## 这个 skill 解决什么问题

当你维护一个长期 fork（例如 `iasi`），它和上游 `main` 已经严重双向分叉：main 在前进，你的 fork 也在独立演进。每提交 cherry-pick 会让结构性分叉点（同一文件双方都改过）反复冲突；不跟踪又会持续落后。本 skill 给出一次性处理 + 建立增量基线的决策框架。

## 边界

- **适用**：双向各领先数十提交，且未来仍需持续同步。
- **不适用**：
  - 单向落后（直接 `git merge main` 即可，无冲突决策）
  - 即将废弃的 fork（不值得建基线，直接 rebase 或丢弃）
  - 历史改写需求（本 skill 不动 history，只产生 merge commit）

## 核心思路：从逐提交 cherry-pick 切换到一次性 merge + 增量基线

**不要**对严重分叉的上游逐提交 cherry-pick。结构性分叉点（双方都大改的文件）会在每一个相关 commit 上反复冲突，代价是 O(n × 冲突文件数)。

**应该**：一次 `git merge main` 把全部增量拉进来，所有冲突在这一次集中解决；之后以这个 merge commit 作为新的增量基线，后续同步只处理 main 的新增量。

## 验收标准

- [ ] 一次性 merge commit 已生成（不是 N 个 cherry-pick commit）
- [ ] 所有冲突已按"决策表"逐一处理并记录理由（至少在 commit message 列出 modify/delete 与取 main/取 fork 的关键文件）
- [ ] 下一次跟踪 main 时，merge 范围仅限于上次 merge commit 之后 main 的新增提交（验证：`git log <merge-base>..main --oneline` 全部为新提交，无回溯）
- [ ] fork 的自定义能力未被破坏（关键功能、关键 skill 条目、关键脚本仍存在且可用）
- [ ] 关键决策已写入 user/repo memory，含"已知分叉点清单"，避免下次重复踩同一组冲突

## 可用资源与工具

- `git merge main --no-commit` 后 `git merge --abort`：dry-run merge，仅评估冲突代价、不落地
- `git log <merge-base>..<branch> -- <file>`：确认目标分支分叉后是否动过某文件，决定权属
- `git log --author=<you> -- <file>` / `git blame`：判断文件作者权属，区分"你维护" vs "上游维护"
- merge-base：`git merge-base fork main`，是判断"分叉后"起点的唯一可靠锚点

## 冲突解决决策表（按优先级）

遇到冲突时按以下顺序判定，从上到下匹配第一个适用的规则：

1. **modify/delete（一方删、一方改）**
   - 若你的 fork 有意删除该文件（例如已迁移到其他国家方案）→ 保留删除（`git rm`）
   - 若是 main 删除而你的 fork 在用 → 保留 fork 版本（`git checkout --ours`）

2. **main 引用了 fork 已删文件**（典型表现：setup_guide/CRONTAB 里仍写着已删除的脚本路径）
   - 取 fork 版本。fork 的删除是主动决策，main 的引用是上游不知道你删了。把 fork 版本作为权威，避免污染文档。

3. **fork 领先 main 的功能性演进**（例如 fork 独立做了某模块的升级）
   - 保留 fork 版本。这是 fork 存在的理由，不能被 main 覆盖。

4. **纯 main 增益**（main 独有的新增内容、bug 修复、清理）
   - 取 main 版本。 fork 没有理由拒绝上游的纯正增益。

5. **双方同一文件都做了实质性修改**（真冲突）
   - 手动合并。读 `git log <merge-base>..main -- <file>` 和 `git log <merge-base>..fork -- <file>` 理解双方意图后逐段合并。
   - 这类文件必须人工审阅，不接受任何一方的整段覆盖。

## 方法论建议（非硬约束）

- **先 dry-run 评估代价**：`git merge main --no-commit` → 看一眼 `git status` → `git merge --abort`。如果冲突文件数 > 30 且大多属于第 5 类真冲突，考虑是否值得本次合并，或先做一次更小的范围合并。
- **保留 INDEX.md 之类含本地独有条目的混合文件**：fork 可能在某个 INDEX 里加了主仓没有的条目，main 又重构了同一 INDEX。这种情况不接受任何一方整段覆盖，必须手动合并保留双方条目。
- **用 commit message 留痕**：把本次合并处理的"已知分叉点"（哪几个文件取了谁、理由是什么）写进 merge commit message，作为下次同步的参考。
- **4 类已知分叉点清单化**：把反复出现冲突的文件类型固化进 memory（例如：heartbeat 归档 / 某个 skill 升级 / Copilot 偏好 / INDEX 独有条目），下次同步时优先看这几类。

## 已知陷阱（来自实战）

| 陷阱 | 表现 | 应对 |
|------|------|------|
| 逐提交 cherry-pick 严重分叉上游 | 第 5 类真冲突在每一个相关 commit 上反复出现，O(n) 倍工时 | 改用一次性 merge + 增量基线 |
| 凭文件名猜权属 | 看到 setup_guide.md 冲突就取 main，结果把 fork 删除的脚本路径又写回去 | 必须用 `git log <merge-base>..<branch> -- <file>` + 作者权属核查 |
| 接受 GitHub 的 "accept current/incoming" 按钮 | 一键解决看似省事，但会丢失另一方的功能性内容 | 禁用一键按钮；第 5 类必须逐段合并 |
| protected ref push 失败误以为冲突没解干净 | `git push` 报 "Cannot update this protected ref" | 这是权限问题不是合并问题，需要 bypass 权限或走 PR 流程 |
| 忘记把决策模式写入 memory | 下次同步时又从头踩同一组分叉点 | merge commit 落地后立即写入 user/repo memory，列出已知分叉点 |

## 输出

- 一个 merge commit，message 含"已知分叉点处理理由"
- 一条 user 或 repo memory，含"已知分叉点清单"和本次策略
- 冲突解决后立即跑一次 fork 的关键功能验证（最小 smoke：关键脚本 `--help`、关键 skill 文件可被 INDEX.md 解析）
- 如果 fork 有外部 skill 的本地 overlay（见 [外部 Skill Overlay 的本地安装与更新](./bestpractice_external_skill_overlay.md)），merge 完成后顺手跑一遍 overlay refresh：`cd external_skills/<repo> && git pull && pip install -e .`，确保本地 clone 与主仓 stub 指向一致
