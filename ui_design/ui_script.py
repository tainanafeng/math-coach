# JS集中管理
import streamlit.components.v1 as components

def inject_scroll_control(do_scroll: str):
    # 注入 JavaScript 攔截器： 1. 攔截自動跳轉 2. 處理一次性置底
    components.html(
        f"""
        <script>
        const pWin = window.parent;
        const container = pWin.document.querySelector('.block-container');
        
        // 1. 攔截自動跳轉 (防止 AI 輸出時亂跳) 封印原生的 scrollIntoView 函數
        if (pWin && !pWin.isScrollLockedFoxie) {{
            pWin.HTMLElement.prototype.scrollIntoView = function() {{}};
            pWin.HTMLElement.prototype.scrollIntoViewIfNeeded = function() {{}};
            pWin.isScrollLockedFoxie = true;
        }}

        // 2. 如果是剛登入，執行一次強制置底
        if ({do_scroll} && container) {{
            setTimeout(() => {{
                container.scrollTop = container.scrollHeight;
            }}, 300);
        }}
        </script>
        """,
        height=0, width=0
    )