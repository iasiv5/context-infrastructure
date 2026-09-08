# 番外 · DSH 插件扩展点地图

「给 DeepSeek Harness 装修」五期机制卡的合订本。一个插件能挂在 DSH 的哪些位置，这张图说全。

## 五个扩展点

| # | 插件 | 扩展点 |
|---|---|---|
| 01 | dsh-m | Web 插件 + agent 工具注册（dshm_*）+ CLI |
| 02 | dsh-skins | 侧栏 footer 入口 + 官方主题服务 + URL 参数 |
| 03 | better-sidebar | 服务化注册：registerTab / registerFileViewer |
| 04 | copilot-auth | patch 三段式：挂服务 · 本地路由 · settings 预置 |
| 05 | skip-browser-auth | patch 替换 + 组合期版本探针 · fail-closed |

## 如何选择

从入口注册到替换内核，五个位置由浅入深，能力与风险同步增长。挂得浅，能力受限于宿主留出的口子；挂得深，行为可替换，就要自己补上宿主原本给你的保证——比如版本白名单与 fail-closed。

对应成图暂未入库，随系列图片一并发布（见 README）。
