#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ctx_window_probe.py — 实测 GLM-5.2（经智谱 Anthropic 兼容端点）最大输入上下文。

策略（锚点优先，针对官方宣称的 1M 上下文优化）：
  0. 自检 + 校准「字符数 / token」填充比例。
  1. 直接打锚点（默认 1,000,000）：
       - 成功 → 官方宣称属实；再往上探一小段（默认 +5%×3 次）找真实硬上限，找到则二分精确定位。
       - 失败 → 尝试从报错消息抠 API 透露的 maximum；抠不到则二分 [自检点, 锚点]。
  2. 二分精扫到设定精度。

  关键：区分两类失败——
    -「输入过长 / 上下文超限」→ 用于判定边界
    -「HTTP 413 / payload too large」→ 网关 body 限制，非上下文限制，单独标记不误判

零依赖（仅标准库 urllib）。密钥只从环境变量读，绝不打印。
"""

import argparse
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.request

BASE_URL = os.environ.get("ANTHROPIC_BASE_URL",
                          "https://open.bigmodel.cn/api/anthropic").rstrip("/")
TOKEN = os.environ.get("ANTHROPIC_AUTH_TOKEN") or os.environ.get("ANTHROPIC_API_KEY")
API_PATH = "/v1/messages"

FILLER_UNIT = "这是用于上下文窗口长度测试的填充段落。"
TAIL_INSTRUCTION = "\n\n请忽略上方所有填充内容，不要做任何思考，只回复一个数字1。"

# 上下文超限的标志词
TOO_LONG_MARKERS = ["too long", "context length", "maximum context", "context window",
                    "reduce the length", "exceed", "maximum", "input length"]
# 网关 body 大小限制的标志词（与上下文限制区分）
BODY_SIZE_MARKERS = ["413", "payload too large", "request entity too large",
                     "request too large", "content too large", "body size"]


def log(msg):
    print(msg, flush=True)


def classify_failure(info):
    """判定失败类型：'context' / 'body_size' / 'transient' / 'other'。"""
    status = info.get("http_status")
    body = (info.get("body") or "").lower()
    if any(m in body for m in BODY_SIZE_MARKERS) or status == 413:
        return "body_size"
    if any(m in body for m in TOO_LONG_MARKERS):
        return "context"
    if status in (429, 500, 502, 503, 504) or status is None:
        return "transient"
    return "other"


def call_api(model, prompt_text, max_tokens=64, timeout=300):
    url = BASE_URL + API_PATH
    body = json.dumps({
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt_text}],
    }).encode("utf-8")
    headers = {
        "content-type": "application/json",
        "anthropic-version": "2023-06-01",
        "authorization": "Bearer " + TOKEN,
    }
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8", "replace"))
            usage = data.get("usage", {}) or {}
            return True, {"input_tokens": usage.get("input_tokens"),
                          "output_tokens": usage.get("output_tokens")}
    except urllib.error.HTTPError as e:
        return False, {"http_status": e.code,
                       "body": e.read().decode("utf-8", "replace")}
    except Exception as e:
        return False, {"http_status": None, "body": str(e)}


def call_with_retry(model, prompt_text, max_tokens=64, max_retries=4):
    """退避重试。body_size / context 类不重试；transient 类退避重试。"""
    ok, info = False, {}
    for attempt in range(max_retries):
        ok, info = call_api(model, prompt_text, max_tokens=max_tokens)
        if ok:
            return ok, info
        kind = classify_failure(info)
        if kind in ("context", "body_size", "other"):
            return ok, info
        # transient
        wait = 2 ** attempt
        log(f"  [retry] 暂时性失败 (status={info.get('http_status')})，{wait}s 后重试…")
        time.sleep(wait)
    return ok, info


def find_context_limit(text):
    """从报错消息抠 API 透露的 maximum context（tokens）。"""
    patterns = [
        r"maximum\s*(?:context|length|tokens?|input)?[:\s]*([0-9]{1,3}(?:,[0-9]{3})+|[0-9]{4,})",
        r"max(?:imum)?\s*(?:context|length|tokens?)[:\s]*([0-9]{1,3}(?:,[0-9]{3})+|[0-9]{4,})",
        r"limit(?:ed)?\s*(?:to)?[:\s]*([0-9]{1,3}(?:,[0-9]{3})+|[0-9]{4,})",
        r">\s*([0-9]{4,})\s*(?:tokens?)?",
        r"([0-9]{1,3}(?:,[0-9]{3})+|[0-9]{4,})\s*-?token\s+(?:context|window|limit)",
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return int(m.group(1).replace(",", ""))
    return None


def build_prompt(target_tokens, chars_per_token):
    target_chars = max(1, int(target_tokens * chars_per_token))
    n_units = math.ceil(target_chars / len(FILLER_UNIT))
    return (FILLER_UNIT * n_units)[:target_chars] + TAIL_INSTRUCTION


def bisect(lo, hi, precision, model, cpt):
    """二分 [lo, hi] 到 precision，返回 (lo, hi, added_tokens)。"""
    added = 0
    while hi - lo > precision:
        mid = (lo + hi) // 2
        ok, info = call_with_retry(model, build_prompt(mid, cpt))
        used = info.get("input_tokens") if ok else None
        log(f"    mid={mid:>9} | {'OK  ' if ok else 'FAIL'} | 实际={used} | ({lo}, {hi})")
        if ok:
            added += used or mid
            lo = used or mid
        else:
            hi = mid
        time.sleep(0.4)
    return lo, hi, added


def main():
    ap = argparse.ArgumentParser(description="实测 GLM-5.2 最大输入上下文（锚点优先）")
    ap.add_argument("--model", default=os.environ.get("ANTHROPIC_MODEL", "glm-5.2"))
    ap.add_argument("--anchor", type=int, default=1_000_000, help="锚点 token 数（官方宣称值）")
    ap.add_argument("--ceiling", type=int, default=1_500_000, help="向上探测的绝对上界")
    ap.add_argument("--up-steps", type=int, default=3, help="锚点成功后向上探测次数")
    ap.add_argument("--up-ratio", type=float, default=0.05, help="每次向上探测的增量比例")
    ap.add_argument("--precision", type=int, default=2000, help="二分收敛精度（token）")
    args = ap.parse_args()

    if not TOKEN:
        log("错误：未找到 API token（环境变量 ANTHROPIC_AUTH_TOKEN / ANTHROPIC_API_KEY）。")
        sys.exit(1)

    log(f"端点 : {BASE_URL}{API_PATH}")
    log(f"模型 : {args.model}")
    log(f"token: 已从环境变量读取（{len(TOKEN)} 字符，不在日志显示）")
    log("=" * 64)

    # Step 0: 自检 + 校准
    log("[0] 链路自检 + 校准填充比例 …")
    probe_prompt = (FILLER_UNIT * 40) + TAIL_INSTRUCTION
    ok, info = call_with_retry(args.model, probe_prompt)
    if not ok:
        log(f"    自检失败：status={info.get('http_status')} "
            f"body={(info.get('body') or '')[:300]}")
        sys.exit(2)
    in_tok = info["input_tokens"]
    cpt = len(probe_prompt) / in_tok if in_tok else 2.0
    log(f"    自检通过。input_tokens={in_tok}，chars/token ≈ {cpt:.3f}")

    cumulative = in_tok
    low_ok = in_tok  # 已知一定成功的点

    # Step 1: 锚点探测
    log(f"[1] 探测锚点 {args.anchor} tokens（官方宣称值）…")
    ok, info = call_with_retry(args.model, build_prompt(args.anchor, cpt))
    used = info.get("input_tokens") if ok else None
    log(f"    锚点 {args.anchor} | {'OK  ' if ok else 'FAIL'} | 实际={used} | body={(info.get('body') or '')[:200]}")

    if not ok:
        kind = classify_failure(info)
        if kind == "body_size":
            log("    ⚠️ 锚点失败原因是【网关 body 大小限制】(413/payload too large)，")
            log("       并非模型上下文限制。说明单次请求体过大被网关拦截，需换策略。")
            log("=" * 64)
            log(f"结论：无法通过单请求测到 1M（受 HTTP body 限制），当前确认可用 ≥ {low_ok} tokens。")
            log(f"累计消耗 input ≈ {cumulative} tokens")
            return
        # context 类失败
        revealed = find_context_limit(info.get("body") or "")
        if revealed and low_ok < revealed <= args.anchor:
            log(f"    🎯 API 报错透露 maximum ≈ {revealed} tokens")
            log("=" * 64)
            log(f"结论（来自 API 报错）：maximum context ≈ {revealed} tokens（≈ {revealed/1000:.0f}K）")
            log(f"累计消耗 input ≈ {cumulative} tokens")
            return
        log(f"    锚点失败，二分 [自检点 {low_ok}, 锚点 {args.anchor}] …")
        lo, hi, added = bisect(low_ok, args.anchor, args.precision, args.model, cpt)
        cumulative += added
        log("=" * 64)
        log(f"结论：最大可 ingest 输入 ≈ {lo} tokens（真实值落在 [{lo}, {hi}]）")
        log(f"累计消耗 input ≈ {cumulative} tokens")
        return

    # 锚点成功
    cumulative += used or args.anchor
    high_ok = used or args.anchor
    log(f"    ✅ 锚点 {args.anchor} 成功（实测 {used}）—— 官方宣称的 1M 可用。继续向上探真实硬上限 …")

    low_fail = None
    t = high_ok
    step = max(int(args.anchor * args.up_ratio), 20000)
    for i in range(args.up_steps):
        t = min(t + step, args.ceiling)
        if t <= high_ok:
            break
        ok2, info2 = call_with_retry(args.model, build_prompt(t, cpt))
        used2 = info2.get("input_tokens") if ok2 else None
        log(f"    上探 {t:>9} | {'OK  ' if ok2 else 'FAIL'} | 实际={used2}")
        if ok2:
            cumulative += used2 or t
            high_ok = used2 or t
        else:
            kind2 = classify_failure(info2)
            if kind2 == "body_size":
                log("    ⚠️ 上探失败为 body 大小限制，停止上探（非上下文限制）。")
            else:
                low_fail = t
            break

    if low_fail is None:
        log("=" * 64)
        log(f"结论：实测最大输入 ≥ {high_ok} tokens（≈ {high_ok/1000:.0f}K），未触发上下文上限。")
        log(f"      （官方宣称 1M；实测至少可用到 {high_ok/1000:.0f}K）")
        log(f"累计消耗 input ≈ {cumulative} tokens")
        return

    log(f"    找到失败点 {low_fail}，二分 [{high_ok}, {low_fail}] 精确定位 …")
    lo, hi, added = bisect(high_ok, low_fail, args.precision, args.model, cpt)
    cumulative += added
    log("=" * 64)
    log(f"结论：最大可 ingest 输入 ≈ {lo} tokens（真实值落在 [{lo}, {hi}]，≈ {lo/1000:.0f}K）")
    log(f"累计消耗 input ≈ {cumulative} tokens")
    log("注：总上下文窗口 ≈ max_input + max_output；本测输出仅约 64 token。")


if __name__ == "__main__":
    main()
