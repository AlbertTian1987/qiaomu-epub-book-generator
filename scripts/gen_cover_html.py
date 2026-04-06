#!/usr/bin/env python3
"""
Generate EPUB cover from HTML template (no AI image generation required).
Uses Playwright to render HTML and take screenshot.
"""

import sys
import os
from pathlib import Path

def generate_cover_html(title, subtitle="", author="", output_path="/tmp/cover.html"):
    """Generate HTML cover page with clean typography."""

    # Clean, minimal cover design
    html_content = f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=900, initial-scale=1.0">
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;700;900&display=swap');

* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    width: 900px;
    height: 1350px;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 80px 60px;
    font-family: 'Noto Serif SC', serif;
    position: relative;
    overflow: hidden;
}}

/* Decorative elements */
body::before {{
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 100%;
    height: 100%;
    background: radial-gradient(circle, rgba(255,255,255,0.03) 0%, transparent 70%);
}}

.container {{
    text-align: center;
    z-index: 1;
    max-width: 700px;
}}

.title {{
    font-size: 72px;
    font-weight: 900;
    color: #ffffff;
    line-height: 1.2;
    margin-bottom: 40px;
    letter-spacing: 0.02em;
    text-shadow: 0 4px 20px rgba(0,0,0,0.3);
}}

.subtitle {{
    font-size: 28px;
    font-weight: 400;
    color: #e0e0e0;
    line-height: 1.5;
    margin-bottom: 60px;
    opacity: 0.9;
}}

.divider {{
    width: 120px;
    height: 3px;
    background: linear-gradient(90deg, transparent, #f39c12, transparent);
    margin: 50px auto;
}}

.author {{
    font-size: 24px;
    font-weight: 400;
    color: #f39c12;
    letter-spacing: 0.1em;
    margin-top: 80px;
}}

.decoration {{
    position: absolute;
    bottom: 60px;
    left: 50%;
    transform: translateX(-50%);
    width: 200px;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(243,156,18,0.5), transparent);
}}
</style>
</head>
<body>
<div class="container">
    <div class="title">{title}</div>
    {f'<div class="subtitle">{subtitle}</div>' if subtitle else ''}
    <div class="divider"></div>
    {f'<div class="author">{author}</div>' if author else ''}
</div>
<div class="decoration"></div>
</body>
</html>"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ HTML cover generated: {output_path}")
    return output_path


def screenshot_cover(html_path, output_image="/tmp/cover.jpg"):
    """Take screenshot of HTML cover using Playwright."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ Playwright not installed. Run: pip install playwright && playwright install chromium")
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 900, "height": 1350}, device_scale_factor=2)
        page.goto(f"file://{os.path.abspath(html_path)}")
        page.wait_for_timeout(2000)  # Wait for fonts to load
        page.screenshot(path=output_image, type='jpeg', quality=95)
        browser.close()

    print(f"✅ Cover screenshot saved: {output_image}")
    return output_image


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 gen_cover_html.py <title> [subtitle] [author] [output_image]")
        print("Example: python3 gen_cover_html.py 'Paul Graham 文集' '230篇创业与编程经典' 'Paul Graham / 向阳乔木' cover.jpg")
        sys.exit(1)

    title = sys.argv[1]
    subtitle = sys.argv[2] if len(sys.argv) > 2 else ""
    author = sys.argv[3] if len(sys.argv) > 3 else ""
    output_image = sys.argv[4] if len(sys.argv) > 4 else "/tmp/cover.jpg"

    # Generate HTML
    html_path = generate_cover_html(title, subtitle, author)

    # Screenshot
    screenshot_cover(html_path, output_image)

    print(f"\n✅ Done! Cover image: {output_image}")
