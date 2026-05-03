#!/usr/bin/env python3
"""
Enhanced EPUB generator with image downloading and better Markdown rendering.

Key improvements:
1. Downloads all images from Markdown (http/https URLs) and embeds them
2. Better code block styling with syntax highlighting
3. Table support with proper styling
4. Preserves all Markdown elements (lists, blockquotes, etc.)

Usage:
    python3 gen_epub_enhanced.py <input_dir> <output.epub> [options]
"""

import argparse
import os
import glob
import re
import sys
import html as html_module
import hashlib
import urllib.request
import urllib.parse
from pathlib import Path
from ebooklib import epub
import markdown
from PIL import Image
import io
import yaml


# Kami 文学版设计语言
# 羊皮纸 + 墨蓝 + serif + 全暖灰 + 零装饰 + 双光照色契约
CHAPTER_CSS = """
/* ===== Kami Literary Design System =====
 * 羊皮纸 + 墨蓝 + serif + 全暖灰 + 零装饰
 * 双光照色契约：浅色 / 暗色    双模式：webnovel（默认）/ literary
 * Anti-patterns: 无 box-shadow, 无渐变, 无第二色相, 无合成粗体/斜体, 无左边栏
 */

/* --- 1. CSS Variables + 双光照色契约 --- */
:root {
    --paper:  #f5f4ed;
    --ivory:  #faf9f5;
    --ink:    #1B365D;
    --text:   #141413;
    --olive:  #504e49;
    --stone:  #6b6a64;
    --border: #e8e6dc;
}

@media (prefers-color-scheme: dark) {
    :root {
        --paper:  #1c1a17;
        --ivory:  #252320;
        --ink:    #6B95C9;
        --text:   #e8e4d8;
        --olive:  #b3aa9b;
        --stone:  #8a8378;
        --border: #3a3631;
    }
}

/* --- 2. Base --- */
html, body {
    background: var(--paper);
    color: var(--text);
    font-family: "Charter", "Iowan Old Style", "Source Han Serif SC",
                 "Noto Serif CJK SC", "Songti SC", "STSong", Georgia, serif;
    line-height: 1.65;
    margin: 1em;
    padding: 0;
    font-size: 1em;
    text-align: justify;
    widows: 2;
    orphans: 2;
    font-feature-settings: "kern" 1, "liga" 1, "onum" 1;
    text-rendering: optimizeLegibility;
    line-break: strict;
    word-break: keep-all;
    hanging-punctuation: allow-end last;
}

.kami-root.mode-literary {
    line-height: 1.55;
}

/* 无合成粗体 */
strong, b { font-weight: 500; color: var(--ink); }

/* 中文着重号，英文真斜体 */
em, i {
    font-style: normal; font-weight: inherit; color: inherit;
    -webkit-text-emphasis: dot;
    -webkit-text-emphasis-position: under right;
    text-emphasis: dot;
    text-emphasis-position: under right;
}
html[lang^="en"] em, html[lang^="en"] i {
    font-style: italic; -webkit-text-emphasis: none; text-emphasis: none;
}
/* 旧阅读器降级 */
@supports not (text-emphasis: dot) {
    em, i { color: var(--ink); font-weight: 500; }
}

/* --- 3. Paragraphs --- */
p { margin: 0; text-indent: 2em; text-align: justify; }

/* 章首/引用后/场景分隔后第一段不缩进 */
.chapter-ornament + p, blockquote + p, .scene-break + p,
h1 + p, h2 + p, h3 + p, h4 + p { text-indent: 0; }

/* --- 4. Chapter Title System --- */
.chapter-header { text-align: center; margin: 25vh 0 0 0; padding: 0; }
.chapter-num { font-size: 0.7em; color: var(--stone); font-weight: 500; }
.chapter-num.num-short { letter-spacing: 0.25em; }
.chapter-num.num-long  { letter-spacing: 0.1em; }
.chapter-title {
    font-weight: 500; color: var(--text); margin: 0;
    text-wrap: balance; word-wrap: break-word; overflow-wrap: break-word;
}
.chapter-num-above .chapter-num { display: block; margin-bottom: 0.3em; }
.chapter-num-inline .chapter-title .chapter-num { display: inline; }
.chapter-num-inline .title-sep { color: var(--stone); margin: 0 0.15em; }

/* webnovel 字号档 */
.kami-root.mode-webnovel .chapter-title.title-l  { font-size: 1.6em; letter-spacing: 0.1em;  line-height: 1.20; }
.kami-root.mode-webnovel .chapter-title.title-m  { font-size: 1.4em; letter-spacing: 0.05em; line-height: 1.25; }
.kami-root.mode-webnovel .chapter-title.title-s  { font-size: 1.2em; letter-spacing: 0;      line-height: 1.35; }
.kami-root.mode-webnovel .chapter-title.title-xs { font-size: 1.1em; letter-spacing: 0;      line-height: 1.45; }

/* literary 字号档 */
.kami-root.mode-literary .chapter-title.title-l  { font-size: 2.4em;  letter-spacing: 0.4em;  line-height: 1.15; }
.kami-root.mode-literary .chapter-title.title-m  { font-size: 1.8em;  letter-spacing: 0.2em;  line-height: 1.20; }
.kami-root.mode-literary .chapter-title.title-s  { font-size: 1.4em;  letter-spacing: 0.05em; line-height: 1.30; }
.kami-root.mode-literary .chapter-title.title-xs { font-size: 1.15em; letter-spacing: 0;      line-height: 1.40; }

/* --- 5. Chapter Ornament --- */
.chapter-ornament { text-align: center; color: var(--ink); margin: 1.5em 0; line-height: 1; }

/* --- 6. Scene Break: <hr> → ❦ --- */
hr { border: none; margin: 2em 0; text-align: center; }
hr::after { content: "\\2766"; color: var(--ink); font-size: 1em; display: block; text-align: center; }
.scene-break { text-align: center; color: var(--ink); margin: 2em 0; line-height: 1; }

/* --- 7. Blockquote --- */
blockquote { margin: 1em 2em; padding: 0; color: var(--olive); line-height: inherit; }

/* --- 8. 普通标题（无左边栏）--- */
h1, h2, h3, h4 { font-weight: 500; color: var(--text); margin: 1.5em 0 0.5em 0; }
h1 { font-size: 1.6em; line-height: 1.20; }
h2 { font-size: 1.3em; line-height: 1.25; }
h3 { font-size: 1.1em; line-height: 1.30; color: var(--olive); }
h4 { font-size: 1em;   line-height: 1.35; color: var(--stone); }

/* --- 9. Code --- */
pre {
    background: var(--ivory); border: 0.5pt solid var(--border);
    border-left: 2pt solid var(--ink); border-radius: 4pt;
    padding: 0.9em 1em; overflow-x: auto; margin: 1em 0;
    font-family: "JetBrains Mono", "SF Mono", "Monaco", "Consolas",
                 "Source Han Serif SC", "Noto Serif CJK SC", monospace;
    font-size: 0.85em; line-height: 1.45; tab-size: 2; color: var(--text);
}
code {
    font-family: "JetBrains Mono", "SF Mono", "Monaco", "Consolas",
                 "Source Han Serif SC", "Noto Serif CJK SC", monospace;
    font-size: 0.9em; background: var(--ivory);
    padding: 0.15em 0.4em; border-radius: 3pt; color: var(--ink);
}
pre code { background: none; padding: 0; color: inherit; }

/* --- 10. Tables --- */
table { border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 0.92em; line-height: 1.5; }
th { text-align: left; font-weight: 500; color: var(--text); padding: 0.5em 0.6em; border-bottom: 1pt solid var(--border); background: transparent; }
td { padding: 0.4em 0.6em; border-bottom: 0.3pt solid var(--border); vertical-align: top; }

/* --- 11. Lists --- */
ul, ol { margin: 0.5em 0 1em 1.5em; padding: 0; }
li { margin: 0.3em 0; }

/* --- 12. Images --- */
img { max-width: 100%; height: auto; display: block; margin: 1em auto; }
.card-img { text-align: center; margin: 1em 0; }

/* --- 13. Metadata & Utility --- */
.metadata { color: var(--stone); font-size: 0.85em; margin-bottom: 1em; font-style: normal; }
.author-note { color: var(--stone); font-size: 0.85em; margin-top: 1.5em; text-indent: 0; }
.unfinished { text-align: center; color: var(--stone); font-size: 0.75em; margin-top: 1em; text-indent: 0; }

/* --- 14. Pygments fix --- */
.codehilite span[style*="border: 1px solid #FF0000"] { border: none !important; }

/* --- 15. TOC Page --- */
.toc-volume { text-align: center; font-weight: 500; color: var(--ink); margin: 1.5em 0 0.5em 0; font-size: 0.9em; letter-spacing: 0.2em; }
.toc-chapter { text-align: center; margin: 0.3em 0; }
.toc-chapter a { color: var(--text); text-decoration: none; font-size: 0.9em; }
.toc-chapter a:hover { color: var(--ink); }
.toc-special-area { margin-top: 1.5em; margin-bottom: 0.3em; text-align: center; font-size: 0.85em; color: var(--stone); }
.toc-special-area a { color: var(--stone); }
"""


