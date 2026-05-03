---
name: qiaomu-epub-book-generator
description: Generate EPUB ebooks from Markdown files with SVG→PNG conversion, remote/local image embedding, compressed illustrations, and WeChat Reading compatibility. The most universal EPUB generator.
version: 2.0.0
trigger_phrases:
  - "生成 EPUB"
  - "制作电子书"
  - "生成电子书"
  - "做成 EPUB"
  - "转换成 EPUB"
  - "generate epub"
  - "create ebook"
  - "make epub"
  - "准备小说源文件"
  - "准备小说"
  - "处理小说"
  - "料理小说"
  - "prepare novel"
  - "split novel"
exclusions:
  - "阅读 EPUB"
  - "打开 EPUB"
  - "解压 EPUB"
  - "编辑 EPUB"
---

# EPUB Book Generator

从 Markdown 文件生成专业 EPUB 电子书，支持封面、配图压缩、目录生成。

## 功能特性

- ✅ 单文件或多文件 EPUB 生成
- ✅ **自动下载 Markdown 中的图片**（支持 http/https URL）
- ✅ **SVG 自动转换**（使用 Playwright 将 SVG 转为 PNG，完美支持网页文章）
- ✅ **本地文件路径支持**（支持本地图片文件直接嵌入）
- ✅ 自动图片压缩（PNG→JPEG，可配置质量）
- ✅ **完整 Markdown 渲染**（代码块、表格、列表等）
- ✅ **专业书籍封面设计**（遵循出版行业最佳实践）
  - SVG 封面：KDP 标准尺寸（1600x2560），专业排版
  - **kami-novel 主题**：羊皮纸 + 墨蓝，零几何装饰，仅字体与双线（网文默认）
  - **literary 布局**：标题上方下方双细线，无几何形状
  - 自动书名长度自适应（4 档字号）
  - 关键词自动路由：网文→kami-novel，文学→literature
- ✅ **Kami 文学版排版系统**
  - **双光照色契约**（仅文字色）：亮色墨蓝 `#1B365D` / 暗色提亮 `#6B95C9`，背景交由阅读器控制
  - **webnovel/literary 双模式**：`--mode` 切换，字号/行高自适应
  - **章节标题 4 档自适应**：根据章号+章名总字符数自动选择字号/字距
  - **中文着重号**：`<em>` 渲染为旁点，英文保留真斜体
  - **段首缩进 2em**：全段落统一，无特例
  - **左对齐排版**：跨阅读器一致
- ✅ **网文特化**
  - **卷分组 + 卷封页**：NCX 嵌套 TOC，frontmatter/文件夹/文件名三种约定
  - **楔子/序章/引子**：TOC 前置区，无章号
  - **番外**：TOC 附录区
  - **场景分隔符归一**：`---`/`***`/连续空行 → ❦
  - **章末 ❦ 花饰**：每章末尾自动添加
  - **未完待续检测**：正文末尾标记自动样式化
  - **作者按**：章末引用块渲染为 stone 小字
- ✅ **跨阅读器兼容**：Apple Books / Calibre / 微信读书
- ✅ **输入合约验收脚本**：`verify_novel_input.py`（12 项检查）
- ✅ **Charter 字体嵌入**（可选，`--embed-charter`）
- ✅ **中文标点归一**（可选，`--no-punct-fix` 关闭）

## 使用方式

### ⚠️ 封面生成规则（重要）

**默认行为**：
- 如果用户提供了书名（`--title`）或作者（`--author`），**必须自动生成封面**
- 默认使用 `--cover-svg` 参数（KDP 标准尺寸，专业排版）
- 副标题（`--subtitle`）可选，默认为 "N articles"
- 主题自动检测，也可手动指定 `--cover-theme`

**封面方法选择**：
| 方法 | 参数 | 尺寸 | 适用场景 |
|------|------|------|----------|
| SVG（推荐） | `--cover-svg` | 1600x2560 (KDP) | 专业出版、高质量封面 |
| HTML | `--cover-html` | 1600x2560 | 快速生成、兼容性好 |
| 自定义图片 | `--cover path.jpg` | 任意 | 用户自己设计的封面 |

**例外情况**：
- 用户明确说"不要封面"或"无封面" → 不生成
- 用户提供了封面图片路径（`--cover`）→ 使用用户封面

