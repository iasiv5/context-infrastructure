# Skill: Public Consensus Net Income Audit Workflow

## 元数据

- **类型**: Workflow
- **适用场景**: 需要用公开网页审计一组股票的 FY / CY consensus net income，尤其是 MarketScreener、Yahoo Finance、MarketWatch 等网页源混用时。
- **创建日期**: 2026-05-06
- **推荐模型**: GPT 系列。不要把核心抽取或 QA 派给 GLM / DeepSeek。

## 目标

把"当前公开网页能追溯到的 consensus net income"整理成可审计表格，并明确区分当前 source availability、历史 baseline availability、revision comparability、direct value 和 derived value。

这个 skill 不做投资建议，不根据估计值推导市场情绪，也不把 EPS 或 revenue trend 偷换成 net income consensus。

## 验收标准

任务完成时必须同时满足这些条件：

1. 每个 ticker 都有一行 audit table；找不到公开 net income 时写清楚 `Current Source Status = Unavailable`，而不是空着。
2. 当前值、六个月前 baseline、revision direction 三件事分开表达。`Not Comparable` 只能表示 revision 无法比较，不能让读者误以为当前 consensus 缺失。
3. 每个非 `N/A` 当前值都有 source URL、retrieved at、source provider、source field、币种、单位和 fiscal period。
4. direct 和 derived 分开标记。direct 指页面明确暴露 `Net income` / `Net income 1` / `Net income Million <currency>` 的目标年度值。derived 指用页面暴露的 net sales × net margin、半年度净利润加总、或其他可复算字段得到的值。
5. 所有 source URL 在最终交付前逐链接复核。复核不只检查 HTTP 可达，还要检查页面抽取文本里能定位到 fiscal period、币种单位、source field 和目标年份列。
6. QA 记录必须列出修正过的值，尤其是列映射、币种和 direct/derived status 的修正。
7. 表格外说明使用用户偏好的自然语言。若用户要求中文说明、英文表格，就保持表格列名和值可复制，正文说明用中文。

## 可用资源

优先使用 Tavily 等网页搜索/抽取 CLI 做网页搜索和抽取。常用命令形态：

```bash
tavily search "<query>" --max-results 6 --search-depth advanced --answer advanced --stdout
tavily extract <url1> <url2> --query "Projected Income Statement Net income 1 Fiscal Period 2026 currency" --chunks-per-source 2 --output tmp/<session>/qa_extract.json
```

按你所安装的 Tavily CLI 的调用方式执行（例如本地 Python entrypoint、独立 binary 或脚本 wrapper）。生成报告到 `tmp/<session_slug>/`，若需对外发布，按你自己的静态站点生成流程同步到最终存放位置。

## 表格语义

推荐 audit table 至少包含这些列：

| Column | Meaning |
|---|---|
| `Current Source Status` | 当前公开源是否有可核对的值；可用值包括 `Available (direct)`、`Available (derived)`、`Available (semiannual direct sum)`、`Unavailable`、`Not live FY2026E` |
| `Current Consensus Estimate` | 当前采用值。只有该列缺失时才写当前值 `N/A` |
| `Baseline Status` | 六个月前同字段、同口径、同 provider baseline 是否可追溯 |
| `Direction` | revision 方向。只有 current 和 baseline 都可比时才写 Up / Down / Flat；否则写 `Not Comparable` |
| `Source Field Name` | 页面字段名，如 `Net income 1`、`Net income Million CNY`、`Net sales 1 / Net margin (%)` |
| `Calculation Notes` | 为什么采用这个页面、direct/derived 逻辑、财年和币种注意事项 |

Working sheet 要保留 provider aggregate 的采用逻辑。公开网页通常没有 firm-level analyst 明细，所以不要伪造 broker average。

## 工作流建议

先定义 universe 和目标 fiscal period，再按 ticker 并行搜索 source URL。搜索阶段可以让 subagent 分批做，但核心抽取、列映射和最终 QA 需要用 GPT 系列模型复核。这个任务对表格列位置、财年口径和币种非常敏感；GLM / DeepSeek 在本次任务中容易把 2026/2027 列、USD/CNY、direct/derived 混掉，后续不要用于核心判断。

采集完成后不要马上发布。先做一轮逐链接 QA：对所有 URL 批量 `extract`，确认 `failed_count=0`，再逐项检查目标值是否真的出现在当前抽取文本里。若 search answer、subagent 摘要和 live extract 冲突，以 live extract 和页面字段为准；如果 live extract 没暴露 direct row，而 search snippet 暴露了，表里要把证据等级写清楚。

## 已知陷阱

**MarketScreener 年份列容易错位。** annual 表通常是 2021-2028，搜索摘要会把最后一列当 2026，或者把 2027 列误读成 2026。解决办法是必须同时检查 `Fiscal Period` header、announcement dates 和目标年份列。

**Calendar 和 finances 页面可能给出不同粒度。** calendar 页常给 `Net income Million CNY` 的 annual row，finances 页常给 `Net income 1` 和 quarterly / halfyear tables。能用 calendar direct annual row 时，优先用 direct row；不要用 Q4 或半年度值冒充全年。

**区域镜像会有旧数据或不同页面状态。** `marketscreener.com`、`in.marketscreener.com` 等镜像可能暴露不同数据。最终表要标明使用的具体 URL，不跨镜像平均。

**币种不能默认换成人民币。** SMIC、Lenovo、Hua Hong 等可能按 USD million 列报。保持 MarketScreener 原始币种，除非报告明确需要换算并给出 FX source/date。

**derived 值必须降级标记。** 如果页面没有直接暴露 annual net income row，只能用 net sales × net margin 或半年度净利润加总，就把 `Current Source Status` 写成 derived / semiannual direct sum，并在 notes 写出公式。不要把 derived 伪装成 direct consensus。

**`N/A` 的含义要限定到列。** baseline 为 `N/A` 只表示没有六个月前 point-in-time 快照；current source 可用时仍要显示当前值。否则读者会以为整行没有数据。

## 输出规格

建议产出三类文件：

1. `tmp/<session>/...audit.md`：工作稿，包含 audit table、working sheet、QA 记录和 caveats。
2. `tmp/<session>/qa_extract_*.json`：逐链接 QA 抽取结果，保留证据链。
3. 如需发布，按你自己的静态站点生成流程复制最终 MD 并生成 HTML。

若任务结束后发现新的真实坑，更新本 skill 和 `rules/skills/INDEX.md`。