# --- 章节标题解析：从 "第一章 灯塔" 提取章号与章名 ---
CHAPTER_PATTERNS = [
    re.compile(r'^(第[一二三四五六七八九十百千万零\d]+[章节篇回])[·\s　]*'),
    re.compile(r'^(第\d+[章节篇回])[·\s]*'),
    re.compile(r'^(Chapter|CHAPTER)\s+\d+[·:\s]*'),
]

def parse_chapter_heading(heading):
    """从 '# 第一章 灯塔' 提取 ('第一章', '灯塔')。
    返回 (chapter_num, chapter_name)，无法识别时 ('', heading)。"""
    heading = heading.strip()
    for pat in CHAPTER_PATTERNS:
        m = pat.match(heading)
        if m:
            num = m.group(1).strip()
            name = heading[m.end():].strip()
            return (num, name)
    return ("", heading)

def chapter_title_class(chapter_num, chapter_name):
    """根据章号+章名总字符数返回字号 class: title-l/m/s/xs"""
    total = len(chapter_num) + len(chapter_name)
    if total <= 8:   return "title-l"
    if total <= 15:  return "title-m"
    if total <= 25:  return "title-s"
    return "title-xs"

def chapter_num_class(chapter_num):
    """章号字距档：4 字以内短（如"第一章"），超过（如"第五百二十五章"）收紧"""
    return "num-long" if len(chapter_num) > 4 else "num-short"

def auto_num_position(chapter_num, chapter_name, mode):
    """webnovel 模式下长章名自动 inline，literary 模式 always above"""
    if mode == "literary":
        return "above"
    if mode == "webnovel" and len(chapter_num) + len(chapter_name) > 15:
        return "inline"
    return "above"

def parse_frontmatter(content):
    """解析 YAML frontmatter，返回 (frontmatter_dict, remaining_content)。"""
    fm = {}
    rest = content
    if content.startswith('---\n'):
        parts = content.split('---\n', 2)
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1]) or {}
                rest = parts[2]
            except Exception:
                pass
    return fm, rest


