# Qiaomu EPUB Book Generator

从 Markdown 文件生成专业 EPUB 电子书，支持封面、配图压缩、目录生成，兼容微信读书。

## 功能特性

- ✅ 单文件或多文件 EPUB 生成
- ✅ 自动图片压缩（PNG→JPEG，可配置质量）
- ✅ 封面图片支持（可选）
- ✅ **HTML 封面生成**（无需 AI 生图 API）
- ✅ 自动目录（TOC）生成
- ✅ **微信读书兼容模式**
- ✅ 中文字体优化排版
- ✅ 命令行参数支持

## 安装

```bash
# 克隆仓库
git clone https://github.com/joeseesun/qiaomu-epub-book-generator.git
cd qiaomu-epub-book-generator

# 安装依赖
pip install ebooklib markdown Pillow

# （可选）安装 Playwright 用于 HTML 封面生成
pip install playwright
playwright install chromium
```

## 使用方式

### 基础用法

```bash
python3 scripts/gen_epub.py ~/articles/ ~/output.epub
```

### 带封面图片

```bash
python3 scripts/gen_epub.py ~/articles/ ~/book.epub \
  --title "我的文集" \
  --author "作者名" \
  --cover cover.jpg
```

### 生成 HTML 封面（无需 AI API）

```bash
python3 scripts/gen_epub.py ~/articles/ ~/book.epub \
  --title "Paul Graham 文集" \
  --subtitle "230篇创业与编程经典" \
  --author "Paul Graham / 向阳乔木" \
  --cover-html
```

### 自定义图片质量

```bash
python3 scripts/gen_epub.py ~/articles/ ~/book.epub \
  --image-quality 95 \
  --image-width 1200
```

## 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `input_dir` | Markdown 文件目录 | 必填 |
| `output_file` | 输出 EPUB 文件路径 | 必填 |
| `--title` | 书名 | 从第一篇文章提取 |
| `--author` | 作者（多个用 `/` 分隔） | 从 Markdown frontmatter 提取 |
| `--language` | 语言代码 | `zh` |
| `--cover` | 封面图片路径 | 无 |
| `--cover-html` | 生成 HTML 封面 | `False` |
| `--subtitle` | HTML 封面副标题 | 无 |
| `--image-quality` | JPEG 压缩质量 (1-100) | `88` |
| `--image-width` | 图片最大宽度（像素） | `1000` |

## 文件结构要求

```
your-project/
├── articles/           # Markdown 文章目录
│   ├── article1.md
│   ├── article2.md
│   └── ...
├── article1.png        # 配图（可选，与文章同名）
├── article2.png
└── cover.jpg           # 封面（可选）
```

**Markdown 格式示例**：

```markdown
# 文章标题
> 作者 · 分类 · 2024

正文内容...
```

## 工作流程

1. **收集输入**
   - 扫描 Markdown 文件
   - 检查配图（同名 PNG/JPG）
   - 确认封面（可选）

2. **处理内容**
   - 解析 Markdown（标题、元数据、正文）
   - 压缩图片（默认宽度 1000px，JPEG 88%）
   - 构建 XHTML 章节

3. **生成 EPUB**
   - 创建 EpubBook 对象
   - 添加元数据（作者、语言、描述）
   - 设置封面（如有）
   - 生成目录（TOC）
   - 写入 EPUB 文件

4. **验证输出**
   - 检查文件大小
   - 统计章节数
   - 报告图片压缩率

## HTML 封面生成

无需 AI 生图 API，使用 Playwright 渲染 HTML 模板生成封面：

```bash
# 单独生成封面
python3 scripts/gen_cover_html.py "书名" "副标题" "作者" cover.jpg

# 在 EPUB 生成时自动生成
python3 scripts/gen_epub.py ~/articles/ ~/book.epub \
  --cover-html \
  --title "我的书" \
  --subtitle "100篇文章" \
  --author "作者名"
```

封面样式：
- 深色渐变背景
- 大标题 + 副标题 + 作者
- 极简设计，科技感
- 2:3 比例（900x1350px）

## 微信读书兼容性

- ✅ 内联 CSS（不依赖外部样式表）
- ✅ XHTML 1.1 严格模式
- ✅ 中文字体优化
- ✅ 图片自动压缩
- ✅ 标准 EPUB 2.0 格式

## 示例项目

参考 [Paul Graham 文集](https://github.com/joeseesun/paul-graham-essays) 项目，包含：
- 230 篇 Markdown 文章
- 230 张信息卡片配图
- 完整 EPUB 生成流程

## 技术栈

- Python 3.8+
- ebooklib 0.18+
- markdown 3.0+
- Pillow 9.0+
- Playwright（可选，用于 HTML 封面）

## 许可证

MIT License

## 作者

vista8 / 向阳乔木

## 关注作者

- **X (Twitter)**: [@vista8](https://x.com/vista8)
- **微信公众号**: 「向阳乔木推荐看」
- **GitHub**: [@joeseesun](https://github.com/joeseesun)
