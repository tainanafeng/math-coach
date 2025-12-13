# 情境分類 RAG 檢索

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import MessagesPlaceholder

from pathlib import Path
import os


# 從「環境變數」讀 API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set")

BASE_DIR = Path(__file__).resolve().parent      # __file__：目前這個 .py 檔案的位置
CONTEXT_CHROMA_DIR = BASE_DIR / "db_context_example"


# 載入情境分類範例資料庫物件
embeddings_model=OpenAIEmbeddings(model='text-embedding-3-large', api_key=OPENAI_API_KEY)
db_context_example = Chroma(
        persist_directory=str(CONTEXT_CHROMA_DIR),
        embedding_function=embeddings_model
        )

# 建立情境分類範例檢索器
context_example_retriever = db_context_example.as_retriever(search_type="mmr", search_kwargs={"k": 3})

# 情境分類所需模型
context_type_select_model = ChatOpenAI(model = 'gpt-5-nano', temperature=1, api_key=OPENAI_API_KEY)


# 建立提示詞 判斷情境類型
context_type_select_prompt = (
    ChatPromptTemplate.from_messages([
        ('system',"""\
          角色: 你是情境分類器。
          任務: 輸入為學生的一句話或一段短文字，請回傳一個代表學習情境的數字(1~8)。
          輸出規範: 只回傳數字(1~8)，禁止文字或標點。
          學習情境的類型:
            1 = 學生只貼上題目、不說明任何困難、直接要求給答案或步驟
            2 = 學生明確表示不知道從何下手或明確要求提示關鍵步驟
            3 = 學生思考過程卡關（有嘗試但卡在中間步驟）
            4 = 回答錯誤
            5 = 學生反覆嘗試但毫無進展
            6 = 學生對基礎概念與定義缺乏理解
            7 = 學生完整走完解題流程且答案正確
            8 = 輸入與數學無關的問題或內容

          下面是範例（User => 類型）。請參考範例模式進行分類：
          "題目：計算 \(\int_0^1 x^2 dx\)" => 1

          "不知道題目在問什麼，完全沒頭緒。" => 2
          "這個題型我以前沒學過，不知道怎麼下手。" => 2

          "我列了方程式但不知道下一步該怎麼化簡，卡在中間。" => 3
          "我用代入法但中間結果看起來不合理，現在卡住。" => 3

          "我做出一整套解法，最後得到 5，但我覺得有問題。" => 4
          "我的解答是 y=2" => 4

          "我已經試了好幾種方法，每次都失敗，完全沒有進展。" => 5

          "指數和對數到底有什麼差別？" => 6

          "最後答案是 \(x=2\)，已驗算過，正確。" => 7
          "我完成題目並確認結果正確，可以幫我總結重點嗎？" => 7

          "今天晚上吃什麼？" => 8

          {rag_instance}
          \
          """
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ('human','{input}')
    ])
)


# 建立情境分類範例檢索函式
def retriever_function(user_input: dict):
    retriever_result = context_example_retriever.invoke(user_input["input"])
    #pprint(retriever_result)
    context = ""
    for item in retriever_result:
        context += item.page_content
        context += "\n"
    #print(context)

    return context

# 檢索對話情境分類範例
rag_context_type_select_chain = (
    {"rag_instance": RunnableLambda(retriever_function), "input": lambda x: x["input"], "chat_history": lambda x: x["chat_history"]}
    | context_type_select_prompt
    | context_type_select_model
    | StrOutputParser()
)