#!/usr/bin/env python3
"""verify_novel_input.py — 验证小说源文件是否符合输入合约 §8 验收标准。

用法:
    python3 verify_novel_input.py <md_dir>
    python3 verify_novel_input.py <md_dir> --json
"""
import os
import sys
import re
import json
import traceback

try:
    import yaml
except ImportError:
    yaml = None  # 降级处理：无 yaml 时 frontmatter 检查将报错


ALLOWED_KINDS = {"正文", "楔子", "序章", "引子", "番外"}


def read_frontmatter(content):
    """解析 YAML frontmatter。

    识别文件开头的 ---\\n...yaml...\\n--- 块。
    返回 (frontmatter_dict, rest_content)；若无 frontmatter 则返回 ({}, content)。
    """
    rest = content.lstrip("﻿")  # 去除可能的 BOM
    if not rest.startswith("---"):
        return {}, rest
    # 找到 closing ---
    end_idx = rest.find("\n---", 3)
    if end_idx == -1:
        return {}, rest
    yaml_block = rest[3:end_idx]
    rest_content = rest[end_idx + 4:]
    if yaml is None:
        # 无 PyYAML，抛出友好错误而非静默跳过
        raise RuntimeError("PyYAML 未安装，无法解析 frontmatter。请执行: pip install pyyaml")
    try:
        fm = yaml.safe_load(yaml_block)
    except yaml.YAMLError as e:
        raise ValueError(f"YAML 解析失败: {e}") from e
    if not isinstance(fm, dict):
        fm = {}
    return fm, rest_content


def check(checks, level, name, passed, detail=""):
    checks.append({
        "level": level,
        "name": name,
        "pass": bool(passed) if not callable(passed) else passed(),
        "detail": detail,
    })


