# DeepSeek Harness 必装插件①：dsh-m

给 agent 装插件，应该像聊天一样自然。所以我推荐的第一件必装，是插件市场。

第 1 期，先搭货架。dsh-m 是一个开在 DeepSeek Harness 侧栏里的插件市场，收录表可以自定义，默认的 registry.json 来自我的自用精选。卡片展开即装，进度实时可见，装完一键重启；一条命令一次装齐 Web 插件、7 个 agent 工具和 CLI。

对 agent 说要装 dsh-skins，它自己搜、自己装；团队想维护内部源，收录清单整体覆盖官方清单就行；每个包按精确版本校验，GitHub 源锁定 commit，校验不过不放行。

把这段贴给 DSH 会话，坐等装好：

```text
安装并启用 DSH 插件 dsh-m：
1. 执行 `dsh plugin --profile web add dsh-m`
2. 重启 DSH Web 使插件加载
3. 轮询 `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:3080`，直到恢复 200
4. 执行 `curl -s -X POST http://127.0.0.1:3080/dshm -H 'content-type: application/json' -d '{"method":"ping"}'`，确认返回 `plugin: dsh-m`
5. 完成后提醒我刷新页面，点击侧栏底部的「插件市场」
```

源码：[iasiv5/dsh-m](https://github.com/iasiv5/dsh-m)。下一篇换张脸：dsh-skins。
