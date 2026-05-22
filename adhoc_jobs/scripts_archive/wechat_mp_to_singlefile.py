r"""Download a WeChat (mp.weixin.qq.com) article as a single-file self-contained HTML.

Version: 1.0.0

Changelog (excerpt):
    1.0.0 (2025-10-09)
        - 默认移动端微信 UA 模拟，可切换 Android / 关闭
        - 图片原尺寸升级（/640 -> /0）默认开启，可关闭
        - 图片内联（含二次重试逻辑）与 CSS 内联默认开启
        - 失败图片 second-pass 重试 & 失败标记
        - 导航超时与 waitUntil 策略可配置，并有 fallback
        - 元数据提取：标题 / 作者 / 发布日期；文件名格式：日期_标题_作者
        - 动态滚动以懒加载图片
        - 图片放大策略：simple / dynamic 两种模式；可配置最大宽；保持纵横比
        - 动态模式下按 naturalWidth 限制放大，不超过原始分辨率
        - 统计注释嵌入：图片总数、失败数、second pass 结果、CSS inlined、升级标记等
        - 代码结构化参数化，可扩展第三方后续增强（JSON 导出 / 第三次下载尝试等）

此文件顶部 Changelog 仅保留最近重要版本摘录，完整历史请参见项目 wechat_mp_to_singlefile_CHANGELOG.md。

Enhancements in this version:
* Mobile WeChat UA simulation NOW DEFAULT (use --no-wechat-mobile to disable, --android to switch UA)
* Second pass image retry NOW DEFAULT (use --no-second-pass to disable)
* Route interception adds Referer header for image requests to improve CDN acceptance
* Parameterised scroll rounds / delay
* CSS inlining NOW ENABLED BY DEFAULT (use --no-inline-css to disable)
* WeChat CDN image original-size upgrade NOW DEFAULT (use --no-upgrade-wechat-img to disable)
* Resilient navigation: configurable timeout & wait-until with fallback when load event stalls
* Image enlargement styling (default ON, use --no-enlarge-images to disable, set width with --img-max-width)
* Dynamic enlargement mode: optionally size each image up to its natural width (threshold controlled)

Usage (PowerShell):
  pip install playwright
  python -m playwright install chromium
  python scripts\wechat_mp_to_singlefile.py --url "<WECHAT_ARTICLE_URL>" --output . --wechat-mobile --second-pass

Notes:
* Some images may still require authenticated cookies; those remain with data-inline-fail attribute.
* Videos are not downloaded; <video> tags remain remote.
* Use --inline-css to inline external CSS (larger file size).
"""
from __future__ import annotations

import argparse
import asyncio
import datetime as dt
import re
from pathlib import Path
from typing import Optional, Dict

from playwright.async_api import async_playwright, Route, Request

__version__ = "1.0.0"


# Defaults
DEFAULT_SCROLL_DELAY_MS = 600
DEFAULT_MAX_SCROLL = 25
IMG_FETCH_RETRIES = 2
CHUNK = 0x8000

# Mobile WeChat UA strings
WECHAT_IPHONE_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/20F66 "
    "MicroMessenger/8.0.48(0x1800302f) NetType/WIFI Language/zh_CN"
)
WECHAT_ANDROID_UA = (
    "Mozilla/5.0 (Linux; Android 13; Pixel 7 Build/TQ3A.230805.001; wv) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/116.0.0.0 Mobile Safari/537.36 "
    "MicroMessenger/8.0.47(0x28002f35) Process/toolsmp WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64"
)

CSS_LINK_SELECTOR = 'link[rel="stylesheet"]'

INLINE_CSS_JS = r"""
(async () => {
  const fetchText = async (href) => {
    if(!href) return null; if(href.startsWith('//')) href = 'https:' + href;
    try { const r = await fetch(href); if(!r.ok) throw new Error('HTTP '+r.status); return await r.text(); } catch { return null; }
  };
  const links = Array.from(document.querySelectorAll('%s'));
  let success = 0, failed = 0;
  for (const ln of links) {
    const href = ln.getAttribute('href');
    const css = await fetchText(href);
    if (css) {
      const style = document.createElement('style');
      style.setAttribute('data-inlined-from', href);
      style.textContent = css;
      ln.replaceWith(style);
      success++;
    } else failed++;
  }
  return {cssInlined: success, cssFailed: failed};
})();
""" % CSS_LINK_SELECTOR

