from langchain_community.tools import DuckDuckGoSearchRun
from pydantic import BaseModel, Field


# 建立搜尋工具
class SearchRun(BaseModel):
    query: str = Field(description="給搜尋引擎的搜尋關鍵字")
search_run = DuckDuckGoSearchRun(
    name="search",
    description="使用網路搜尋你不知道的事物",
    args_schema=SearchRun
)