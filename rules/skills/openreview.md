# Skill: OpenReview API

查询 AI 学术会议的论文 metadata 和作者 profile。覆盖 ICLR、NeurIPS、ICML 等 OpenReview 托管会议。

## When to Use

- 拿某个会议的 accepted paper 列表（title、authors、authorids）
- 查某个作者的 profile：institution history、position、起止年份
- 按名字搜索作者，找到 tilde ID
- 批量查一组 tilde ID 的 profile

## CLI 工具

路径：your CLI script（例如 `tools/openreview_cli.py` 或你 workspace 中的对应入口）。

依赖：`openreview-py`（在你的 Python 环境中安装）。

认证：使用你自己的 OpenReview account。`.env` 里的 `openreview_email` / `openreview_password`，或环境变量 `OPENREVIEW_EMAIL` / `OPENREVIEW_PASSWORD`。Token 自动缓存到 `tmp/openreview_token.json`，避免重复登录触发 rate limit（login 限 3 次/窗口）。

### 子命令

```bash
# 获取会议 accepted papers
python <your_cli_script> papers ICLR.cc/2024/Conference
python <your_cli_script> papers NeurIPS.cc/2024/Conference -o papers.json

# 查单个 profile
python <your_cli_script> profile ~Bohan_Lyu1
python <your_cli_script> profile ~Bohan_Lyu1 --publications --relations

# 按名字搜索
python <your_cli_script> search "Bohan Lyu"
python <your_cli_script> search "Chen Zhang" --institution "Peking University"

# 批量查 profiles
python <your_cli_script> profiles --ids "~A1,~B2,~C3"
python <your_cli_script> profiles --ids-file author_ids.txt
```

### 输出格式

默认 stdout JSON。加 `-o path.json` 写文件（stdout 只返回 `{"status":"ok","file":"...","summary":"..."}`）。

Profile JSON 结构：

```json
{
  "id": "~Bohan_Lyu1",
  "preferred_name": "Bohan Lyu",
  "all_names": ["Bohan Lyu"],
  "history": [
    {
      "position": "Undergrad student",
      "start": 2022, "end": 2026,
      "institution": "Tsinghua University",
      "domain": "tsinghua.edu.cn",
      "country": "CN",
      "city": null, "department": null
    }
  ],
  "emails": ["****@mails.tsinghua.edu.cn", "****@gmail.com"],
  "homepage": "",
  "dblp": "", "google_scholar": "", "semantic_scholar": ""
}
```

Paper JSON 结构：

```json
{
  "id": "rhgIgTSSxW",
  "title": "TabR: Tabular Deep Learning Meets Nearest Neighbors",
  "authors": ["Yury Gorishniy", "Ivan Rubachev"],
  "authorids": ["~Yury_Gorishniy1", "~Ivan_Rubachev1"],
  "venue": "ICLR 2024 poster",
  "venueid": "ICLR.cc/2024/Conference",
  "abstract": "...",
  "keywords": ["tabular", "deep learning"],
  "primary_area": "...",
  "pdf": "/pdf/..."
}
```

## 已确认的 Venue ID

| 会议 | Venue ID |
|------|----------|
| ICLR 2024 | `ICLR.cc/2024/Conference` |
| ICLR 2025 | `ICLR.cc/2025/Conference` |
| NeurIPS 2024 | `NeurIPS.cc/2024/Conference` |
| NeurIPS 2023 | `NeurIPS.cc/2023/Conference` |
| ICML 2024 | `ICML.cc/2024/Conference` |

CVPR 2023+ 可能可用，AAAI/ACL 覆盖有限，需逐个确认。

## 已知限制

1. **Affiliation 不在 paper 上。** paper 只有 authorids，机构信息在 profile 里。流程：papers → 提取 authorids → 批量查 profiles → 读 history。
2. **邮箱被遮蔽。** 公开 API 只返回域名部分（`****@tsinghua.edu.cn`），拿不到完整邮箱。
3. **History 是自填的。** 实测 ICLR 作者群体填充率高（100% history、85% country），但不保证所有用户都如此。需要用机构名匹配 + email 域名（`.edu.cn`）做兜底判断中国机构。
4. **Login rate limit。** 每个时间窗口最多 3 次登录。CLI 已做 token 缓存，正常使用不会触发。如果 token 过期导致 403，删除 `tmp/openreview_token.json` 后重试一次即可。
5. **常见名搜索噪声大。** `search "Chen Zhang"` 返回 247 个结果。用 `--institution` 过滤，或优先从 paper authorids 直接查 profile 而不是按名字搜。

## 典型工作流

### 从会议批量获取中国学生论文作者

```bash
# 1. 拿 papers
python <your_cli_script> papers ICLR.cc/2024/Conference -o tmp/iclr2024_papers.json

# 2. 提取所有 authorids
cat tmp/iclr2024_papers.json | python -c "
import sys,json
papers = json.load(sys.stdin)
ids = set()
for p in papers:
    ids.update(p['authorids'])
print('\n'.join(sorted(ids)))
" > tmp/iclr2024_authorids.txt

# 3. 批量查 profiles
python <your_cli_script> profiles --ids-file tmp/iclr2024_authorids.txt -o tmp/iclr2024_profiles.json
```

### 查已知候选人的 OpenReview profile

```bash
# 按名字搜索 + 机构过滤
python <your_cli_script> search "Xiaohu Huang" --institution "Hong Kong"

# 如果知道 tilde ID，直接查
python <your_cli_script> profile ~Xiaohu_Huang1
```

## 测试

按你 CLI 工具自带的测试流程执行，覆盖全部 4 个子命令。这些测试调用 live API，需要有效 credentials。