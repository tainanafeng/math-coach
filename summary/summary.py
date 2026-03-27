import sqlite3
import streamlit as st

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

import os


# 從「環境變數」讀 API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set")


chat_model = ChatOpenAI(model = 'gpt-5-nano',       #gpt-4o-mini可以改溫度，但是gpt-5-nano不行! 預設為1
                        api_key=OPENAI_API_KEY,
                        temperature=1,
                        streaming=False)


# 彙整過往對話紀錄的函式
def summary_function(messages):    # messages: list[BaseMessage]
    # 確保 summary_messages 是 BaseMessage list；若不是，轉成 content 列表
    contents = []
    for m in messages:
        c = getattr(m, "content", str(m))
        contents.append(c.strip())

    # 拼接（保留順序，舊->新）
    big_text = "\n\n".join(contents)

    # 建立一個單一 human message 輸入 summarizer
    summary_prompt = (
        SystemMessage(content=(
            "任務：將下列所有既有摘要與對話內容做合併整合，"
            "去重、保留要點與公式，產出一份不超過800字的長期記憶筆記。"
            "若有多個主題，請分段列出每個主題的重點。"
            "數學算式必須為 LaTeX 格式，且使用 $...$、$$...$$ 或 \[...\] ，避免多餘空白或換行。")) +
        HumanMessage(content="以下為需整合的內容：\n\n" + big_text)
    )

    summarizer = (
        summary_prompt
        | chat_model
        | StrOutputParser()
    )

    return summarizer.invoke({})



# ====== 摘要載入與儲存 ======
def load_summary(username):
    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()

    cursor.execute("SELECT summary_text FROM summary WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()

    return row[0] if row else None

def save_summary(username, text):
    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO summary (username, summary_text)
        VALUES (?, ?)
        ON CONFLICT(username)
        DO UPDATE SET summary_text=excluded.summary_text,
                      updated_at=CURRENT_TIMESTAMP
    """, (username, text))

    conn.commit()
    conn.close()


# ====== 摘要進度管理 ======
def load_summary_pointer(username):
    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()

    cursor.execute("SELECT last_summarized_id FROM summary_pointer WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()

    return row[0] if row else 0  # 如果沒有資料，代表從頭開始摘要

def save_summary_pointer(username, last_id):
    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO summary_pointer (username, last_summarized_id)
        VALUES (?, ?)
        ON CONFLICT(username)
        DO UPDATE SET last_summarized_id=excluded.last_summarized_id
    """, (username, last_id))

    conn.commit()
    conn.close()


# ====== 讀取尚未摘要的舊訊息 ======
def load_messages_after_id(username, last_id):
    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, role, content FROM messages
        WHERE username=? AND id > ?
        ORDER BY id
    """, (username, last_id))

    rows = cursor.fetchall()
    conn.close()

    return [{"id": r[0], "role": r[1], "content": r[2]} for r in rows]



def maybe_run_summary(username):
    """
    檢查是否達到20筆舊訊息 → 若是，產生摘要，回傳最新摘要內容
    若沒有需要摘要 → 回傳 None 或舊摘要
    """

    # 載入摘要(如果有)
    summary_text = load_summary(username)

    # 讀取 summary_pointer
    last_ptr = load_summary_pointer(username)

    # 讀取尚未摘要的舊訊息
    older_msgs = load_messages_after_id(username, last_ptr)

    if len(older_msgs) < 20:
        return summary_text  # 不需要重摘要
    
    
    with st.spinner("✨ 執行摘要 ✨"):
        # 整理成 LangChain message 格式
        older_lc = [
            HumanMessage(content=m["content"]) if m["role"] == "user"
            else AIMessage(content=m["content"])
            for m in older_msgs
        ]

        # 舊摘要(如果有)
        base = [AIMessage(content=summary_text)] if summary_text else []

        # 建立新的摘要
        new_summary = summary_function(base + older_lc)

        # 儲存摘要
        save_summary(username, new_summary)

        # 更新摘要進度 pointer
        save_summary_pointer(username, older_msgs[-1]["id"])

    return new_summary
