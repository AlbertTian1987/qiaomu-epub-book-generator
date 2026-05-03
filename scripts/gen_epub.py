#!/usr/bin/env python3
"""
Generate EPUB ebook from Markdown files.
WeChat Reading compatible, with optional cover image and illustration compression.

Usage:
    python3 gen_epub.py <input_dir> <output.epub> [options]

Options:
    --title       Book title (default: extracted from first article)
    --author      Author name (default: extracted from Markdown frontmatter)
    --language    Language code (default: zh)
    --cover       Cover image path (JPG/PNG)
    --cover-html  Generate cover from HTML template (requires Playwright)
    --subtitle    Subtitle for HTML cover
    --image-quality  JPEG compression quality 1-100 (default: 88)
    --image-width    Max image width in pixels (default: 1000)

Examples:
    python3 gen_epub.py ~/articles/ ~/output.epub
    python3 gen_epub.py ~/articles/ ~/book.epub --title "My Book" --author "Author" --cover cover.jpg
    python3 gen_epub.py ~/articles/ ~/book.epub --cover-html --title "My Book" --subtitle "100 essays"
"""

import argparse
import os
import glob
import re
import sys
import html as html_module
from pathlib import Path
from ebooklib import epub
import markdown
from PIL import Image
import io


# ─── Kami 设计语言 CSS（WeChat 兼容简化版，无背景色） ───
CHAPTER_CSS = """
body {
    font-family: "Charter", "Iowan Old Style", "Source Han Serif SC",
                 "Noto Serif CJK SC", "Songti SC", "STSong", Georgia, serif;
    line-height: 1.55;
    margin: 1em;
    padding: 0;
    font-size: 1em;
    color: #141413;
    letter-spacing: 0.02em;
}
h1, h2, h3 {
    font-family: "Charter", "Iowan Old Style", "Source Han Serif SC",
                 "Noto Serif CJK SC", "Songti SC", Georgia, serif;
    font-weight: 500;
    color: #141413;
}
h1 {
    font-size: 1.7em;
    line-height: 1.20;
    margin: 0 0 1em 0;
    border-left: 2.5pt solid #1B365D;
    border-radius: 1.5pt;
    padding-left: 0.5em;
}
h2 {
    font-size: 1.3em;
    line-height: 1.25;
    margin: 1.8em 0 0.6em 0;
    border-left: 2pt solid #1B365D;
    padding-left: 0.45em;
}
h3 {
    font-size: 1.1em;
    line-height: 1.30;
    margin: 1.4em 0 0.4em 0;
    color: #3d3d3a;
}
p {
    margin: 0 0 0.85em 0;
    text-align: justify;
}
strong, b {
    font-weight: 600;
    color: #141413;
}
em, i {
    font-style: italic;
    color: #3d3d3a;
}
blockquote {
    border-left: 2pt solid #1B365D;
    padding: 0.2em 0 0.2em 1em;
    margin: 1em 0;
    color: #504e49;
    line-height: 1.55;
}
img {
    max-width: 100%;
    height: auto;
}
.metadata {
    color: #6b6a64;
    font-size: 0.85em;
    margin-bottom: 1em;
    font-style: italic;
}
.card-img {
    text-align: center;
    margin: 1em 0;
}
hr {
    border: none;
    border-top: 0.5pt solid #e8e6dc;
    margin: 2em 0;
}
"""


def compress_image(img_path, target_width=1000, jpeg_quality=88):
    """Compress image to JPEG with configurable quality."""
    try:
        img = Image.open(img_path)

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
        print(f"  Warning: Image compression failed for {img_path}: {e}")
        return None


def parse_article(md_path):
    """Parse Markdown article, extract title and metadata."""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.strip().split('\n')

    title = "Untitled"
    metadata = ""
    body_start = 0

    for i, line in enumerate(lines):
        if line.startswith('# '):
            title = line[2:].strip()
            body_start = i + 1
            if i + 1 < len(lines) and lines[i + 1].startswith('> '):
                metadata = lines[i + 1][2:].strip()
                body_start = i + 2
            break

    body = '\n'.join(lines[body_start:]).strip()
    return title, metadata, body


def build_xhtml(title, metadata, image_html, body_html):
    """Build valid XHTML document with inline CSS (WeChat Reading compatible)."""
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
    html_str = re.sub(r'<br\s*>', '<br/>', html_str)
    html_str = re.sub(r'<hr\s*>', '<hr/>', html_str)
    html_str = re.sub(r'<img([^/]*?)>', r'<img\1/>', html_str)
    html_str = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\d+;|#x[0-9a-fA-F]+;)', '&amp;', html_str)
    return html_str


