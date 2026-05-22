# PUA 引擎对比：`pua.prompt.MD` vs `pua` skill

下表逐节比较仓库中的 `c:\iasi_workspace\.github\prompts\pua.prompt.MD`（简称 prompt 文件）与 `c:\Users\ies255050\.claude\skills\pua\SKILL.md`（简称 skill 文件）。

| 节/主题 | prompt 文件（摘要） | skill 文件（摘要） | 差异与建议 |
|---|---|---|---|
| 元数据 / frontmatter | 无结构化元数据，纯 Markdown steering 文档 | 包含 YAML 元数据（name/description/license）和更长的实现文档 | skill 更适合平台化管理与索引，prompt 适合会话级快速激活 |
| 目的与适用场景 | 激活 PUA 行为、会话内引导模型行为 | 同上，但同时声明触发条件与使用范围（自动触发） | 二者目的相近，但 skill 增加触发/自动化语义 |
| 三条铁律与方法论 | 完整列出三条铁律与 5 步方法论 | 内容基本一致，表述更详细并加入操作性说明 | 内容重复，可先用 prompt 验证，稳定后迁移为 skill |
| 能动性等级 & 检查清单 | 有说明但偏简介 | 更详细，加入验证/证据要求与具体操作 | skill 更偏可执行流程与证据收集 |
| 压力升级与话术（PUA 风味） | 列出 L1-L4 与若干话术示例 | 更丰富，包含多种“大厂味道”与示例回复 | skill 提供更多可复用模板，便于自动化触发 |
| 团队集成 | 无团队角色/Leader机制 | 明确 Agent Team 集成：Leader/Teammate/协议/汇报格式 | skill 明显适合多 agent 协作场景 |
| 触发条件与自动化 | 需会话中手动或由 prompt loader 加载 | 带触发条件（如失败次数、行为模式），可被平台识别自动触发 | skill 更利于监控、统计与升级策略实现 |
| 可维护性与迭代 | 修改即时，但无持久触发记录 | 支持长期维护、license 与元数据、易被注册为 skill | 推荐：先 prompt 快速迭代，再将稳定版本落地为 skill |
| 推荐使用场景 | 单次会话、快速试验、临时 steering | 生产化、自动触发、团队协作、监控与度量 | 两者配合使用效果最佳 |

---

文件已保存到仓库： [pua_comparison.md](pua_comparison.md)

如果需要，我可以将该对照导出为 CSV 或者将两份文件逐节合并生成更详细的对照文档（包含行级引用）。要哪个格式？