INLINE_IMAGES_JS_TEMPLATE = r"""
(async () => {
    const MAX_SCROLL = %(max_scroll)d; const DELAY = %(delay)d;
    const delay = ms => new Promise(r => setTimeout(r, ms));
    let lastHeight = -1;
    for (let i = 0; i < MAX_SCROLL; i++) {
        window.scrollTo(0, document.body.scrollHeight); await delay(DELAY);
        const newHeight = document.body.scrollHeight; if (newHeight === lastHeight) break; lastHeight = newHeight;
    }
    const toBase64 = async (url, retries = %(retries)d) => {
        if(!url) return null; if(url.startsWith('data:')) return url; if(url.startsWith('//')) url = 'https:' + url;
        while (retries >= 0) {
            try {
                const resp = await fetch(url, {credentials:'omit'}); if(!resp.ok) throw new Error();
                const blob = await resp.blob(); const ab = await blob.arrayBuffer(); const bytes = new Uint8Array(ab);
                let binary=''; const CHUNK=%(chunk)d; for (let i=0;i<bytes.length;i+=CHUNK) { binary += String.fromCharCode(...bytes.subarray(i,i+CHUNK)); }
                const b64 = btoa(binary); const mime = blob.type || (/\.jpe?g$/i.test(url)?'image/jpeg':/\.png$/i.test(url)?'image/png':'application/octet-stream');
                return `data:${mime};base64,${b64}`;
            } catch(e) { if(retries===0) return null; await delay(400); }
            retries--;
        }
        return null;
    };
    const imgs = Array.from(document.querySelectorAll('img'));
    let inlined=0, failed=0;
    for (const img of imgs) {
        let src = img.getAttribute('data-src') || img.getAttribute('data-srcset') || img.currentSrc || img.src;
        if(!src){ failed++; continue; }
        const dataUri = await toBase64(src);
        if(dataUri){ img.setAttribute('src', dataUri); ['data-src','data-srcset','crossorigin','referrerpolicy'].forEach(a=>img.removeAttribute(a)); inlined++; }
        else { img.setAttribute('data-inline-fail', src); failed++; }
    }
    // Remove non-essential scripts
    const scripts = Array.from(document.querySelectorAll('script'));
    for(const s of scripts){ const type=(s.getAttribute('type')||'').toLowerCase(); if(type.includes('ld+json')) continue; s.remove(); }
    // Metadata extraction (title, author, publish date)
    const textTrim = s => (s||'').replace(/\s+/g,' ').trim();
    let title = textTrim(document.querySelector('#activity-name')?.textContent) || textTrim(document.title) || 'wechat_article';
    if(!title){ const h1=document.querySelector('h1'); if(h1) title = textTrim(h1.textContent); }
    const authorCandidates = [];
    ['#js_name','#js_author_name','[id*=author]','.rich_media_meta_list .rich_media_meta.rich_media_meta_text'].forEach(sel=>{
        const el = document.querySelector(sel); if(el) authorCandidates.push(textTrim(el.textContent));
    });
    // Collect all meta text blocks and filter
    document.querySelectorAll('.rich_media_meta_text').forEach(el=>authorCandidates.push(textTrim(el.textContent)));
    let author = authorCandidates.find(a=>a && !/^20\d{2}[-年]/.test(a) && a.length<=40 && !/\d{4}-\d{2}-\d{2}/.test(a)) || 'author';
    // Date
    let pubRaw = textTrim(document.querySelector('#publish_time')?.textContent);
    if(!pubRaw){
        // Try to parse from global variable ct
        const m = /var\s+ct\s*=\s*"(\d+)"/.exec(document.documentElement.innerHTML);
        if(m){ try { const d=new Date(parseInt(m[1])*1000); pubRaw = d.toISOString().slice(0,10); } catch{} }
    }
    if(pubRaw){
        // Normalize Chinese format YYYY年MM月DD日
        const m2 = pubRaw.match(/(20\d{2})[年-](\d{1,2})[月-](\d{1,2})/);
        if(m2){
            const y=m2[1]; const mo=m2[2].padStart(2,'0'); const da=m2[3].padStart(2,'0');
            pubRaw = `${y}-${mo}-${da}`;
        } else {
            // Already maybe YYYY-MM-DD
            const m3 = pubRaw.match(/(20\d{2}-\d{2}-\d{2})/); if(m3) pubRaw = m3[1];
        }
    } else {
        pubRaw = '0000-00-00';
    }
    const sanitizedTitle = title.replace(/[\\/:*?"<>|]/g,'_');
    const sanitizedAuthor = author.replace(/[\\/:*?\"<>|]/g,'_');
    /*__ENLARGE_IMAGES_PLACEHOLDER__*/
    return {title, sanitizedTitle, author, sanitizedAuthor, publishDate: pubRaw, img:{total:imgs.length,inlined,failed}};
})();
"""

