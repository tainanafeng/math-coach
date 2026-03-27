from ui_design.ui_style import apply_login_style
import streamlit as st

# 登入頁面
def login_page(TEST_USERS):
    # 套用 css
    apply_login_style()

    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        # 登入卡片增加毛玻璃與陰影
        st.markdown("""
        <div class='glass-card'>
            <h1 style='font-size: 80px; margin: 0;'>🦊</h1>
            <h2 style='color: #5D4037; margin-bottom: 5px;'>Foxie MathTA</h2>
            <p style='color: #8D6E63; font-size: 1.1em;'>讓 AI 陪你拆解每一道數學思考 ✨</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        
        # 輸入框容器
        with st.container():
            u = st.text_input("📝 帳號", placeholder="輸入您的學號或帳號")
            p = st.text_input("🔑 密碼", type="password", placeholder="輸入您的密碼")
            if st.button("開啟學習之旅 🤎", use_container_width=True):
                if u in TEST_USERS and TEST_USERS[u] == p:
                    st.session_state["user"] = u
                    st.session_state["just_logged_in"] = True # 標記剛登入
                    st.rerun()
                else:
                    st.error("哎呀！帳號或密碼不小心寫錯了 🖍️")