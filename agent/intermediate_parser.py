from langchain_core.messages import AIMessage

def convert_intermediate_steps(intermediate_steps):
    """
    將 AgentExecutor 回傳的 intermediate_steps 解析成人類可讀的 log，
    並包裝成一個 AIMessage 物件，供 agent scratchpad 使用。

    intermediate_steps 結構：
    [
        (AgentAction, tool_result),
        (AgentAction, tool_result),
        ...
    ]
    """

    log = ""

    for action, observation in intermediate_steps:
        log += (
            f"選用的工具：{action.tool}\n"
            f"工具參數：{action.tool_input}\n"
            f"工具執行結果：{observation}\n\n"
        )

    return [AIMessage(content=log)]