# 给 DeepSeek Harness 装修 · 系列图文（2026）

iasi.AI 公众号「DeepSeek Harness 必装插件」系列，共五期正片 + 一张番外图。本目录收录该系列的**文字正式产出**，供 upstream 到 GitHub。

## 系列结构

| 期 | 插件 | 层 | 作者 |
|---|---|---|---|
| 01 | [dsh-m](https://github.com/iasiv5/dsh-m) | 货架 · 插件市场 | iasiv5 |
| 02 | [dsh-skins](https://github.com/iasiv5/dsh-skins) | 脸面 · 皮肤 | iasiv5（维护者） |
| 03 | [dsh-better-sidebar](https://github.com/omdsh-dev/DSH-better-sidebar) | 工作台 · 侧边栏 | omdsh-dev（第三方，本期为评测） |
| 04 | [dsh-copilot-auth](https://github.com/iasiv5/dsh-copilot-auth) | 电源 · GitHub Copilot 登录 | iasiv5 |
| 05 | [dsh-skip-browser-auth](https://github.com/iasiv5/dsh-skip-browser-auth) | 门锁 · 跳过 BrowserAuth | iasiv5 |

主线：把 DeepSeek Harness 从聊天窗口，装修成一个真正的工作站——分发、外观、工作台、接入、信任，五层递进。

## 文件对照

| 文件 | 内容 |
|---|---|
| `series_plan.md` | 总策划：系列定位、每期立意、机制卡体系、合规清单 |
| `00_系列统一元素.md` | 系列名、封面模板、固定栏目、lint 口径 |
| `articles/01..05_发布文案.md` | 五期公众号正文（每篇 ≤300 字，含安装提示词与源码地址） |
| `bonus_extension_map.md` | 番外「DSH 插件扩展点地图」文字版 |

## 图片说明

五期贴图卡（共 58 张 3:4 卡 + 1 张番外地图）由设计管线生成，**暂未收入本目录**。成图与制作源文件位于仓库工作区 `adhoc_jobs/articles_archive/dsh_plugin_article_series/cards/<期>/output/`，需要时可按期补入或改由发布时直传公众号。

## 发布约定

- 每期固定栏目：机制卡（扩展点）、提示词安装卡、设计决策卡、预告卡
- 合规：05 期「跳过认证」全程用信任边界框架表述；04 期计费表述为 UBB（2026-06 起）；02 期粉丝作品边界声明随文
- 文字均通过 external-prose-lint（0 hard findings）
