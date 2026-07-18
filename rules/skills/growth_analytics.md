---
title: 增长数据分析工具集
category: API Guide
tags: [analytics, ga4, kit, gsc, typefully, growth, metrics]
created: 2026-03-14
updated: 2026-03-29
---

# Skill: 增长数据分析（GA4 / Kit / GSC / Typefully / short_url）

五个数据入口，分别查询网站流量（GA4）、邮件订阅（Kit）、搜索引擎表现（GSC）、Twitter 发布与互动（Typefully），以及短链接点击与转化链路（short_url）。

## When to Use

用户说出以下意图时触发：
- "查一下最近的流量"、"网站数据怎么样"
- "订阅者增长了多少"、"打开率多少"
- "搜索排名怎么样"、"GSC 数据"、"关键词表现"
- "Twitter 互动数据"、"impression 多少"
- "短链点击怎么样"、"short_url 数据"
- "做一下增长分析"、"拉一下 growth 数据"
- 任何涉及网站、Newsletter、搜索引擎指标、社交媒体指标的查询

## Prerequisites

- 根目录 `.env` 包含：
  - `KIT_API_KEY` — Kit (ConvertKit) API v4 key
  - `TYPEFULLY_API_KEY` — Typefully v2 API key（发布查询用）
  - `GA4_CREDENTIALS_PATH` — GA4/GSC service account JSON 文件的绝对路径（两个工具共用同一个 service account）
- GA4 和 GSC CLI 共享认证：都从 `GA4_CREDENTIALS_PATH` 读取 service account JSON，但各自使用不同的 API scope（GA4 用 Analytics Data API，GSC 用 Webmasters API）
- Typefully 浏览器级凭据（可选，仅 engagement metrics 需要）：
  - `TYPEFULLY_AUTHORIZATION`、`TYPEFULLY_ACCOUNT`、`TYPEFULLY_SESSION`
- `short_url.db` 位于你的短链接项目数据目录中
- Python venv 已激活（`source .venv/bin/activate`）

## 工具一：Kit 订阅数据