**命令模板**：
```bash
# SVG 封面（推荐，KDP 标准）
python3 gen_epub_enhanced.py <input_dir> <output.epub> \
  --title "书名" \
  --author "作者" \
  --cover-svg \
  --subtitle "副标题（可选）" \
  --cover-theme "tech" \
  --cover-layout "minimal"

# HTML 封面
python3 gen_epub_enhanced.py <input_dir> <output.epub> \
  --title "书名" \
  --author "作者" \
  --cover-html \
  --subtitle "副标题（可选）"
```

**可用主题**：kami（默认）, kami-novel（网文专用，羊皮纸+墨蓝）, tech, business, design, literature, science, personal

### 完整 CLI 参数

```bash
# 网文小说（推荐）
python3 gen_epub_enhanced.py <input_dir> <output.epub> \
  --title "书名" --author "作者" --mode webnovel --cover-svg

# 可选增强
  --embed-charter            # 嵌入 Charter 字体（~1.5MB）
  --no-punct-fix             # 关闭中文标点归一
  --chapter-num-position {above|inline|hidden}  # 章号位置
```

| 参数 | 说明 | 默认 |
|------|------|------|
| `--mode` | 排版模式：webnovel / literary | webnovel |
| `--chapter-num-position` | 章号位置：above / inline / hidden | 自动 |
| `--no-punct-fix` | 关闭标点归一 | 关（归一开启） |
| `--embed-charter` | 嵌入 Charter 字体 | 不嵌入 |
| `--cover-theme` | 封面主题 | 自动检测 |
| `--cover-layout` | 封面布局 | minimal |
**可用布局**（仅 SVG）：minimal, classic, modern, **literary**（网文默认，零几何装饰）

### 基础用法

```
生成 EPUB：
- 输入目录：~/articles/
- 输出：~/output.epub
- 自动生成封面（如果有书名/作者）
```

### 带自定义封面

```
生成带封面的 EPUB：
- 文章：~/articles/*.md
- 封面：~/cover.jpg
- 输出：~/book.epub
```

### 自动生成封面（推荐）

```
生成 EPUB 并设计封面：
- 书名：《我的书》
- 副标题：精选文章合集
- 作者：向阳乔木
- 风格：kami 编辑感（默认）
```

**真实案例**：

```
生成马斯克传记电子书：
- 书名：《埃隆·马斯克传》
- 副标题：从南非少年到世界首富的传奇人生
- 作者：向阳乔木
- 章节：10 章（01-南非少年.md 到 10-首富人生.md）
- 输出：0.2 MB，兼容微信读书和 Apple Books
```

## 工作流程

1. **收集输入**
   - 扫描 Markdown 文件
   - 检查配图（同名 PNG/JPG）
   - 确认封面（可选）

2. **处理内容**
   - 解析 Markdown（标题、元数据、正文）
   - **自动下载远程图片**（http/https URL）
   - **SVG 自动转换**（使用 Playwright 渲染为 PNG）
   - **本地文件嵌入**（支持相对/绝对路径）
   - 压缩图片（宽度 1000px，JPEG 88%）
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

## 参数配置

详见 [references/config-spec.md](references/config-spec.md)

## 脚本说明

- `scripts/gen_epub_enhanced.py` - **推荐** 增强版（Kami 文学版排版、卷分组、NCX 嵌套 TOC、标点归一、双光照色契约、Charter 字体嵌入、520 章实测通过）
- `scripts/gen_epub.py` - 基础 EPUB 生成（本地图片匹配模式，WeChat 兼容简化版 CSS）
- `scripts/gen_cover_svg.py` - SVG 封面生成器（KDP 标准 1600x2560，7 主题 × 3 布局）
- `scripts/gen_cover_html.py` - HTML 封面生成器（Playwright 截图模式）

## 常见问题与解决方案

### SVG 图片缺失问题

**症状**：生成的 EPUB 中 SVG 图片不显示

**原因**：大多数 EPUB 阅读器不支持 SVG 格式

**解决方案**：
1. `gen_epub_enhanced.py` 会自动检测 SVG 图片
2. 使用 Playwright 将 SVG 渲染为 PNG
3. 自动替换 Markdown 中的图片链接

