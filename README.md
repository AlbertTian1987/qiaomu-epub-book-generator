# 📚 EPUB Book Generator

> 把你的 Markdown 文章一键生成专业电子书

从博客文章、技术笔记、学习资料生成精美 EPUB 电子书。自动下载图片、完美渲染代码块、生成专业封面，兼容微信读书和 Apple Books。

**[English](#english) | [中文](#中文)**

---

<a name="english"></a>
## English

### What It Does

Converts Markdown files into professional EPUB ebooks with:
- ✅ Auto-downloads remote images (http/https URLs)
- ✅ SVG to PNG conversion (perfect for web articles)
- ✅ Code blocks, tables, lists rendering
- ✅ Professional cover generation (SVG/HTML)
- ✅ Image compression (PNG→JPEG)
- ✅ WeChat Reading & Apple Books compatible

### Installation

**Option 1: npx (Recommended)**
```bash
npx skills add joeseesun/qiaomu-epub-book-generator
```

**Option 2: Git Clone**
```bash
git clone https://github.com/joeseesun/qiaomu-epub-book-generator.git ~/.claude/skills/qiaomu-epub-book-generator
```

### Prerequisites

- [ ] Python 3.8+ (`python3 --version`)
- [ ] pip installed (`pip3 --version`)
- [ ] Install dependencies:
  ```bash
  pip install ebooklib markdown Pillow playwright beautifulsoup4
  playwright install chromium
  ```
  Verify: `python3 -c "import ebooklib; print('OK')"`

### Quick Start

**Step 1: Prepare Markdown files**
```bash
mkdir ~/my-articles
# Put your .md files in ~/my-articles/
```

**Step 2: Generate EPUB**

Tell Claude Code:
- "Generate EPUB from ~/my-articles/"
- "Create ebook from my blog posts"
- "Make EPUB with title 'My Tech Blog' and author 'John Doe'"

Or run directly:
```bash
cd ~/.claude/skills/qiaomu-epub-book-generator/scripts
python3 gen_epub_enhanced.py ~/my-articles ~/output.epub \
  --title "My Tech Blog" \
  --author "John Doe" \
  --cover-svg
```

**Step 3: Verify output**
```bash
ls -lh ~/output.epub
# Should see file size (e.g., 2.5 MB)
```

### Usage Examples

**Basic (auto-detect title from first article)**
```bash
python3 gen_epub_enhanced.py ~/articles ~/book.epub
```

**With SVG cover (KDP standard 1600x2560)**
```bash
python3 gen_epub_enhanced.py ~/articles ~/book.epub \
  --title "My Book" \
  --subtitle "A Collection of Essays" \
  --author "Your Name" \
  --cover-svg \
  --cover-theme tech \
  --cover-layout minimal
```

**With custom cover image**
```bash
python3 gen_epub_enhanced.py ~/articles ~/book.epub \
  --title "My Book" \
  --author "Your Name" \
  --cover ~/my-cover.jpg
```

**Custom image quality**
```bash
python3 gen_epub_enhanced.py ~/articles ~/book.epub \
  --image-quality 95 \
  --image-width 1200
```

### Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `input_dir` | Directory with Markdown files | Required |
| `output_file` | Output EPUB path | Required |
| `--title` | Book title | From first article |
| `--author` | Author name(s), separate with `/` | From frontmatter |
| `--subtitle` | Subtitle for cover | None |
| `--language` | Language code | `zh` |
| `--cover` | Cover image path | None |
| `--cover-svg` | Generate SVG cover (KDP 1600x2560) | `False` |
| `--cover-html` | Generate HTML cover | `False` |
| `--cover-theme` | Cover theme: tech, business, design, literature, science, personal | Auto-detect |
| `--cover-layout` | SVG layout: minimal, classic, modern | `minimal` |
| `--image-quality` | JPEG quality (1-100) | `88` |
| `--image-width` | Max image width (pixels) | `1000` |

### Cover Themes

| Theme | Keywords | Style |
|-------|----------|-------|
| `tech` | programming, AI, code, algorithm | Deep navy + cyan |
| `business` | startup, marketing, growth, product | Deep blue + gold |
| `design` | design, UI/UX, visual, brand | Deep purple + pink |
| `literature` | novel, poetry, story, philosophy | Navy blue + warm yellow |
| `science` | science, physics, research, theory | Teal + mint |
| `personal` | growth, learning, notes, reflection | Deep purple + peach |

### Real-World Example

**Tw93 Tech Blog → EPUB**
```bash
# 4 articles, 53 images (33 SVG→PNG), 2.9 MB output
python3 gen_epub_enhanced.py /tmp/tw93_articles ~/Tw93-Tech.epub \
  --title "Tw93技术文集" \
  --subtitle "Claude、Agent、LLM 与学习方法论" \
  --author "Tw93" \
  --cover ~/cover.png \
  --image-quality 88 \
  --image-width 1000
```

### Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'ebooklib'` | Run `pip install ebooklib markdown Pillow` |
| `playwright._impl._api_types.Error: Executable doesn't exist` | Run `playwright install chromium` |
| Code blocks show red boxes around special characters | Fixed in v2.0+ (regex removes Pygments error borders) |
| Images not embedded | Check image URLs are valid http/https or local paths |
| SVG conversion fails | Ensure Playwright installed: `pip install playwright && playwright install chromium` |
| EPUB file too large | Reduce `--image-quality` (e.g., 75) or `--image-width` (e.g., 800) |

### ⚠️ Notes

- **Playwright required** for SVG conversion and cover generation
- **Image download**: Remote images are downloaded and embedded automatically
- **File size**: Typical 2-5 MB for 10-20 articles with images
- **Compatibility**: Tested on WeChat Reading, Apple Books, Calibre

### Credits

- Based on [ebooklib](https://github.com/aerkalov/ebooklib) by Aleksandar Erkalović
- Markdown rendering: [Python-Markdown](https://github.com/Python-Markdown/markdown)
- Image processing: [Pillow](https://github.com/python-pillow/Pillow)

---

<a name="中文"></a>
## 中文

### 核心价值

把 Markdown 文章转换成专业 EPUB 电子书，支持：
- ✅ 自动下载远程图片（http/https URL）
- ✅ SVG 自动转 PNG（完美支持网页文章）
- ✅ 完整渲染代码块、表格、列表
- ✅ 专业封面生成（SVG/HTML）
- ✅ 图片智能压缩（PNG→JPEG）
- ✅ 兼容微信读书和 Apple Books

### 安装方式

**方式 1：npx（推荐）**
```bash
npx skills add joeseesun/qiaomu-epub-book-generator
```

**方式 2：Git 克隆**
```bash
git clone https://github.com/joeseesun/qiaomu-epub-book-generator.git ~/.claude/skills/qiaomu-epub-book-generator
```

### 前置条件

- [ ] Python 3.8+ (`python3 --version` 检查)
- [ ] pip 已安装 (`pip3 --version` 检查)
- [ ] 安装依赖：
  ```bash
  pip install ebooklib markdown Pillow playwright beautifulsoup4
  playwright install chromium
  ```
  验证：`python3 -c "import ebooklib; print('OK')"`

### 快速开始

**第 1 步：准备 Markdown 文件**
```bash
mkdir ~/my-articles
# 把你的 .md 文件放到 ~/my-articles/ 目录
```

**第 2 步：生成 EPUB**

直接对 Claude Code 说：
- "从 ~/my-articles/ 生成 EPUB"
- "把我的博客文章做成电子书"
- "生成 EPUB，书名《我的技术博客》，作者张三"

或直接运行命令：
```bash
cd ~/.claude/skills/qiaomu-epub-book-generator/scripts
python3 gen_epub_enhanced.py ~/my-articles ~/output.epub \
  --title "我的技术博客" \
  --author "张三" \
  --cover-svg
```

**第 3 步：验证输出**
```bash
ls -lh ~/output.epub
# 应该看到文件大小（如 2.5 MB）
```

### 使用示例

**基础用法（自动从第一篇文章提取标题）**
```bash
python3 gen_epub_enhanced.py ~/articles ~/book.epub
```

**生成 SVG 封面（KDP 标准 1600x2560）**
```bash
python3 gen_epub_enhanced.py ~/articles ~/book.epub \
  --title "我的书" \
  --subtitle "文章合集" \
  --author "你的名字" \
  --cover-svg \
  --cover-theme tech \
  --cover-layout minimal
```

**使用自定义封面图片**
```bash
python3 gen_epub_enhanced.py ~/articles ~/book.epub \
  --title "我的书" \
  --author "你的名字" \
  --cover ~/my-cover.jpg
```

**自定义图片质量**
```bash
python3 gen_epub_enhanced.py ~/articles ~/book.epub \
  --image-quality 95 \
  --image-width 1200
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `input_dir` | Markdown 文件目录 | 必填 |
| `output_file` | 输出 EPUB 文件路径 | 必填 |
| `--title` | 书名 | 从第一篇文章提取 |
| `--author` | 作者（多个用 `/` 分隔） | 从 frontmatter 提取 |
| `--subtitle` | 封面副标题 | 无 |
| `--language` | 语言代码 | `zh` |
| `--cover` | 封面图片路径 | 无 |
| `--cover-svg` | 生成 SVG 封面（KDP 1600x2560） | `False` |
| `--cover-html` | 生成 HTML 封面 | `False` |
| `--cover-theme` | 封面主题：tech, business, design, literature, science, personal | 自动检测 |
| `--cover-layout` | SVG 布局：minimal, classic, modern | `minimal` |
| `--image-quality` | JPEG 压缩质量 (1-100) | `88` |
| `--image-width` | 图片最大宽度（像素） | `1000` |

### 封面主题

| 主题 | 关键词 | 风格 |
|------|--------|------|
| `tech` | 编程、AI、代码、算法 | 深蓝 + 青色 |
| `business` | 创业、营销、增长、产品 | 深蓝 + 金色 |
| `design` | 设计、UI/UX、视觉、品牌 | 深紫 + 粉色 |
| `literature` | 小说、诗歌、故事、哲学 | 海军蓝 + 暖黄 |
| `science` | 科学、物理、研究、理论 | 青绿 + 薄荷 |
| `personal` | 成长、学习、笔记、反思 | 深紫 + 桃色 |

### 真实案例

**Tw93 技术博客 → EPUB**
```bash
# 4 篇文章，53 张图片（33 SVG→PNG），2.9 MB 输出
python3 gen_epub_enhanced.py /tmp/tw93_articles ~/Tw93技术文集.epub \
  --title "Tw93技术文集" \
  --subtitle "Claude、Agent、LLM 与学习方法论" \
  --author "Tw93" \
  --cover ~/cover.png \
  --image-quality 88 \
  --image-width 1000
```

### 常见问题

| 问题 | 解决方法 |
|------|----------|
| `ModuleNotFoundError: No module named 'ebooklib'` | 运行 `pip install ebooklib markdown Pillow` |
| `playwright._impl._api_types.Error: Executable doesn't exist` | 运行 `playwright install chromium` |
| 代码块特殊字符有红框 | v2.0+ 已修复（正则移除 Pygments 错误边框） |
| 图片没有嵌入 | 检查图片 URL 是否有效（http/https 或本地路径） |
| SVG 转换失败 | 确保安装 Playwright：`pip install playwright && playwright install chromium` |
| EPUB 文件太大 | 降低 `--image-quality`（如 75）或 `--image-width`（如 800） |

### ⚠️ 注意事项

- **需要 Playwright**：用于 SVG 转换和封面生成
- **图片下载**：远程图片会自动下载并嵌入
- **文件大小**：10-20 篇文章带图片通常 2-5 MB
- **兼容性**：已在微信读书、Apple Books、Calibre 测试

### 致谢

- 基于 [ebooklib](https://github.com/aerkalov/ebooklib)（作者：Aleksandar Erkalović）
- Markdown 渲染：[Python-Markdown](https://github.com/Python-Markdown/markdown)
- 图片处理：[Pillow](https://github.com/python-pillow/Pillow)

---

## 📱 关注作者

如果这个项目对你有帮助，欢迎关注我获取更多技术分享：

- **X (Twitter)**: [@vista8](https://x.com/vista8)
- **微信公众号「向阳乔木推荐看」**:

<p align="center">
  <img src="https://github.com/joeseesun/terminal-boost/raw/main/assets/wechat-qr.jpg?raw=true" alt="向阳乔木推荐看公众号二维码" width="300">
</p>

- **GitHub**: [@joeseesun](https://github.com/joeseesun)

## 许可证

MIT License
