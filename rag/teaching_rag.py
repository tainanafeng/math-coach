# 教學範例 RAG 檢索(filter by context_type)

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

from pathlib import Path
import os


# 從「環境變數」讀 API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set")

BASE_DIR = Path(__file__).resolve().parent      # __file__：目前這個 .py 檔案的位置
TEACHING_CHROMA_DIR = BASE_DIR / "db_teaching_example"

# 載入教法庫物件
embeddings_model=OpenAIEmbeddings(model='text-embedding-3-large', api_key=OPENAI_API_KEY)
db_teaching_example = Chroma(
                        persist_directory=str(TEACHING_CHROMA_DIR),
                        embedding_function=embeddings_model
                        )


# 建立教法範例檢索函式
def teaching_example_function(user_input: str, context_type: str):

    #建立教法範例檢索器
    teaching_example_retriever = db_teaching_example.as_retriever(
                                    search_type="mmr",
                                    search_kwargs={"k": 3, "filter": {"context_type": context_type}}
                                    )

    teaching_example_result = teaching_example_retriever.invoke(user_input)

    teaching_example_output = "\n更多教學範例:\n"
    for doc in teaching_example_result:
       teaching_example_output += doc.page_content
       teaching_example_output += "\n"
    #print(teaching_example_output)

    return teaching_example_output   # [SystemMessage(content=teaching_example_output)]