# EPUB 生成配置规范

## 基础参数

### 输入
- `input_dir`: Markdown 文件目录（必需）
- `output_file`: 输出 EPUB 文件路径（必需）
- `cover_image`: 封面图片路径（可选，与 `--cover-html` / `--cover-svg` 互斥）

### 元数据
- `title`: 书名（默认：从第一篇文章提取）
- `author`: 作者（默认：从 Markdown frontmatter 提取）
- `language`: 语言代码（默认：`zh`）
- `description`: 书籍描述（可选）

### 图片处理
- `image_max_width`: 图片最大宽度（默认：1000px）
- `image_quality`: JPEG 压缩质量（默认：88）
- `convert_png_to_jpg`: 是否转换 PNG 为 JPEG（默认：true）

### 排版（Kami 设计语言，默认）
- `font_family`: 字体族（默认：`Charter, "Iowan Old Style", "Source Han Serif SC", "Noto Serif CJK SC", "Songti SC", Georgia, serif`）
- `mono_family`: 等宽字体（默认：`"JetBrains Mono", "SF Mono", Monaco, Consolas, "Source Han Serif SC", monospace`）
- `line_height`: 行高（默认：1.55）
- `font_size`: 基础字号（默认：1em，跟随阅读器）
- `body_background`: **不设**（让阅读器决定，兼容暗色模式）
- 强调色：`#1B365D`（墨蓝），用于标题左边栏、引用左边栏、行内代码字色

## 使用示例

### 命令行调用（推荐）

```bash
# 基础版（不带封面，WeChat 兼容简化版）
python3 scripts/gen_epub.py ~/articles ~/output.epub

# 增强版 + Kami 风格 SVG 封面（默认主题）
python3 scripts/gen_epub_enhanced.py ~/articles ~/book.epub \
  --title "我的文集" --author "作者" --cover-svg \
  --subtitle "精选合集"

# 用户自带封面图片
python3 scripts/gen_epub_enhanced.py ~/articles ~/book.epub \
  --title "我的文集" --author "作者" --cover ~/cover.jpg

# 指定主题（默认是 kami）
python3 scripts/gen_epub_enhanced.py ~/articles ~/book.epub \
  --title "Tw93技术文集" --author "Tw93" --cover-svg --cover-theme tech
```

### 单独生成封面

```bash
# SVG 封面（KDP 标准 1600x2560）
python3 scripts/gen_cover_svg.py "书名" "副标题" "作者" cover.jpg kami minimal

# HTML 封面（基于 Playwright 截图）
python3 scripts/gen_cover_html.py "书名" "副标题" "作者" cover.jpg kami
```

## 微信读书兼容性

`gen_epub.py` 是 WeChat 简化版：
- CSS 仅包含 h1/h2/h3、p、blockquote、img、metadata、hr 风格
- 没有 `<pre>`、`<table>`、`<ul ol>` 高级样式块
- 适合纯文本类书籍（散文、长篇、传记）

`gen_epub_enhanced.py` 是完整版：
- 完整 Markdown 渲染（代码块、表格、列表、内联代码）
- 自动下载远程图片、SVG 转 PNG
- Kami 设计语言（墨蓝左边栏、ivory 代码块、无填充表格）
- 适合技术类、含代码或表格的书籍

## 封面主题

7 种主题，默认 `kami`。`detect_theme()` 根据书名/副标题/作者匹配关键词，未命中关键词时回退到 `kami`。

| 主题 | 风格 | 关键词触发 |
|------|------|------------|
| `kami` | 羊皮纸 + 墨蓝 + serif（默认，编辑感） | 不通过关键词，作为兜底 |
| `tech` | 深海军 + 青色 | 技术、编程、AI、Claude、Agent、LLM |
| `business` | 深蓝 + 金色 | 创业、商业、营销、增长、产品 |
| `design` | 深紫 + 粉色 | 设计、美学、UI、UX、品牌 |
| `literature` | 海军蓝 + 暖黄 | 文学、小说、散文、传记、哲学 |
| `science` | 墨绿 + 薄荷 | 科学、物理、化学、生物、数学 |
| `personal` | 紫红 + 蜜桃 | 成长、学习、思考、笔记、随笔 |

### 布局（仅 SVG 封面）

| 布局 | 视觉元素 |
|------|----------|
| `minimal` | 几何块（默认） |
| `classic` | 横向线条 |
| `modern` | 对角线条 |

封面统一输出 1600x2560px（KDP 标准）。
