"""
Application Layer:
- Defines one complete AI teaching turn
- UI-agnostic
"""

from chat_history.chat_history import build_chat_history
from task_type_select import task_type_select_chain
#from rag.teaching_rag import teaching_example_function
from prompts.prompt_builder import build_full_prompt
from agent.agent_executor import build_agent_executor
from utils.latex_postprocess import format_latex
from db.safe_crud import save_message
from utils.error_handler import safe_call, format_error_msg
from langchain_core.messages import SystemMessage, HumanMessage

import streamlit as st


# streamlit 每一次 UI 互動 = 整個 script 從上到下重新跑 每次 rerun，整支 Python 檔案都會重新執行一次
# 只有 cache 保留（跨 rerun）
# 同一個 Streamlit worker process 中，只建立一次
@st.cache_resource
def st_cache_agent_executor():
    return build_agent_executor()


def run_application_turn(username: str, user_input: str, mode: str) -> dict:
    """
    One complete AI teaching turn.
    一次 AI 教學回合

    """

    # 1. 取得完整 chat_history（含摘要）
    input_chat_history, err = safe_call(build_chat_history, username)
    if err:
        return {"answer": format_error_msg(err)}

    # 2. 任務分類
    task_type, err = safe_call(
        task_type_select_chain.invoke,
        {"input": user_input, "chat_history": input_chat_history}
    )
    if err:
        return {"answer": format_error_msg(err)}
    print(f"任務類型: {task_type}")

    # 3. 教學範例 RAG
    #teaching_example, err = safe_call(
    #    teaching_example_function,
    #    user_input,
    #    task_type
    #)
    #if err:
    #    return {"answer": format_error_msg(err)}

    # 4. 組合成完整 System_Prompt
    system_prompt, err = safe_call(
        build_full_prompt,
        mode,
        task_type,
        #teaching_example
    )
    if err:
        return {"answer": format_error_msg(err)}

    # 5. 建立最終輸入llm的 messages
    messages = []
    messages.append(SystemMessage(content=system_prompt))
    messages.extend(input_chat_history)
    messages.append(HumanMessage(content=user_input))

    # 檢查輸入llm的 messages 和教學模式
    print(f"\n🧠 [MODE] {mode}")
    #for m in messages:
    #    if m.type == "system":
    #        print(f"\n🟡 [SYSTEM]\n{m.content}")
    #    elif m.type == "human":
    #        print(f"\n🔵 [USER]\n{m.content}")
    #    elif m.type == "ai":
    #        print(f"\n🟢 [AI]\n{m.content}")

    # 6. 呼叫 Agent
    agent_executor = st_cache_agent_executor()  # 建立 Agent（初始化一次）
    result, err = safe_call(
        agent_executor.invoke,
        {
            "messages": messages
        }
    )
    if err:
        return {"answer": format_error_msg(err)}

    answer = result["messages"][-1].content
    print(answer)

    # 7. Latex 後製處理
    answer = format_latex(answer)

    # 8. 存入 DB
    save_message(username, "user", user_input)
    save_message(username, "assistant", answer)

    return {
        "answer": answer,
        "task_type": task_type,
        #"teaching_example": teaching_example,
        "history_used": input_chat_history
    }