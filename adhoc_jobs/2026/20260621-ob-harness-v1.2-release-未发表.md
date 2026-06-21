# ob-harness V1.2：给 ob 做一次系统性治理

V1.0 给 ob 带来 init、build、status，V1.1 带来 QEMU 起停。两版下来子命令齐了，但脚本本身长到 4200 多行。它能用，谈不上可被信赖。尤其是对 agent 这个新调用方来说，ob 在三个层面上还立不住：结构糊的脚本难维护，退出码语义混乱导致 agent 分不清该重试还是该放弃，改完之后又缺自动化回归手段来确认没带出新问题。

V1.2 做的事情可以收成四条线：重构脚本结构、统一退出码协议、从零搭测试体系、确立 ob-first 共识。四件事互相咬合。退出码协议统一了，但没有测试，改对没改对没人知道；测试体系搭好了，但结构糊着，后面的人不知道去哪找函数写断言；ob-first 共识写进了规则，但 ob 自己说话不算数的话，这条共识也立不住。所以是一起做的。

## 重构：让脚本重新可维护

4200 行的 bash 脚本，是几轮增量迭代累积下来的形态。函数物理顺序散乱，数字菜单选择、Y/N 确认、键值读取这些模式各重复两到四处，main 和命令编排层、领域函数、通用工具之间也没有明确分层。继续往上加功能，改一处的时候越来越没有把握不会带出别的问题。

V1.2 第一件事是按 §1 到 §7 给整份脚本建立物理分区：全局变量、通用工具、仓库与 machine、QEMU、构建流程、命令编排、入口。同时抽出 5 个公共函数。`select_from_list` 替换原本散落在 4 处的数字菜单选择循环，`confirm_action` 归并 4 处 Y/N 确认，`read_kv_field` 统一 6 处散落的键值读取，`require_path` 兜住前置检查，`download_qemu_binary_core` 抽出下载 QEMU 二进制的共享骨架。

重复代码的麻烦不在行数，在调试。修一个 bug，如果它有四份副本，你得先找全四处再逐个确认改法一致。抽成公共函数之后改一处即可，这是可维护性上最直接的收益。

顺带清掉了死代码。`write_pid_file` 这个函数零调用方，函数体里用的是 `pid=$!`，而 ob 现在用 setsid 做前台启动，两者对不上，说明它是更早的实现留下来的残留。删干净之后，后面读代码的人不用再猜它到底还起不起作用。

> 配图位 1：重构前后对照。左边是之前散乱分布的函数物理顺序示意，右边是整理后的 §1-§7 分区。同样的函数、更清楚的骨架。

## 退出码：收拾一个早就混乱的协议

ob 早就在用 exit 3 表示前置缺失。V1.2 做的事情是把退出码协议从混乱状态统一到一致状态，同时修掉了一个由混乱直接导致的 bug。

混乱的表现有三层。第一，同一种语义混用了不同的码：用户取消这个场景，5 处用 exit 0，另外 5 处用 exit 2。第二，bitbake 失败时，它的非零退出码未经处理直接透传出来，可能撞上 ob 自己保留的 2 或 3。第三，命令编排层（`cmd_*`）的前提检查用 exit 3，但领域函数层（`ensure_qemu_*`、`resolve_qb_vars` 这些）的前提检查用 exit 1，于是同一句 `ob start-qemu` 在前置没满足时，退出码取决于这一路走的是自检还是 ensure 链，结果是不确定的。

这种混乱直接产生了一个 bug。ob 的交互菜单 `cmd_menu` 按子命令返回的退出码来判断要不要报错。它用 `init_rc == 0` 来识别 init 成功，而 init 的取消路径走的是 exit 0。结果是用户在 source 选择或 machine 确认时取消了，菜单却显示 Init succeeded。

V1.2 把退出码语义统一定死：0 成功或良性无操作，2 用户主动取消，3 前置条件不满足，1 硬错误。四档语义从 ob 现有用法中归纳而来。取消的全部归 2，前提不满足的全部归 3（包括之前领域函数层用 1 的那些），bitbake 码不再透传（改打印出来再 exit 1）。菜单的解码逻辑改成「非 0、非 2、非 3 才报错」，取消和前置缺失都静默回菜单。