def compress_image(img_data_or_path, target_width=1000, jpeg_quality=88):
    """Compress image to JPEG with configurable quality."""
    try:
        if isinstance(img_data_or_path, bytes):
            img = Image.open(io.BytesIO(img_data_or_path))
        else:
            img = Image.open(img_data_or_path)

        if img.mode == 'RGBA':
            bg = Image.new('RGB', img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            img = bg
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        if img.width > target_width:
            ratio = target_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((target_width, new_height), Image.Resampling.LANCZOS)

        output = io.BytesIO()
        img.save(output, format='JPEG', quality=jpeg_quality, optimize=True)
        return output.getvalue()
    except Exception as e:
        print(f"  Warning: Image compression failed: {e}")
        return None


def convert_svg_to_png(svg_data, width=1000):
    """Convert SVG data to PNG using Playwright headless browser."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  Warning: Playwright not installed, cannot convert SVG")
        return None

    try:
        import tempfile
        # Write SVG to temp file
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False, mode='wb') as f:
            f.write(svg_data)
            svg_path = f.name

        png_path = svg_path.replace('.svg', '.png')

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": width, "height": 800})
            page.goto(f"file://{svg_path}")
            page.wait_for_timeout(1000)

            # Get the SVG element dimensions
            dimensions = page.evaluate("""() => {
                const svg = document.querySelector('svg');
                if (!svg) return null;
                const rect = svg.getBoundingClientRect();
                return { width: rect.width, height: rect.height };
            }""")

            if dimensions:
                # Resize viewport to fit SVG
                page.set_viewport_size({
                    "width": max(int(dimensions['width']), 200),
                    "height": max(int(dimensions['height']), 100)
                })
                page.wait_for_timeout(300)

            page.screenshot(path=png_path, full_page=True)
            browser.close()

        with open(png_path, 'rb') as f:
            png_data = f.read()

        # Clean up temp files
        os.unlink(svg_path)
        os.unlink(png_path)

        return png_data
    except Exception as e:
        print(f"  Warning: SVG conversion failed: {e}")
        return None


# Shared Playwright browser instance for batch SVG conversion
_svg_browser = None
_svg_playwright = None


def _get_svg_browser():
    """Get or create a shared Playwright browser for SVG conversion."""
    global _svg_browser, _svg_playwright
    if _svg_browser is None:
        try:
            from playwright.sync_api import sync_playwright
            _svg_playwright = sync_playwright().start()
            _svg_browser = _svg_playwright.chromium.launch(headless=True)
        except Exception as e:
            print(f"  Warning: Cannot start Playwright for SVG: {e}")
            return None
    return _svg_browser


def _close_svg_browser():
    """Close shared Playwright browser."""
    global _svg_browser, _svg_playwright
    if _svg_browser:
        _svg_browser.close()
        _svg_browser = None
    if _svg_playwright:
        _svg_playwright.stop()
        _svg_playwright = None


def convert_svg_to_png_fast(svg_data, width=1000):
    """Convert SVG to PNG reusing a shared browser instance (faster for batch)."""
    browser = _get_svg_browser()
    if not browser:
        return None

    try:
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False, mode='wb') as f:
            f.write(svg_data)
            svg_path = f.name

        png_path = svg_path.replace('.svg', '.png')
        page = browser.new_page(viewport={"width": width, "height": 800})

        try:
            page.goto(f"file://{svg_path}")
            page.wait_for_timeout(800)

            dimensions = page.evaluate("""() => {
                const svg = document.querySelector('svg');
                if (!svg) return null;
                const rect = svg.getBoundingClientRect();
                return { width: rect.width, height: rect.height };
            }""")

            if dimensions:
                page.set_viewport_size({
                    "width": max(int(dimensions['width']), 200),
                    "height": max(int(dimensions['height']), 100)
                })
                page.wait_for_timeout(300)

            page.screenshot(path=png_path, full_page=True)
        finally:
            page.close()

        with open(png_path, 'rb') as f:
            png_data = f.read()

        os.unlink(svg_path)
        os.unlink(png_path)
        return png_data
    except Exception as e:
        print(f"  Warning: SVG conversion failed: {e}")
        return None


def download_image(url, timeout=15):
    """Download image from URL or read from local file, converting SVG to PNG via Playwright."""
    try:
        # Skip blob:, data: URLs
        if url.startswith('blob:') or url.startswith('data:'):
            return None

        url_path = url.split('?')[0].lower()
        is_svg = url_path.endswith('.svg')

        # 处理本地文件路径：所有非 HTTP/HTTPS URL 都视作本地路径
        # 修复：原条件仅匹配 /、./、../ 前缀，遗漏了形如 020_images/020_01.jpg 的相对路径
        if not url.startswith(('http://', 'https://')):
            if not os.path.exists(url):
                print(f"  Warning: Local file not found: {url}")
                return None
            with open(url, 'rb') as f:
                data = f.read()
            content_type = 'image/png' if url.lower().endswith('.png') else 'image/jpeg'
        else:
            # Handle remote URLs
            # Strip CDN webp conversion params to get original format
            # e.g. alipayobjects ?x-oss-process=image/auto-orient,1/resize,w_2000/format,webp
            clean_url = url
            if not is_svg and ('format,webp' in url or 'format/webp' in url):
                # Try to get original format by removing format conversion
                clean_url = re.sub(r'/format,webp', '', url)
                clean_url = re.sub(r'/format/webp', '', clean_url)
                # Also cap resize to reasonable width
                clean_url = re.sub(r'/resize,w_\d+', '/resize,w_1200', clean_url)

            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'image/png, image/jpeg, image/webp, image/svg+xml, image/*'
            }
            req = urllib.request.Request(clean_url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                content_type = response.headers.get('Content-Type', '')
                data = response.read()

        # Detect SVG content (by URL extension, content-type, or data signature)
        is_svg_content = (
            is_svg
            or 'svg' in content_type
            or data[:5] == b'<?xml'
            or data[:4] == b'<svg'
            or (data[:200].find(b'<svg') >= 0)
        )

        if is_svg_content:
            print(f"    Converting SVG: {url_path.split('/')[-1]}")
            png_data = convert_svg_to_png_fast(data)
            if png_data:
                return png_data
            else:
                print(f"  Warning: SVG conversion failed for: {url_path.split('/')[-1]}")
                return None

        # Skip HTML error pages
        if content_type.startswith('text/html') or data[:15].lstrip().startswith(b'<!DOCTYPE'):
            print(f"  Skipping HTML error page from: {url[:60]}...")
            return None

        # Validate the data is a real image PIL can open
        try:
            img_test = Image.open(io.BytesIO(data))
            img_test.load()  # force decode; verify() consumes pointer and is less reliable
        except Exception:
            # Fallback: try stripping all query params
            base_url = url.split('?')[0]
            if base_url != url:
                req2 = urllib.request.Request(base_url, headers=headers)
                try:
                    with urllib.request.urlopen(req2, timeout=timeout) as response2:
                        data = response2.read()
                    # Validate fallback data too
                    img_test2 = Image.open(io.BytesIO(data))
                    img_test2.load()
                except Exception:
                    print(f"  Warning: Not a valid raster image: {url[:60]}...")
                    return None
            else:
                print(f"  Warning: Not a valid raster image: {url[:60]}...")
                return None

        return data
    except Exception as e:
        print(f"  Warning: Failed to download {url[:80]}...: {e}")
        return None


def extract_and_download_images(markdown_text, book, image_width=1000, jpeg_quality=88, base_dir=None):
    """
    从 Markdown 中提取图片 URL，下载后加入 EPUB，并替换原 URL。
    返回：(modified_markdown, image_count, total_size)

    base_dir：源 Markdown 文件所在目录。提供后，对没有 URL scheme（如
    ``521_images/521_01.png``）的图片引用会基于该目录解析为本地路径，
    避免把这种裸相对路径误当作远程 URL。
    """
    # Find all image references: ![alt](url)
    img_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    matches = list(re.finditer(img_pattern, markdown_text))

    if not matches:
        return markdown_text, 0, 0

    downloaded_images = {}
    total_size = 0

    for match in matches:
        alt_text = match.group(1)
        img_url = match.group(2)

        # Skip if already processed
        if img_url in downloaded_images:
            continue

        # 裸相对路径（无 URL scheme、且不以 / ./ ../ 开头）基于 base_dir 解析为绝对路径，
        # 否则后续 download_image 中的 os.path.exists 判断会受 cwd 影响而找不到文件。
        download_url = img_url
        if (
            base_dir
            and not re.match(r'^[a-zA-Z][a-zA-Z0-9+\-.]*:', img_url)
            and not img_url.startswith(('/', './', '../'))
        ):
            candidate = os.path.join(base_dir, img_url)
            if os.path.exists(candidate):
                download_url = candidate

        # Download image
        img_data = download_image(download_url)
        if not img_data:
            continue

        # Compress image
        compressed_data = compress_image(img_data, image_width, jpeg_quality)
        if not compressed_data:
            continue

        # Generate unique filename
        url_hash = hashlib.md5(img_url.encode()).hexdigest()[:8]
        img_filename = f"images/img_{url_hash}.jpg"

        # Add to EPUB
        img_item = epub.EpubItem(
            uid=f"img_{url_hash}",
            file_name=img_filename,
            media_type="image/jpeg",
            content=compressed_data
        )
        book.add_item(img_item)

        downloaded_images[img_url] = img_filename
        total_size += len(compressed_data)

    # Replace URLs in Markdown
    def replace_url(match):
        alt_text = match.group(1)
        img_url = match.group(2)
        if img_url in downloaded_images:
            return f'![{alt_text}]({downloaded_images[img_url]})'
        return match.group(0)

    modified_markdown = re.sub(img_pattern, replace_url, markdown_text)

    return modified_markdown, len(downloaded_images), total_size


def parse_article(md_path):
    """Parse Markdown article, extract title, metadata, and frontmatter fields.
    Returns: (title, metadata, body, frontmatter_dict)"""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    frontmatter, content = parse_frontmatter(content)

    lines = content.strip().split('\n')

    title = frontmatter.get('title', "Untitled")
    metadata = ""
    body_start = 0

    # Clean jina.ai metadata headers
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if line.startswith('Title:') and title == "Untitled":
            title = line.split(':', 1)[1].strip()
            i += 1
            continue

        if line.startswith('URL Source:') or line.startswith('Published Time:'):
            i += 1
            continue

        if line.startswith('Markdown Content:'):
            body_start = i + 1
            break

        if line.startswith('# ') and title == "Untitled":
            title = line[2:].strip()
            body_start = i + 1
            if i + 1 < len(lines) and lines[i + 1].startswith('> '):
                metadata = lines[i + 1][2:].strip()
                body_start = i + 2
            break

        if not line:
            i += 1
            continue

        if i < 5:
            i += 1
            continue

        body_start = i
        break

    body = '\n'.join(lines[body_start:]).strip()
    return title, metadata, body, frontmatter


def split_markdown_by_headers(content):
    """
    Split a single Markdown file into chapters based on ## headers.
    Returns: [(title, content), ...]
    """
    lines = content.split('\n')
    chapters = []
    current_title = None
    current_content = []

    for line in lines:
        # Match ## headers (second level)
        if line.startswith('## '):
            # Save previous chapter
            if current_title:
                chapters.append((current_title, '\n'.join(current_content).strip()))
            # Start new chapter
            current_title = line[3:].strip()
            current_content = [line]  # Include the header in content
        else:
            if current_title:
                current_content.append(line)
            # Skip content before first ## header

    # Save last chapter
    if current_title:
        chapters.append((current_title, '\n'.join(current_content).strip()))

    return chapters


def build_xhtml(title, metadata, image_html, body_html):
    """Build valid XHTML document with inline CSS."""
    escaped_title = html_module.escape(title)

    meta_section = ""
    if metadata:
        meta_section = f'<p class="metadata">{html_module.escape(metadata)}</p>'

    img_section = ""
    if image_html:
        img_section = f'<div class="card-img">{image_html}</div>'

    return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>{escaped_title}</title>
<link rel="stylesheet" type="text/css" href="style.css" />
</head>
<body>
<h1>{escaped_title}</h1>
{meta_section}
{img_section}
{body_html}
</body>
</html>"""


def fix_xhtml(html_str):
    """Fix common HTML issues for XHTML compatibility."""
    # Fix self-closing tags
    html_str = re.sub(r'<br\s*>', '<br/>', html_str)
    html_str = re.sub(r'<hr\s*>', '<hr/>', html_str)
    html_str = re.sub(r'<img([^/]*?)>', r'<img\1/>', html_str)

    # Remove Pygments error token red borders
    # Pygments marks unknown tokens with border: 1px solid #FF0000
    html_str = re.sub(r'border:\s*1px\s+solid\s+#FF0000;?\s*', '', html_str)

    # Fix remaining & symbols outside code blocks
    # Note: Pygments (codehilite) already escapes content inside <code> blocks,
    # so we only need to fix unescaped & in regular text
    html_str = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9a-fA-F]+;)', '&amp;', html_str)

    return html_str


