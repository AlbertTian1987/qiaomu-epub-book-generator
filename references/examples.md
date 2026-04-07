# EPUB 生成示例

## 基础用法

### 1. 单个 Markdown 文件生成 EPUB

```bash
python3 ~/.claude/skills/qiaomu-epub-book-generator/scripts/gen_epub.py \
  --title "我的书" \
  --author "作者名" \
  ~/articles/ \
  ~/output.epub
```

**说明**：
- 自动扫描 `~/articles/` 目录下的所有 `.md` 文件
- 从第一篇文章提取标题和作者
- 自动查找同名 PNG/JPG 配图并压缩嵌入
- 生成微信读书兼容的 EPUB

### 2. 带封面的 EPUB

```bash
python3 ~/.claude/skills/epub-book-generator/scripts/gen_epub_with_cover.py \
  ~/articles/ \
  ~/book.epub \
  ~/cover.jpg
```

**说明**：
- 第三个参数指定封面图片路径
- 封面会自动设置为 EPUB 的 cover image
- 支持 JPG/PNG 格式

### 3. 生成 Mondo 风格封面

```bash
# 生成第 0 号设计（极简主义）
python3 ~/.claude/skills/epub-book-generator/scripts/gen_pg_covers.py 0 1

# 生成第 3-5 号设计（瑞士国际主义）
python3 ~/.claude/skills/epub-book-generator/scripts/gen_pg_covers.py 3 3

# 生成所有 10 种设计
python3 ~/.claude/skills/epub-book-generator/scripts/gen_pg_covers.py 0 10
```

**说明**：
- 第一个参数：起始设计编号（0-9）
- 第二个参数：生成数量
- 输出：`cover-{n}.png`（1200x1800px）

**设计风格**：
- 0-2: 极简主义（几何图形）
- 3-5: 瑞士国际主义（网格系统）
- 6-9: Paul Rand 风格（色块拼贴）

## Python 脚本调用

### 基础版本（gen_epub.py）

```python
from scripts.gen_epub import generate_epub

generate_epub(
    input_dir="~/articles",
    output_file="~/output.epub",
    title="我的文集",
    author="作者名"
)
```

### 微信读书优化版（gen_epub.py）

```python
from scripts.gen_epub import generate_epub

generate_epub(
    input_dir="~/articles",
    output_file="~/output.epub",
    title="我的文集",
    author="作者名",
    language="zh",
    image_quality=85  # JPEG 压缩质量
)
```

### 带封面版本（gen_epub_with_cover.py）

```python
from scripts.gen_epub_with_cover import generate_epub_with_cover

generate_epub_with_cover(
    input_dir="~/articles",
    output_file="~/book.epub",
    cover_image="~/cover.jpg",
    title="我的书",
    author="作者名"
)
```

## 完整工作流示例

### 场景：传记类电子书制作（马斯克传）

**真实案例**：10 章节传记，从南非少年到世界首富

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

# 3. 一键生成（自动生成 HTML 封面）
python3 ~/.claude/skills/qiaomu-epub-book-generator/scripts/gen_epub.py \
  --title "埃隆·马斯克传" \
  --subtitle "从南非少年到世界首富的传奇人生" \
  --author "向阳乔木" \
  --language zh \
  --cover-html \
  /tmp/musk-book/articles/ \
  ~/Downloads/埃隆马斯克传.epub

# 4. 输出结果
# ✅ Done!
#   Output: ~/Downloads/埃隆马斯克传.epub
#   File size: 0.2 MB
#   Chapters: 10
```

**最佳实践**：
- ✅ 文章按章节编号（01-、02-...）确保顺序
- ✅ 使用 `--cover-html` 自动生成精美封面
- ✅ 副标题概括核心内容
- ✅ 纯文本传记约 0.2 MB，适合快速阅读
- ✅ 兼容微信读书、Apple Books

### 场景：技术文集制作

```bash
# 1. 准备目录结构
mkdir -p ~/tech-essays/{articles,covers}

