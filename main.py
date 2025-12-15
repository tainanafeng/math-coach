# 匯入自製函式
from chat_history.chat_history import build_chat_history
from rag.context_rag import rag_context_type_select_chain
from rag.teaching_rag import teaching_example_function
from prompts.prompt_builder import build_full_prompt
from agent.agent_executor import build_agent_executor
from utils.latex_postprocess import format_latex
from db.safe_crud import load_messages, save_message
from config.users_account import TEST_USERS
from utils.error_handler import safe_call, format_error_msg
from utils.input_builder import build_user_input

from langchain.agents import AgentExecutor
import streamlit as st
import time


# ===== 建立 Agent (初始化一次) ===== #
agent_executor = build_agent_executor()


# 功能: 呼叫模型
def ask_ai(username: str, input_msg: str):

    """
    - 組合 chat_history + 摘要
    - 決定 context_type
    - 提供教學範例
    - 組合 system_prompt
    - 呼叫 agent_executor
    - 讀寫資料庫
    """

    # 取得完整 chat_history (含摘要)
    input_chat_history, err = safe_call(build_chat_history, username)
    if err:
        return {"answer": format_error_msg(err)}

    # RAG 問題類型判斷
    context_type, err = safe_call(
        rag_context_type_select_chain.invoke,
        {"input": input_msg, "chat_history": input_chat_history}
    )
    if err:
        return {"answer": format_error_msg(err)}
    print(context_type)

    # RAG 獲得教學範例
    teaching_example, err = safe_call(
        teaching_example_function, input_msg, context_type
    )
    if err:
        return {"answer": format_error_msg(err)}

    # 組合成完整 Prompt
    system_prompt, err = safe_call(
        build_full_prompt, context_type, teaching_example
    )
    if err:
        return {"answer": format_error_msg(err)}

    # 呼叫 Agent   
    result, err = safe_call(
        agent_executor.invoke,
        {"input": input_msg, "system_prompt": system_prompt, "chat_history": input_chat_history}
    )
    if err:
        return {"answer": format_error_msg(err)}

    # Latex 修正
    result["output"] = format_latex(result["output"])   

    # 本輪對話存入 SQLite
    save_message(username, "user", input_msg)
    save_message(username, "assistant", result["output"])

    return {
        "answer": result["output"],
        "context_type": context_type,
        "teaching_example": teaching_example,
        "history_used": input_chat_history
    }




# ========== 以下為 streamlit ========== #
st.set_page_config(page_title="AI數學助教")



# 初始化登入狀態
if "user" not in st.session_state:
    st.session_state["user"] = None


# ======= 登入畫面 ======= #
def login_page():
    st.title("AI_MathTA Login")

    username = st.text_input("帳號：")
    password = st.text_input("密碼：", type="password")

    if st.button("登入",use_container_width=True):
        if username in TEST_USERS and TEST_USERS[username] == password:
            st.session_state["user"] = username
            st.success("登入成功！")
            st.rerun()    # 重新執行 → 進入主畫面
        else:
            st.error("帳號或密碼錯誤")



# ======= 主畫面 ======= #
def main_page():
    st.title(f"AI_MathTA - {st.session_state['user']}")

    # 為不同 user 建立不同的聊天 key
    username = st.session_state["user"]
    msg_key = f"messages_{username}"


    # 初始化該使用者的聊天紀錄
    if msg_key not in st.session_state:
        st.session_state[msg_key] = load_messages(username)    # 每則結構：{"role": "user/assistant", "content": "..."}
    # 避免雙重呼叫 & 聊天紀錄亂序
    if "is_generating" not in st.session_state:
        st.session_state["is_generating"] = False


    # 用 container 來顯示歷史訊息（這個容器不會被清掉）
    chat_container = st.container()

    # 載入聊天紀錄
    with chat_container:
        for msg in st.session_state[msg_key]:
            if msg["role"] == "user":
                st.code(msg['content'])
            else:
                st.markdown(msg['content'])
                st.markdown('***')



    # 使用 form 接收輸入
    with st.form("form", clear_on_submit=True):

        text = st.text_area("🧑‍🎓 You :", placeholder="請提出問題")

        # 使用者上傳文檔
        uploaded_file = st.file_uploader("上傳 Word / PDF 題目（選填）",type=["pdf", "docx", "doc"])

        submitted = st.form_submit_button("送出", use_container_width=True)

        if submitted and text and not st.session_state["is_generating"]:

            st.session_state["is_generating"] = True

            # 存使用者訊息到 session_state
            st.session_state[msg_key].append({"role": "user", "content": text})


            with chat_container:
                # 立刻顯示使用者輸入訊息
                st.code(text)
                ai_stream_placeholder = st.empty()

                # 呼叫 AI
                with st.spinner("請耐心等待 :hourglass:"):
                    full_input = build_user_input(text, uploaded_file)
                    ai_reply = ask_ai(username, full_input)["answer"]

            # 存 AI 回覆到 session_state
            st.session_state[msg_key].append({"role": "assistant", "content": ai_reply})

            # fake streaming
            streamed_text = ""
            for ch in ai_reply:
                streamed_text += ch
                ai_stream_placeholder.markdown(streamed_text)
                time.sleep(0.02)

            with chat_container:
                st.markdown('***')

            st.session_state["is_generating"] = False



    # 自動捲到底部  目前只有登入主頁面才生效
    import streamlit.components.v1 as components
    components.html(
        """
        <script>
            const parentDoc = parent.document;

            // 尋找畫面中所有可能可捲動的 DOM
            const nodes = parentDoc.querySelectorAll("*");

            nodes.forEach(n => {
                if (n.scrollHeight > n.clientHeight + 10) {
                    n.scrollTo({ top: n.scrollHeight, behavior: "smooth" });
                }
            });
        </script>
        """,
        height=0,
    )



    # ======「登出」====== #
    if st.button("登出", use_container_width=True):
        # 清除登入狀態
        st.session_state["user"] = None

        # 清除聊天紀錄
        st.session_state.pop(msg_key, None)

        # 回到登入畫面
        st.rerun()



# ======= 程式入口 ======= #
if st.session_state["user"] is None:    # session_state 是「每個瀏覽器分頁tab session」獨立，不是「每個帳號」獨立，只是一塊存在於記憶體的「暫存資料」，只是 UI cache，不是後端 session
    login_page()
else:
    main_page()