def generate_html_cover(title, subtitle="", author=""):
    """Generate cover image from HTML template using Playwright."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Warning: Playwright not installed, skipping HTML cover generation")
        print("Install with: pip install playwright && playwright install chromium")
        return None

    # Import the cover generator
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, script_dir)
    from gen_cover_html import generate_cover_html, screenshot_cover

    html_path = generate_cover_html(title, subtitle, author)
    cover_path = "/tmp/epub_cover.jpg"
    screenshot_cover(html_path, cover_path)

    with open(cover_path, 'rb') as f:
        return f.read()


def find_article_image(slug, input_dir):
    """Find matching image for an article (same dir or parent dir)."""
    # Check common image locations and extensions
    for ext in ['png', 'jpg', 'jpeg']:
        # Same directory as articles
        path = os.path.join(input_dir, f"{slug}.{ext}")
        if os.path.exists(path):
            return path
        # Parent directory (common pattern: articles/ subdir + images in parent)
        parent = os.path.dirname(input_dir.rstrip('/'))
        path = os.path.join(parent, f"{slug}.{ext}")
        if os.path.exists(path):
            return path
    return None


def create_epub(args):
    """Generate EPUB with WeChat Reading compatibility."""
    input_dir = os.path.expanduser(args.input_dir)
    output_path = os.path.expanduser(args.output_file)

    md_files = sorted(glob.glob(os.path.join(input_dir, "*.md")))
    if not md_files:
        print(f"Error: No .md files found in {input_dir}")
        sys.exit(1)

    print(f"Generating EPUB (WeChat Reading compatible)...")
    print(f"  Input: {input_dir} ({len(md_files)} articles)")
    print(f"  Output: {output_path}")

    # Extract title from first article if not provided
    title = args.title
    if not title:
        first_title, _, _ = parse_article(md_files[0])
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
    elif args.cover_html:
        subtitle = args.subtitle or f"{len(md_files)} articles"
        cover_data = generate_html_cover(title, subtitle, args.author or "")
        print(f"  Cover: HTML generated")

    if cover_data:
        book.set_cover("cover.jpg", cover_data)

    # Process articles
    chapters = []
    toc_items = []
    spine = ['nav']
    total_img_size = 0

    for i, md_path in enumerate(md_files, 1):
        slug = Path(md_path).stem

        if i % 50 == 0 or i == 1:
            print(f"  [{i}/{len(md_files)}] {slug}")

        title_text, metadata, body = parse_article(md_path)

        # Find and compress illustration
        img_path = find_article_image(slug, input_dir)
        image_html = ""

        if img_path:
            img_data = compress_image(img_path, args.image_width, args.image_quality)
            if img_data:
                total_img_size += len(img_data)
                img_filename = f"images/{slug}.jpg"
                img_item = epub.EpubItem(
                    uid=f"img_{slug}",
                    file_name=img_filename,
                    media_type="image/jpeg",
                    content=img_data
                )
                book.add_item(img_item)
                image_html = f'<img src="{img_filename}" alt="{html_module.escape(title_text)}"/>'

        # Markdown → HTML
        md_html = markdown.markdown(body, extensions=['extra'])
        md_html = fix_xhtml(md_html)

        chapter_html = build_xhtml(title_text, metadata, image_html, md_html)

        chapter = epub.EpubHtml(
            title=title_text,
            file_name=f"chapter_{i:03d}.xhtml",
            lang=args.language
        )
        chapter.set_content(chapter_html.encode('utf-8'))
        chapter.add_item(css_item)

        book.add_item(chapter)
        chapters.append(chapter)
        toc_items.append(epub.Link(f"chapter_{i:03d}.xhtml", title_text, f"ch{i}"))
        spine.append(chapter)

    # TOC and navigation
    book.toc = toc_items
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

    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    img_size_mb = total_img_size / (1024 * 1024)
    print(f"\n✅ Done!")
    print(f"  Output: {output_path}")
    print(f"  File size: {size_mb:.1f} MB")
    print(f"  Images: {img_size_mb:.1f} MB")
    print(f"  Chapters: {len(chapters)}")


def main():
    parser = argparse.ArgumentParser(description='Generate EPUB from Markdown files (WeChat Reading compatible)')
    parser.add_argument('input_dir', help='Directory containing Markdown files')
    parser.add_argument('output_file', help='Output EPUB file path')
    parser.add_argument('--title', help='Book title')
    parser.add_argument('--author', help='Author name(s), separate multiple with /')
    parser.add_argument('--language', default='zh', help='Language code (default: zh)')
    parser.add_argument('--cover', help='Cover image path (JPG/PNG)')
    parser.add_argument('--cover-html', action='store_true', help='Generate cover from HTML template')
    parser.add_argument('--subtitle', help='Subtitle for HTML cover')
    parser.add_argument('--image-quality', type=int, default=88, help='JPEG quality 1-100 (default: 88)')
    parser.add_argument('--image-width', type=int, default=1000, help='Max image width px (default: 1000)')

    args = parser.parse_args()
    create_epub(args)


if __name__ == "__main__":
    main()
