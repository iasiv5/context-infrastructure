# 外部 Skill Overlay 的本地安装与更新

## 元数据

- **类型**: BestPractice
- **适用场景**: 主仓（context-infrastructure）把某些 skill 文件迁移到独立外部 repo 后，在本地 clone 一份完整内容并保持更新；以及"merge main to iasi branch" 同步时顺手刷新 overlay
- **创建日期**: 2026-08-13
- **来源**: PR #86 把 5 个写作 skill 迁移到 `grapeot/writing-skill` 后的本地 overlay 实践

## 这个 skill 解决什么问题

主仓为了保持单一职责，把日益成熟的 skill 模块抽到独立 repo（如 writing-skill、semantic-search-skill）。抽走后，主仓里的同名文件变成转发桩（只有 GitHub 链接，不含内容）。

问题：**AI agent 读桩文件只能拿到一个 URL，不会自动 fetch GitHub，所以拿不到任何操作流程、验收 gate、voice contract 规格**。如果你直接说"写公众号文章"，AI 读到的是空壳，不会跑完整工作流。

解法：在本地 clone 外部 repo，让 AI 读到完整内容；同时保持一个 overlay 路由文件告诉 AI 去哪读。

## 边界

- **适用**：主仓 skill 文件被迁移到外部 repo，且你日常需要 AI 按该 skill 工作（不只是参考 URL）
- **不适用**：
  - 外部 repo 只是偶尔查一下文档（用的时候让 AI 打开 URL 就行，不需要 overlay）
  - 外部 repo 含 secret / 个人隐私（不适合本地常驻 clone，改为按需临时 clone）

## 核心步骤：首次安装一个 overlay

对每个需要本地常驻的外部 skill repo：

1. **clone 到 `external_skills/<repo-name>/`**（统一目录，不散落各处）
2. **如果有 CLI（pyproject.toml）**：`pip install -e .` 以 editable 模式安装，这样 `git pull` 后代码立即生效
3. **`.gitignore` 加 `external_skills/`**：整个目录不进版本控制，避免污染主仓
4. **在主仓创建一个 overlay 路由文件** `rules/skills/<repo>_local_overlay.md`：
   - 写明完整 skill 内容的本地路径表
   - 写明 AI agent 行为规则（"先读哪个文件、按什么路由走"）
   - 写明 CLI 已安装、怎么调用
   - 写明更新方式（`git pull` + 重装）
5. **在 INDEX.md 加一个条目**（纯新增，放在你的 fork 专属区域），描述 overlay 文件并加触发词

## 核心步骤：更新已有 overlay

```powershell
cd external_skills/<repo-name>
git pull                          # 拉上游最新
pip install -e .                  # 如果 src/ 里的代码变了，重装
```

- overlay 路由文件一般不需要改（路径表不变）
- 如果上游重构了 skills/ 目录的文件名，更新路由文件里的路径表即可

## 何时触发更新（三种触发时机）

| 时机 | 谁触发 | 原因 |
|---|---|---|
| **merge main to iasi 流程的一部分** | agent 执行 merge main | **无条件必做**——即使 git merge 报 already-up-to-date，仍须跑 overlay refresh。main 可能改了 stub 的 URL/格式，顺手刷新确保一致 |
| **上游 repo 有新 PR/commit** | 你看到通知或想用新功能 | writing-skill 一周 7 个 commit，比较活跃 |
| **CLI 报错或行为异常** | 你发现 lint/写作工具不工作 | 可能是上游修了 bug，pull 一下再说 |

### merge main 时的自动 refresh

"merge main to iasi branch" 这个操作做完后，agent 应该**顺手检查 overlay 是否需要刷新**。这个检查很轻量：

```powershell
# 对每个已有 overlay
foreach ($repo in (Get-ChildItem external_skills -Directory)) {
    Push-Location $repo.FullName
    $before = git rev-parse HEAD
    git pull --ff-only 2>$null
    $after = git rev-parse HEAD
    if ($before -ne $after) {
        Write-Host "$($repo.Name) updated: $before..$after"
        if (Test-Path pyproject.toml) { pip install -e . 2>$null }
    } else {
        Write-Host "$($repo.Name) already up to date"
    }
    Pop-Location
}
```

## 与 forked_upstream_sync 的关系

- `bestpractice_forked_upstream_sync.md`：管**主仓内** main→iasi 的 git merge，解决主仓内部文件的冲突决策
- 本文件：管**外部 repo** 的本地 clone 保持最新，不涉及主仓 merge 冲突
- 两者是**引用关系**，不是包含关系：merge main 完成后，引用本文件的 refresh 步骤刷一下 overlay；但本文件的更新步骤也可以独立运行

关键不变量：**overlay 的所有文件（clone 目录 + 路由文件 + INDEX 条目）不碰 main 独占的 stub 文件**。这样 merge main 时零冲突，overlay 更新时不动 merge 决策。

## 验收标准

- [ ] `external_skills/<repo>/` 存在且最新（`git status` clean）
- [ ] CLI（如有）可调用：`<repo-cli> --help` 或 `python -m <module> --help` 正常
- [ ] overlay 路由文件存在，路径表指向真实存在的文件
- [ ] INDEX.md 有 overlay 条目（放在 fork 专属区域，不混进 main 的 stub 引用区）
- [ ] `.gitignore` 含 `external_skills/`，主仓 status 看不到 clone 目录

## 已知陷阱

| 陷阱 | 表现 | 应对 |
|---|---|---|
| clone 目录污染主仓 | `git status` 显示一堆 untracked 的 clone 文件 | `.gitignore` 加 `external_skills/`，merge 前确认 `git check-ignore` 返回 0 |
| 往 main 独占的 stub 里写 fork 内容 | 下次 merge main 时该行跟 main 改动冲突 | stub 保持 main 纯净，fork 专属逻辑只写 overlay 路由文件 |
| 忘记 pip install -e . 后代码没更新 | `git pull` 了但 CLI 行为没变 | pull 后如果有 src/ 变化，必须 `pip install -e .`；editable 模式下一般自动生效但保险起见重装 |
| 上游重构了 skills/ 目录文件名 | overlay 路由文件的路径表失效，AI 读不到内容 | pull 后快速扫一眼 `git log --oneline -3`；如果有 rename/restructure，更新路由文件路径表 |

## 输出

- overlay 路由文件（主仓内，fork 专属）
- `external_skills/<repo>/` 本地 clone（gitignore，不进版本）
- CLI 已安装（如有）
- INDEX.md 条目（纯新增）