SECOND_PASS_JS = r"""
(async () => {
  const delay = ms => new Promise(r => setTimeout(r, ms));
  const candidates = Array.from(document.querySelectorAll('img[data-inline-fail]'));
  let retried = 0, recovered = 0;
  for (const img of candidates) {
    const url = img.getAttribute('data-inline-fail'); if(!url) continue; retried++;
    try {
      let u = url; if(u.startsWith('//')) u='https:'+u;
      const resp = await fetch(u, {credentials:'omit'}); if(!resp.ok) continue;
      const blob = await resp.blob(); const ab = await blob.arrayBuffer(); const bytes = new Uint8Array(ab);
      let binary=''; const CHUNK=%(chunk)d; for(let i=0;i<bytes.length;i+=CHUNK){binary+=String.fromCharCode(...bytes.subarray(i,i+CHUNK));}
      const b64=btoa(binary); const mime = blob.type || (/\.jpe?g$/i.test(u)?'image/jpeg':/\.png$/i.test(u)?'image/png':'application/octet-stream');
      img.setAttribute('src', `data:${mime};base64,${b64}`); img.removeAttribute('data-inline-fail'); recovered++;
      await delay(30);
    } catch {}
  }
  return {secondPassTried: retried, secondPassRecovered: recovered, remaining: document.querySelectorAll('img[data-inline-fail]').length};
})();
""" % {"chunk": CHUNK}

GET_FULL_HTML_JS = r"""
(() => { const html = '<!DOCTYPE html>\n' + document.documentElement.outerHTML; return { length: html.length, head: html.slice(0,200), html }; })();
"""

SANITIZE_FILENAME = re.compile(r"[\\/:*?\"<>|]")


def safe_filename(name: str) -> str:
    return SANITIZE_FILENAME.sub('_', name)


