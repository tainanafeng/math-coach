from langchain_core.messages import HumanMessage, AIMessage
from summary.summary import maybe_run_summary
from db.safe_crud import load_recent_messages

def build_chat_history(username):
    """
    對外提供唯一接口：
    回傳 LLM 可用的 chat_history(含摘要 + 最近 N 則訊息)
    """

    # 每次請求都建立新的空 list 組合成 chat_history
    input_chat_history = []

    # ---- 1. 加入摘要（若有） ----
    summary_text = maybe_run_summary(username)
    if summary_text:
        input_chat_history.append(AIMessage(content=f"[過往摘要]\n{summary_text}"))

    # 從 SQLite 載入最近 n 則對話
    recent_msgs = load_recent_messages(username)

    for m in recent_msgs:
        if m["role"] == "user":
            input_chat_history.append(HumanMessage(content=m["content"]))
        else:
            input_chat_history.append(AIMessage(content=m["content"]))

    return input_chat_history
