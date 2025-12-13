# 模型輸出後製
import re

def convert_display_math(text: str) -> str:
    """
    將 LaTeX display math:
        \[ ... \]
    轉成 Markdown 支援的：
        $$ ... $$

    使用 DOTALL 因為 display math 通常跨行。
    """
    return re.sub(
        r'\\\[(.*?)\\\]',
        r'$$\1$$',
        text,
        flags=re.DOTALL
    )

def convert_inline_math(text: str) -> str:
    """
    將 inline math:
        \( ... \)
    轉成：
        $ ... $

    不允許跨行（符合 inline 規則）。
    """
    return re.sub(
        r'\\\((.*?)\\\)',
        r'$\1$',
        text
    )

def normalize_latex(text: str) -> str:
    """
    統一處理 AI 模型輸出的 LaTeX 格式：
    1. \[...\] → $$...$$
    2. \(...\) → $...$
    3. 清理前後空白
    """
    text = convert_display_math(text)
    text = convert_inline_math(text)

    return text.strip()

def ensure_math_block_spacing(text: str) -> str:
    """
    避免 $$ ... $$ 與前後文字黏在一起，確保渲染正確。
    若需要可以在 Markdown 渲染前呼叫。
    """
    # 在 $$ 前後補空行
    text = re.sub(r'\$\$(.*?)\$\$', r'\n$$\1$$\n', text, flags=re.DOTALL)
    return text



def format_latex(text: str) -> str:
    """
    對外提供的統一介面。
    Streamlit 主程式呼叫這個即可。

    適合你的需求：
    - 模型輸出後修正 LaTeX 標記
    - 避免渲染錯誤
    - 保持 Markdown 組織不被破壞
    """
    text = normalize_latex(text)
    text = ensure_math_block_spacing(text)
    return text
