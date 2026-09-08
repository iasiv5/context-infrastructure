# DeepSeek Harness 必装插件③：dsh-better-sidebar

前两期都是我自己做的插件，这一期换一件我裂墙推荐的作品：omdsh-dev 的 dsh-better-sidebar。它把聊天窗口旁边，变成一套完整的工作台：文件树、代码编辑器、真实终端、内嵌浏览器、Git 文件变动、后台任务、侧边对话。

最让我服气的是它的开放：注册接口开放给所有插件，内置页签和 28 个以上的生态插件走同一套 API。流镜、服务器监控、Agent 浏览器，都是第三方接上这个底座做出来的，并可额外独立安装、独立开关。

我的日常用法：底部终端跑 OpenBMC 构建，Git 视角看模型这轮改了什么，代码和文档渲染成页面，在右边直接看、直接改。

一站式工作台的意义：不用再开第二个窗口，也不用再开第二个 APP。

装法，贴给 DSH 会话里的 agent：

```text
帮我安装 dsh-better-sidebar 插件（DSH 侧边栏工作台），步骤：
1. 执行 dsh plugin --profile web add dsh-better-sidebar@latest（首次会被 pnpm 11 拦截 node-pty 构建脚本而失败，属正常）
2. 在 ~/.dsh/profiles/web 下执行 pnpm approve-builds --all（放行构建脚本，会自动重跑安装）
3. 再次执行 dsh plugin --profile web add dsh-better-sidebar@latest
4. 完成后提醒我硬刷新浏览器（Cmd/Ctrl+Shift+R）
遇到报错先查 https://github.com/omdsh-dev/DSH-better-sidebar README 的常见问题表。
```

源码：[omdsh-dev/DSH-better-sidebar](https://github.com/omdsh-dev/DSH-better-sidebar)。生态目录：GitHub topic dsh-better-sidebar。下一篇：copilot-auth，接上公司发的电。