**技术细节**：
- SVG 检测：通过 URL 扩展名、Content-Type、文件头识别
- 转换方式：Playwright headless browser 渲染 + 截图
- 批处理优化：共享浏览器实例，提升转换速度

### Blob URL 问题

**症状**：脚本卡住不动，或报错 "unknown url type: blob:"

**原因**：Markdown 中包含 `blob:http://localhost/...` 等浏览器内存 URL，无法下载

**解决方案**：
```bash
# 清理 blob URLs
sed -i '' '/!\[.*\](blob:http:\/\/localhost\//d' your-article.md
```

### 本地文件路径支持

**用法**：Markdown 中可以直接使用本地图片路径

```markdown
![本地图片](./images/photo.png)
![绝对路径](/tmp/converted/image.jpg)
```

**支持的路径格式**：
- 相对路径：`./images/photo.png`
- 绝对路径：`/tmp/photo.png`
- 父目录：`../assets/photo.png`

### 网页文章转 EPUB 最佳实践

**场景**：从技术博客（如 tw93.fun）生成 EPUB

**推荐流程**：
1. 使用 `qiaomu-markdown-proxy` 或 `baoyu-url-to-markdown` 下载文章
2. 检查 Markdown 中的图片 URL（特别是 SVG）
3. 如果有大量 SVG，可选择：
   - **方案 A**（推荐）：直接运行 `gen_epub_enhanced.py`，自动转换
   - **方案 B**：预先批量转换 SVG，然后替换 URL
4. 清理 blob URLs（如有）
5. 生成 EPUB

**真实案例**：
```bash
# Tw93 技术文集（4 篇文章，33 个 SVG 图片）
python3 gen_epub_enhanced.py /tmp/tw93_articles/ output.epub \
  --title "Tw93技术文集" \
  --author "Tw93" \
  --image-width 1000 \
  --image-quality 88

# 输出：2.8 MB，53 张图片（33 SVG→PNG + 20 其他）
```

## 示例

详见 [references/examples.md](references/examples.md)

---

## 网文源文件准备 / 小说料理人

当用户说"准备小说源文件"、"帮我把这些 HTML/TXT 处理成小说"或类似意图时，你进入「小说料理人」模式。

**核心原则：不要直接用 Read/Write 逐文件处理。先写脚本，再跑验收，迭代到全绿。**

**输入合约**：详见 [references/input-contract.md](references/input-contract.md)

### 工作流

```
① 分析原始材料结构（打开样本看规律）
    ↓
② 编写一次性 Python 转换脚本
    ↓
③ 编写一次性 Python 验收脚本（基于合约 §8 验收标准）
    ↓
④ 跑转换脚本 → 跑验收脚本
    ↓  (有强制项未通过)
⑤ 分析失败原因 → 改转换脚本 → 回到 ④
    ↓  (全部通过)
⑥ 报告统计结果
```

### Step by Step

**① 分析**：读 2-3 个样本文件，识别：
- HTML：正文容器选择器、需去除的噪声、分页关系
- TXT：章节分隔符的正则模式、编码
- 已有 MD：文件命名是否规范、H1 是否完整

**② 写转换脚本**：
- 针对**这一次的源材料**，不是通用工具
- 用 Python + BeautifulSoup（HTML）或 re（TXT）
- 幂等设计（覆盖输出目录）
- 每章输出单个 `.md` 文件

**③ 写验收脚本**：
- 基于合约 §8 的验收模板
- 补充本次源材料特有的检查（如"HTML 来源无残留标签"）

**④ 迭代**：
- 每轮：跑转换 → 跑验收 → 看失败项 → 修正则/逻辑 → 重跑
- 验收全部强制项通过才算完成
- 改脚本而不是改产出文件

**⑤ 收尾**：报告文件数、总字数、警告项。脚本可留在 `scripts/prepare/` 供复现。

### 不做的

- 不改正文内容（错别字、润色、删减段落）
- 不用 Read/Write 工具代替脚本处理大量文件

### 章节拆分正则（TXT 来源参考）

```
^第[一二三四五六七八九十百千万零0-9]+[章节篇集部卷回]\s*
^第\d+[章节篇集部卷回]\s*
^Chapter\s+\d+
^CHAPTER\s+\d+
```
