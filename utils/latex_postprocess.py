#此版本沒有重大bug，存在一些隨機影響較小的bug

# 模型輸出後製
import re

# ========================
# 1. 轉換 LaTeX 標記
# ========================

def convert_display_math(text: str) -> str:
    """
    將 \\[ ... \\] 轉換為 $$ ... $$（區塊公式）

    為什麼要做：
    - 有些模型會輸出 \\[ \\]（LaTeX display math）
    - 但 Markdown / Streamlit 通常用 $$...$$

    範例:
    輸入:  \\[ x^2 + 1 \\]
    輸出:  $$x^2 + 1$$
    """
    return re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', text, flags=re.DOTALL)


def convert_inline_math(text: str) -> str:
    """
    將 \\( ... \\) 轉換為 $ ... $（行內公式）

    注意：
    - 不允許跨行（符合 inline math 規則）

    範例:
    輸入:  \\( x^2 \\)
    輸出:  $x^2$
    """
    return re.sub(r'\\\(([^\n]*?)\\\)', r'$\1$', text)


# ========================
# 2. Unicode → LaTeX
# ========================

def replace_unicode_symbols(text: str) -> str:
    """
    將 Unicode 數學符號轉為 LaTeX

    為什麼要做：
    - 模型可能輸出 ∑ ∞ ∫ 等符號
    - 這些在 LaTeX 中應使用 \\sum \\infty \\int

    範例:
    輸入:  ∑ x + ∞
    輸出:  \\sum x + \\infty
    """
    replacements = {
        '∑': r'\\sum',
        '∞': r'\\infty',
        '∫': r'\\int',
        'Δ': r'\\Delta',
        'π': r'\\pi',
        '·': r'\\cdot',
        '×': r'\times',
        '÷': r'\div',
        '≤': r'\le',
        '≥': r'\ge',
        '≠': r'\neq',
        '≈': r'\approx',
        '→': r'\to',
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    return text


# ========================
# 3. 數學函數修正
# ========================

def fix_math_functions(text: str) -> str:
    """
    將 ln, sin, cos, tan, exp, log 等轉為 LaTeX 指令

    為什麼要做：
    - LaTeX 中函數需寫成 \\ln \\sin

    範例:
    輸入:  sin x + ln x
    輸出:  \\sin x + \\ln x
    """
    funcs = [
        'arcsin', 'arccos', 'arctan',
        'cot', 'sec', 'csc',
        'sqrt',
        'ln', 'log', 'exp',
        'sin', 'cos', 'tan',
        'min', 'max'
    ]

    # 長字串優先，避免局部命中造成干擾
    for f in funcs:
        text = re.sub(rf'(?<!\\)\b{f}\b', rf'\\{f}', text)

    return text


# ========================
# 4. 分數修正
# ========================

def fix_simple_fractions(text: str) -> str:
    """
    將 a/b 轉為 \\frac{a}{b}

    限制：
    - 只處理「簡單分數」（單一變數或數字）
    - 避免誤傷 (x+1)/y 這種複雜情況

    範例:
    輸入:  y/x
    輸出:  \\frac{y}{x}
    """
    return re.sub(
        r'(?<!\\frac\{)(?<!\\)\b([a-zA-Z0-9]+)\s*/\s*([a-zA-Z0-9]+)\b',
        r'\\frac{\1}{\2}',
        text
    )


# ========================
# 5. 切分「非數學區塊」
# ========================

def split_by_math_blocks(text: str):
    """
    將文字切成：
    - 數學區塊（$...$ 或 $$...$$）
    - 非數學區塊

    為什麼要做：
    - 後續只處理「非數學區塊」
    - 避免重複包裝

    回傳:
    list of (is_math, content)

    範例:
    輸入:  text $x^2$ text
    輸出:
    [
      (False, "text "),
      (True, "$x^2$"),
      (False, " text")
    ]
    """
    parts = re.split(r'(\$\$.*?\$\$|\$.*?\$)', text, flags=re.DOTALL)

    result = []
    for part in parts:
        if part.startswith('$'):
            result.append((True, part))
        else:
            result.append((False, part))

    return result


# ========================
# 6. 自動包裝 LaTeX（核心🔥）
# ========================

MATH_COMMANDS = [
    'arcsin', 'arccos', 'arctan',
    'cot', 'sec', 'csc',
    'frac', 'sqrt', 'sum', 'prod', 'int', 'lim',
    'ln', 'log', 'exp', 'sin', 'cos', 'tan',
    'min', 'max',
    'left', 'right', 'bigl', 'bigr', 'Bigl', 'Bigr'
]

# 已有數學區塊就不要再包
CJK_CHUNK_RE = re.compile(r'([\u4e00-\u9fff]+)')

# 只要命中這些特徵，就把整段非中文片段視為公式
# 這是 demo-safe 的保守規則：寧可多包一點，不要切碎公式
FORMULA_HINT_RE = re.compile(
    r'(\\[A-Za-z]+)|'      # LaTeX 指令
    r'([=^_])|'             # 結構符號
    r'(/)'                  # 分數
)


# ========================
# 判斷工具
# ========================

CJK_RE = re.compile(r'[\u4e00-\u9fff]')
# 修正：只允許 LaTeX 指令作為「數學起點」
MATH_START_RE = re.compile(r'(\\[A-Za-z]+)')
# 擴展允許符號
MATH_CHAR_RE = re.compile(r'[\\A-Za-z0-9=^_{}()\[\]+\-*/., ]')
STOP_RE = re.compile(r'[，。；：！？]')


def _expand_math_segment(text: str, start: int):
    """
    從數學起點開始，向右擴展完整公式

    終止條件：
    - 遇到中文
    - 遇到標點（，。；等）
    - 遇到非數學字符
    """
    i = start
    n = len(text)

    while i < n:
        ch = text[i]

        if CJK_RE.match(ch):
            break
        if STOP_RE.match(ch):
            break
        if not MATH_CHAR_RE.match(ch):
            break

        i += 1

    return i


# ========================
# 核心：數學片段 grouping
# ========================

def _wrap_math_in_text(text: str) -> str:
    """
    在純文字中找出數學片段並包裝

    範例:
    在 x>0 時，\frac{dy}{dx} = ...
    → 在 x>0 時，$\frac{dy}{dx} = ...$
    """
    i = 0
    n = len(text)
    result = []

    while i < n:
        # 找數學起點
        match = MATH_START_RE.search(text, i)

        if not match:
            result.append(text[i:])
            break

        start = match.start()

        # 先加入前面的普通文字
        result.append(text[i:start])

        # 向右擴展數學片段
        end = _expand_math_segment(text, start)
        segment = text[start:end].strip()

        # 避免包空字串
        if segment:
            result.append(f"${segment}$")
        else:
            result.append(text[start:end])

        i = end

    return ''.join(result)


# ========================
# 主包裝函式（取代舊版）
# ========================

def wrap_latex_math(text: str) -> str:
    """
    最終策略策略：
    - 中文永遠不會被包
    - 連續公式會整段包住
    - 已有 $...$ / $$...$$ 完全不動
    - 只在「純文字區塊」做 grouping
    - 不會破壞既有數學結構
    """
    blocks = re.split(r'(\$\$.*?\$\$|\$.*?\$)', text, flags=re.DOTALL)

    result = []

    for block in blocks:
        if not block:
            continue

        # 已有數學區塊
        if block.startswith('$'):
            result.append(block)
        else:
            result.append(_wrap_math_in_text(block))

    return ''.join(result)



# ========================
# 7. 區塊公式排版
# ========================

def normalize_block_math(text: str) -> str:
    """
    確保 $$ 區塊有正確換行

    為什麼要做：
    - 避免 $$ 與文字黏在一起導致渲染錯誤

    範例:
    輸入: text$$x^2$$text
    輸出: 自動加空行
    """
    def repl(match):
        content = match.group(1).strip()
        return f"\n\n$$\n{content}\n$$\n\n"

    return re.sub(r'\$\$(.*?)\$\$', repl, text, flags=re.DOTALL)


# ========================
# 8. 修復 $ 不平衡
# ========================

def fix_unbalanced_dollars(text: str) -> str:
    """
    若 $ 數量為奇數，補一個在最後

    為什麼要做：
    - 避免 Markdown / MathJax 渲染崩潰

    範例:
    輸入:  $x^2
    輸出:  $x^2$
    """
    if text.count('$') % 2 != 0:
        text += '$'

    return text


# ========================
# 9. 主流程
# ========================

def format_latex(text: str) -> str:
    """
    LaTeX 後處理總流程(Pipeline)

    ⚠ 順序非常重要：

    1. 轉換 LaTeX 標記
    2. Unicode → LaTeX
    3. 函數修正
    4. 分數修正
    5. 自動包裝 LaTeX
    6. 修復 $
    7. 區塊排版

    範例:
    輸入:
    d/dx = y/x + ∑x

    輸出:
    $$ \\frac{y}{x} $$
    $$ \\sum x $$
    """
    text = convert_display_math(text)
    text = convert_inline_math(text)

    text = replace_unicode_symbols(text)
    text = fix_math_functions(text)
    text = fix_simple_fractions(text)

    text = wrap_latex_math(text)

    text = fix_unbalanced_dollars(text)
    text = normalize_block_math(text)

    return text.strip()