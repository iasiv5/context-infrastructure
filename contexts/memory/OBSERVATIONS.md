# Memory Observations

这是三层记忆系统的动态记忆日志。observer 会把当天观测追加到这里；reflector 会回看这里的近期内容，清理低价值项，并据此产出规则晋升与报告。默认触发方式是 `.github/hooks/pre-session.ps1` 调用 `periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py`。

## 格式说明

每个日期条目格式如下：

```raw
Date: YYYY-MM-DD

🔴 High: [方法论/约束] 描述
🟡 Medium: [项目状态/决策] 描述
🟢 Low: [任务流水] 描述
```

### 优先级定义

- **🔴 High**：跨项目通用的经验教训、硬性约束、影响系统架构的重大决策。永久保留，候选晋升为 axiom 或 skill。
- **🟡 Medium**：活跃项目的关键进展、技术决策背景、未来几周仍需参考的信息。
- **🟢 Low**：日常任务流水、瞬时 debug 记录、临时上下文。定期垃圾回收。

## 如何加载记忆

不要全文加载这个文件（可能很大）。按需检索：

```bash
# 搜索特定主题
grep -n "关键词" contexts/memory/OBSERVATIONS.md

# 搜索最近 N 天
grep -A 20 "Date: $(date -v-7d +%Y-%m-%d)" contexts/memory/OBSERVATIONS.md
```

或使用语义搜索（`rules/skills/semantic_search.md`）做跨日期语义检索。

---

<!-- 以下是记录区域，由 AI Heartbeat 本地执行器追加与整理 -->

Date: 2026-05-24

🔴 High: AI Heartbeat 架构重大重构——`periodic_jobs/ai_heartbeat/src/v0/heartbeat_local_runner.py` 从本地确定性机械扫描改造为 Claude Code CLI 驱动的触发器模式。选择方案 C（Claude 全权执行 observer / reflector，Python 只做触发与审计），放弃机械降级路径，reflector 引入 git checkpoint 恢复机制和 allowlist 约束。设计文档：`docs/specs/2026-05-24-claude-code-smart-heartbeat-design.md`；实施计划：`docs/plans/2026-05-24-claude-code-smart-heartbeat-implementation-plan.md`。
🟡 Medium: 新增 observer / reflector 独立 prompt 模板：`periodic_jobs/ai_heartbeat/src/v0/prompts/observer.md` 和 `periodic_jobs/ai_heartbeat/src/v0/prompts/reflector.md`，将任务协议从 Python 硬编码拆离为 Markdown 模板，支持变量渲染。`rules/skills/project_scaffold.md` 增加公开仓库脚手架门控（commit b660593）。

Date: 2026-05-27

🟡 Medium: 图片生成能力从 workspace 内置 skill 拆分为独立 public repo `grapeot/image-generation-skill`。删除了 `rules/skills/generate_image.md`、`tools/generate_image.py` 及测试，改为在 `docs/SKILL_ECOSYSTEM.md` 引用。这是 skill 管理从单体打包向生态系统模型迁移的延续，已有 Tavily、Stripe、PPTX 等多个 skill 走了同样的路径。
🟡 Medium: 新增 PQC（后量子密码）芯片安全文章 `adhoc_jobs/2026/20260526-pqc-chip-security-foundation.md`，覆盖 NIST FIPS 203/204/205、Caliptra 2.0 RTL 冻结集成 ML-KEM/ML-DSA、ASPEED AST2700 BMC SoC 的 PQC 落地方案。文章定位在固件安全与新密码标准交汇点，与 iasi 的固件专家身份高度契合。
🟢 Low: 清理 `.understand-anything/` 目录，移除过时的 meta.json、fingerprints 和知识图谱文件（16K+ 行删除）。AI Heartbeat 手动提醒实施计划中的测试引用做了一次小更新。
