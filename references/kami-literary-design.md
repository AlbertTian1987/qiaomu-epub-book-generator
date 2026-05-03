# Kami 文学版 (Kami Literary) — EPUB 设计改进计划

> 本文档面向 `qiaomu-epub-book-generator` skill 的**小说场景**优化。目标：让用户用本 skill 生成的 EPUB「一看就觉得高级」，且风格严格遵循 [Kami](https://github.com/tw93/kami) 设计语言。
>
> 适用对象：`gen_epub_enhanced.py`（CSS 主题）+ `gen_cover_svg.py`（封面）。
> 不适用：`gen_epub.py`（基础版，保留现状作为兼容路径）。
>
> **本 fork 的主要场景是网文 / 长篇连载**——长章名（如「第五百二十五章 重逢于雨夜的破败茶馆」）是大概率现象，不是边缘 case。所以 `webnovel` 是默认模式，`literary` 作为短章名场景的 opt-in 切换。

---

## 1. 北极星 (North Star)

> **读者打开第一页，应感到这是一本被认真排版的书，不是一份被自动转换的文档。**

策略不是「加装饰显得高级」，而是 **做减法 + 把对的细节做对**。

Kami 文学版 = Kami 的克制 × 西方书籍 70 年的排版传统 × 中文小说的约定。

---

## 2. 设计契约：把 Kami invariants 翻译到 EPUB

| Kami invariant | EPUB 文学版落地 |
|---|---|
| 羊皮纸底，永不纯白 | **强制 `body { background: var(--paper) }`，双光照色板（见 §2.5），零阅读器决定权** |
| 唯一墨蓝 `#1B365D` | 章节编号 / 首字下沉 / `<strong>` / 分隔花饰 / 封面双线，全部共用（暗色下提亮为 `#6B95C9`，色相不变）|
| 全暖灰，无冷蓝灰 | stone 元数据；olive 副文 / 引用；dark-warm 副标题。**暗色版同样全暖色调**（见 §2.5）|
| serif 仅 400/500，禁合成粗体 | `<strong>` 锁 500 + 改色（不加粗）；正文 400；标题 500 |
| 不用 italic | **中文用着重号** (`text-emphasis: dot`)；**英文保留真斜体**（Charter 自带，非合成）|
| 无硬阴影 | EPUB 一律 0 阴影 |
| 行高 1.50–1.55（reading body）| 网文模式 1.65；文学模式 1.55；引文 / 题记 1.45；章节标题 1.15–1.45（按长度分档）|
| 字距 | 中文 0.05em（TsangerJinKai 密度补偿）；英文 0；日文 0.02em |

---

## 2.5. 双光照色契约：Kami Light + Kami Dark

> Kami 母体只面对印刷品（光照条件单一），EPUB 必须面对屏幕的两种光照条件。这是 Kami EPUB 比 Kami 母体「多走一步」的地方——**把单光照设计扩展为双光照设计**。

### 核心决定

**EPUB 不让阅读器决定背景色。** 我们对自己的视觉负责，亮色 / 暗色都精心设计自己的色板。Kami 十大不变量第一条「永不纯白」必须在所有光照条件下成立。

承认妥协：微信读书 / Kindle 老设备会强制覆盖 body 背景，这部分用户看到的依然是阅读器默认。**我们做不到 100%，但能赢的地方都赢。**

### Kami Light（屏幕浅色 / 默认）

| Token | Hex | 用途 |
|---|---|---|
| `--paper` | `#f5f4ed` | 页面底（羊皮纸） |
| `--ivory` | `#faf9f5` | 卡片 / 提升容器 |
| `--ink` | `#1B365D` | 唯一 accent |
| `--text` | `#141413` | 正文 |
| `--olive` | `#504e49` | 副文 / 引用 |
| `--stone` | `#6b6a64` | 元数据 / 三级文字 |
| `--border` | `#e8e6dc` | 边线 |

### Kami Dark（屏幕暗色 / 关键设计）

**不是反色，而是把 Kami 暖色调向深处延伸**：

| Token | Hex | 用途 |
|---|---|---|
| `--paper` | `#1c1a17` | 页面底（暗墨棕，不是黑） |
| `--ivory` | `#252320` | 卡片 |
| `--ink` | `#6B95C9` | 提亮版墨蓝（色相不变，明度提升）|
| `--text` | `#e8e4d8` | 正文（暖象牙，不是冷白）|
| `--olive` | `#b3aa9b` | 副文 |
| `--stone` | `#8a8378` | 元数据 |
| `--border` | `#3a3631` | 边线 |

**关键约束**：
- **零冷蓝灰**——所有暗色都带黄棕底色
- 墨蓝必须提亮（`#1B365D` 在深色背景上几乎不可见），但**色相不变**——依然是 Kami 那条墨蓝
- ❦ 花饰、首字下沉、章节编号、`<strong>` 全部沿用 `--ink`
- 文字色 `#e8e4d8` 而非 `#fff`——**纯白在 Kami DNA 里同样禁**

### 落地：CSS variables + media query

```css
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

html, body {
    background: var(--paper);
    color: var(--text);
}
```

**所有色值通过变量引用**——没有任何写死的 hex（除封面 SVG 印刷品场景）。

### 反向修订旧条目（覆盖前文 / 路线图）

本节生效后，以下条目被本节取代或合并：

- ~~§2 设计契约第一行原 EPUB 落地「正文不设 body 背景」~~ → **改为强制背景 + 双光照色板**
- ~~原路线图 P0「暗色模式 fallback」~~ → **升级为本节完整 Kami Dark 实现，仍 P0**
- ~~原路线图 P2「CSS variables 化」~~ → **并入本节 P0 双光照实现，不再独立 P2**

---

## 3. 页面架构

```
封面 → 目录 → 正文章节 ... ( 仅此 )
```

**不生成**：半书名页 / 书名页 / 献辞 / 题记 / 版权页 / 封底。

理由：用户明确指示「除封面外，不多余生成」。EPUB 的前后附件在阅读器场景下读者很少翻看，反而稀释了「直接进入故事」的体验。

---

## 3.5. 主模式：webnovel（默认）vs literary

### 模式开关

CLI: `--mode {webnovel|literary}` （**default: `webnovel`**）

理由：本 fork 主要场景是网文 / 长篇连载，长章名是大概率现象。把 webnovel 设为默认更贴合实际使用，避免每次都要显式指定。

### 两种模式的设计差异

| 维度 | `webnovel`（默认）| `literary`（opt-in）|
|---|---|---|
| 默认章名字距 | 0.05em（仅密度补偿）| 0.4em（短而精，戏剧化）|
| 默认章号位置 | inline（与章名同行，中点 ` · ` 分隔）| above（独立上方一行）|
| 章首字号基准 | 1.6em（4 档自适应见 §5.5）| 2.4em |
| 章号风格 | 沿用源文「第 525 章」/「第五百二十五章」 | 沿用源文，可参数化为罗马 I / II / III |
| 正文行高 | 1.65（网文段更密，行高放宽更舒服）| 1.55 |
| 首字下沉 | **全关**（章名长度不一，下沉视觉破碎）| 中文关 / 英文开 |
| 章末 `page-break-after` | 不强制（网文章节切换快速）| 强制（章末留白）|
| TOC 章序 | 阿拉伯数字 1 / 2 / 3 | 罗马数字 I / II / III |
| 章末花饰 | 仅 ❦ | ❦ + 强制换页 |

### 设计哲学差异

**字距是给「短而精」的标题用的**：
- 「灯塔」「Chapter One」字距 0.4em → 优雅
- 「重逢于雨夜的破败茶馆」字距 0.4em → **灾难**

**网文章名是「长而具体」的**——它的高级感不能靠字距表演，只能靠：
- 字号节制（1.6em 而非 2.4em）
- 行高宽松（1.3 允许优雅换行）
- 字距收紧（0.05em 仅密度补偿）
- 留白依然充足（章首上方 25vh 不变）

**两种模式都是 Kami**——都用羊皮纸 + 墨蓝 + serif + 全暖灰 + 零装饰。区别在于「字距戏剧化 vs 字号节制」的取舍。

### Body class 注入

```html
<body class="mode-webnovel">  <!-- 或 mode-literary -->
```

CSS 用 body class 选择器切换，不重复加载样式表。

---

## 3.6. 预处理层契约：输入合约与分工

EPUB 生成器不参与源数据清洗。站特定的工作（HTML 清洗、TXT 拆分）是外部准备层的责任，排版层不猜源格式。

### 分工边界

| 任务 | 负责方 | 理由 |
|---|---|---|
| 站特定 HTML 清洗、TXT 切分、数据去重 | 外部准备层 | 规则发散，排版层猜不中就是破坏数据 |
| 章号解析（从「第一章」「第1章」「Chapter 1」提取文字部分） | 生成器 | §5.5 字号自适应需要数字感知 |
| 标点归一（`...` → `……`、`--`/`—` → `——`、中英空格、半全角清理） | 生成器（`--no-punct-fix` 可关） | 每个站点重写不可复用 |
| 章名 / 卷分组 / 特殊元素识别 | 生成器 | 按输入合约约定的 frontmatter/文件名 消费 |
| 正文语义正确性（错别字、段落遗漏） | 外部准备层 | 排版层不碰数据质量 |

### 输入合约速览

生成器期望的输入：**一个 `.md` = 一章**，文件名字母序决定阅读顺序。详细合约见 `references/input-contract.md`。

**最小形态**：
```markdown
# 第一章 灯塔

正文…
```

**带 YAML frontmatter（推荐）**：
```markdown
---
volume: 卷一
kind: 正文          # 可选: 楔子 | 序章 | 引子 | 番外 | 正文(默认)
---

# 第一章 灯塔
```

**文件组织三原则**：
1. 文件名 `NNN-章名.md` 形式，字母序=阅读顺序
2. 第一行 `# 章名`
3. 卷分组通过 frontmatter / 文件夹 / 文件名前缀三种约定之一表达

**不做的**：生成器不猜源 HTML 的 `<div class="content">` 选择器、不猜 TXT 的编码、不猜哪段是正文哪段是广告——这些全是外部准备层的责任。

---

## 3.7. 卷 / 部 / 篇层级

长篇网文（500+ 章常见）几乎都以卷分组。EPUB 的 NCX 支持嵌套 TOC，但当前路线图未考虑这一层。

### 设计决定

**有卷时**：

```
封面 → TOC(嵌套: 卷→章) → 卷封页 → 章 ... 卷封页 → 章 ... 番外(附录区)
```

- NCX 嵌套 TOC：卷为父节点，章为子节点
- 每卷开头插入卷封页（独立 XHTML，spine 中独立一页）
- 卷封页 anchor 到 TOC 父节点

**无卷时（默认）**：

```
封面 → TOC(扁平) → 章 ...
```

保持现有路径，扁平 TOC。

### 卷封页设计

```
[ 上方留白 ~35vh ]

         卷  一            ← 1.4em，字距 0.4em，serif 500
            ❦
      初入江湖              ← 可选 volume_title，olive 0.85em
```

零装饰，仅留白 + 字距 + ❦。作用：翻新卷时的视觉锚点。

### 卷分组识别（按优先级）

| 方案 | 优先级 | 示例 |
|---|---|---|
| frontmatter `volume:` 字段 | 最高（最显式） | `---\nvolume: 卷一\n---` |
| 文件夹分层 | 中 | `卷一/001-灯塔.md` |
| 文件名前缀 | 低（弱约定） | `卷一-001-灯塔.md` |

三种方案在输入合约 `references/input-contract.md` 中有完整规范。无卷标记时全扁平。

---

## 3.8. 网文特殊元素

### 楔子 / 序章 / 引子

TOC 位置：第一卷之前的「前置区」，与正文卷平级。

章首页：

```
[ 上方留白 ~25vh ]

            ❦

他记得那个秋天的早晨...    ← 无章号，首段不下沉，后续缩进 2em
```

文件约定：
```markdown
---
kind: 楔子
---

# 楔子
```

约束：单本书中各最多出现一次（生成器不强制校验，但设计上不允许多个楔子共存）。

### 番外

TOC 位置：最后一卷之后的「附录区」，独立区域。

章首页同楔子——无章号，直达正文。番外可多个。文件名：

```
007-中秋夜.md   ← kind: 番外
008-后记.md      ← kind: 番外
```

### 作者按 / PS:

Inline 嵌入正文末尾，排版层渲染为 stone 色 0.85em 小字块，与正文通过上下间距 + 缩小字号形成视觉分离。不另占行，不单独成页。

```
正文结束。

> 作者按：本章写于 2024 年深夜。
```

排版层将 `>` 引用块渲染为 olive 小字（stone 0.85em）。

### "未完待续"

章末居中 stone 0.75em，自动识别：

```
正文最后一行

（未完待续）
```

正则匹配：`[（(][未Ww][完][待Tt][续][）)]`。识别后渲染为居中 stone 0.75em 小字，与 ❦ 互斥（有❦就不显示"未完待续"）。

### 场景切换符（多形式识别）

Markdown 中的以下表示均归一为居中墨蓝 ❦：

| 源格式 | 归一 |
|---|---|
| `---` | ❦ |
| `* * *` | ❦ |
| `--------`（连续短横线） | ❦ |
| `————` 全角破折号 | ❦ |
| `（一）（二）（三）` | ❦ |
| 正文中连续三空行 | ❦ |

CSS：`hr { display: none 或替换为 ::after 伪元素 }`，统一渲染为 `❦`。

---

## 4. 章首页：双模式 + 自适应

每章固定结构（**全部居中，无任何左边栏 / 方框**），具体字号 / 字距由模式 + 章名长度联合决定。

### webnovel 模式（默认，长章名场景）

```
[ 上方留白 ~25vh ]

  第五百二十五章 · 重逢于雨夜的破败茶馆     ← 1.2em，字距 0，居中（title-s 档）
                                          
            ❦                              ← 墨蓝小花饰
                                          
他坐在被雨打湿的茶馆门口...                  ← 章首段：全段不下沉
那已是九年前的春天...                        ← 后续段落，缩进 2em
```

要点：
1. 章号与章名 **inline 同一行**，中点 ` · ` 分隔
2. 字号 / 字距按 §5.5 长度档位自动选择
3. 长章名超过 25 字 → 自动降级到 `title-xs`（1.1em）
4. **首字下沉全关**（章名长度不齐，下沉与正文边界不齐很难看）

### literary 模式（短章名场景，opt-in）

```
[ 上方留白 ~25vh ]

         CHAPTER ONE              ← stone 色，small-caps 间距 0.25em，0.7em
   
         灯  塔                   ← serif 500，2.4em，字距 0.4em（title-l 档）
   
            ❦                     ← 墨蓝小花饰
   
   T he morning began...          ← 章首段：首字下沉 3.4em 墨蓝（仅英文）
   he sea was calm that day...    ← 后续段落，缩进 2em
```

要点（与原计划一致）：
1. 章号上方独立一行，small-caps 字距
2. 字号 2.4em，字距 0.4em（短题表演）
3. 首字下沉**只在英文开**

### 共享要点（两种模式）

1. **去掉墨蓝左边栏** — 那是 Kami long-doc 语法
2. **标题与正文之间放 ❦**，不用 `<hr>`
3. **章首第一段不缩进**；后续段落首行缩进 2em
4. **章首上方留白 ~25vh**

---

## 5. 正文排版决策

| 元素 | 决定 | 与现状的差异 |
|---|---|---|
| 段落 | 中文首行缩进 2em，英文 1.5em，**段间距 0** | 现行 `margin-bottom: 0.85em` + 无缩进，是博客排版 |
| 行高 | webnovel 1.65 / literary 1.55 | 网文段密，需更宽行高 |
| 对齐 | `text-align: justify` + `hyphens: auto` + `widows: 2; orphans: 2` | 防西文 river 与孤行 |
| 字体特性 | `font-feature-settings: "kern" 1, "liga" 1, "onum" 1` | onum = oldstyle 数字，更书卷气 |
| 引用 `<blockquote>` | 去左边栏，改「双侧 4em 缩进 + olive 色 + 上下 1em 空行」 | 去除编辑感，回归书卷气 |
| 场景切换 | Markdown 中三空行 → 居中 ❦ | 当前完全不处理 |
| `<hr>` | 渲染为居中 ❦ 而非横线 | 一致性 |
| 章首/引用后/分隔后第一段 | `text-indent: 0` 例外规则 | 西文与中文小说传统一致 |
| CJK 避头尾 | `line-break: strict; word-break: keep-all;` | 行首禁 `）」』。，；！？`，行末禁 `（「『` |

---

## 5.5. 章节标题长度自适应（共享基础设施）

> 网文章号 + 章名总长度变化极大（4 字到 30+ 字），固定字号 / 字距必然在某些边界爆炸。本节是 webnovel / literary 两种模式共享的「字号 / 字距感知层」。

### 字号 / 字距 4 档

生成期检测「章号 + 章名总字符数」，自动选 class：

| 总字符数 | 例子 | class | webnovel 字号 | literary 字号 | 字距（webnovel / literary）| 行高 |
|---|---|---|---|---|---|---|
| ≤ 8 | 第一章 灯塔 | `title-l` | 1.6em | 2.4em | 0.1em / 0.4em | 1.20 / 1.15 |
| 9–15 | 第十二章 灯塔的守夜人 | `title-m` | 1.4em | 1.8em | 0.05em / 0.2em | 1.25 / 1.20 |
| 16–25 | 第五百二十五章 重逢于雨夜的破败茶馆 | `title-s` | 1.2em | 1.4em | 0 / 0.05em | 1.35 / 1.30 |
| > 25 | 第一千两百零三章 在那个再也回不去的春天里 | `title-xs` | 1.1em | 1.15em | 0 / 0 | 1.45 / 1.40 |

### 章号 2 档（独立处理，两模式共享）

| 章号字数 | 例子 | class | 字距 | 字号 |
|---|---|---|---|---|
| ≤ 4 | 第一章 / Chapter 1 | `num-short` | 0.25em（small-caps 风）| 0.7em |
| > 4 | 第五百二十五章 | `num-long` | **0.1em**（不再戏剧化）| 0.7em |

「第五百二十五章」字距 0.25em 会撑成 ~150px 宽，看着像图表标题——必须收紧。

### 章号位置自动切换（webnovel 模式）

webnovel 模式下，**当 `title-s` / `title-xs` 触发时，章号位置自动从 above 切到 inline**。

理由：长章名再加一个上方独立章号 = 三行视觉块，章首过厚。inline 反而干净：

```
第五百二十五章 · 重逢于雨夜的破败茶馆
              ❦
```

可手动覆盖：`--chapter-num-position {above|inline|hidden}`

### 工程实现

```python
def chapter_title_class(num_text: str, title_text: str) -> str:
    """根据章号 + 章名总字符数返回字号档 class。"""
    total = len(num_text) + len(title_text)
    if total <= 8:   return "title-l"
    if total <= 15:  return "title-m"
    if total <= 25:  return "title-s"
    return "title-xs"

def chapter_num_class(num_text: str) -> str:
    """章号字距档：4 字以内开字距戏剧化，超过收紧。"""
    return "num-long" if len(num_text) > 4 else "num-short"

def auto_num_position(num_text: str, title_text: str, mode: str) -> str:
    """webnovel 模式下，长章名自动切 inline。"""
    if mode == "webnovel" and len(num_text) + len(title_text) > 15:
        return "inline"
    return "above"
```

CSS（按模式 × 长度组合）：

```css
/* webnovel 模式（默认）字号档 */
body.mode-webnovel .chapter-title.title-l  { font-size: 1.6em; letter-spacing: 0.1em;  line-height: 1.20; }
body.mode-webnovel .chapter-title.title-m  { font-size: 1.4em; letter-spacing: 0.05em; line-height: 1.25; }
body.mode-webnovel .chapter-title.title-s  { font-size: 1.2em; letter-spacing: 0;      line-height: 1.35; }
body.mode-webnovel .chapter-title.title-xs { font-size: 1.1em; letter-spacing: 0;      line-height: 1.45; }

/* literary 模式 字号档 */
body.mode-literary .chapter-title.title-l  { font-size: 2.4em;  letter-spacing: 0.4em;  line-height: 1.15; }
body.mode-literary .chapter-title.title-m  { font-size: 1.8em;  letter-spacing: 0.2em;  line-height: 1.20; }
body.mode-literary .chapter-title.title-s  { font-size: 1.4em;  letter-spacing: 0.05em; line-height: 1.30; }
body.mode-literary .chapter-title.title-xs { font-size: 1.15em; letter-spacing: 0;      line-height: 1.40; }

/* 章号字距档（两模式共享） */
.chapter-num.num-short { letter-spacing: 0.25em; font-size: 0.7em; color: var(--stone); }
.chapter-num.num-long  { letter-spacing: 0.1em;  font-size: 0.7em; color: var(--stone); }

/* 章名换行兜底 */
.chapter-title {
    text-wrap: balance;          /* 让多行字数大致相等（Apple Books / Edge 支持，其他降级）*/
    word-wrap: break-word;
    overflow-wrap: break-word;
    font-weight: 500;
    color: var(--text);
}
```

### 三个验收 case

```
[case 1] 短：第一章 灯塔
  → title-l, num-short, above
  → webnovel: 1.6em / 0.1em / 章号上方
  → literary: 2.4em / 0.4em / 章号上方

[case 2] 中：第十二章 灯塔的守夜人
  → title-m, num-short, above
  → webnovel: 1.4em / 0.05em / 章号上方
  → literary: 1.8em / 0.2em / 章号上方

[case 3] 长（网文典型）：第五百二十五章 重逢于雨夜的破败茶馆
  → title-s, num-long, **inline**（webnovel 自动切）
  → webnovel: 1.2em / 0 / 章号 inline 中点分隔
  → literary: 1.4em / 0.05em / 章号上方
```

---

## 6. 强调系统：三种语义，三种视觉

**Kami 文学版的关键设计——绝不让强调「全部用同一种方式」。**

| 语义 | HTML 标记 | 中文渲染 | 英文渲染 |
|---|---|---|---|
| 加重（重要概念） | `<strong>` | 墨蓝 `var(--ink)` + 字重 500 | 墨蓝 + 字重 500 |
| 内心独白 / 外语 / 书名 | `<em>` | 着重号（旁点 `text-emphasis: dot`）| 真斜体 (Charter italic) |
| 引文出处 | `<cite>` | small-caps 间距 + olive 色 | small-caps + olive |

**绝不出现**：合成粗体（字重 ≥ 600）、中文合成斜体、变红、加粗 + 变色叠加。

### 着重号兜底

```css
em { font-style: normal; color: inherit; }
html[lang^="en"] em, html[lang^="en"] i { font-style: italic; }
html[lang^="zh"] em, html[lang^="zh"] i {
    text-emphasis: dot;
    text-emphasis-position: under right;
    -webkit-text-emphasis: dot;
    -webkit-text-emphasis-position: under right;
}
/* 旧 Kindle / 不支持 text-emphasis 的阅读器降级到墨蓝 + 字重 500 */
@supports not (text-emphasis: dot) {
    html[lang^="zh"] em { color: var(--ink); font-weight: 500; }
}
```

---

## 7. 封面重做

### 现状问题

`gen_cover_svg.py` 的三种 layout 全废：
- `minimal` (geometric_blocks) — 几何色块
- `classic` (horizontal_lines) — 横线
- `modern` (diagonal_accent) — 对角形

**对小说全是噪音。** 读者期待的是字体本身的力量。

### 新增 `literary` layout（小说默认，两模式共享）

```
┌─────────────────────────────────┐
│                                 │
│                                 │
│            ─────                │  ← 墨蓝细线 1.5pt，宽 25%
│                                 │
│         灯  塔                  │  ← 标题，180px，字距 0.4em (中文)
│                                 │
│            ─────                │  ← 更细线 1pt，宽 18%
│                                 │
│     一座岛、一封信、九个夜晚      │  ← 副标题，44px，olive
│                                 │
│                                 │
│            张  三                │  ← 作者，48px，stone，字距 0.3em
│                                 │
└─────────────────────────────────┘
```

**零几何形状**，所有「设计」来自字距、留白、双线。

封面**不响应双光照色契约**——封面始终是 Kami Light（羊皮纸 + 墨蓝），因为封面是「书的物质封面」，不是「正文的可读环境」。

### 网文封面：长书名兜底

网文书名也可能很长（「我开局获得了一座灵脉山」13 字），封面字号同样需自适应：

| 书名字数 | 字号 | 字距 |
|---|---|---|
| ≤ 4 | 220px | 0.4em |
| 5–8 | 180px | 0.3em |
| 9–14 | 140px | 0.15em |
| ≥ 15 | 110px | 0.05em |

### `kami-novel` 主题（小说默认）

```python
THEMES["kami-novel"] = {
    "keywords": ["小说", "novel", "fiction", "长篇", "短篇", "故事", "story",
                  "网文", "连载", "仙侠", "修真", "玄幻", "都市", "穿越", "重生"],
    "primary": "#f5f4ed",
    "secondary": "#ece9d8",
    "accent": "#1B365D",
    "text": "#141413",
    "subtitle_text": "#504e49",
    "is_light": True,
    "default_layout": "literary",
}
```

### 关键词路由调整

- 上述网文 / 小说关键词 → `kami-novel` (浅色 + literary layout)
- `传记 / 历史 / 哲学 / 思想 / 散文 / 诗歌` → 保留 `literature` (dark)

---

## 8. 字体策略：分层降级

EPUB 字体的真相：阅读器（特别是微信读书、Kindle）会强制替换字体。所以策略是分层降级 + 嵌入关键字体。

```
首选（嵌入 EPUB）：
  中文: TsangerJinKai02 W04（~6MB，从 ../Kami/assets/fonts/ 复用）
  英文: Charter（~200KB，开源，可嵌入；macOS 系统已有但其他平台没有）

次选（系统）：
  Source Han Serif SC / Noto Serif CJK SC / Songti SC / Georgia

末选: serif

全局开启:
  font-feature-settings: "kern" 1, "liga" 1, "onum" 1;
  text-rendering: optimizeLegibility;
```

**注意**：Tsanger 商用需授权（见 tsanger.cn）。生成器加 `--embed-tsanger` 开关，**默认关闭**，README 写清授权要求。Charter 是 IBM 1987 释出的开源字体，可直接嵌入无授权问题。

---

## 9. Anti-patterns（写进 CSS 注释）

明确禁忌，避免后续维护时漂移：

- 不用任何 box-shadow / text-shadow
- 不用任何渐变（封面顶底极淡羊皮纸渐变除外）
- 不用第二色相（任何红 / 黄 / 橙 / 绿 / 紫 / 青 / 粉都禁，只有羊皮纸 + 墨蓝 + 暖灰；暗色版同样无第二色相）
- 不用合成粗体（字重 ≥ 600）/ 中文合成斜体
- 不用左边栏 / 方框装饰章节标题（那是 Kami long-doc 的语法，不是文学体）
- 不用斑马纹 / 条纹 / 任何「网页感」装饰
- 不用 emoji、不用 icon font（仅一个 ❦ 例外）
- EPUB 里完全去除 sans-serif（包括 metadata、caption）
- **不写死任何 hex 色值**——必须通过 `var(--ink)` 等变量引用（除封面 SVG 印刷品场景）
- **不让阅读器决定背景**——`body { background: var(--paper) }` 永远存在

---

## 10. 路线图与优先级

| 优先级 | 改动 | 文件 | 投入 |
|---|---|---|---|
| **P0** | 双光照色契约（Kami Light + Kami Dark）+ CSS variables 化 ← §2.5 | `gen_epub_enhanced.py` (CSS) | ~1h |
| **P0** | `--mode {webnovel\|literary}` 双模式开关 + body class 注入 ← §3.5 | `gen_epub_enhanced.py` | ~30min |
| **P0** | 章节标题 4 档自适应 + 章号 2 档 + 自动 inline 切换 ← §5.5 | `gen_epub_enhanced.py` | ~1.5h |
| **P0** | 段首缩进 + 章首结构（双模式）+ 着重号 + ❦ 分隔 + 避头尾 | `gen_epub_enhanced.py` (CSS) | ~1h |
| **P0** | `literary` layout + `kami-novel` 主题 + 网文关键词路由 + 封面书名长度档 | `gen_cover_svg.py` | ~1.5h |
| **P0** | 输入合约解析（frontmatter 读取 + 卷分组三种识别 + kind 字段 + 章号/章名拆分）← §3.6/§3.7/§3.8 | `gen_epub_enhanced.py` | ~1.5h |
| **P0** | 卷封页生成（spine 独立页 + NCX 嵌套 TOC）← §3.7 | `gen_epub_enhanced.py` | ~1h |
| **P0** | 网文特殊元素：楔子/番外 TOC 区 + 场景切换符多形式识别归一 + 未完待续 + 作者按 ← §3.8 | `gen_epub_enhanced.py` | ~1h |
| **P0** | styled TOC 目录页（serif 章号 + stone 章名 + 卷分组 + 楔子/番外区域）← §3.7/§3.8 | `gen_epub_enhanced.py` | ~1h |
| **P0** | 章末 ❦ 花饰（含三空行/`<hr>`/场景分隔符多形式识别触发）← §5 + §3.8 | `gen_epub_enhanced.py` | ~45min |
| **P1** | 字体特性 + `<strong>` 锁 500 + `<em>` 中英分流 + 着重号兜底 | `gen_epub_enhanced.py` | ~30min |
| **P1** | 标点归一（`...→……`、`--→——`、中英空格、半全角清理）← §3.6 | `gen_epub_enhanced.py` | ~45min |
| **P1** | Charter 字体嵌入（开源，无授权） | `gen_epub_enhanced.py` | ~30min |
| **P1** | 嵌入 TsangerJinKai（待商用授权确认） | `gen_epub_enhanced.py` | ~30min |
| **P1** | 数字单位不可拆 + alt text 保留 + EPUB metadata 完整化 | `gen_epub_enhanced.py` | ~45min |
| **P1** | 章号位置 `--chapter-num-position {above\|inline\|hidden}` 参数 | `gen_epub_enhanced.py` | ~15min |
| **P2** | `<cite>` 独立样式 + 引用块重做 | `gen_epub_enhanced.py` | ~1h |
| **P2** | dropcap 用 `<span>` 包装（跨阅读器稳定，仅 literary 模式英文）| `gen_epub_enhanced.py` | ~30min |
| **P2** | `--dry-run` 单页 HTML 预览 + slug 化章节文件名 + epubcheck 自动校验 | `gen_epub_enhanced.py` | ~1.5h |

### 反向修订（明确覆盖之前版本）

- ~~原 P0「暗色模式 fallback」~~ → 升级为「双光照色契约」（§2.5），仍 P0
- ~~原 P2「CSS variables 化」~~ → 并入 P0 双光照实现，不再独立条目
- ~~原 §2 设计契约「正文不设 body 背景」~~ → 改为强制背景 + var(--paper)
- ~~原 §4 章首页单一 literary 设计~~ → 改为 webnovel（默认）+ literary（opt-in）双方案
- ~~原 P1「styled TOC 目录页」~~ → 升为 P0，封面后的第一印象不能接受默认工具式 TOC
- ~~原 P2「章末花饰 + 三空行触发场景 ❦」~~ → 拆为 P0 章末 ❦（独立花饰）与原 P2「literary 模式强制换页」
- ~~原 P2「三空行触发场景 ❦」~~ → 并入 §3.8 场景切换符多形式识别（P0）

### 工时汇总

- **P0 全做 ≈ 10.25h**：「完整的小说出品类体验，卷 + 特殊元素 + 精致 TOC + 花饰」
- **P0 + P1 全做 ≈ 12.5h**：「再加标点归一和字体优化」
- **全部完成 ≈ 17h**

---

## 11. 验收标准

P0 完成后，**用真实网文（章名长度跨度大，建议至少 50 章）** 跑测试，分别用：

1. 现状版本
2. P0 完成版本（webnovel 模式，默认）
3. P0 完成版本（literary 模式，对照组）

在 **3 个阅读器（Apple Books / 微信读书 / Calibre） × 2 种光照（浅 / 暗） = 6 种场景** 下截屏对比。

### 关键观察点

- **章首页：长章名（「第五百二十五章 重逢于雨夜的破败茶馆」）是否优雅落地，无溢出 / 无字符踩字符**
- **章首页：短章名（「第一章 灯塔」）在两种模式下区分明显（webnovel 1.6em vs literary 2.4em）**
- **暗色模式：背景是暖墨棕 `#1c1a17` 而非纯黑**
- **暗色模式：墨蓝提亮版 `#6B95C9` 清晰可见，✦/❦ 没消失在暗背景里**
- 段首缩进是否生效（最容易翻车）
- 着重号在中文阅读器是否正确渲染
- 封面在缩略图模式下是否依然「书感」充足
- 网文长书名在封面是否自适应字号

### 失败标准（出现即返工）

- 任何场景下出现纯白 / 纯黑背景
- 章名换行后字符相互踩贴
- 暗色下墨蓝不可见
- 微信读书覆盖了我们的字距设置导致章名挤成一团

---

## 12. 不在本计划范围内

避免范围蔓延，以下**明确不做**：

- 修改 `gen_epub.py`（基础版保持现状）
- 修改 `gen_cover_html.py`（HTML 封面路径作为兼容选项保留）
- 多语言切换（日文虽在 Kami 母体支持，但本 EPUB 路径不主动优化）
- 打字机 / 手写 / Markdown source 风格变体
- 任何前后附件页面（半书名 / 书名 / 献辞 / 题记 / 版权 / 封底）
- TXT/HTML 具体站点的清洗逻辑——那是外部准备层的责任
- 正文字数据质量（错别字、段落遗漏、编码猜测）
- ~~暗色模式 fallback~~ → 已升级为正式 §2.5 双光照契约
- ~~CSS variables 化~~ → 已并入 P0 双光照实现

---

## 附录 A：参考资料

- Kami 设计规范：`/Users/graytian/dev/projects/gray/Kami/references/design.md`
- Kami 速查表：`/Users/graytian/dev/projects/gray/Kami/CHEATSHEET.md`
- Kami 写作规范：`/Users/graytian/dev/projects/gray/Kami/references/writing.md`
- 输入合约：`references/input-contract.md`（外部准备层与生成器之间的文件格式约定）
- 现行 EPUB CSS：`scripts/gen_epub_enhanced.py` (`CHAPTER_CSS` 常量)
- 现行封面 SVG：`scripts/gen_cover_svg.py` (`THEMES` / `LAYOUTS` 常量)

## 附录 B：决策记录

| 日期 | 决定 | 理由 |
|---|---|---|
| 2026-05-03 | 强制 body 背景 + 双光照色契约 | Kami「永不纯白」必须在所有光照下成立 |
| 2026-05-03 | webnovel 设为默认模式 | 本 fork 主要用途是网文，长章名是大概率场景 |
| 2026-05-03 | 章节标题 4 档自适应 | 「第五百二十五章 重逢于雨夜的破败茶馆」需要优雅落地 |
| 2026-05-03 | 砍掉前后附件（半书名/版权页等）| 用户明确要求「除封面外不多余生成」 |
| 2026-05-03 | 预处理分工边界：外部管清洗，排版管归一 | 站特定规则发散，排版层猜不中会破坏数据 |
| 2026-05-03 | 输入合约以 YAML frontmatter 为首选约定 | frontmatter 比文件夹/文件名前缀更显式且可校验 |
| 2026-05-03 | 卷封页 + NCX 嵌套 TOC | 长篇网文 500+ 章必须做卷分组，否则 TOC 体验灾难 |
| 2026-05-03 | styled TOC 从 P1 升 P0 | 封面后的第一印象不能是工具式 TOC |
| 2026-05-03 | 章末 ❦ 花饰从 P2 升 P0 | 廉价但有效的"翻完一章"信号 |
| 2026-05-03 | 场景切换符归一为 ❦ | `---` / `***` / 连续空行等全部走同一渲染路径 |
