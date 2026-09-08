# DeepSeek Harness 必装插件⑤：dsh-skip-browser-auth

这一篇的由来最简单：我的云主机在 DSH 前面，早就用 Caddy 自建了一层认证。0.1.2-rc.1 新增的 BrowserAuth，要求每次把启动 URL 里的随机 token 抄进浏览器。对自用机器，这是重复劳动，也很繁琐。于是有了这个插件：装上即跳过BrowserAuth，浏览器打开 3080 端口直接用。

涉及安全，所以这也是我做得最克制的一个插件：只在实测过的版本里激活，其它版本自动休眠，官方行为分毫不变；版本探测使用双锚点加双分支确认，有任何漂移一律休眠；只移除身份层，信任栅栏原样保留，激活时日志逐字输出警告。卸载重启，官方行为完整恢复。

提醒放最后：仅限本机与可信网络，别把 DSH 端口暴露给不可信网络。

装了 dsh-m 的同学，在插件市场里搜 Skip Browser Auth 一键安装；或贴给 agent：执行 dsh plugin --profile web add @iasiv5/dsh-skip-browser-auth，重启即生效。

源码：[iasiv5/dsh-skip-browser-auth](https://github.com/iasiv5/dsh-skip-browser-auth)。

系列完结：五期装完，聊天窗口已经是像样的工作站。对 DSH 有想法、有需求的同学，评论区见。
