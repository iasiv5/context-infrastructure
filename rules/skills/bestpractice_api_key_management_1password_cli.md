---
title: API Key 管理与调用最佳实践（1Password CLI）
category: BestPractice
tags: [security, api-key, 1password, op-cli, environment-variables]
difficulty: Medium
related_projects: [dotfiles, debianinit]
created: 2026-02-13
updated: 2026-02-13
---

# API Key 管理与调用最佳实践（1Password CLI）

本文总结本地开发与生产环境中，如何使用 1Password CLI（`op`）安全管理并注入 API Key，避免明文泄漏与长期驻留风险。

## 1. 核心原则

1. 不在 `.zshrc`、仓库文件、脚本参数中存放明文密钥。
2. 本地开发使用 `op run --env-file ... -- <command>` 按需注入。
3. 生产环境使用机器身份（Service Account），不要依赖桌面 App 指纹弹窗。
4. 密钥最小权限、可轮换、可吊销，泄漏后优先 rotate。

## 2. 本地开发（Mac）推荐模式

### 2.1 使用 secret reference 而非明文

在本地文件 `~/.config/op/env.secrets` 存放引用：

```dotenv
OPENAI_API_KEY=op://dev/dev-api-keys/openai_api_key
TAVILY_API_KEY=op://dev/dev-api-keys/tavily_api_key
GEMINI_API_KEY=op://dev/dev-api-keys/gemini_api_key
```

此文件不包含明文密钥，可安全于本机保存（建议权限 `600`）。

### 2.2 命令级注入

```bash
op run --env-file ~/.config/op/env.secrets -- python app.py
op run --env-file ~/.config/op/env.secrets -- nvim
```

优点：只对目标进程生效，不污染当前 shell 的全局环境变量。

### 2.3 关于指纹/密码授权

本地出现 1Password 授权弹窗是正常安全行为。通常只在 1Password 锁定时触发，并非每条命令都重复授权。频率由自动锁定策略决定。

## 3. 生产环境（无交互）推荐模式

生产环境目标是“可自动重启、可无人值守”，不应依赖桌面授权。

推荐方案：

1. 创建 1Password Service Account（只读、限定 vault）。
2. 在服务器安全保存 `OP_SERVICE_ACCOUNT_TOKEN`（如 systemd EnvironmentFile）。
3. 启动脚本内使用 `op read` 拉取密钥后启动进程管理器（如 PM2）。

示意：

```bash
export OPENAI_API_KEY="$(op read 'op://dev/dev-api-keys/openai_api_key')"
pm2 start ecosystem.config.js --env production --update-env
pm2 save
```

## 4. 避免的反模式

1. 在 `.zshrc` 里 `export API_KEY=...` 明文。
2. 在命令行参数里直接传密钥（会落历史、可被进程查看）。
3. 把同一组 key 混用在 dev/staging/prod。
4. 只做“导入”不做“轮换”，导致历史泄漏长期有效。

## 5. 最小落地清单

1. 清理 dotfiles 中明文密钥。
2. 建立 `dev-api-keys` item，并统一字段命名（snake_case）。
3. 使用 `~/.config/op/env.secrets` + `op run`。
4. 为生产环境配置 Service Account token 注入链路。
5. 为密钥设置定期轮换流程与泄漏应急流程。

## 6. 字段命名约定

vault 固定 `dev`，item 固定 `dev-api-keys`。推断新 service 的 1Password 路径时，按以下规则拼 field name：

| 类型 | 模式 | 示例 |
|---|---|---|
| API key（最常见） | `<service>_api_key` | `ollama_api_key`、`typefully_api_key`、`koyeb_api_key` |
| Token | `<service>_<descriptor>_token` | `circle_api_v2_token`、`ai_builder_space_token`、`data_for_seo_token` |
| 应用专用密码 | `<service>_app_password` | `gmail_skill_app_password` |
| Webhook 签名密钥 | `<service>_<use>_signing_secret` | `resend_webhook_signing_secret` |
| Account ID | `<service>_account_id` | `cloudflare_account_id` |
| 用户名/密码对 | `<service>_username` / `<service>_password` | `twine_username` / `twine_password` |
| 环境变体 | `<service>_api_key_<env>` | `shippo_test_api_key`、`deepseek_api_key_opencode`、`resend_api_key_full` |

完整路径：`op://dev/dev-api-keys/<field_name>`。

**推断流程：**
1. 确定 service 名（typefully、kimi、deepseek…），snake_case。
2. 加对应类型后缀（默认 `_api_key`）。
3. 拼成 `op://dev/dev-api-keys/<field>`。
4. 如果不确定 field 是否存在，先列出现有 field 确认：`op item get dev-api-keys --vault dev --format json` 后检查 `fields[*].label`。避免因拼写（如 `olama` vs `ollama`）静默失败。

## 7. 代码中调用 API Key

在 Python/Node 脚本中，不要硬编码或读取 .env，而是通过 `op read` 获取：

```python
import subprocess
import os

def get_api_key(service: str) -> str:
    """从 1Password 获取 API key。
    
    Args:
        service: 如 'tavily_api_key', 'openai_api_key'
    """
    # 优先环境变量（CI/CD 场景）
    env_key = os.environ.get(service.upper())
    if env_key:
        return env_key
    
    # 从 1Password 读取
    result = subprocess.run(
        ["op", "read", f"op://dev/dev-api-keys/{service}"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()

# 使用
api_key = get_api_key("tavily_api_key")
```

**要点**：
1. 优先检查环境变量（兼容 CI/CD）
2. 本地开发走 `op read`
3. vault 路径统一为 `op://dev/dev-api-keys/<service>`