def run_checks(md_dir):
    """对 md_dir 中所有 *.md 文件执行 12 项验收检查，返回检查结果列表。"""
    checks = []

    # ── 收集文件 ──────────────────────────────────────────────────────────
    all_items = os.listdir(md_dir)
    md_files_raw = [f for f in all_items if f.endswith(".md") and os.path.isfile(os.path.join(md_dir, f))]
    md_files = sorted(md_files_raw)  # 字母序

    # ── C11: 文件总数 >= 1 ────────────────────────────────────────────────
    check(checks, "强制", "至少1个文件", len(md_files) >= 1)

    # ── C4: 文件名字母序 = 阅读顺序（无随机漂移） ──────────────────────────
    if md_files:
        is_sorted = (md_files == sorted(md_files_raw))
        detail = "" if is_sorted else f"文件系统顺序与字母序不一致: {md_files_raw} ≠ {md_files}"
        check(checks, "强制", "文件名字母序等于阅读顺序（无随机漂移）", is_sorted, detail)
    else:
        check(checks, "强制", "文件名字母序等于阅读顺序（无随机漂移）", True)

    # ── 逐文件读取并缓存 ──────────────────────────────────────────────────
    file_contents = {}  # fname -> (content, fm, h1, kind, volume, exception?)
    file_errors = []

    for fname in md_files:
        fpath = os.path.join(md_dir, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as fh:
                content = fh.read()
        except Exception as exc:
            file_errors.append((fname, f"读取失败: {exc}"))
            file_contents[fname] = None
            continue

        if not content.strip():
            file_errors.append((fname, "文件内容为空"))
            file_contents[fname] = None
            continue

        # 解析 frontmatter
        try:
            fm, rest = read_frontmatter(content)
        except (ValueError, RuntimeError) as exc:
            file_errors.append((fname, f"frontmatter 解析失败: {exc}"))
            fm, rest = {}, content

        # 提取 H1（跳过 frontmatter，跳过前导空行）
        first_line = ""
        for line in rest.split("\n"):
            if line.strip():
                first_line = line.strip()
                break
        h1_text = first_line[2:].strip() if first_line.startswith("# ") else ""

        file_contents[fname] = {
            "content": content,
            "fm": fm,
            "h1": h1_text,
            "kind": fm.get("kind", ""),
            "volume": fm.get("volume", ""),
        }

    # ── C1: 每个 .md 文件可读（UTF-8, 非空） ────────────────────────────
    unreadable = [f for f in md_files if file_contents.get(f) is None]
    if unreadable:
        detail = "不可读文件: " + ", ".join(unreadable)
        check(checks, "强制", "每个 .md 文件可读（UTF-8, 非空）", False, detail)
    else:
        check(checks, "强制", "每个 .md 文件可读（UTF-8, 非空）", True)

    # ── C2: 文件名格式 NNN.md, NNN-*.md 或 NNN_*.md ──────────────────────
    bad_fnames = []
    for fname in md_files:
        if not re.match(r"\d+[-_].+\.md$", fname) and not re.match(r"\d+\.md$", fname):
            bad_fnames.append(fname)
    if bad_fnames:
        detail = "不合规文件名: " + ", ".join(bad_fnames)
        check(checks, "强制", "文件名格式: NNN-*.md 或 NNN_*.md", False, detail)
    else:
        check(checks, "强制", "文件名格式: NNN-*.md 或 NNN_*.md", True)

    # ── C3: 第一行以 # 开头（H1 章名） ──────────────────────────────────
    no_h1 = []
    for fname in md_files:
        fc = file_contents.get(fname)
        if fc is None:
            no_h1.append(f"{fname} → 文件不可读，无法检查")
            continue
        if not fc["h1"]:
            no_h1.append(f"{fname}")
    if no_h1:
        detail = "缺失 H1: " + ", ".join(no_h1)
        check(checks, "强制", "第一行以 # 开头（H1 章名）", False, detail)
    else:
        check(checks, "强制", "第一行以 # 开头（H1 章名）", True)

    # ── C5: H1 与文件名关键词匹配（近似校验，警告） ─────────────────────
    h1_mismatches = []
    for fname in md_files:
        fc = file_contents.get(fname)
        if fc is None or not fc["h1"]:
            continue
        # 从文件名中提取 "NNN-关键词" 的 "关键词" 部分
        m = re.match(r"\d+[-_](.+)\.md$", fname)
        if not m:
            continue
        kw = m.group(1)
        # 将文件名关键词中的 _/- 替换为空格，再检查 H1 是否包含之
        kw_normalized = re.sub(r"[-_]", " ", kw).lower()
        h1_lower = fc["h1"].lower()
        # 检查 H1 是否包含关键子段：把 kw 按分隔符拆成若干词，看是否都有
        kw_parts = [p for p in re.split(r"[-_\s]", kw_normalized) if p]
        missing_parts = [p for p in kw_parts if p not in h1_lower]
        if missing_parts:
            h1_mismatches.append(f"{fname}: H1=「{fc['h1']}」, 文件名关键词=「{kw}」")
    if h1_mismatches:
        detail = "以下文件 H1 与文件名关键词不匹配（近似校验）:\n  " + "\n  ".join(h1_mismatches)
        check(checks, "警告", "H1 与文件名关键词匹配（近似校验）", False, detail)
    else:
        check(checks, "警告", "H1 与文件名关键词匹配（近似校验）", True)

    # ── C6: 同卷拼写一致（不同卷不冲突）──────────────────────────────────
    volumes_map = {}  # normalized_num -> set(original_values)
    for fname in md_files:
        fc = file_contents.get(fname)
        if fc is None:
            continue
        v = str(fc["volume"]).strip() if fc["volume"] else ""
        if not v:
            continue
        # 提取卷号核心数字/"一"/"二"等，忽略 第/卷/部 等前缀后缀
        m = re.search(r'[一二三四五六七八九十零\d]+', v)
        norm = m.group(0) if m else v
        volumes_map.setdefault(norm, set()).add(v)
    conflicts = {n: vs for n, vs in volumes_map.items() if len(vs) > 1}
    check(checks, "强制", '同卷 volume 值拼写一致（无"卷一"vs"第一卷"混用）',
          len(conflicts) == 0,
          f"同一卷存在不同拼写: {conflicts}" if conflicts else "")

    # ── C7: kind 值来自合法集合 ──────────────────────────────────────────
    bad_kinds = []
    for fname in md_files:
        fc = file_contents.get(fname)
        if fc is None:
            continue
        k = fc["kind"]
        if k and k not in ALLOWED_KINDS:
            bad_kinds.append(f"{fname}: kind=「{k}」")
    if bad_kinds:
        detail = "非法 kind 值: " + ", ".join(bad_kinds)
        check(checks, "强制", "kind 值来自合法集合", False, detail)
    else:
        check(checks, "强制", "kind 值来自合法集合", True)

    # ── C8: 楔子/序章/引子 每种最多出现一次 ─────────────────────────────
    kind_counts = {}
    for fname in md_files:
        fc = file_contents.get(fname)
        if fc is None:
            continue
        k = fc["kind"]
        if k in ("楔子", "序章", "引子"):
            kind_counts.setdefault(k, []).append(fname)
    dup_kinds = {k: v for k, v in kind_counts.items() if len(v) > 1}
    if dup_kinds:
        parts = [f"{k}({len(v)}次): {', '.join(v)}" for k, v in dup_kinds.items()]
        detail = "重复的特殊章节: " + "; ".join(parts)
        check(checks, "警告", "楔子/序章/引子 每种最多出现一次", False, detail)
    else:
        check(checks, "警告", "楔子/序章/引子 每种最多出现一次", True)

    # ── C9: 无重复 H1 章名 ──────────────────────────────────────────────
    h1_seen = {}
    for fname in md_files:
        fc = file_contents.get(fname)
        if fc is None or not fc["h1"]:
            continue
        h1_seen.setdefault(fc["h1"], []).append(fname)
    dup_h1 = {k: v for k, v in h1_seen.items() if len(v) > 1}
    if dup_h1:
        parts = [f"「{h}」({', '.join(fs)})" for h, fs in dup_h1.items()]
        detail = "重复 H1: " + "; ".join(parts)
        check(checks, "警告", "无重复 H1 章名", False, detail)
    else:
        check(checks, "警告", "无重复 H1 章名", True)

    # ── C10: 内容中不含常见残留 HTML 标签 ──────────────────────────────
    html_tag_pattern = re.compile(r"<(div|\s*a\s+|script|style|nav[\s>])", re.IGNORECASE)
    html_files = []
    for fname in md_files:
        fc = file_contents.get(fname)
        if fc is None:
            continue
        if html_tag_pattern.search(fc["content"]):
            html_files.append(fname)
    if html_files:
        detail = "含残留 HTML 标签: " + ", ".join(html_files)
        check(checks, "警告", "内容中不含常见残留 HTML 标签", False, detail)
    else:
        check(checks, "警告", "内容中不含常见残留 HTML 标签", True)

    # ── C12: frontmatter YAML 格式正确（若有） ────────────────────────────
    bad_yaml = []
    for fname in md_files:
        fpath = os.path.join(md_dir, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as fh:
                raw = fh.read()
        except Exception:
            continue  # 已在 C1 中报告
        rest = raw.lstrip("﻿")
        if not rest.startswith("---"):
            continue  # 无 frontmatter，跳过
        try:
            read_frontmatter(raw)
        except (ValueError, RuntimeError) as exc:
            bad_yaml.append(f"{fname}: {exc}")
    if bad_yaml:
        detail = "frontmatter YAML 格式错误:\n  " + "\n  ".join(bad_yaml)
        check(checks, "强制", "frontmatter YAML 格式正确（若有）", False, detail)
    else:
        check(checks, "强制", "frontmatter YAML 格式正确（若有）", True)

    return checks


def colorize(text, color):
    """用 ANSI 颜色包裹文本（终端支持时）。"""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "cyan": "\033[96m",
        "bold": "\033[1m",
        "reset": "\033[0m",
    }
    return colors.get(color, "") + text + colors["reset"]


def report_human(checks):
    """输出人类可读的红绿灯式报告。"""
    total = len(checks)
    passed = sum(1 for c in checks if c["pass"])
    failed_mandatory = sum(1 for c in checks if c["level"] == "强制" and not c["pass"])
    warnings = sum(1 for c in checks if c["level"] == "警告" and not c["pass"])

    print()
    print(colorize("验收结果:", "bold"))
    print(colorize("━" * 80, "cyan"))

    for c in checks:
        if c["pass"]:
            icon = colorize("✓", "green")
        elif c["level"] == "强制":
            icon = colorize("✗", "red")
        else:
            icon = colorize("⚠", "yellow")

        label = f"[{c['level']}]"
        print(f"  {icon} {label} {c['name']}")
        if c["detail"]:
            # 缩进细节
            for line in c["detail"].split("\n"):
                print(f"       {line}")

    print(colorize("━" * 80, "cyan"))
    passed_color = "green" if passed == total else ("yellow" if warnings else "red")
    print(f"  {colorize('通过:', 'bold')} {colorize(f'{passed}/{total}', passed_color)}")
    if failed_mandatory:
        print(f"  {colorize('强制失败:', 'bold')} {colorize(str(failed_mandatory), 'red')}   ← 需要修复")
    if warnings:
        print(f"  {colorize('警告:', 'bold')} {colorize(str(warnings), 'yellow')}")
    print()

    return failed_mandatory > 0


def report_json(checks):
    """输出 JSON 格式的结果。"""
    result = {
        "total": len(checks),
        "passed": sum(1 for c in checks if c["pass"]),
        "failed_mandatory": sum(1 for c in checks if c["level"] == "强制" and not c["pass"]),
        "warnings": sum(1 for c in checks if c["level"] == "警告" and not c["pass"]),
        "checks": checks,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result["failed_mandatory"] > 0


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__, end="")
        sys.exit(0)

    md_dir = sys.argv[1]
    use_json = "--json" in sys.argv[2:] if len(sys.argv) > 2 else False

    if not os.path.isdir(md_dir):
        print(f"错误: 目录不存在: {md_dir}", file=sys.stderr)
        sys.exit(1)

    checks = run_checks(md_dir)

    if use_json:
        has_failures = report_json(checks)
    else:
        has_failures = report_human(checks)

    sys.exit(1 if has_failures else 0)


if __name__ == "__main__":
    main()
