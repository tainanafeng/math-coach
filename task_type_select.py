# 任務分類
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

import os


# 從「環境變數」讀 API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set")


# 任務分類模型
task_type_select_model = ChatOpenAI(model = 'gpt-5-nano', temperature=0, api_key=OPENAI_API_KEY)


# 建立提示詞 判斷任務類型
task_type_select_prompt = (
    ChatPromptTemplate.from_messages([
        ('system',"""\
角色: 你是任務分類器
任務: 輸入為學生的一句話或一段短文字，請回傳一個代表任務類型的數字(1~5)        
判斷原則：
- 若輸入是在詢問概念、定義或原因 → 1
- 若輸入包含明確數學問題或要求計算 → 2
- 若輸入要求例題、練習或示範 → 3
- 對學生的疑問、作答或思路給建議、指出錯誤 → 4
- 若與數學無關 → 5
- 若同時包含多種任務，選擇「主要任務」
輸出規範: 只回傳數字(1~5)，禁止文字或標點

下面是範例（User => 類型）。請參考範例模式進行分類：
"可以解釋一下什麼是矩陣的秩嗎？" => 1
"我不太懂微分的意義，可以講一下嗎？" => 1
"向量空間是什麼意思？" => 1

"請解這題：2x + 3 = 7" => 2
"這題積分怎麼算：∫x² dx" => 2
"求矩陣 A 的特徵值：[[1,2],[2,1]]" => 2

"可以給我一個矩陣乘法的例子嗎？" => 3
"有沒有簡單一點的例題可以練習？" => 3
"可以示範一題類似的題目嗎？" => 3

"我不懂為什麼要這樣做?" => 4
"我解這題答案是5，你可以幫我檢查哪裡錯嗎？" => 4
"我這步驟算對了嗎？" => 4
"我寫的證明有哪裡不對？" => 4

"今天天氣怎麼樣？" => 5
"你覺得我該不該轉系？" => 5
"幫我寫一段自我介紹" => 5
\
"""
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ('human','{input}')
    ])
)


# 執行任務分類
task_type_select_chain = (
    {"input": lambda x: x["input"], "chat_history": lambda x: x["chat_history"]}
    | task_type_select_prompt
    | task_type_select_model
    | StrOutputParser()
)