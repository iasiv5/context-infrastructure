# DeepSeek Harness 必装插件④：dsh-copilot-auth

如果你和我一样，用的也是 GitHub Copilot 订阅，在 DSH 的设置里却只能填 API Key 来连接。

第 4 期：copilot-auth，把设备码登录流程补上，杜绝 API Key 泄露的风险。

让 DSH 也走网页加设备码的认证流程，同 VS Code 客户端保持一致：使用设备码在浏览器里授权，回来就是已登录。全程不填 Token，SSO 组织授权友好度拉满。

我的设计原则是克制：插件不实现任何 GitHub 协议代码，token 轮换、模型发现全走 DSH 内置通道，插件只做三件事：
1、挂载授权服务；
2、提供设置页；
3、预置路由。
上游模型目录更新跟不上，刷新按钮就做一次数据级原子补丁：先看 diff，二次确认，协议代码一行不动。

规矩说在前面：Copilot 订阅自 2026 年 6 月起切换 Usage Billing Base（UBB）计费，按 Tokens / Credits 用量计量；通道为社区通用路线，非 GitHub 官方 API，公司账号请正常强度使用。

装法，贴给 DSH 会话里的 agent：

```text
帮我安装 GitHub Copilot 登录插件：
1. dsh plugin --profile web add @inventec/dsh-copilot-auth
2. 重启 DSH Web，刷新页面
3. 设置页打开 GHC 设置，点登录
```

源码：[iasiv5/dsh-copilot-auth](https://github.com/iasiv5/dsh-copilot-auth)。下一篇：skip-browser-auth，安全地拆掉一道安全检查。
