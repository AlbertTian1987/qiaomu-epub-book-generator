# EPUB 生成示例

## 基础用法

### 1. 单个 Markdown 目录生成 EPUB（基础版，WeChat 兼容简化样式）

```bash
python3 ~/.claude/skills/qiaomu-epub-book-generator/scripts/gen_epub.py \
  ~/articles/ \
  ~/output.epub \
  --title "我的书" \
  --author "作者名"
```

**说明**：
- 自动扫描 `~/articles/` 目录下所有 `.md` 文件
- 从第一篇文章提取标题（如未指定）
- 自动查找同名 PNG/JPG 配图并压缩嵌入
- CSS 仅含基础风格（h1/h2/h3、p、blockquote、img），适合纯文本类书籍

### 2. 增强版生成（默认推荐，含完整 Markdown 渲染 + Kami 设计语言）

```bash
python3 ~/.claude/skills/qiaomu-epub-book-generator/scripts/gen_epub_enhanced.py \
  ~/articles/ \
  ~/book.epub \
  --title "我的文集" \
  --author "作者名" \
  --cover-svg \
  --subtitle "精选合集"
```

**说明**：
- `--cover-svg` 自动生成 KDP 标准 1600x2560 封面（默认 kami 主题）
- 完整支持代码块、表格、列表、内联代码
- 自动下载远程图片、SVG 转 PNG
- 章节正文使用 Kami 设计语言：羊皮纸调色板 + 墨蓝左边栏 + serif 字体栈

### 3. 用户自带封面图片

```bash
python3 ~/.claude/skills/qiaomu-epub-book-generator/scripts/gen_epub_enhanced.py \
  ~/articles/ \
  ~/book.epub \
  --title "我的书" \
  --author "作者名" \
  --cover ~/cover.jpg
```

**说明**：
- `--cover` 与 `--cover-svg` / `--cover-html` 互斥
- 支持 JPG/PNG 格式

### 4. 切换封面主题

```bash
# kami 主题（默认，编辑感羊皮纸 + 墨蓝 serif）
python3 .../gen_epub_enhanced.py ~/articles ~/book.epub \
  --title "我的散文集" --author "作者" --cover-svg

# tech 主题（深海军 + 青色，关键词命中"AI/技术/Claude"等会自动切换）
python3 .../gen_epub_enhanced.py ~/articles ~/book.epub \
  --title "AI 编程实战" --author "作者" --cover-svg
# 或显式指定：--cover-theme tech

# business / design / literature / science / personal 类似
```

未匹配关键词时自动回退到 kami。

## 单独生成封面

```bash
# SVG 封面（推荐，KDP 标准）
python3 ~/.claude/skills/qiaomu-epub-book-generator/scripts/gen_cover_svg.py \
  "书名" "副标题" "作者" cover.jpg kami minimal

# HTML 封面（Playwright 截图）
python3 ~/.claude/skills/qiaomu-epub-book-generator/scripts/gen_cover_html.py \
  "书名" "副标题" "作者" cover.jpg kami
```

## 完整工作流示例

### 场景：传记类电子书（马斯克传）

10 章节传记，从南非少年到世界首富。

```bash
# 1. 准备文章目录
mkdir -p /tmp/musk-book/articles/

# 2. 文章命名规范（按章节顺序）
/tmp/musk-book/articles/
  ├── 01-南非少年.md
  ├── 02-初试锋芒.md
  ├── 03-PayPal传奇.md
  ├── 04-仰望星空.md
  ├── 05-电动革命.md
  ├── 06-多线作战.md
  ├── 07-AI野心.md
  ├── 08-推特风云.md
  ├── 09-政治漩涡.md
  └── 10-首富人生.md

# 3. 一键生成（kami 风格 SVG 封面）
python3 ~/.claude/skills/qiaomu-epub-book-generator/scripts/gen_epub_enhanced.py \
  /tmp/musk-book/articles/ \
  ~/Downloads/埃隆马斯克传.epub \
  --title "埃隆·马斯克传" \
  --subtitle "从南非少年到世界首富的传奇人生" \
  --author "向阳乔木" \
  --language zh \
  --cover-svg
```

**最佳实践**：
- 文章按章节编号（01-、02-...）确保顺序
- 副标题概括核心内容
- 纯文本传记约 0.2 MB，适合快速阅读
- 兼容微信读书、Apple Books、Kindle

### 场景：技术文集（Tw93 博客 → EPUB）