def normalize_scene_breaks(html):
    """将正文中的场景分隔符（---, ***, <hr>, 连续 <br/>）归一为 ❦。"""
    html = re.sub(r'<hr\s*/>', '<div class="scene-break">&#10086;</div>', html)
    html = re.sub(r'(<br/>\s*){3,}', '<div class="scene-break">&#10086;</div>', html)
    return html


def detect_unfinished(text):
    """检测正文末尾是否有（未完待续）标记，返回 (cleaned_text, has_unfinished)。"""
    m = re.search(r'[（(]未完待续[）)]\s*$', text.strip())
    if m:
        return text[:m.start()].strip(), True
    return text, False


def normalize_punctuation(text):
    """归一化中文标点。在 Markdown 转换前的纯文本上操作。
    可通过 --no-punct-fix 关闭。

    规则：
    1. ... -> ……（英文省略号转中文）
    2. -- -> ——（双连字符转破折号，不要动减号）
    3. 全角字母数字 -> 半角（Ａ->A，１->1）
    4. 中英文之间插空格（"读完Chapter 5" -> "读完 Chapter 5"）
    5. 中文与数字之间不插空格（"12月"不动）
    6. 连续全角/半角空格 -> 一个空格
    7. 行首/行尾空白 trim
    8. 不处理代码块内的内容（不好检测，接受误伤）
    """
    # 1. 英文省略号 -> 中文省略号
    text = re.sub(r'\.{3,}', '……', text)
    text = re.sub(r'\.\s*\.\s*\.', '……', text)

    # 2. 双连字符 -> 破折号（至少两个连续）
    text = re.sub(r'-{2,}', '——', text)

    # 3. 全角字母数字 -> 半角（U+FF01~FF5E -> U+0021~007E，U+3000 -> U+0020）
    result = []
    for ch in text:
        code = ord(ch)
        if 0xFF01 <= code <= 0xFF5E:
            result.append(chr(code - 0xFEE0))
        elif code == 0x3000:  # 全角空格 -> 半角空格
            result.append(' ')
        else:
            result.append(ch)
    text = ''.join(result)

    # 4. 中英文之间插空格
    text = re.sub(r'([一-鿿])([a-zA-Z])', r'\1 \2', text)
    text = re.sub(r'([a-zA-Z])([一-鿿])', r'\1 \2', text)

    # 5. 中文与数字之间不插空格（由第4步保证，\d 不在 [a-zA-Z] 范围内）

    # 6. 连续空白 -> 一个空格
    text = re.sub(r'[ \t]+', ' ', text)

    # 7. 行首行尾 trim
    text = '\n'.join(line.strip() for line in text.split('\n'))

    return text


