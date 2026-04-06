# EPUB 生成配置规范

## 基础参数

### 输入
- `input_dir`: Markdown 文件目录（必需）
- `output_file`: 输出 EPUB 文件路径（必需）
- `cover_image`: 封面图片路径（可选）

### 元数据
- `title`: 书名（默认：从第一篇文章提取）
- `author`: 作者（默认：从 Markdown frontmatter 提取）
- `language`: 语言代码（默认：`zh`）
- `description`: 书籍描述（可选）

### 图片处理
- `image_max_width`: 图片最大宽度（默认：1000px）
- `image_quality`: JPEG 压缩质量（默认：88）
- `convert_png_to_jpg`: 是否转换 PNG 为 JPEG（默认：true）

### 排版
- `font_family`: 字体族（默认：`'Noto Serif SC', 'Source Han Serif SC', serif`）
- `line_height`: 行高（默认：1.8）
- `font_size`: 基础字号（默认：16px）

## 使用示例

### Python 脚本调用

```python
from scripts.gen_epub_v2 import generate_epub

generate_epub(
    input_dir="~/articles",
    output_file="~/output.epub",
    title="我的文集",
    author="作者名",
    cover_image="~/cover.jpg",
    image_quality=85
)
```

### 命令行调用

```bash
# 基础版（无封面）
python3 scripts/gen_epub_v2.py ~/articles ~/output.epub

# 带封面版
python3 scripts/gen_epub_with_cover.py ~/articles ~/output.epub ~/cover.jpg

# 生成封面
python3 scripts/gen_pg_covers.py 0 1  # 生成第 0 号封面设计
```

## 微信读书兼容性

`gen_epub_v2.py` 针对微信读书优化：
- 使用 `<h2>` 作为章节标题（而非 `<h1>`）
- 简化 CSS（避免复杂选择器）
- 图片居中对齐
- 段落间距优化

## 封面设计风格

`gen_pg_covers.py` 提供 10 种 Mondo 风格设计：
- 0-2: 极简主义（几何图形）
- 3-5: 瑞士国际主义（网格系统）
- 6-9: Paul Rand 风格（色块拼贴）

每种设计自动生成 1200x1800px 高清封面。