协议统一之后，exit 3 加上 remedy line 才对 agent 有用。agent 跑 `ob build romulus`，romulus 没初始化过，ob 返回 exit 3，同时给一行提示：Run 'ob init romulus' first。agent 读到这行，照做重试即可，不用猜这个非零码到底是编译失败还是前置没满足。在协议混乱的状态下，同一个非零码含义不固定，这行提示给出来 agent 也缺乏信心去照做。

> 配图位 2：agent 跑 ob build romulus 遇到 exit 3、读到 remedy line 后自动执行 ob init romulus 重试的一条对话流截图。最能讲清协议怎么落到 agent 决策上。

## 测试体系：从几乎零自动化到分层覆盖

在 V1.2 之前，ob 的自动化回归保护几乎为零。一个 smoke test，4 个 case，其中一行还硬编码了绝对路径，仓库挪个位置就直接挂。两个 expect 手动脚本覆盖一些交互分支。核心功能：init 8 步流水线、依赖解析、子仓库克隆、lockfile 生成、QEMU 二进制下载、端口和 PID 管理，全靠真实使用兜底。

V1.2 搭起来的测试体系分四层。protocol 层断言每条子命令的退出码协议（参数解析、前提分支、取消分支）。unit 层对单个函数做单测，范围是约 40 个纯函数、文件 IO 函数、交互叶子函数，目标覆盖率 95% 以上。orchestration 层用 PATH 注入 fake git/bitbake/curl，测编排函数（clone_sub_repos、lockfile 生成等）的调用顺序和参数。integration 层跑 init→build→QEMU 的端到端，因为重资源、需联网，只放在定期门禁里跑。

分层调度由 `run_all.sh` 负责，GitHub Actions 上每次 PR 跑前三层的快速子集。

覆盖度的衡量方式也做了选择。ob 是重编排脚本，92 个函数里大量逻辑依赖 git、bitbake、curl 等外部命令。如果要砌行覆盖率，就得 fake 掉所有外部命令，最终只证明了 fake 本身写对了，对实际可靠性贡献有限。V1.2 用两个独立来源做交叉：一边是人声明的功能点 checklist（哪些子功能该被测、由哪个 test 覆盖），另一边是 xtrace 运行时实测出来的函数命中雷达。两边对不齐的地方互相暴露：checklist 声明覆盖了但雷达没命中，说明测试可能在空转；雷达命中了但 checklist 没认领，说明漏了登记或只是路过。

此外还有一份诚实的覆盖盲区清单。92 个函数里哪些自动化覆盖、哪些只能靠 integration、哪些靠真实使用兜底，一一列清，不报一个虚高的覆盖率数字。

再说一个细节：shellcheck baseline 的比对方式。直接拿当前告警和 baseline 文件做集合比对，看起来够了。但 ob 的 baseline 里有 SC2012（建议把 `ls` 改成 `find`）出现 4 次、SC2002（无用 cat）出现 3 次这类同类型重复。集合去重之后，「又多引入了一个 ls /tmp，第 5 个 SC2012」会被判成良性而自动吸收。V1.2 把比对改成 multiset（带计数的集合），凡是比 baseline 多出来的实例都算新增告警报错，不自动吸收。这类细节是踩过坑之后才会加上的防线。

> 配图位 3：覆盖率雷达图与功能点 checklist 的交叉对照，或者四层测试的架构示意图。

## ob-first：给这整套东西立共识

前三件事合起来，ob 在结构、反馈、回归上都靠得住了。但还差一件事：让 agent 知道它应该走 ob，而不是绕过 ob 去手撸 bitbake 或 git clone。

这套约定写在了 AGENTS.md（每会话自动加载的最小守卫）、ADR 0003（记录决策和被否的备选）、新建的 bestpractice_06 skill（完整协议）里。核心一条：做 OpenBMC 环境动作之前，先 `ob --help` 查 ob 是否提供这项能力，提供就走 `ob <cmd>`，不要先手动。`ob --help` 是唯一权威的能力清单。