def style_author_notes(html):
    """将章末引用块中的 PS: / 作者按 / 作者注 样式化为 author-note。"""
    html = re.sub(
        r'<blockquote>\s*<p>(PS[:：]|作者按|作者注)',
        r'<blockquote class="author-note"><p>\1',
        html
    )
    return html


def build_chapter_xhtml(chapter_info, body_html, mode="webnovel"):
    """Build XHTML with Kami literary chapter structure.
    chapter_info: dict with keys: title, chapter_num, chapter_name, kind,
                  title_class, num_class, num_position"""
    escaped_title = html_module.escape(chapter_info["title"])

    # Build chapter header based on kind and num_position
    kind = chapter_info.get("kind", "正文")
    if kind in ("楔子", "序章", "引子", "番外"):
        # No chapter number display
        header = (
            f'<div class="chapter-header">'
            f'<h1 class="chapter-title {chapter_info["title_class"]}">{escaped_title}</h1>'
            f'</div>\n'
            f'<div class="chapter-ornament">❦</div>'
        )
    elif chapter_info["num_position"] == "inline":
        # Chapter number inline with title (webnovel long titles)
        header = (
            f'<div class="chapter-header chapter-num-inline">'
            f'<h1 class="chapter-title {chapter_info["title_class"]}">'
            f'<span class="chapter-num {chapter_info["num_class"]}">{html_module.escape(chapter_info["chapter_num"])}</span>'
            f'<span class="title-sep"> · </span>'
            f'{html_module.escape(chapter_info["chapter_name"])}'
            f'</h1>'
            f'</div>\n'
            f'<div class="chapter-ornament">❦</div>'
        )
    else:
        # Chapter number above title
        header = (
            f'<div class="chapter-header chapter-num-above">'
            f'<div class="chapter-num {chapter_info["num_class"]}">{html_module.escape(chapter_info["chapter_num"])}</div>'
            f'<h1 class="chapter-title {chapter_info["title_class"]}">{html_module.escape(chapter_info["chapter_name"])}</h1>'
            f'</div>\n'
            f'<div class="chapter-ornament">❦</div>'
        )

    body_class = f"mode-{mode}"
    return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>{escaped_title}</title>
<link rel="stylesheet" type="text/css" href="style.css" />
</head>
<body>
<div class="kami-root {body_class}">
{header}
{body_html}
<div class="chapter-ornament chapter-end">&#10086;</div>
</div>
</body>
</html>"""


def generate_html_cover(title, subtitle="", author=""):
    """Generate cover image from HTML template using Playwright."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Warning: Playwright not installed, skipping HTML cover generation")
        return None

    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, script_dir)
    from gen_cover_html import generate_cover_html, screenshot_cover

    html_path = generate_cover_html(title, subtitle, author)
    cover_path = "/tmp/epub_cover.jpg"
    screenshot_cover(html_path, cover_path)

    with open(cover_path, 'rb') as f:
        return f.read()