async def capture(
    url: str,
    output: Path,
    *,
    inline_css: bool = False,
    user_agent: Optional[str] = None,
    wechat_mobile: bool = False,
    android: bool = False,
    add_mobile_suffix: bool = False,
    second_pass: bool = False,
    max_scroll: int = DEFAULT_MAX_SCROLL,
    scroll_delay: int = DEFAULT_SCROLL_DELAY_MS,
    upgrade_wechat_img: bool = False,
    nav_timeout: int = 90000,
    wait_until: str = "load",
    enlarge_images: bool = True,
    img_max_width: int = 1080,
    enlarge_mode: str = "dynamic",  # "simple" or "dynamic"
    min_natural_width: int = 600,
) -> Path:
    inline_images_js = INLINE_IMAGES_JS_TEMPLATE % {
        "max_scroll": max_scroll,
        "delay": scroll_delay,
        "retries": IMG_FETCH_RETRIES,
        "chunk": CHUNK,
    }
    if enlarge_images:
        if enlarge_mode not in ("simple", "dynamic"):
            enlarge_mode = "dynamic"
        if enlarge_mode == "simple":
            enlarge_js = (
                "try{"  # guard
                "const style=document.createElement('style');"
                "style.id='__singlefile_img_enlarge';"
                f"style.textContent='#js_content img, .rich_media_content img, img {{display:block;margin:16px auto;height:auto !important;}}';"
                "document.head.appendChild(style);"
                # 为每张图片设定具体宽度：不超过 img_max_width，也不超过原始 naturalWidth，保持比例
                f"const MAXW={img_max_width};"
                "for(const im of imgs){im.removeAttribute('width');im.removeAttribute('height');const nw=im.naturalWidth||0;const nh=im.naturalHeight||0;let target=MAXW; if(nw>0){target=Math.min(nw,MAXW);} im.style.width=target+'px'; im.style.maxWidth=target+'px'; im.style.height='auto'; if(nw>0&&nh>0){im.style.aspectRatio=nw+'/'+nh;}}"
                # onload 再次修正（懒加载或延迟解码情况）
                "for(const im of imgs){if(!im.complete){im.addEventListener('load',()=>{try{const nw=im.naturalWidth||0;const nh=im.naturalHeight||0;if(nw>0){const target=Math.min(nw,MAXW);im.style.width=target+'px';im.style.maxWidth=target+'px';if(nh>0){im.style.aspectRatio=nw+'/'+nh;}}}catch(e){}},{once:true});}}"
                # rAF 双次兜底
                "const redo=()=>{for(const im of imgs){const nw=im.naturalWidth||0;const nh=im.naturalHeight||0;if(nw>0){const target=Math.min(nw,MAXW);im.style.width=target+'px';im.style.maxWidth=target+'px';if(nh>0){im.style.aspectRatio=nw+'/'+nh;}}}}; requestAnimationFrame(()=>{redo();requestAnimationFrame(()=>redo());});"
                "}catch(e){}"
            )
        else:  # dynamic
            # Dynamic: per image use its naturalWidth up to img_max_width; only upscale if naturalWidth exceeds current rendered width & above threshold
            enlarge_js = (
                "try{" \
                "const style=document.createElement('style');style.id='__singlefile_img_enlarge';" \
                f"style.textContent='#js_content img, .rich_media_content img, img {{display:block;margin:16px auto;height:auto !important;}}';" \
                "document.head.appendChild(style);" \
                f"const TH={min_natural_width};const MAXW={img_max_width};" \
                "const setDim=(im)=>{const nw=im.naturalWidth||0;const nh=im.naturalHeight||0;const cw=im.clientWidth||0;let target=null; if(nw>0){if(nw>TH){target=Math.min(nw,MAXW);} else {target=Math.min(nw,MAXW);} if(nw>TH && target<=cw*1.05){target=Math.min(cw,MAXW);} } else {target=MAXW;} if(!target) target=MAXW; im.style.width=target+'px'; im.style.maxWidth=target+'px'; im.style.height='auto'; if(nw>0&&nh>0){im.style.aspectRatio=nw+'/'+nh;}};" \
                "for(const im of imgs){im.removeAttribute('width');im.removeAttribute('height');setDim(im); if(!im.complete){im.addEventListener('load',()=>setDim(im),{once:true});}}" \
                "const rerun=()=>{for(const im of imgs){if(im.complete) setDim(im);}}; requestAnimationFrame(()=>{rerun();requestAnimationFrame(()=>rerun());});" \
                "}catch(e){}"
            )
        inline_images_js = inline_images_js.replace("/*__ENLARGE_IMAGES_PLACEHOLDER__*/", enlarge_js)
    else:
        inline_images_js = inline_images_js.replace("/*__ENLARGE_IMAGES_PLACEHOLDER__*/", "")
    # Inject upgrade logic if requested (replace /640 or similar width segment with /0 on mmbiz.qpic.cn)
    if upgrade_wechat_img:
        # Use simpler pattern: find "/<width>" segment near end and replace with /0.
        # Avoid overly escaped regex that previously produced SyntaxError inside page.evaluate.
        inject_upgrade = (
            "function __upgradeWechatUrl(u){"  # function start
            "try{"  # try
            "if(!u)return u;"  # guard
            "if(u.startsWith('//'))u='https:'+u;"  # protocol
            "const o=new URL(u);"  # parse
            "if(/mmbiz.qpic.cn/.test(o.hostname)){"  # host check (dot not escaped in JS regex literal is fine inside string)
            # Replace last numeric path segment of length 2-4 with 0 (WeChat size variants like /640 /258 etc)
            r"o.pathname=o.pathname.replace(/\/(\d{2,4})(?=($|\/|\.?))/,'/0');"  # keep trailing query etc
            "return o.toString();}"  # return upgraded
            "}catch(e){} return u;}"  # swallow errors
        )
        # Insert helper at start of JS and wrap src selection
        inline_images_js = inline_images_js.replace(
            "let src = img.getAttribute('data-src') || img.getAttribute('data-srcset') || img.currentSrc || img.src;",
            """%s\n    let src = img.getAttribute('data-src') || img.getAttribute('data-srcset') || img.currentSrc || img.src;\n    src = __upgradeWechatUrl(src);"""
            % inject_upgrade,
        )

    # Build second pass script (needs same upgrade logic)
    second_pass_js = SECOND_PASS_JS
    if upgrade_wechat_img:
        second_pass_js = second_pass_js.replace(
            "const candidates = Array.from(document.querySelectorAll('img[data-inline-fail]'));",
            "const candidates = Array.from(document.querySelectorAll('img[data-inline-fail]'));\n  %s" % inject_upgrade,
        ).replace(
            "const url = img.getAttribute('data-inline-fail');",
            "let url = img.getAttribute('data-inline-fail'); url = __upgradeWechatUrl(url);",
        )

    async with async_playwright() as pw:
        # UA precedence: explicit > wechat-mobile flag > browser default
        final_user_agent = user_agent
        if not final_user_agent and wechat_mobile:
            final_user_agent = WECHAT_ANDROID_UA if android else WECHAT_IPHONE_UA

        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=final_user_agent,
            viewport={"width": 430, "height": 900} if wechat_mobile else None,
        )

        # Intercept all to add Referer for images
        async def route_handler(route: Route, request: Request):
            headers: Dict[str, str] = dict(request.headers)
            if request.resource_type == 'image':
                headers.setdefault('Referer', 'https://mp.weixin.qq.com/')
            await route.continue_(headers=headers)

        await context.route('**/*', route_handler)
        page = await context.new_page()

        print(f"[+] Navigating: {url}")
        if final_user_agent:
            print(f"[+] Using User-Agent: {final_user_agent[:180]}{'...' if len(final_user_agent) > 180 else ''}")
        # Robust navigation with fallback if full load stalls.
        primary_event = wait_until
        try:
            resp = await page.goto(url, wait_until=primary_event, timeout=nav_timeout)
        except Exception as exc:  # TimeoutError or others
            print(f"[!] Primary navigation ({primary_event}) failed: {exc}. Attempting fallback 'domcontentloaded'.")
            try:
                resp = await page.goto(url, wait_until='domcontentloaded', timeout=nav_timeout)
            except Exception as exc2:
                print(f"[!] Fallback navigation still failed: {exc2}. Continuing with partial content.")
                resp = None
        if not resp or (hasattr(resp, 'ok') and not resp.ok):
            print(f"[!] Warning: navigation status: {getattr(resp,'status',None)}")
        # Best-effort wait for article body
        try:
            await page.wait_for_selector('#js_content', timeout=5000)
        except Exception:
            pass

        result = await page.evaluate(inline_images_js)
        css_stats = None
        if inline_css:
            css_stats = await page.evaluate(INLINE_CSS_JS)

        second_stats = None
        if second_pass:
            print("[+] Second pass retrying failed images ...")
            second_stats = await page.evaluate(second_pass_js)

        html_obj = await page.evaluate(GET_FULL_HTML_JS)
        title = result['title']
        author = (result.get('author') or 'author').strip() or 'author'
        publish_date = (result.get('publishDate') or '0000-00-00').strip() or '0000-00-00'
        sanitized_title = result.get('sanitizedTitle') or 'wechat_article'
        sanitized_author = result.get('sanitizedAuthor') or 'author'
        # Detect parse failures for comment flags
        author_failed = (author.lower() == 'author')
        date_failed = (publish_date == '0000-00-00') or not publish_date.startswith('20')
        # Build filename base: YYYY-MM-DD_Title_Author (date first)
        filename_base = f"{publish_date}_{sanitized_title}_{sanitized_author}"
        # Collapse duplicate underscores and trim
        filename_base = re.sub(r'_+', '_', filename_base).strip('_')

        stats_comment = (
            f"<!-- Single-file export {dt.datetime.now(dt.timezone.utc).isoformat()} title='{title}' "
            f"images_total={result['img']['total']} images_inlined={result['img']['inlined']} images_failed_initial={result['img']['failed']}"
        )
        if second_stats:
            stats_comment += (
                f" second_pass_tried={second_stats['secondPassTried']} "
                f"second_pass_recovered={second_stats['secondPassRecovered']} remaining_failed={second_stats['remaining']}"
            )
        if css_stats:
            stats_comment += f" css_inlined={css_stats['cssInlined']} css_failed={css_stats['cssFailed']}"
        if upgrade_wechat_img:
            stats_comment += " upgraded_wechat_img=1"
        if enlarge_images:
            stats_comment += f" enlarge_images=1 img_max_width={img_max_width} enlarge_mode={enlarge_mode} min_natural_width={min_natural_width}"
        if author_failed:
            stats_comment += " author_parse_failed=1"
        if date_failed:
            stats_comment += " date_parse_failed=1"
        stats_comment += " -->\n"

        html_full = stats_comment + html_obj['html']
        if output.is_dir():
            output = output / f"{safe_filename(filename_base)}.html"
        output.write_text(html_full, encoding='utf-8')
        print(f"[+] Saved: {output} ({len(html_full)/1024/1024:.2f} MB)")
        if second_stats:
            print(
                f"[+] Second pass recovered {second_stats['secondPassRecovered']} / {second_stats['secondPassTried']} failed; remaining {second_stats['remaining']}"
            )
        await browser.close()
        return output


