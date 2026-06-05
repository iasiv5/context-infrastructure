---
title: PDF 转 Markdown
category: BestPractice
tags: [pdf, markdown, docling, document-conversion]
difficulty: Easy
created: 2026-04-27
---

# PDF 转 Markdown

需要把 PDF 转成 Markdown（喂给 LLM、做内容提取、归档原始资料）时，**默认用 Docling**。

## 为什么是 Docling

OpenDataLoader benchmark 12 个 PDF→Markdown 引擎里 Docling 综合得分最高（0.882），表格和标题保真都最好。MIT 许可证，纯 Python，CPU 也能跑（约 3 秒/页），有 GPU 更快。

实测过的几类反例不要用：

- **MarkItDown**：底层是 pdfminer.six，标题层级保留率 0%，表格基本崩溃。Office 文档 OK，PDF 不行。
- **PyMuPDF4LLM**：速度最快但 AGPL，商用受限。
- **Marker**：质量接近 Docling 但 GPL，商用要付费。

如果你要在自己的 workspace 里保留引擎对比调研，把调研记录放在项目文档或 `contexts/` 下，并在本 skill 里链接到你的本地报告。

## 快速用法

```bash
uv pip install --python .venv/bin/python docling
```

```python
from docling.document_converter import DocumentConverter

conv = DocumentConverter()
result = conv.convert("input.pdf")
md = result.document.export_to_markdown()
```

首次调用会下载约 1 GB 模型权重到 HuggingFace 缓存，之后复用。同一个 `DocumentConverter()` 实例可以连续转多份，不要每份都新建。

也可以直接使用本 skill 自带的 CLI。它把 Docling、LM Studio VLM OCR 和环境检查封装成固定命令，适合 agent 反复调用：

```bash
source .venv/bin/activate
python rules/skills/pdf_to_markdown_cli.py doctor --format json
python rules/skills/pdf_to_markdown_cli.py docling input.pdf --output output.md --format json
```

## 验收

- 输出 Markdown 中表格用标准 `| ... |` 语法保留，列对齐
- 标题层级（`#`、`##`、`###`）和原 PDF 视觉层级一致
- 体积上：纯文字 PDF 一般 5–10x 压缩到 Markdown，纯扫描件不会显著变小

## 已知陷阱

**Section 标题被吞掉**。当 PDF 里某个标题是表格内的强调文字（不是真正的 layout heading），docling 可能识别成普通单元格。表现是连续两个 `## HOLDINGS` 中间没有账户名区分。处理方法：用上下文（账户编号、beginning balance）回查原 PDF 对应页，必要时手动补 section header。

**两份 PDF 内容相同但文件名不同**。如果两份转出来字符数完全相等，先 `md5` 比较原文件——很可能是上传时弄错了。docling 不会主动 dedupe。

**venv 里 pip 不存在**。在用 uv 创建的 venv 里通常没装 pip，`venv/bin/python -m pip install` 会报 `No module named pip`。改用 `uv pip install --python .venv/bin/python <pkg>`。

## 已知陷阱（续）

**macOS MPS float64 崩溃**。Apple Silicon 上 Docling 的 RT-DETR V2 模型做 layout 检测时会调用 `torch.float64`，MPS 后端不支持，整份 PDF 转换崩溃。workaround：

```bash
PYTORCH_ENABLE_MPS_FALLBACK=1 python -c "
from docling.document_converter import DocumentConverter
...
"
```

或直接改 `~/.bashrc`/`.zshrc` 加 `export PYTORCH_ENABLE_MPS_FALLBACK=1`。如果仍然失败（已知特定版本组合下 MPS fallback 也不生效），切换到 VLM OCR 路径。

## 适用边界与路径选择

| PDF 类型 | 首选 | fallback | 不推荐 |
|---------|------|----------|--------|
| 文本 PDF（Office/WPS 导出、LaTeX） | Docling | — | MarkItDown |
| 扫描件（英文为主） | Docling（自带 OCR） | Tesseract | — |
| 扫描件/图片 PDF（中文为主、图文混排、pitch deck） | **LM Studio VLM OCR** | Tesseract（精度低） | Docling（MPS float64 风险） |
| 复杂数学公式 | Docling（导出 LaTeX） | 人工校对 | — |

## CLI：PDF→Markdown

