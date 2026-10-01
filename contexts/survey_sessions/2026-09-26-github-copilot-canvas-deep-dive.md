# GitHub Copilot canvas：把 agent 从聊天框里请出来

9 月 25 日，GitHub 的 Senior AI Developer Tools Advocate Kayla Cinnamon 发了一篇[教程](https://github.blog/ai-and-ml/github-copilot/github-copilot-app-for-beginners-how-to-build-custom-workflows-with-canvases/)，官方标注 3 分钟读完，讲 Copilot app 里的 /create-canvas 怎么用。我第一遍是当一篇新手教程扫过去的：Beginners 标签，release notes 看板的例子，一句话描述、界面就出现的套路，看完归档。同一天，微软发布了带 Home、Code、Autopilot 的新 Copilot，前文刚分析过。同一周、同一家公司，一边给不写代码的人造应用，一边给写代码的人造界面，两件事凑在一起不像巧合，于是我回头按工具链的眼光把这篇小稿重读了一遍。第二遍看到的东西不一样了：canvas 没有停在给 Copilot app 加一个 UI 自定义功能，它在把 agent 协作的主战场从聊天流搬进工作面，而搬运所用的界面，本身也是生成的。

## 一、三分钟的稿子，装着一整套机制

博文第一句就站了队：大多数工具给你一组固定界面，要求你把工作塞进去；canvases 反过来，从你想要的工作流出发，让界面围绕它成型。kanban 板、issue 分诊板、发布检查单、仪表盘、表单，甚至电子表格，都能装进这个壳。博文给它的类比是 live shared whiteboard：agent 工作时更新它，你也用按钮、卡片、过滤器这些控件直接改，两头改的是同一块板。

造这样一块板的入口是一个 skill。在 agent 会话里输入 /create-canvas，用自然语言描述。描述要覆盖三件事：这块 canvas 支持什么工作流；你在界面上能做什么；agent 能做什么。示例 prompt 只有一句话：为跨 Copilot app 会话完成的新功能工作建一个 release notes canvas，带上评审和组织条目的控件，并允许 agent 添加和更新条目。agent 收到后把界面建出来，在右侧面板打开，全程不写文件、不调布局。一段描述，变成一件可用的定制工具。

教程到这为止。真正让我放慢速度的，是教程主体之外的两段。

一段讲迭代。第一版只是起点，之后可以继续让 agent 加列、加过滤器、拉取 open PR，或者把整块 canvas 改成每日检查单。原文特意强调没有固定布局菜单：凡是能描述的工作流，大概率都能变成 canvas。另一段给协作模式起了名字：Instant collaboration, not command and wait。你点按钮、改字段、移卡片，canvas 的共享态立即变化，agent 不需要一个单独的 send/sync 动作就能看到；反过来，你让 agent 加一条 release note、移一张卡片，它用的是和你相同的 action 集合，改动直接落在界面上。博文把这叫共同掌舵，以区别于发命令然后等响应。

配上 [GitHub Docs 的 working-with-canvas-extensions](https://docs.github.com/en/copilot/how-tos/github-copilot-app/working-with-canvas-extensions) 一页，工程形态就齐了。canvas 落地为一个 extension：项目级的放进仓库的 .github/extensions 目录，提交进 git 由团队共享；个人级的放在本机 ~/.copilot/extensions。典型组成是 package.json（元数据加依赖）、一个 extension 入口文件（例如 extension.mjs，定义行为与能力），再加一个可选的 JSON artifacts 目录，持久化 canvas 的数据与状态。人走 UI 控件，agent 走 agent-callable capability，读写的是同一份共享态，Docs 给出的能力示例是 get_board、add_card、move_card 这样一组接口。它还能作为 plugin 的一部分，和 skills、MCP server 并列分发，装 Azure DevOps 插件就能拿到它的 canvas。

三分钟的稿子对目录结构只字未提，但结构摆在那里：一件可以 commit、可以 review、可以随 plugin 装卸的东西。教程正文里露出的这个尾巴，已经超出了 UI 偏好设置能覆盖的量级。

## 二、chat 是意图层，工作面才是执行层

GitHub 在 Docs 里把位置一句话说尽：chat 适合定义意图和讨论，但大多数工作发生在工作面上，终端、浏览器、文档、仪表盘。这一年用下来的体感与此一致：agent session 里聊得再清楚，活最终还是落在某件具体的工作制品上，聊天记录至多是那件工作的注释。可当前几乎所有 agent 产品都把交互压在聊天框里，人和 agent 的每一点对齐，都要靠消息往返来完成。

canvas 动的就是这一层。界面在这套设计里换了角色，它同时是人的视图和 agent 的读写对象。博文里 send/sync 缺席的细节，说穿了是把对齐动作从消息协议里拿掉了：状态摆在界面上，双方都看得见，也就无需互相转述。Docs 列了四个适用时机，我认为最有力的是两条。其一，把 agent 的工作锚定在贴合真实工作流的制品上，别让它悬在聊天流里。其二，跨 turn、跨会话、跨交接保持工作连续，看板上的卡片不会随会话结束而消失，下一个接手的人或 agent 看到的是同一块板。进展的形态随之改变，从聊天流里的一条响应，变成共享制品上可见的变化。

博文的收尾三问，回头看正是这套设计的压缩版：我想看到什么信息；我想直接改什么；agent 能更新什么、做什么。拆任何一块工作面，这三问分别对应数据模型、人的操作集、agent 的能力集。一篇 Beginners 教程把接口设计的三个基本问题藏进收尾的问句里，这个安排本身就说明作者清楚重点在哪。

再往前推一步，就到了让我停下来的判断：/create-canvas 把为 agent 造工具这件事本身，也交给了 agent。以前给 agent 配工作台，终端集成、IDE 面板、自定义 dashboard，都得人写代码；现在描述工作流、描述两边的操作集，界面就生成出来，之后还能像代码一样迭代、像依赖一样分发。界面正在获得与代码、文档同等的待遇。让我心动和让我警觉的是同一件事：如果界面可以一句话生成，它作为人和 agent 之间契约的地位就松动了，今天描述得再清楚，明天 agent 也可以把它重排一遍。这个边界，目前公开的材料里没有回答。

## 三、和微软 Code 对读：同一周的两条路线

把 9 月 25 日的两份稿子并排放，路线差异一眼可见。微软 Code 面向不写代码的人：一句话描述，Copilot 选技术路线、生成应用，托管在自己租户里，产出从小组件到云托管的内部应用。GitHub canvas 面向写代码的人：界面以 extension 的形式存在，进仓库、进 git、随 plugin 分发，可编程、可 review、可改造。前一条路线把生成物锁进托管运行时，换来零运维；后一条把生成物交还给代码工程，换来全部控制权。

两条路线底下压着同一个判断：界面本身能生成出来。微软拿它去接业务人员，GitHub 拿它去接开发者。载体也是同一个，Copilot app。于是冒出一个两篇稿子都没回答的问题：Code 生成的仪表盘和 canvas 生成的看板，边界在哪。更可能的解释是，这本就是同一件事的两端：一头从想要一个应用起生成，一头从手头的工作流起生成。

对做 agent 工具链的团队，GitHub 这条路线的信息量更大，因为它把生成物放进了现有的工程治理结构，git 仓库、plugin 体系、代码审查，而没有另开一个托管环境。最终形态没人知道；共享工作面、可生成界面、extension 分发这个组合，可以先按 agent 协作界面的候选基线来跟踪。

## 四、没说的，和现在就能动手的

也得直说：一篇信息量刻意压低的入门稿，几件决定成败的事，它一个字没提。多用户并发没讲。两个人同时移一张卡片，共享态怎么合并？artifacts 目录里的 JSON 由谁仲裁？错误处理没讲，agent 调 move_card 失败时，界面停在什么状态？权限与安全边界没讲，agent-callable capability 是一组能读写持久状态的接口，Docs 只给了能力名，调用粒度、审计、撤销机制都没有下文。共享状态的一致性设计是 live whiteboard 这类架构里最难的部分，入门稿不谈可以理解，但目前公开材料里确实找不到，只能等实测。

可动手的倒不少。社区已经在 [Awesome Copilot](https://github.com/github/awesome-copilot) 仓库里分享了现成的 canvas extensions，release notes 工具、kanban 板、issue 分诊工作流都有，装一个接近需求的，再让 agent 定制，比从零描述快。博文自己的建议是 start small：开个会话，跑 /create-canvas，为手头的事描述一块简单的板或检查单。落到我们的试点上，我会挑一个跨会话的重复性工作面，发布检查单或 issue 分诊，先跑两周；界面好不好用先放一边，要观察的是共享态在人和 agent 同时写入时会不会烂。上面那些没人回答的问题，两周实测比任何文档回答得都快。

三分钟、Beginners 标签、温和的例子，这些表层信息让我第一遍把它扫了过去。第二遍读完，我把它移进了另一个文件夹：和微软 Code 同一周发布的、关于 agent 界面往哪走的两份证据之一。chat 表达意图、工作面承载工作，这个分法早已有之；变化在于工作面本身正在变成可生成、可分发、人和 agent 共同读写的东西。接下来要盯的是治理层。等第一批团队真的把 canvas 提交进 .github/extensions 并发使用，那套没讲的一致性与权限问题就会浮出来。到时候再看 GitHub 是补文档，还是补架构。
