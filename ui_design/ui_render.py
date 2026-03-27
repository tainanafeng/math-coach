import streamlit as st

# 只用於第一次載入頁面
def render_all(messages):
    for msg in messages:
        render_one(msg)

# 只 render 一則訊息
def render_one(msg):
    if msg["role"] == "user":
        # 使用者：保留氣泡(HTML沒問題)
        st.markdown(
            f'<div class="chat-row user-row"><div class="bubble user-bubble">🐣 {msg["content"]}</div></div>',
            unsafe_allow_html=True
        )
    else:
        # 建立左右留白，中間放內容
        left, center, right = st.columns([1, 7, 1])
        # AI：不用氣泡 → 改用 markdown        
        with center:
            st.markdown("🦊 **Foxie**")
            st.markdown(msg["content"]) # 正確渲染 LaTeX
            st.markdown('---')