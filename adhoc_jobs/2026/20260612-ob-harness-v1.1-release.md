# ob-harness V1.1：一条命令拉起 QEMU 仿真

ob-harness V1.0 让 OpenBMC 的环境初始化和镜像构建变成了一条命令的事。但镜像编出来之后呢？想看看它能不能正常起来，得自己找一份能用的 QEMU binary，手动拼一长串 `qemu-system-arm` 命令行，SSH、Redfish、IPMI 端口转发逐个配，换台机器再来一遍。V1.1 把这件事也收进了 `ob`。

> 配图位 1：手工拼 `qemu-system-arm ...` 命令行截图（终端里一长行命令，作为「之前的样子」对照）。也可以做 before/after 拼图。

## 两条新命令

`ob start-qemu [machine]`：选一个编译出 Image 过的 machine，一条命令走完 QEMU binary 准备、端口分配和实例启动。

`ob stop-qemu [machine]`：安全停掉 QEMU 实例，支持按 machine 停、`--all` 批量停，或在交互菜单里选。

加上这两条，`ob` 覆盖了从 init、build 到 start-qemu、stop-qemu 的完整开发回路，镜像不必烧到实际主板就能验证 OpenBMC 的大部分上层功能。

> 配图位 2：`ob` 不带参数进入的交互菜单截图，标出新增的选项 4（start-qemu）和 5（stop-qemu）。

## 手工起 QEMU 踩的几个坑，start-qemu 怎么收

**QEMU binary 从哪来。** 社区源的 binary 挂在 OpenBMC Jenkins 上，企业定制的 QEMU 得各家自己配地址。`start-qemu` 按 `openbmc-source.lock` 里的 `source_label` 分流：community 源自动从 Jenkins 下载，并比对远程 build number，有新版本时提示更新；custom 源首次启动时让你交互输入一次地址，写进配置文件，之后直接复用。下载走 `curl -C -`，断网重连不必从头来。

> 配图位 3：`start-qemu` 首次跑 custom 源时提示输入 QEMU binary URL 的交互界面；或 community 源检测到新 build number 后的更新提示。两选一。

**架构怎么选。** AST2600 用 `qemu-system-arm`，AST2700 用 `qemu-system-aarch64`，选错了起不来。`start-qemu` 通过 `bitbake -e` 解析 `QB_SYSTEM_NAME`，自动定位到对应的 binary，不用人管。

**端口和进程管理。** 一个 BMC 实例要占 SSH、Redfish、IPMI、HTTP 四组端口，同时跑多个 machine 容易出现资源冲突。`start-qemu` 拉起前会扫一遍物理机的端口占用，有冲突就给出可选端口让你换。每个实例写一份 PID 文件，记录 PID、启动用户、machine 名、binary 路径和启动时间；后续操作前先校验进程是否还活着、binary 路径是否对得上，防止 PID 回收后误杀无关进程，也防止多人共用编译机时彼此干扰。

`stop-qemu` 先发 SIGTERM 信号，等待优雅退出，若超时，再发 SIGKILL；失效的 PID 文件也会自动清理。

`ob status` 也随之升级，会列出当前运行中的 QEMU 实例，一眼看清哪些 machine 占着资源。

> 配图位 4：`ob status` 截图，框出新增的 Running QEMU instances 区块（machine、PID、端口、启动时间）。整篇最有信息量的一张图，建议放这里。

## 接下来

有了 start-qemu，Agent 编完 OB 代码之后可以自己拉 QEMU 验证。下一步是把这条路径再往前推一步：起实例、跑基础 sanity check、返回结果，让「开发、编译、验证」收进同一个 agent session。再往后还有规划中的 `ob dev`，把 devtool 的 modify / reset 流程整合进来。

QEMU 自动启停这块从设计到落地，仍然由 `/grill-with-docs`、`/brainstorming` 和 `/writing-plans` 这三个 skill 驱动。过程中 `/grill-with-docs` 沉淀出的术语表和 ADR 文档，后续也会考虑融合进 ob-harness 的基础设施层。

> 配图位 5（可选）：BMC 在 QEMU 里启动成功的截图，比如串口登录提示符、浏览器访问 Redfish 端点返回的 JSON。视觉收尾。

仓库地址：https://github.com/iasiv5/ob-harness

Release note：https://github.com/iasiv5/ob-harness/releases/tag/v1.1

---

摘要：ob-harness V1.1 新增 `ob start-qemu` 和 `ob stop-qemu`，把 BMC 镜像在 QEMU 上的启停纳入 `ob` 工作台。start-qemu 自动处理 QEMU binary 来源（community 比对 Jenkins build number、custom 交互记忆地址、断点续传）、按 `QB_SYSTEM_NAME` 区分 AST2600 / AST2700 架构、检测端口冲突、PID 文件防误杀；stop-qemu 支持单停或 `--all` 批量停，优雅退出失败再降级 SIGKILL。`ob` 由此覆盖 init / build / start-qemu / stop-qemu 完整回路。