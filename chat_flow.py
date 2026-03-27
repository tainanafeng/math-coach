from utils.input_builder import build_user_input
from application_chain import run_application_turn
from ui_design.ui_render import render_one

import streamlit as st
import time


# 處理對話流程
def process_user_turn(
    username: str,
    user_input: str,
    pdf,
    mode: str,
    msg_list: list,
    chat_container
):
    """
    處理一整個 user → AI 的對話流程

    包含：
    1. append user message
    2. render user
    3. 呼叫 LLM
    4. append AI message
    5. fake streaming render

    設計重點：
    - UI / 邏輯 解耦
    - 可插拔（未來可加 retry / logging / 真 streaming）
    """
    # 存使用者輸入到 session_state
    user_msg = {"role": "user", "content": user_input}
    msg_list.append(user_msg)    

    # 立即 render 使用者輸入
    with chat_container:
        render_one(user_msg)

    # 顯示 loading 呼叫 llm
    with st.spinner("Foxie 正在思考... 🍀"):
        try:
            full_input = build_user_input(user_input, pdf)
            result = run_application_turn(username, full_input, mode=mode)
            reply = result["answer"]
        except Exception as e:
            # 保底錯誤（防止整個 UI 爆掉）
            reply = f"⚠ 系統錯誤：{str(e)}"

    # 存 AI 回覆到 session_state
    ai_msg = {"role": "assistant", "content": reply}
    msg_list.append(ai_msg)

    # 只 render AI 回覆
    with chat_container:
        left, center, right = st.columns([1, 7, 1])
        with center:
            st.markdown("🦊 **Foxie**")

            # 建立 placeholder
            stream_placeholder = st.empty()
            streamed_text = ""

            # fake streaming(逐字輸出)
            for ch in reply:
                streamed_text += ch
                stream_placeholder.markdown(streamed_text)
                time.sleep(0.01)  # 可調整速度

            st.markdown('---')

    # return(為未來擴展預留)
    return {
        "user_msg": user_msg,
        "ai_msg": ai_msg,
        "raw_reply": reply
    }