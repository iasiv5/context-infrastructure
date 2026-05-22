# 一次 brainstorming skill 的实战记录：移植卡兹克洁癖.skill

0、这次实操要解决什么？
这次实操的目标，是把卡兹克的洁癖.skill 改造成适合 GitHub Copilot 使用的 cleanup skill，并与之前已经完成的 handoff skill 配合，补齐『会话交接.handoff』与『会话总结.cleanup』这一组更完整的闭环操作。
    卡兹克洁癖.skill地址：https://github.com/KKKKhazix/khazix-skills/tree/main/neat-freak
    iasi handoff skill地址：https://github.com/iasiv5/m/tree/main/plugins/iasi/skills/handoff
    iasi cleanup skill地址：https://github.com/iasiv5/m/tree/main/plugins/iasi/skills/cleanup

1、动手之前，我做了superpowers 两组关键技能的中文化适配：
 1.1、先基于 obra/superpowers 的 brainstorming skill，改造成适合 GitHub Copilot 使用的中文版本。它主要用于需求澄清和方案比较，帮助用户在真正动手写计划之前先把设计想清楚，避免过早陷入编码细节。输出物为 docs/specs/<YYYY-MM-DD>-<topic>-design.md
    原版地址：https://github.com/obra/superpowers/tree/main/skills/brainstorming/
    汉化适配：https://github.com/iasiv5/m/blob/main/plugins/iasi/skills/brainstorming/

 1.2、再基于 obra/superpowers 的 writing-plans skill，改造成适合 GitHub Copilot 使用的中文版本。它承接 brainstorming 阶段产出的 spec 设计文档，继续把设计拆成具体实施步骤，规划文件结构和职责边界，并明确验证方式，最终产出可执行的计划。输出物为 docs/plans/<YYYY-MM-DD>-<feature>-implementation-plan.md
    原版地址：https://github.com/obra/superpowers/tree/main/skills/writing-plans/
    汉化适配：https://github.com/iasiv5/m/blob/main/plugins/iasi/skills/writing-plans/

2、实操过程：
第一轮提示词：

/brainstorming 我准备把卡兹克的洁癖.skill改造成适合GitHub Copilot使用的版本，重命名为 cleanup，配合之前的 hand off skill，补齐『会话交接.handoff』与『会话总结.cleanup』这样的一组闭环操作。帮我分析一下这个需求，看看我有没有考虑全面，或者有什么可以改进的地方。
    卡兹克洁癖.skill地址：https://github.com/KKKKhazix/khazix-skills/tree/main/neat-freak
    iasi handoff skill 本地路径：m\plugins\iasi\skills\handoff

Agent的回复有几个关键点：
1、赞同我的需求大方向，已经做好的handoff管会话接力，正在改造的cleanup管经验沉淀。

2、但是关于 handoff 和 cleanup skill使用的顺序，Agent的想法和我心里的预期并不一致，我的设想是，前期不论多少轮会话，都只用/handoff进行交接，等到最后任务完成后，基于最后一轮的会话终版结论，用/cleanup 做一次完整的、深度的经验沉淀，并且整理长期知识和记忆。所以接下来，第二轮会话我会再次和它对齐这一点。


第二轮提示词：


关于 handoff 和 cleanup skill使用的顺序，
我的设想是，前期不论多少轮会话，都只用/handoff进行不断交接，等到最后任务完成后，基于最后一轮的会话终版结论，用/cleanup 做一次完整的、深度的经验沉淀，并且整理长期知识和记忆。否则每一轮的会话，用户都要先沉淀，再交接，流程上太过繁琐了。深度分析并评估我的建议和想法，提出专业的意见。

Agent 同意了我从用户体验以及流程负担层面的考量，并且分析了优点（图）。

不过同时也指出了我的方案中的风险点（图）

并且试图说服我，在发现中途形成“稳定长期事实”时，做一次checkpoint的cleanup，但是这个checkpoint的判断也是需要消耗用户心力的，我并不愿意弄的太过复杂。


第三轮提示词：
所以我还是坚持“1、只保留终态时做deep cleanup”，并不再解释原因。


第四轮提示词：2
Agent就还在“挣扎”，但是我心意已决，减轻用户流程负担以及避免过早沉淀污染长期知识，都是我坚持不要中途cleanup的重要原因。

第五轮提示词：
经过最后一轮的“拉扯“，我和Agent基本上达成以下共识：
- handoff 负责带着不稳定但足够继续工作的上下文往前跑；

- cleanup 只负责把已经收敛成稳定事实的东西沉淀到长期载体。


并且Agent提到的允许实现过程中更新正式工件，这个点我也是同意（默认允许）的，所以，愉快的做了如下决定：


第六轮提示词：
brainstorming skill是懂苏格拉底心法的，每次只问一个关键问题，在这一轮，确定了保守的触发策略（且部分时间应该是手动触发 /cleanup）


第七轮提示词：
针对硬触发的弊端，增加了软提醒。认可，并让Agent继续。

第八轮提示词：
用户显式调用了 /cleanup skill，提醒用户是本分，后果由用户自己承担！

第九轮提示词：
/cleanup skill默认可更新范围限定在仓库内的文档以及记忆

第十轮提示词：
Agent把Spec设计文档落盘，进入writting-plans 写计划阶段

第十一轮提示词：
Agent调用/brainstorming 后续技能 /
writting-plans，按照设计文档，写好了实施计划。让Agent开始按实施计划执行 cleanup skill 改造与开发工作。




第十二轮提示词：
Agent按照实施计划完成了第一轮落地，发现了两个问题：
1、
cleanup skill /reference 文件夹下的资产为什么没有移植过来？
2、cleanup skill 的致谢章节和其他skill一样，可以带上洁癖skill的原地址：
https://github.com/KKKKhazix/khazix-skills/tree/main/neat-freak

第十三轮提示词：
Agent解释了为什么不移植 /reference下 两个文档的原因，我选择需要移植，只不过做一次GitHub Copilot的适配删减。

第十四轮提示词：
最后做一次冒烟测试，收尾




任务完成✅

归档后上传到 GitHub：
https://github.com/iasiv5/m/tree/main/plugins/iasi/skills/cleanup



3、终章：/cleanup skill 试用结果：


4、小结：这套链路为什么值得用
把 brainstorming 和 writing-plans 串起来之后，这套流程在中等复杂度任务中表现很稳定。尤其是在需求还没有完全收敛、方案仍需要反复推敲的场景里，它能先帮你把问题想清楚，再把实施路径排清楚，从而明显降低返工成本和落地风险。

如要试用，可至以下地址获取，欢迎反馈使用体验：
https://github.com/iasiv5/m/tree/main/plugins/iasi/skills