使用 `kit-skill analytics` CLI（见 [kit-skill](https://github.com/grapeot/kit-skill)）：

```bash
cd <kit-skill-project-dir>
op run --env-file=.env -- .venv/bin/kit-skill analytics account --format json
op run --env-file=.env -- .venv/bin/kit-skill analytics growth --format json
op run --env-file=.env -- .venv/bin/kit-skill analytics growth --start-date 2026-02-28 --end-date 2026-03-14 --format json
op run --env-file=.env -- .venv/bin/kit-skill analytics email-stats --format json
op run --env-file=.env -- .venv/bin/kit-skill analytics subscriber-count
op run --env-file=.env -- .venv/bin/kit-skill analytics broadcasts --limit 10 --format json
op run --env-file=.env -- .venv/bin/kit-skill analytics broadcast-stats <broadcast-id> --format json
op run --env-file=.env -- .venv/bin/kit-skill analytics snapshot --format json
op run --env-file=.env -- .venv/bin/kit-skill analytics snapshot --output /tmp/kit_snapshot.json
op run --env-file=.env -- .venv/bin/kit-skill analytics sequences --format json
op run --env-file=.env -- .venv/bin/kit-skill analytics sequence <sequence-id> --format json
op run --env-file=.env -- .venv/bin/kit-skill analytics sequence <sequence-id> --include-subscribers --format json
```

### Kit 关键指标

- **growth_stats**：时间段内的新增、退订、净增、总数
- **email_stats**：90 天汇总发送量、打开数、点击数
- **broadcast stats**：单期 open_rate、click_rate、unsubscribes
- **subscribers**：活跃/非活跃/退订订阅者列表和总数；`subscriber-count` 是全账户 active count，不等于某个 newsletter tag 的发送人数；列表命令默认脱敏 email，只有私有输出场景才加 `--show-emails`
- **audience 口径**：若你把多个人群合并进 Kit 并用 tag 区分（例如 `audience:example` 标记某条 newsletter 人群），newsletter/日报规模一律看对应 tag：`kit-skill analytics subscriber-count --tag audience:example`（列出全部 tag 用 `analytics tags`）；账户级 active count 是所有人群的并集，growth 端点跨合并日的窗口会把合并算进"新增"
- **sequences / sequence**：欢迎序列等 automation 的 active 状态、邮件数、当前在列订阅者数。`subscriber_count` 是流转口径（订阅者完成全部邮件后转出），自然订阅 2-3 人/天时稳态在列 8-15 人；判断健康看它是否在这个区间波动，不要期望它随累计订阅增长
- **sequence e2e 验证**：在 kit-skill 项目目录内运行 `KIT_ENABLE_LIVE_TESTS=1 .venv/bin/python -m pytest -m live_integration tests/test_analytics.py`（默认 skip；会创建探针订阅者走一遍真实序列，跑完需清理探针）

## 工具二：GA4 网站流量

```bash
python tools/ga4_metrics.py daily --days 7        # 每日流量趋势
python tools/ga4_metrics.py weekly --days 90       # 周级汇总
python tools/ga4_metrics.py top-pages --limit 20   # 热门页面
python tools/ga4_metrics.py sources                # 流量来源明细
python tools/ga4_metrics.py channels               # 渠道分组
python tools/ga4_metrics.py campaigns --days 14    # UTM campaign 归因（Twitter 效果追踪）
python tools/ga4_metrics.py snapshot --output /tmp/ga4_snapshot.json  # 全量
```

### GA4 关键指标

- **daily/weekly**：activeUsers, newUsers, sessions, screenPageViews, averageSessionDuration, bounceRate
- **top-pages**：pagePath, pageTitle, screenPageViews, activeUsers
- **sources**：sessionSource, sessionMedium 维度的流量分布
- **channels**：sessionDefaultChannelGroup（Direct, Organic Search, Referral, Social 等）
- **campaigns**：sessionCampaignName — 用于验证 UTM 标记的 Twitter thread 等是否真正带来了流量

### GA4 Property

- 主站 property ID 形如 `<your-ga4-property-id>`（在你的 GA4 后台获取）
- 若有多个站点（例如主站和子站），各自绑定不同的 `G-` measurement ID，但可以在同一个 Google Analytics account 下共用同一个 service account 认证
- Service Account JSON 位置：由 `.env` 中 `GA4_CREDENTIALS_PATH` 指定

## 工具三：GSC 搜索引擎数据（Google Search Console）

```bash
python tools/gsc_metrics.py overview --days 30          # 总览：总点击、展现、CTR、平均排名
python tools/gsc_metrics.py top-queries --days 30 --limit 20  # 热门搜索词
python tools/gsc_metrics.py top-pages --days 30 --limit 20    # 热门着陆页
python tools/gsc_metrics.py daily --days 30                 # 每日趋势
```

### GSC 关键指标

- **overview**：总 clicks、总 impressions、平均 CTR、平均 position
- **top-queries**：query 维度的 clicks, impressions, ctr, position（按 clicks 降序）
- **top-pages**：page 维度的 clicks, impressions, ctr, position（按 clicks 降序）
- **daily**：date 维度的 clicks, impressions, ctr, position（按日期升序）

### GSC Property

- 默认 Site URL：`sc-domain:example.com`（域名级 property，替换为你的实际域名）
- 若有多个域名，可通过 `GSC_SITE_URL` 环境变量或 `--site sc-domain:<your-domain>` 直接查询
- 默认查询天数：30 天
- 认证与 GA4 共用同一个 service account（`GA4_CREDENTIALS_PATH`），但使用独立的 scope（`webmasters.readonly`）

### GSC 注意事项

- GSC 数据有 2-3 天延迟，当天发布的内容不会立即出现
- GSC 的 25,000 行/请求限制意味着超大数据集需要分页（工具已内置分页逻辑）

## 工具四：Typefully Twitter 数据

### 统一 Typefully/X CLI

走 typefully-twitter-skill：

```bash
cd <typefully-twitter-skill-project-dir>
.venv/bin/typefully-twitter doctor config --format json
.venv/bin/typefully-twitter post list --status published --limit 10 --format json
.venv/bin/typefully-twitter metrics snapshot --start-date 2026-03-01 --end-date 2026-03-14 --format json
.venv/bin/typefully-twitter x fetch --days 7 --format json
```

详见 [typefully-twitter-skill](https://github.com/grapeot/typefully-twitter-skill)。Typefully 发布、Typefully account-level metrics、X per-post analytics 是三组独立凭据；`doctor config` 会分别报告可用能力。

## 工具五：Short URL & Conversion Analytics (short_url.db)

用于追踪短链接点击、转化归因以及社区标签同步。

### 数据库位置与同步

- **位置**：你的短链接项目数据目录中的 `short_url.db`
- **同步**：若数据库源文件在远端服务器，通过 rsync 等方式拉取本地副本，不是自动实时同步

### 核心 Schema
- `short_links`：存储短链接配置（`short_code`, `long_url`, `circle_tag_name` 等）
- `access_logs`：存储点击日志（`short_code`, `ip_address`, `user_agent`, `accessed_at`）
- `circle_tag_cache`：存储标签元数据（`tag_id`, `tag_name`, `member_count`）

### 关键解读规则：SSO vs. Acquisition
**SSO 是认证路径，不是获客标签。**
- 分析应采用二维视角：**认证路径**（SSO, Email, etc.）与 **获客标签**（Affiliate, Landing Page, etc.）
- SSO 登录的用户可能同时带有 affiliate 或 landing-page 标签，两者并不互斥
- 不要把报表里的 residual `sso` 桶误读为全部 SSO 用户。现有报表通常是先按 tag 分类，再把剩余的 SSO 单列出来

### 关联逻辑 (Joins)
1. **short_url -> 社区**：通过 `circle_tag_name` 对齐。它适合做按 tag 的趋势对比，不是 user-level 归因
2. **社区 -> 支付**：通过 `email` 关联。社区成员邮箱与支付记录匹配
3. **short_url -> 支付**：没有直接 join。要经过 `circle_tag_name -> 社区 member -> email -> 支付平台` 这条间接链路，并明确写出口径局限

### 查询示例 (sqlite3)

```bash
# 查看特定短链接的点击趋势
sqlite3 <path>/short_url.db \
  "SELECT date(accessed_at), count(*) FROM access_logs WHERE short_code = 'your_code' GROUP BY 1;"

# 查看某个 tag 对应的短链点击
sqlite3 <path>/short_url.db \
  "SELECT short_code, circle_tag_name, count(*) AS clicks FROM short_links LEFT JOIN access_logs USING(short_code) WHERE circle_tag_name = 'your_tag' GROUP BY short_code, circle_tag_name;"

# 查看所有带标签的短链接
sqlite3 <path>/short_url.db \
  "SELECT short_code, circle_tag_name, long_url FROM short_links WHERE circle_tag_name IS NOT NULL;"
```

## 典型用法

### 快速查看增长概况

```bash
# 一条命令看 Kit 全量
cd <kit-skill-project-dir> && op run --env-file=.env -- .venv/bin/kit-skill analytics snapshot --format json

# 一条命令看 GA4 全量
python tools/ga4_metrics.py snapshot

# 一条命令看 GSC 全量
python tools/gsc_metrics.py overview --days 30
```

### SEO 诊断：GSC + GA4 交叉对比

```bash
# GSC: 用户搜什么词进来的
python tools/gsc_metrics.py top-queries --days 30 --limit 20

# GA4: 这些词对应的着陆页表现如何
python tools/ga4_metrics.py top-pages --limit 20

# GSC: 哪些页面有展现但 CTR 低（需要优化标题/描述）
python tools/gsc_metrics.py top-pages --days 30 --limit 50
```

### 验证 Twitter 推广效果

```bash
# 查 GA4 UTM campaign 数据，看 Twitter thread 是否带来了流量
python tools/ga4_metrics.py campaigns --days 14
```

### 转化归因：Short URL + 社区 + 支付

```bash
# 1. 查短链接点击
sqlite3 <path>/short_url.db "SELECT count(*) FROM access_logs WHERE short_code = 'xyz';"

# 2. 查社区标签成员（配合社区 analytics 工具）
# 3. 查支付记录（配合支付分析 skill）
# 核心：社区里把 auth path 和 acquisition tag 分开看；short_url 用 circle_tag_name 对齐社区，社区用 email 对齐支付
```

### 交叉分析

同时拉取 Kit、GA4、GSC、short_url，再和社区/支付做对照：

```bash
cd <kit-skill-project-dir> && op run --env-file=.env -- .venv/bin/kit-skill analytics growth --start-date 2026-03-01 --end-date 2026-03-14 --format json
python tools/ga4_metrics.py weekly --days 30
python tools/gsc_metrics.py daily --days 30
sqlite3 <path>/short_url.db "SELECT date(accessed_at), count(*) FROM access_logs GROUP BY 1 ORDER BY 1 DESC LIMIT 30;"
```

## 数据存储

如需持久化历史数据，用 `--output` 参数保存 JSON。

## 注意事项

- Kit API rate limit：120 requests / 60 seconds
- GA4 Data API 有配额限制，snapshot 命令一次跑多个 report，注意不要频繁调用
- GSC Data API 有 25,000 行/请求限制，工具已内置分页；数据有 2-3 天延迟
- Typefully engagement API 是私有 API，可能随时变动
- `short_url.db` 是本地同步副本，不是实时库。分析前先确认最近一次同步时间
- `short_url` 点击与社区注册之间没有 user-level join。它适合做同一 tag 的多层信号对照，不适合写成精确端到端转化率
- 所有工具默认输出 JSON 到 stdout，可用 `| python3 -m json.tool` 格式化