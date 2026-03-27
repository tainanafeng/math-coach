# 匯入自製函式
from config.users_account import TEST_USERS
from db.safe_crud import load_messages
from chat_flow import process_user_turn
from ui_design.ui_style import apply_global_style, apply_main_page_style
from ui_design.ui_script import inject_scroll_control
from ui_design.ui_render import render_all, render_one
from ui_design.ui_login import login_page

import streamlit as st
import time


# 設置頁面標題, icon
st.set_page_config(page_title="AI MathTA", layout="wide", initial_sidebar_state="expanded")

# 應用全局 css
apply_global_style()

# ---- 主對話介面 ----
def main_page():
    # 應用主介面 css
    apply_main_page_style()

    # 防止使用者重複送出（非常重要）
    if "is_generating" not in st.session_state:
        st.session_state["is_generating"] = False

    # 判斷是否需要執行「一次性」置底捲動
    do_scroll = "true" if st.session_state.get("just_logged_in", False) else "false"
    if st.session_state.get("just_logged_in"):
        st.session_state["just_logged_in"] = False # 執行後立即重設

    # 注入 JavaScript 攔截器： 1. 攔截自動跳轉 2. 處理一次性置底
    inject_scroll_control(do_scroll)

    # 側邊欄與其他 UI
    with st.sidebar:
        st.markdown("<div style='text-align: center; padding: 15px; background: #FFFFFF; border-radius: 20px; margin-bottom: 20px; border: 2px solid #E5D3B3;'><span style='font-size: 40px;'>🦊</span><p style='margin: 0; font-size: 18px; color: #5D4037; font-weight: bold;'>Foxie Guide</p></div>", unsafe_allow_html=True)
        st.markdown(f"### 👋 哈囉，{st.session_state['user']}！")

        mode_label = st.radio("🎨 學習風格選擇", ["🍰 循序引導", "💡 思考解謎"])
        # 預設為引導模式
        st.session_state["mode"] = "guided" if "引導" in mode_label else "socratic"
        # 顯示目前模式
        if st.session_state["mode"] == "guided":
            st.success("Foxie 會詳細解釋步驟！")
        else:
            st.warning("Foxie 會引導你自己想！")
        
        # 使用者上傳文檔
        st.caption("📎 選填：上傳 PDF 作為題目／參考")
        pdf = st.file_uploader("PDF", type=["pdf"], key=f"pdf_ref_{st.session_state['user']}", label_visibility="collapsed")
        
        # 登出按鈕
        if st.button("下次再見 👋", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    st.markdown("<h3 style='color: #5D4037;'>📝 學習思考紀錄</h3>", unsafe_allow_html=True)

    # 為不同 user 建立不同的聊天 key
    username = st.session_state["user"]
    msg_key = f"messages_{username}"

    # 初始化該使用者的聊天紀錄
    if msg_key not in st.session_state:
        st.session_state[msg_key] = load_messages(username)   # 每則結構：{"role": "user/assistant", "content": "..."}

    # render 聊天紀錄
    chat_container = st.container()
    with chat_container:
        render_all(st.session_state[msg_key])

    # 使用內建 chat_input
    prompt = st.chat_input("在這裡寫下你的疑問... ✍️", key=f"chat_input_{username}")
    # 防呆：避免空字串 + 防連點
    if prompt and prompt.strip() and not st.session_state["is_generating"]:
        # 上鎖
        st.session_state["is_generating"] = True

        # 對話流程控制
        process_user_turn(
            username=username,
            user_input=prompt.strip(),
            pdf=pdf,
            mode=st.session_state["mode"],
            msg_list=st.session_state[msg_key],
            chat_container=chat_container
        )

        # 解鎖
        st.session_state["is_generating"] = False



# ======= 程式入口 ======= #
if "user" not in st.session_state or st.session_state["user"] is None:    # session_state 是「每個瀏覽器分頁tab session」獨立，不是「每個帳號」獨立，只是一塊存在於記憶體的「暫存資料」，只是 UI cache，不是後端 session
    login_page(TEST_USERS)
else:
    main_page()