CLI 文件位于 `rules/skills/pdf_to_markdown_cli.py`。它不是独立服务，不保存状态；每次运行只读取输入 PDF，写出 Markdown，并把结果摘要输出到 stdout。进度和错误写到 stderr。

### 前置环境

在 workspace 根目录使用 `.venv`：

```bash
source .venv/bin/activate
uv pip install docling
```

如果要走 LM Studio VLM OCR fallback，还需要：

```bash
uv pip install pdf2image pillow requests
```

`pdf2image` 依赖系统里的 Poppler。macOS 可用：

```bash
brew install poppler
```

LM Studio 需要手动打开并加载视觉模型。默认 API 是 `http://127.0.0.1:1234/v1`，默认模型名是 `qwen/qwen3.5-35b-a3b`。

### Doctor

先跑 doctor 看本地环境是否齐全：

```bash
python rules/skills/pdf_to_markdown_cli.py doctor --format json
```

需要检查 LM Studio 是否在线、目标模型是否已加载时：

```bash
python rules/skills/pdf_to_markdown_cli.py doctor --check-lmstudio --format json
```

### Docling 路径（默认首选）

普通文本 PDF、LaTeX PDF、Office 导出的 PDF，优先走 Docling：

```bash
python rules/skills/pdf_to_markdown_cli.py docling input.pdf --output output.md --format json
```

等价的通用命令：

```bash
python rules/skills/pdf_to_markdown_cli.py convert input.pdf --engine docling --output output.md --format json
```

### LM Studio VLM OCR 路径

当 Docling 对中文扫描件、图片 PDF、pitch deck 的 OCR 明显失败时，再显式切换到 VLM OCR：

```bash
python rules/skills/pdf_to_markdown_cli.py vlm-ocr input.pdf \
  --output output.md \
  --model qwen/qwen3.5-35b-a3b \
  --timeout 300 \
  --format json
```

常用调参：

- `--dpi 150`：图片太大、模型响应慢或输出漂移时降低 DPI
- `--start-page N --end-page M`：只处理部分页面，先验证再跑整份
- `--api-base http://127.0.0.1:1234/v1`：LM Studio 不在默认端口时显式指定

VLM OCR 输出带 `=== PAGE N ===` 分页标记。大 PDF 每页约 30-60 秒，17 页 pitch deck 约 10-15 分钟，取决于模型和机器负载。

### CLI 验收

- `--format json` 时 stdout 必须是可解析 JSON
- `doctor` 能准确报告缺失依赖或 LM Studio 不在线
- Docling 输出应保留标题层级和 Markdown 表格
- VLM OCR 输出应保留原文语言，不总结、不翻译，并包含页码分隔

## LM Studio VLM OCR 原理

当 Docling 和 Tesseract 都处理不好时（中文 pitch deck、图像密集的幻灯片），用本地视觉模型做 OCR。CLI 位于 `rules/skills/pdf_to_markdown_cli.py`：

```bash
source .venv/bin/activate
python rules/skills/pdf_to_markdown_cli.py vlm-ocr input.pdf --output output.md --timeout 300
```

前提：LM Studio 在本地运行（默认 `http://127.0.0.1:1234`），已加载视觉模型。默认模型为 `qwen/qwen3.5-35b-a3b`，该模型对中英文混排 pitch deck 的 OCR 效果远超 Tesseract。

脚本会逐页渲染 PDF 为图片（200 DPI），通过 LM Studio 的 `/v1/chat/completions` 端点逐页喂图，输出带 `=== PAGE N ===` 分页的 Markdown。prompt 为通用 OCR，不做财务 schema 约束。大 PDF 每页约 30-60 秒，整份 17 页 pitch deck 约 10-15 分钟。

注意：LM Studio 的 VLM API 是 OpenAI-compatible 的，不是专用 OCR API。输出质量取决于模型能力和 prompt。如果某页 OCR 结果明显偏离原图，降低 DPI（`--dpi 150`）或缩短 prompt 指令再试。

## 仍需人工复核的场景

- 复杂数学公式：Docling 可以导出 LaTeX，但保真度有限
- 需要保留页码、页眉页脚的归档场景：Docling 默认会清掉这些，VLM OCR 也可能改写布局
- 法律、财务、医疗等高风险文档：转换后必须抽样回查原 PDF
