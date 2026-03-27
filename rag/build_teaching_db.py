from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import json

import os


# 從「環境變數」讀 API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set")
embeddings_model=OpenAIEmbeddings(model='text-embedding-3-large', api_key=OPENAI_API_KEY)


#載入教法範例json檔轉成document
with open("C:/Users/taina/Python_learning/math_coach/rag/rag_teaching_example.json", "r", encoding="utf-8") as f:
    json_data = json.load(f)  #不需要 close()，因為 with 區塊結束後會自動關閉檔案

docs = [
    Document(
        page_content=item["content"],
        metadata={
            "id": item["id"],
            "context_type": item["context_type"],
            "topic": item["topic"]
        }
    )
    for item in json_data  #列表生成式(list comprehension)
]

#建立教法資料庫
Chroma.from_documents(documents=docs,
                      embedding=embeddings_model,
                      persist_directory='C:/Users/taina/Python_learning/math_coach/rag/db_teaching_example',
                      collection_metadata={"hnsw:space": "cosine"})