def parse_args():
    p = argparse.ArgumentParser(description="Save WeChat article as single-file HTML")
    p.add_argument('--version', action='store_true', help='Print version and exit')
    p.add_argument('--url', required=False, help='mp.weixin.qq.com article URL')
    p.add_argument('--output', '-o', default='.', help='Output file or directory (if directory, auto-named)')
    # Inline CSS is now ON by default; retain --inline-css (no-op enable) & add --no-inline-css to disable.
    p.add_argument('--inline-css', dest='inline_css', action='store_true', help='Enable CSS inlining (default ON)')
    p.add_argument('--no-inline-css', dest='inline_css', action='store_false', help='Disable CSS inlining')
    p.add_argument('--user-agent', help='Custom User-Agent (overrides --wechat-mobile)')
    p.add_argument('--wechat-mobile', dest='wechat_mobile', action='store_true', help='Enable mobile WeChat UA emulation (default ON)')
    p.add_argument('--no-wechat-mobile', dest='wechat_mobile', action='store_false', help='Disable mobile WeChat UA emulation')
    p.add_argument('--android', action='store_true', help='With --wechat-mobile, use Android UA')
    p.add_argument('--mobile-suffix', action='store_true', help='Append _mobile to filename when using mobile UA')
    # Second pass now ON by default; provide disable flag.
    p.add_argument('--second-pass', dest='second_pass', action='store_true', help='Enable second pass image retry (default ON)')
    p.add_argument('--no-second-pass', dest='second_pass', action='store_false', help='Disable second pass image retry')
    p.add_argument('--max-scroll', type=int, default=DEFAULT_MAX_SCROLL, help='Max scroll rounds (default: %(default)s)')
    p.add_argument('--scroll-delay', type=int, default=DEFAULT_SCROLL_DELAY_MS, help='Delay ms between scroll rounds (default: %(default)s)')
    p.add_argument('--upgrade-wechat-img', dest='upgrade_wechat_img', action='store_true', help='Enable upgrading WeChat CDN image size (default ON)')
    p.add_argument('--no-upgrade-wechat-img', dest='upgrade_wechat_img', action='store_false', help='Disable upgrading WeChat CDN image size')
    p.add_argument('--nav-timeout', type=int, default=90000, help='Navigation timeout in ms (default: %(default)s)')
    p.add_argument('--wait-until', choices=['load','domcontentloaded','networkidle','commit'], default='load', help='Primary waitUntil event (default: %(default)s)')
    p.add_argument('--enlarge-images', dest='enlarge_images', action='store_true', help='Enlarge images with consistent max width (default ON)')
    p.add_argument('--no-enlarge-images', dest='enlarge_images', action='store_false', help='Disable image enlargement styling')
    p.add_argument('--img-max-width', type=int, default=1080, help='Max image width when enlargement enabled (default: %(default)s)')
    p.add_argument('--enlarge-mode', choices=['simple','dynamic'], default='dynamic', help='Image enlarge mode: simple=uniform CSS; dynamic=respect naturalWidth (default: %(default)s)')
    p.add_argument('--min-natural-width', type=int, default=600, help='In dynamic mode, only upscale images whose naturalWidth >= this threshold (default: %(default)s)')
    p.set_defaults(inline_css=True, second_pass=True, upgrade_wechat_img=True, wechat_mobile=True, enlarge_images=True)
    return p.parse_args()


def main():
    args = parse_args()
    if getattr(args, 'version', False):
        print(__version__)
        return
    if not args.url:
        print("Error: --url is required unless --version is specified", flush=True)
        return
    out_path = Path(args.output)
    if out_path.exists() and out_path.is_dir():
        pass
    else:
        out_path.parent.mkdir(parents=True, exist_ok=True)

    asyncio.run(
        capture(
            args.url,
            out_path,
            inline_css=args.inline_css,
            user_agent=args.user_agent,
            wechat_mobile=args.wechat_mobile,
            android=args.android,
            add_mobile_suffix=args.mobile_suffix,
            second_pass=args.second_pass,
            max_scroll=args.max_scroll,
            scroll_delay=args.scroll_delay,
            upgrade_wechat_img=args.upgrade_wechat_img,
            nav_timeout=args.nav_timeout,
            wait_until=args.wait_until,
            enlarge_images=args.enlarge_images,
            img_max_width=args.img_max_width,
            enlarge_mode=args.enlarge_mode,
            min_natural_width=args.min_natural_width,
        )
    )


if __name__ == '__main__':
    main()
