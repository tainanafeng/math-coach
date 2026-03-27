# 匯入自製函式
from agent_tools.registry import tools

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

import os


# 從「環境變數」讀 API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set")

chat_model = ChatOpenAI(model='gpt-5-nano',
                        api_key=OPENAI_API_KEY,
                        temperature=0.7,
                        streaming=False)

# 功能: 建立代理
def build_agent_executor():
    agent_executor = create_agent(
        tools=tools,
        model=chat_model
    )

    return agent_executor