```bash
# 4 篇文章，53 张图片（33 SVG→PNG），约 2.9 MB 输出
python3 ~/.claude/skills/qiaomu-epub-book-generator/scripts/gen_epub_enhanced.py \
  /tmp/tw93_articles/ \
  ~/Tw93技术文集.epub \
  --title "Tw93技术文集" \
  --subtitle "Claude、Agent、LLM 与学习方法论" \
  --author "Tw93" \
  --cover-svg \
  --cover-theme tech \
  --image-quality 88 \
  --image-width 1000
```

`--cover-theme tech` 显式覆盖默认的 kami（因为本例希望用深色技术封面）。

### 场景：多篇文章 + 同名配图

```
~/my-articles/
  ├── article1.md
  ├── article1.png       # 配图（同名自动嵌入）
  ├── article2.md
  ├── article2.png
  └── article3.md
```

```bash
python3 ~/.claude/skills/qiaomu-epub-book-generator/scripts/gen_epub_enhanced.py \
  ~/my-articles/ \
  ~/output.epub
```

自动处理：
- 扫描所有 `.md` 文件
- 查找同名 `.png` / `.jpg` 配图
- 压缩图片（默认宽度 1000px，JPEG 88%）
- 生成目录（TOC）
- 输出压缩报告

## 配置参数示例

### 自定义图片压缩

```bash
python3 .../gen_epub_enhanced.py ~/articles ~/output.epub \
  --image-width 600 \
  --image-quality 75
```

### 完整元数据

```bash
python3 .../gen_epub_enhanced.py ~/articles ~/output.epub \
  --title "我的文集" \
  --subtitle "副标题" \
  --author "作者名" \
  --language zh \
  --cover-svg
```

## 输出验证

```bash
# 查看文件大小
ls -lh ~/output.epub

# 验证章节数
python3 -c "
from ebooklib import epub
book = epub.read_epub('$HOME/output.epub')
chapters = [i for i in book.items if isinstance(i, epub.EpubHtml)]
print(f'章节数: {len(chapters)}')
"

# 在 Apple Books 中打开
open ~/output.epub
```

## 常见问题

### Q: 图片太大，EPUB 超过 100MB？

降低 `--image-width` 和 `--image-quality`：

```bash
python3 .../gen_epub_enhanced.py ~/articles ~/output.epub \
  --image-width 600 --image-quality 70
```

### Q: 微信读书显示不正常？

用基础版 `gen_epub.py`，CSS 简化更兼容：

```bash
python3 ~/.claude/skills/qiaomu-epub-book-generator/scripts/gen_epub.py \
  ~/articles/ ~/output.epub \
  --title "我的书" --author "作者"
```

### Q: 如何批量生成多本书？

```bash
#!/bin/bash
for dir in ~/books/*/; do
  book_name=$(basename "$dir")
  python3 ~/.claude/skills/qiaomu-epub-book-generator/scripts/gen_epub_enhanced.py \
    "$dir" \
    ~/output/"$book_name".epub \
    --title "$book_name" \
    --cover-svg
done
```

### Q: 想给所有书统一用浅色封面？

直接用默认（kami 已是默认主题）。如果某本书因为关键词被自动识别成 tech/business 等深色主题，可显式指定：

```bash
--cover-theme kami
```

## 技术细节

### Markdown 解析

- 支持标准 Markdown 语法
- 自动提取 frontmatter 元数据
- 保留代码块、引用、列表等格式
- `gen_epub_enhanced.py` 额外支持 GFM 表格、内联代码、列表嵌套

### 图片处理流程

1. 扫描 Markdown 文件，识别远程 URL 和本地路径
2. 远程 URL 用 urllib 下载，SVG 用 Playwright 渲染为 PNG
3. 使用 Pillow 加载图片
4. 按比例缩放到 `--image-width`
5. 转换为 JPEG（RGBA 透明区域填充白色）
6. 压缩到 `--image-quality`
7. 嵌入 XHTML 章节

### EPUB 结构

```
output.epub
├── META-INF/
│   └── container.xml
├── OEBPS/
│   ├── content.opf       # 元数据和清单
│   ├── toc.ncx           # 目录
│   ├── nav.xhtml         # EPUB3 导航
│   ├── chapter1.xhtml    # 章节内容
│   ├── chapter2.xhtml
│   ├── images/
│   │   ├── img1.jpg
│   │   └── img2.jpg
│   └── cover.jpg         # 封面（如有）
└── mimetype
```

## 相关资源

- [配置规范](config-spec.md) - 完整参数说明
- [ebooklib 文档](https://github.com/aerkalov/ebooklib) - Python EPUB 库
- [EPUB 3 规范](https://www.w3.org/publishing/epub3/) - 官方标准
