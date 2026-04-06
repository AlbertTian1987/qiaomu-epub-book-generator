---
name: qiaomu-epub-book-generator
description: Generate EPUB ebooks from Markdown files with optional cover images, compressed illustrations, and WeChat Reading compatibility. Supports single or multiple articles with automatic TOC generation.
version: 1.0.0
trigger_phrases:
  - "生成 EPUB"
  - "制作电子书"
  - "生成电子书"
  - "做成 EPUB"
  - "转换成 EPUB"
  - "generate epub"
  - "create ebook"
  - "make epub"
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
- ✅ 自动图片压缩（PNG→JPEG，可配置质量）
- ✅ 封面图片支持（可选）
- ✅ 自动目录（TOC）生成
- ✅ 微信读书兼容模式
- ✅ 中文字体优化排版
- ✅ Mondo 风格封面设计生成

## 使用方式

### 基础用法

```
生成 EPUB：
- 输入目录：~/articles/
- 输出：~/output.epub
```

### 带封面

```
生成带封面的 EPUB：
- 文章：~/articles/*.md
- 封面：~/cover.jpg
- 输出：~/book.epub
```

### 自动生成封面

```
生成 EPUB 并设计封面：
- 书名：《Paul Graham 文集》
- 副标题：230篇创业与编程经典
- 风格：极简主义
```

## 工作流程

1. **收集输入**
   - 扫描 Markdown 文件
   - 检查配图（同名 PNG/JPG）
   - 确认封面（可选）

2. **处理内容**
   - 解析 Markdown（标题、元数据、正文）
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

- `scripts/gen_epub.py` - 基础 EPUB 生成
- `scripts/gen_epub_v2.py` - 微信读书兼容版
- `scripts/gen_epub_with_cover.py` - 带封面版本
- `scripts/gen_cover.py` - Mondo 风格封面生成

## 示例

详见 [references/examples.md](references/examples.md)