设计里评估过 SessionStart 提醒和 PreToolUse 命令拦截两种 hook 方案。前者和常驻守卫重复，后者误报率高、可能挡掉正当的裸 bitbake 调试。最终选择约定层加 CI 闸，不依赖 hook。

这套约定还得防 ob 自己漂移。之前出过一件事：`--skip-deps` 这个选项加了，但 `ob --help` 里没写，等于 agent 只能凭运气知道有这个开关。V1.2 加了一条防漂移测试 `usage_dispatch_sync.sh`，断言 `usage()` 的 Commands 段和 dispatch 的 case 子命令集合完全一致。ob 以后加子命令忘了更新 help，这条测试会直接挂掉。

`ob build` 现在的纯交互模式是一条已登记的缺口：非 TTY 直接 exit 3，没有 `ob build <machine>` 的非交互路径。agent 遇到时按 exit 3 协议处理，不转去手动跑裸 bitbake，登记为 ob 待补项。缺口本身也是协议起作用的例子：知道是缺口，比假装没有好。

## 这一版还做了哪些具体改动

四条主线之外，这一版还有一些让 ob 更顺手的改动。`ob start-qemu` 加了串口交互登录，BMC 起来后直接在串口 console 登录调试。start-qemu 的 machine 列表只列已经构建过的机器，避免选到没镜像的机器白跑一轮。多用户安全上，PID 检测改成 serial socket 加启动用户过滤，修掉了在共享编译机上误判别人 QEMU 进程的风险，同时主动清理失效的 SSH host key。交互菜单支持输 0 取消，不再死循环。

还有一处 Yocto 配置层面的 bug 修复：`DL_DIR` / `SSTATE_DIR` 原来用 `??=`（weak default）会被 OpenBMC 默认值压过而失效，改成条件强赋值解决。这里的条件强赋值指用 `?=` 或匿名 Python 函数把值钉死，确保不被 OpenBMC 默认的 `??=` 压回去。生成的 .inc 同时补上了 `BB_HASHSERVE_DB_DIR`。

## 接下来

有了这一整套作为基础，agent 驱动 ob 的路就接得上了。下一步是把 V1.1 结尾规划的闭环真正跑通：agent 编完代码，自己拉起 QEMU 验证、跑基础 sanity check、把结果带回来，让开发、编译、验证收进同一个 session。再往后还有规划中的 `ob dev`，把 devtool 的 modify / reset 流程整合进 ob。

仓库里带的 Agent Skill 会继续扩充。目前在用的三个：`/brainstorming`、`/writing-plans` 和 `/grill-with-docs`，在 V1.2 这版的设计、ADR 起草和测试规划里又跑了一轮。这套流程每跑一轮，都会更清楚哪些环节该沉淀成新的 skill。

> V1.2 这版的设计和实现，仍然由 /grill-with-docs、/brainstorming 和 /writing-plans 三个 skill 驱动。从系统性治理的立意、ADR 0003 的定稿，到退出码怎么统一、测试体系分哪几层、ob-first 约定怎么落，这套流程把决策和落地串在了一起。代码部分，继续 100% AI-made。

仓库：https://github.com/iasiv5/ob-harness

Release note：https://github.com/iasiv5/ob-harness/releases/tag/v1.2

---

摘要：ob-harness V1.2 是一次系统性治理。四条互锁的主线：重构（§1-§7 物理分层 + 抽 5 个公共函数 + 清死代码，让 4200 行脚本重新可维护）、退出码统一（取消 5 处 exit 0 与 5 处 exit 2 混用、bitbake 码透传、领域函数层前提用 1 而非 3，修正 menu 把取消误报为成功的 bug，统一到 0/2/3/1 四档）、从零搭起四层测试体系（protocol / unit / orchestration / integration + CI + 双核心层交叉覆盖 + multiset baseline 防同类告警静默吸收）、立 ob-first 共识（ADR + skill + 守卫 + usage↔dispatch 防漂移测试）。四件事合在一起，让 ob 从能用升级到可被 agent 稳定依赖。