def generate_svg_cover(title, subtitle="", author="", theme=None, layout="minimal"):
    """Generate cover image from SVG template using Playwright."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Warning: Playwright not installed, skipping SVG cover generation")
        return None

    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, script_dir)
    from gen_cover_svg import generate_svg_cover as gen_svg, convert_svg_to_image

    svg_path = gen_svg(title, subtitle, author, theme=theme, layout=layout)
    cover_path = "/tmp/epub_cover_svg.jpg"
    convert_svg_to_image(svg_path, cover_path)

    with open(cover_path, 'rb') as f:
        return f.read()


def build_volume_page(volume_name, volume_title="", mode="webnovel"):
    """生成卷封页 XHTML。"""
    body_class = f"mode-{mode}"
    title_html = (
        f'<div class="chapter-header" style="margin-top:35vh">'
        f'<h1 class="chapter-title title-l" style="font-size:1.4em;letter-spacing:0.4em">{html_module.escape(volume_name)}</h1>'
        f'</div>'
    )
    if volume_title:
        title_html += f'\n<p style="text-align:center;color:var(--olive);font-size:0.85em;margin-top:1em">{html_module.escape(volume_title)}</p>'
    title_html += '\n<div class="chapter-ornament">&#10086;</div>'
    return f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh">
<head><title>{html_module.escape(volume_name)}</title><link rel="stylesheet" type="text/css" href="style.css" /></head>
<body><div class="kami-root {body_class}">{title_html}</div></body>
</html>'''


def build_toc_page(toc_entries, mode="webnovel"):
    """生成 Kami 风格的 TOC 目录页。
    toc_entries: [(level, title, file_name, is_volume), ...]"""
    items_html = ""
    for level, title, fname, is_volume in toc_entries:
        if is_volume:
            items_html += f'<div class="toc-volume">{html_module.escape(title)}</div>\n'
        else:
            items_html += f'<div class="toc-chapter"><a href="{fname}">{html_module.escape(title)}</a></div>\n'

    body_class = f"mode-{mode}"
    return f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh">
<head><title>目录</title><link rel="stylesheet" type="text/css" href="style.css" /></head>
<body><div class="kami-root {body_class}">
<h1 style="text-align:center;font-size:1.2em;margin:2em 0 1.5em 0">目　录</h1>
<div class="toc-list">
{items_html}
</div>
</div></body></html>'''


def create_epub(args):
    """Generate EPUB with enhanced Markdown rendering and image downloading."""
    input_dir = os.path.expanduser(args.input_dir)
    output_path = os.path.expanduser(args.output_file)

    md_files = sorted(glob.glob(os.path.join(input_dir, "*.md")))
    if not md_files:
        print(f"Error: No .md files found in {input_dir}")
        sys.exit(1)

    print(f"Generating Enhanced EPUB...")
    print(f"  Input: {input_dir} ({len(md_files)} articles)")
    print(f"  Output: {output_path}")

    # Extract title from first article if not provided
    title = args.title
    mode = args.mode
    # 如果指定了显式章号位置，覆盖 auto_num_position 的结果
    explicit_num_pos = getattr(args, 'chapter_num_position', None)
    if not title:
        first_title, _, _, _ = parse_article(md_files[0])
        title = first_title

    book = epub.EpubBook()
    book.set_identifier(f'epub-{title.replace(" ", "-").lower()[:30]}')
    book.set_title(title)
    book.set_language(args.language)

    # 注册 Kami 设计语言 CSS 为独立 style.css 资源（ebooklib 会丢弃内联 <style>）
    css_item = epub.EpubItem(
        uid="style_css",
        file_name="style.css",
        media_type="text/css",
        content=CHAPTER_CSS,
    )
    book.add_item(css_item)

    if args.author:
        for a in args.author.split('/'):
            book.add_author(a.strip())

    book.add_metadata('DC', 'description', f'{len(md_files)} articles')

    # Handle cover
    cover_data = None
    if args.cover:
        cover_path = os.path.expanduser(args.cover)
        if os.path.exists(cover_path):
            cover_data = compress_image(cover_path, target_width=1400, jpeg_quality=95)
            print(f"  Cover: {cover_path}")
    elif args.cover_svg:
        subtitle = args.subtitle or f"{len(md_files)} articles"
        theme = args.cover_theme if hasattr(args, 'cover_theme') else None
        layout = args.cover_layout if hasattr(args, 'cover_layout') else "minimal"
        cover_data = generate_svg_cover(title, subtitle, args.author or "", theme, layout)
        print(f"  Cover: SVG generated")
    elif args.cover_html:
        subtitle = args.subtitle or f"{len(md_files)} articles"
        cover_data = generate_html_cover(title, subtitle, args.author or "")
        print(f"  Cover: HTML generated")

    if cover_data:
        book.set_cover("cover.jpg", cover_data)

    # Process articles
    total_img_size = 0
    total_img_count = 0
    chapter_records = []

    # Check if we should split by headers (single file with ## headers)
    should_split = len(md_files) == 1
    if should_split:
        with open(md_files[0], 'r', encoding='utf-8') as f:
            full_content = f.read()

        # Extract book title from # header
        title_text, metadata, body, frontmatter = parse_article(md_files[0])

        # Split by ## headers
        chapter_list = split_markdown_by_headers(body)

        if len(chapter_list) > 1:
            print(f"  Splitting into {len(chapter_list)} chapters by ## headers")
        else:
            # Fallback to single chapter
            chapter_list = [(title_text, body)]
            should_split = False
    else:
        chapter_list = None

    chapter_num = 0
    for i, md_path in enumerate(md_files, 1):
        slug = Path(md_path).stem
        md_dir = os.path.dirname(os.path.abspath(md_path))

        if should_split and chapter_list:
            # Process split chapters from single file
            for ch_title, ch_body in chapter_list:
                chapter_num += 1
                print(f"  [{chapter_num}/{len(chapter_list)}] {ch_title}")

                # --- P0: 未完待续标记检测 ---
                ch_body_clean, has_unfinished = detect_unfinished(ch_body)

                # --- P1: 标点归一（--no-punct-fix 可关闭）---
                if not getattr(args, 'no_punct_fix', False):
                    ch_body_clean = normalize_punctuation(ch_body_clean)

                # Download and embed images from Markdown
                ch_body_processed, img_count, img_size = extract_and_download_images(
                    ch_body_clean, book, args.image_width, args.image_quality, base_dir=md_dir
                )
                total_img_count += img_count
                total_img_size += img_size

                if img_count > 0:
                    print(f"    → Downloaded {img_count} images ({img_size / 1024:.1f} KB)")

                # Markdown → HTML with full extensions
                md_html = markdown.markdown(
                    ch_body_processed,
                    extensions=[
                        'extra',          # Tables, fenced code blocks, etc.
                        'codehilite',     # Syntax highlighting
                        'nl2br',          # Newline to <br>
                        'sane_lists'      # Better list handling
                    ],
                    extension_configs={
                        'codehilite': {
                            'noclasses': True,
                            'pygments_style': 'default'
                        }
                    }
                )
                md_html = fix_xhtml(md_html)

                # --- P0: 场景分隔符归一 + 作者按样式 + 未完待续追加 ---
                md_html = normalize_scene_breaks(md_html)
                md_html = style_author_notes(md_html)
                if has_unfinished:
                    md_html += '\n<div class="unfinished">（未完待续）</div>'

                # 从标题提取章号/章名
                chapter_num_text, chapter_name = parse_chapter_heading(ch_title)
                if not chapter_num_text:
                    chapter_num_text, chapter_name = "", ch_title

                chapter_info = {
                    "title": ch_title,
                    "chapter_num": chapter_num_text,
                    "chapter_name": chapter_name,
                    "volume": None,
                    "kind": "正文",
                    "title_class": chapter_title_class(chapter_num_text, chapter_name),
                    "num_class": chapter_num_class(chapter_num_text),
                    "num_position": auto_num_position(chapter_num_text, chapter_name, mode),
                }
                if explicit_num_pos:
                    chapter_info["num_position"] = explicit_num_pos

                chapter_html = build_chapter_xhtml(chapter_info, md_html, mode=mode)

                chapter = epub.EpubHtml(
                    title=ch_title,
                    file_name=f"chapter_{chapter_num:03d}.xhtml",
                    lang=args.language
                )
                chapter.set_content(chapter_html.encode('utf-8'))
                chapter.add_item(css_item)

                book.add_item(chapter)
                chapter_records.append({
                    "ch_info": chapter_info,
                    "epub_html": chapter,
                    "file_name": f"chapter_{chapter_num:03d}.xhtml",
                })
        else:
            # Process multiple files normally
            chapter_num += 1
            print(f"  [{chapter_num}/{len(md_files)}] {slug}")

            title_text, metadata, body, frontmatter = parse_article(md_path)

            # --- P0: 未完待续标记检测 ---
            body_clean, has_unfinished = detect_unfinished(body)

            # --- P1: 标点归一（--no-punct-fix 可关闭）---
            if not getattr(args, 'no_punct_fix', False):
                body_clean = normalize_punctuation(body_clean)

            # Download and embed images from Markdown
            body_processed, img_count, img_size = extract_and_download_images(
                body_clean, book, args.image_width, args.image_quality, base_dir=md_dir
            )
            total_img_count += img_count
            total_img_size += img_size

            if img_count > 0:
                print(f"    → Downloaded {img_count} images ({img_size / 1024:.1f} KB)")

            # Markdown → HTML with full extensions
            md_html = markdown.markdown(
                body_processed,
                extensions=[
                    'extra',          # Tables, fenced code blocks, etc.
                    'codehilite',     # Syntax highlighting
                    'nl2br',          # Newline to <br>
                    'sane_lists'      # Better list handling
                ],
                extension_configs={
                    'codehilite': {
                        'noclasses': True,
                        'pygments_style': 'default'
                    }
                }
            )
            md_html = fix_xhtml(md_html)

            # --- P0: 场景分隔符归一 + 作者按样式 + 未完待续追加 ---
            md_html = normalize_scene_breaks(md_html)
            md_html = style_author_notes(md_html)
            if has_unfinished:
                md_html += '\n<div class="unfinished">（未完待续）</div>'

            chapter_num_text, chapter_name = parse_chapter_heading(title_text)
            if not chapter_num_text:
                chapter_num_text, chapter_name = "", title_text

            kind = frontmatter.get("kind", "正文") if frontmatter else "正文"
            volume = frontmatter.get("volume") if frontmatter else None
            chapter_info = {
                "title": title_text,
                "chapter_num": chapter_num_text,
                "chapter_name": chapter_name,
                "volume": volume,
                "kind": kind,
                "title_class": chapter_title_class(chapter_num_text, chapter_name),
                "num_class": chapter_num_class(chapter_num_text),
                "num_position": auto_num_position(chapter_num_text, chapter_name, mode),
            }
            if explicit_num_pos:
                chapter_info["num_position"] = explicit_num_pos

            chapter_html = build_chapter_xhtml(chapter_info, md_html, mode=mode)

            chapter = epub.EpubHtml(
                title=title_text,
                file_name=f"chapter_{chapter_num:03d}.xhtml",
                lang=args.language
            )
            chapter.set_content(chapter_html.encode('utf-8'))
            chapter.add_item(css_item)

            book.add_item(chapter)
            chapter_records.append({
                "ch_info": chapter_info,
                "epub_html": chapter,
                "file_name": f"chapter_{chapter_num:03d}.xhtml",
            })

    # --- Phase 2: Build structure (volume grouping, NCX, TOC page) ---
    has_volumes = any(r["ch_info"].get("volume") for r in chapter_records)

    if not has_volumes:
        # 无卷：保持现有扁平行为
        spine = ['nav']
        toc_items = []
        for r in chapter_records:
            fn = r["file_name"]
            ci = r["ch_info"]
            toc_items.append(epub.Link(fn, ci["title"], fn))
            spine.append(r["epub_html"])
        book.toc = toc_items
        book.spine = spine
    else:
        # 有卷：分组构建嵌套 TOC 和卷封页
        preamble = []      # 楔子/序章/引子
        named_volumes = {} # volume_name -> [entries]
        none_vol = []      # 正文无 volume
        extras = []        # 番外

        for r in chapter_records:
            ci = r["ch_info"]
            kind = ci.get("kind", "正文")
            vol = ci.get("volume")
            entry = (ci, r["epub_html"], r["file_name"])
            if kind in ("楔子", "序章", "引子"):
                preamble.append(entry)
            elif kind == "番外":
                extras.append(entry)
            elif vol:
                named_volumes.setdefault(vol, []).append(entry)
            else:
                none_vol.append(entry)

        # 保持 volume 首次出现顺序
        ordered_vols = []
        seen = set()
        for r in chapter_records:
            vol = r["ch_info"].get("volume")
            if vol and vol not in seen:
                seen.add(vol)
                ordered_vols.append(vol)

        # 构建嵌套 TOC 和 spine
        nested_toc = []
        spine = ['nav']
        toc_entries = []  # 用于 styled TOC 页
        vol_counter = 0

        # 前置区（楔子/序章/引子）
        if preamble:
            preamble_links = []
            for ci, chapter, fn in preamble:
                preamble_links.append(epub.Link(fn, ci["title"], fn))
                spine.append(chapter)
            toc_entries.append((0, "楔子／序章", "", True))
            for ci, chapter, fn in preamble:
                toc_entries.append((1, ci["title"], fn, False))
            nested_toc.append(
                (epub.Section("楔子／序章", preamble_links[0].href if preamble_links else ""),
                 preamble_links))

        # 命名卷
        for vol_name in ordered_vols:
            entries = named_volumes[vol_name]
            vol_counter += 1
            vp_file = f"volume_{vol_counter:03d}.xhtml"
            vp_html = build_volume_page(vol_name, mode=mode)
            vp_chapter = epub.EpubHtml(
                title=vol_name, file_name=vp_file, lang=args.language
            )
            vp_chapter.set_content(vp_html.encode('utf-8'))
            vp_chapter.add_item(css_item)
            book.add_item(vp_chapter)

            vol_links = [epub.Link(vp_file, vol_name, f"vp{vol_counter}")]
            spine.append(vp_chapter)
            toc_entries.append((0, vol_name, "", True))
            for ci, chapter, fn in entries:
                vol_links.append(epub.Link(fn, ci["title"], fn))
                spine.append(chapter)
                toc_entries.append((1, ci["title"], fn, False))
            nested_toc.append(
                (epub.Section(vol_name, vol_links[0].href if vol_links else ""),
                 vol_links))

        # 无卷正文章节
        if none_vol:
            none_links = []
            toc_entries.append((0, "正文", "", True))
            for ci, chapter, fn in none_vol:
                none_links.append(epub.Link(fn, ci["title"], fn))
                spine.append(chapter)
                toc_entries.append((1, ci["title"], fn, False))
            nested_toc.append(
                (epub.Section("正文", none_links[0].href if none_links else ""),
                 none_links))

        # 番外
        if extras:
            extras_links = []
            toc_entries.append((0, "番外", "", True))
            for ci, chapter, fn in extras:
                extras_links.append(epub.Link(fn, ci["title"], fn))
                spine.append(chapter)
                toc_entries.append((1, ci["title"], fn, False))
            nested_toc.append(
                (epub.Section("番外", extras_links[0].href if extras_links else ""),
                 extras_links))

        # 生成 styled TOC 页（在 nav 之后）
        toc_page_html = build_toc_page(toc_entries, mode=mode)
        toc_item = epub.EpubHtml(
            title="目录", file_name="toc.xhtml", lang=args.language
        )
        toc_item.set_content(toc_page_html.encode('utf-8'))
        toc_item.add_item(css_item)
        book.add_item(toc_item)
        spine.insert(1, toc_item)

        book.toc = nested_toc
        book.spine = spine

    book.add_item(epub.EpubNcx())

    # Write EPUB
    options = {
        'epub3_pages': False,
        'epub3_landmark': False,
        'spine_direction': True
    }

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    epub.write_epub(output_path, book, options)

    # Clean up shared Playwright browser for SVG conversion
    _close_svg_browser()

    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    img_size_mb = total_img_size / (1024 * 1024)
    print(f"\n✅ Done!")
    print(f"  Output: {output_path}")
    print(f"  File size: {size_mb:.1f} MB")
    print(f"  Downloaded images: {total_img_count} ({img_size_mb:.1f} MB)")
    print(f"  Chapters: {len(chapter_records)}")


def main():
    parser = argparse.ArgumentParser(description='Enhanced EPUB generator with image downloading')
    parser.add_argument('input_dir', help='Directory containing Markdown files')
    parser.add_argument('output_file', help='Output EPUB file path')
    parser.add_argument('--title', help='Book title')
    parser.add_argument('--author', help='Author name(s), separate multiple with /')
    parser.add_argument('--language', default='zh', help='Language code (default: zh)')
    parser.add_argument('--cover', help='Cover image path (JPG/PNG)')
    parser.add_argument('--cover-html', action='store_true', help='Generate cover from HTML template')
    parser.add_argument('--cover-svg', action='store_true', help='Generate cover from SVG template (KDP 1600x2560)')
    parser.add_argument('--cover-theme', help='Cover theme: tech, business, design, literature, science, personal')
    parser.add_argument('--cover-layout', default='minimal', help='SVG cover layout: minimal, classic, modern (default: minimal)')
    parser.add_argument('--subtitle', help='Subtitle for cover')
    parser.add_argument('--image-quality', type=int, default=88, help='JPEG quality 1-100 (default: 88)')
    parser.add_argument('--image-width', type=int, default=1000, help='Max image width px (default: 1000)')
    parser.add_argument('--mode', default='webnovel', choices=['webnovel', 'literary'],
                        help='排版模式: webnovel（默认，长章名自适应）, literary（短章名戏剧化）')
    parser.add_argument('--chapter-num-position', choices=['above', 'inline', 'hidden'], default=None,
                        help='章号位置: above（上方独立行）, inline（与章名同行）, hidden（隐藏）')
    parser.add_argument('--no-punct-fix', action='store_true',
                        help='关闭中文标点自动归一化')

    args = parser.parse_args()
    create_epub(args)


if __name__ == "__main__":
    main()