# 2. 生成 EPUB（自动生成封面）
python3 ~/.claude/skills/qiaomu-epub-book-generator/scripts/gen_epub.py \
  --title "我的技术文集" \
  --subtitle "230篇创业与编程经典" \
  --author "作者名" \
  --language zh \
  --cover-html \
  ~/tech-essays/articles/ \
  ~/tech-essays/output.epub

# 3. 验证输出
ls -lh ~/tech-essays/output.epub
```

### 场景：多篇文章快速生成

```bash
# 文章目录结构
~/my-articles/
  ├── article1.md
  ├── article1.png  # 配图（可选）
  ├── article2.md
  ├── article2.png
  └── article3.md

# 一键生成
python3 ~/.claude/skills/epub-book-generator/scripts/gen_epub_v2.py \
  ~/my-articles/ \
  ~/output.epub
```

**自动处理**：
- 扫描所有 `.md` 文件
- 查找同名 `.png` 或 `.jpg` 配图
- 压缩图片（宽度 1000px，JPEG 88%）
- 生成目录（TOC）
- 输出压缩报告

## 配置参数示例

### 自定义图片压缩

```python
generate_epub(
    input_dir="~/articles",
    output_file="~/output.epub",
    image_max_width=800,      # 图片最大宽度（默认 1000px）
    image_quality=75,         # JPEG 质量（默认 88）
    convert_png_to_jpg=True   # PNG 转 JPEG（默认 True）
)
```

### 自定义排版

```python
generate_epub(
    input_dir="~/articles",
    output_file="~/output.epub",
    font_family="'Noto Serif SC', 'Source Han Serif SC', serif",
    line_height=1.8,          # 行高（默认 1.8）
    font_size="16px"          # 基础字号（默认 16px）
)
```

### 完整元数据

```python
generate_epub(
    input_dir="~/articles",
    output_file="~/output.epub",
    title="我的文集",
    author="作者名",
    language="zh",            # 语言代码（默认 zh）
    description="这是一本关于创业和编程的文集",
    cover_image="~/cover.jpg"
)
```

## 输出验证

### 检查 EPUB 文件

```bash
# 查看文件大小
ls -lh ~/output.epub

# 验证章节数（需要 Python）
python3 -c "
from ebooklib import epub
book = epub.read_epub('~/output.epub')
print(f'章节数: {len([item for item in book.items if isinstance(item, epub.EpubHtml)])}')
"

# 在 Apple Books 中打开
open ~/output.epub
```

### 压缩报告示例

```
图片压缩报告：
- 原始总大小: 460.8 MB
- 压缩后大小: 45.2 MB
- 压缩率: 90.2%
- 处理图片数: 230 张
```

## 常见问题

### Q: 图片太大，EPUB 文件超过 100MB？

**A**: 调整压缩参数：

```python
generate_epub(
    input_dir="~/articles",
    output_file="~/output.epub",
    image_max_width=600,      # 降低宽度
    image_quality=70          # 降低质量
)
```

### Q: 微信读书显示不正常？

**A**: 使用 `gen_epub_v2.py`（微信读书优化版）：
- 使用 `<h2>` 作为章节标题
- 简化 CSS
- 图片居中对齐

### Q: 如何批量生成多本书？

**A**: 使用 Shell 脚本：

```bash
#!/bin/bash
for dir in ~/books/*/; do
  book_name=$(basename "$dir")
  python3 ~/.claude/skills/epub-book-generator/scripts/gen_epub_v2.py \
    "$dir" \
    ~/output/"$book_name".epub
done
```

## 技术细节

### Markdown 解析

- 支持标准 Markdown 语法
- 自动提取 frontmatter 元数据
- 保留代码块、引用、列表等格式

### 图片处理流程

1. 扫描 Markdown 文件，查找同名图片
2. 使用 Pillow 加载图片
3. 按比例缩放到指定宽度
4. 转换为 JPEG（可选）
5. 压缩到指定质量
6. 嵌入 XHTML 章节

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
│   └── style.css         # 样式表
└── mimetype
```

## 相关资源

- [配置规范](config-spec.md) - 完整参数说明
- [ebooklib 文档](https://github.com/aerkalov/ebooklib) - Python EPUB 库
- [EPUB 3 规范](https://www.w3.org/publishing/epub3/) - 官方标准
