# 微软新 Copilot：把发布稿读到第二遍，看见的东西变了

9 月 25 日，[微软发布了新版 Copilot](https://blogs.microsoft.com/blog/2026/09/25/introducing-the-new-copilot-with-home-code-and-autopilot/)。我第一遍是当新闻扫的：聊天入口改版，多了个代码生成器，加了个智能体，标题里 Home、Code、Autopilot 三个名字排在一起，像又一批 AI 功能更新，扫完准备归档。第二遍是因为一句话停下来的。微软原文说：「迄今知识工作的单位是文件——文档、表格、幻灯片。它们不会消失，但 Code 增加了第四种：小型的、为特定目的构建的解决方案。学会构建它们，正在成为和写备忘录、做预算模型一样的基本技能。」功能介绍不会写成这样；写备忘录、做预算模型、造小应用被并成同一级技能，等于替未来办公室里的人画了像。于是我把整篇发布稿重读了一遍。三个功能各自的完成度还是谈不上惊艳，但显出来的东西变了：它们摆放的位置，以及同一份稿子里一起收拢的计费、治理和数据底盘。

微软在 PC 时代用过一次这种摆法，产品叫 Office。这次像是在复刻同一路数。

## 一、三个名字，第一遍我是跳着读的

**Home。** Chat 管即时的事：问答、草稿、查询。Cowork 管端到端委托的事，比如响应一份 RFP、打包一套产品发布物料、整理一份财务关账包；这个能力 6 月就已经可用，这次是被正式编入 Home 的结构。路线图还往前走了一步：连模式选择都会取消，用户只陈述需求，Copilot 自己判断该路由到 Chat、Cowork 还是 Code。同时，Word、Excel、PowerPoint 的能力被内置进 Copilot，官方称之为 Office in Copilot：生成的文档真实、可编辑、可团队共享，与 Office 客户端双向同步，@提及队友的编辑会实时出现。让我多看一眼的是几个细节：PowerPoint 自动保持品牌规范，Excel 会显示改了什么和为什么，财务技能进 Excel、法律技能进 Word（Skills 功能）。这些细节指向的用法，比入口改版本身深一层。

**Code。** 用自然语言描述想要的应用、追踪器、仪表盘、自动化或工作流，Copilot 选技术路线并直接构建，产出从桌面小组件、交互式仪表盘到云托管的内部应用。三件事我当时记在了旁边：技术底座与 GitHub Copilot 同源；应用跑在沙箱里，可托管在企业自己的租户内；官方明确开发者继续用 GitHub Copilot，专业开发者不受影响。节奏上，月底进 Frontier 计划（付费早期采用者），数周内扩大可用，年内进 M365 Premium/Pro 预览。

**Autopilot。** 前身是 Build 2026 上发布的 Scout。给它一个名字、角色和目标，它会持续工作：盯频道、跟线程、做周期性任务，隔几天自己把放下的项目捡起来。官方示例是一场供应商评审的全流程，从排期、做 workback 计划、筹备会议，到跟进事项、向利益相关者催办，全程自主跑完。它在租户内是一等公民：有自己的身份、记忆、计算机和工作空间，出现在 Teams、Outlook、频道和文档里，可以被 @，背后有权限、审计和治理。月底扩至 private preview。

供应商评审这个示例让我放慢了速度。我自己经手过的供应商评审里，排期、催办这类事占掉的注意力，和示例里的每一步都对得上。让我心动和让我警觉的是同一件事：它进入组织的方式已经超出软件的范畴，一个有名字、有权限、可被 @ 的成员。

## 二、第二遍把三段并排看，三层结构才显出来

单看每个功能，都能想到做过类似事情的创业公司。第二遍我把三段并排读，微软摆的三层结构才浮出来。

入口层。一个普通职场人的一天大致是这样：早上问 Copilot 昨天的会议纪要，上午让它起草一封回复，下午委托它做一份客户简报。这些动作以前分散在聊天框、Office 客户端和各种内部工具之间，现在被 Home 收进一个界面，Office 成了被它调用的渲染层。微软自己的定位句说得更直白：「正如 Office 定义了 PC 时代的生产力，Copilot 正在定义 AI 时代的工作。」入口养成习惯之后，用户记住的动作会从打开 Excel 变成问 Copilot。Google 的 Gemini for Workspace 在抢同一个位置，Home 手里多了两张牌。一张是 Office 文档格式的原生性：生成的直接就是可编辑的 Word/Excel 文件，聊天产物的导出品比不了。另一张是取消模式选择的意图路由：用户不用判断该用哪个模式，这层复杂性被收进系统内部。

工具层。这层的场景可以落到具体的人身上：品控同事想要个缺陷追踪看板，项目助理想要个会议跟进小工具。以前的路要么是提需求、排 IT 队伍的期，要么是去买 SaaS；现在一句话描述就能生成，还托管在自己租户里。被收进来的除了造工具的权利，还有 no-code/low-code 平台的腹地，而 Power Platform 的升级替代恰好也由微软自己做，肥水没流外人田。对照第四种知识工作单元那句原文，Code 实际是在为全员造工具做官方叙事：写备忘录、做预算模型、造小应用，被并列为同等级的职场基本技能。

劳动力层。把 Autopilot 的示例再想一遍：一场供应商评审，从排期到催办全程自主跑完，人只在目标设定和例外处理时出现。IT-Connect 的点评点中了要害：IT 又多了一种要管理的身份（顺带一提，它和 Windows Autopilot 只是重名，没有关系）。三层各自的对手都不弱，但叠起来之后，入口带来订阅，工具带来用量，数字劳动力带来持续运营收入，商业闭环都落在微软自己手里。

## 三、暗线：Microsoft IQ 的地基，和两本账

三个功能吸走了发布稿的全部注意力，撑起这套结构的却是另外两条线。我第二遍才注意到它们。

**Microsoft IQ 在做统一地基。** Microsoft IQ 是 Copilot 的企业上下文层，这次被大幅扩充。Fabric IQ 把 Power BI 两千多万个语义模型接进 Copilot 的数据理解能力，已经在 Chat 和 Cowork 正式可用。Dynamics 365 和 Power Platform 的数据与工作流接入将在未来一个月公开预览，场景是销售写提案时自动带入交易历史和工单，不用切应用。统一插件注册表数周内正式推出：微软、伙伴、自建插件进同一个目录，IT 集中审批，一次发布多端生效。三件事指向同一个结果：无论 agent 跑在 Home、Code 还是 Autopilot 里，它理解组织数据的来源都是同一个受治理的池子。自主 agent 在企业里最常见的死法是无源之水，不了解组织上下文，每一步都要人喂。微软补的就是这一层。

**计费跟着 Agent 形态分账。** 微软把 AI 花费切成两本账。一本是用户订阅（USL），覆盖日常 AI：Chat、Office 全家桶、模型选择权，其中 Auto 模式按准确率、速度、成本逐请求挑模型。另一本是按量计费（UBB），覆盖 Agent 工作：Cowork、Code、Autopilot 等 agentic 体验和前沿模型走 Credits，前提是先持有 USL。模型供应商目前是 OpenAI 与 Anthropic 双供，更多实验室和开放权重模型在计划中。

配套的 FinOps for AI 逐项看下来。成本管理扩展到 Code 和运行时；管理员可用 API 配置支出策略；额度请求走审批流；能按用户组限定可用模型族；终端用户在 Copilot 里能直接看到自己的额度和用量历史。还有一个细节：企业客户的按量计费默认关闭，管理员没在 M365 管理中心创建支出策略之前，一分钱不计费。云账单震惊的教训被提前写进了产品设计。往后 Agent 平台的采购决胜项，可能落在治理配套的完备度上，功能和价格的对比只是入场券。

## 四、单点都有对手，合起来呢

放到竞争地图上，每一层都有叫得出名字的对手。Home 对 Google Gemini for Workspace，胜负手在前文说的文档原生性和意图路由。Code 对 Lovable、Bolt、v0、Replit 这批 AI 应用生成器，对方生成能力强，缺的是企业运行时。Autopilot 对 Salesforce Agentforce 和一批 agent 创业公司，微软手里是租户内身份、Teams/Outlook 触点和组织记忆。上下文层对各家数据中台，Fabric IQ 的两千万语义模型是现成存量。

信息量最大的一步棋落在 Lovable 身上。Copilot Managed Runtime 这次开放了 SDK 和 CLI：项目脚手架、数据连接、TypeScript 类型化服务、Git 版本控制、Entra 身份认证，是正经的平台级能力，玩具沙箱给不了这些。用 Cowork/Code/Copilot Studio 构建的应用都跑在它上面；托管应用统一进 M365 管理中心的应用清单，访问、用量、健康、策略一屏可见。Lovable 全球合作负责人 Lan Roche 在[微软博文中](https://blogs.microsoft.com/blog/2026/09/25/introducing-the-new-copilot-with-home-code-and-autopilot/)说：「With the Copilot Managed Runtime SDK, an app made with Lovable can now run inside your Microsoft tenant, the same way everything else does: same sign-in, same policies, same app inventory.」

我最初把这段当成常规的伙伴站台，越想越觉得姿态清楚：微软不抢生成器，做生成器的企业级宿主。生成器赛道竞争激烈、毛利趋零；带治理的运行时，也就是 Entra 身份、租户边界、合规体系、应用清单这一套，是微软的独有资产。Lovable 们对抗平台的企业身份层并不理性；微软这边，每接入一家，Code 的生态位就厚一分。接下来一年，大概率会看到更多生成器宣布接入。

回到开头的问题：单点都有对手，合起来呢。赢下一个单点功能，对手要付的成本不高；要同时补齐文档、应用、agent、身份、数据、计费治理这六件事，每件都得从零建。某个功能领先一两个版本，撑不起壁垒；六件事已经装好、且互相咬合，这才是对手难办的地方。

## 五、稿子里没有的数字

本文的依据只有[厂商发布稿](https://blogs.microsoft.com/blog/2026/09/25/introducing-the-new-copilot-with-home-code-and-autopilot/)和两篇第三方报道（[Unite.AI](https://www.unite.ai/microsoft-copilot-overhaul-adds-home-hub-code-builder-and-autopilot-agent/)、[IT-Connect](https://www.it-connect.tech/microsoft-unveils-the-new-copilot-with-home-code-and-autopilot/)），有几件事稿子里没说，而它们恰恰决定这套结构的成色。

长任务的完成率，稿子里没有任何数字。隔几天自己捡起项目的前提是长周期任务不崩，而当前业界长任务 agent 的可靠性并不好看；Autopilot 的供应商评审示例能否稳定复现，只能等 private preview 的实测。Code 产出的维护责任同样没有交代：业务人员造出的小工具，三个月后数据源变了谁来修？一次发布多端生效说的是插件，应用的生命周期管理没有对应说法，影子 IT 2.0 的治理成本可能被低估。模型混排的一致性也没有答案：Auto 逐请求在多个模型间路由，同一个任务今天和明天可能走不同模型，企业如何验收输出的可复现性？管理员能限定模型族来收窄范围，这个开关的存在，本身说明微软知道问题在哪。lock-in 还在加深，六件事咬合越紧，迁移成本越高；采购时把数据和应用的可导出承诺写进合同，是对冲。

[IT-Connect 的一条评论](https://www.it-connect.tech/microsoft-unveils-the-new-copilot-with-home-code-and-autopilot/)我打算留着对照后续：发布稿不等于交付。Home 和 Code 进的是 Frontier 付费早期采用者计划，Autopilot、Today、@Copilot in Teams 全在 preview 阶段。三箭齐发的完成度要按这个折扣看，实际可用性和时间表都可能变动。

这些功能正式落地之前，有几件事现在就能做，且不依赖微软的时间表。最实际的一件是把内部的重复性劳动盘点出来：Code 年内进 M365 订阅预览，届时第一批小工具需求应该已经排好队，从零想起就晚了。成本护栏同理：UBB 默认关闭、租户/组/用户三级预算、阈值告警、API 化策略，这份清单可以直接照抄进任何内部 Agent 试点的制度设计，第一天就建，事后补的成本高得多。身份、权限、审计这三样，引入任何常驻 agent 时都该当作验收底线；Autopilot 的架构是一个现成的参考模板。

1990 年代 Excel 让业务人员自己建模；这次 Code 让业务人员自己造应用，Home 对应 Word 的入口位，Autopilot 对应 Outlook 的常驻异步位。打法是熟悉的那一套，锁定的对象从桌面换成了 AI 时代的工作平台。这场复刻能推进到哪一步，11 月 17 到 20 日旧金山的 Microsoft Ignite 会给出下一批证据；到时候我会拿着 private preview 的实测数字，回来对照今天写下的判断。
