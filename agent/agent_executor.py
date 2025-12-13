# 匯入自製函式
from agent_tools.registry import tools
from agent.intermediate_parser import convert_intermediate_steps

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain.agents import AgentExecutor
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser

import os


# 從「環境變數」讀 API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set")

# gpt-4o-mini可以改溫度，但是gpt-5-nano不行! 預設為1
chat_model = ChatOpenAI(model='gpt-5-nano',
                        api_key=OPENAI_API_KEY,
                        temperature=1,
                        streaming=False)


# 固定提示詞模板 + 動態提示詞 + 動態教學範例
main_prompt = ChatPromptTemplate.from_messages([
    ('system', '{system_prompt}'),
    MessagesPlaceholder(variable_name="chat_history"),
    ('human', '{input}'),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])


# 功能: 建立代理
def build_agent_executor():
    
    llm_with_tools = chat_model.bind_tools(tools)

    agent = (
        RunnablePassthrough().assign(
            agent_scratchpad=lambda x: convert_intermediate_steps(x["intermediate_steps"])
        )
        | main_prompt
        | llm_with_tools
        | OpenAIToolsAgentOutputParser()
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        return_intermediate_steps=True,
    )

    return agent_executor