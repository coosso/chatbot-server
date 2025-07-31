from typing import Annotated, List, TypedDict
from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph, add_messages

def get_agent():
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "你是一个专业的助手, 名叫文心一言，并在每次回答后添加一句{end}。",
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    chat_model = ChatTongyi(model="qwen-plus", streaming=True)

    chain = prompt | chat_model


    class State(TypedDict):
        messages: Annotated[List[BaseMessage], add_messages]
        end: str


    builder = StateGraph(State)


    def call_model(state: State):
        content = ""
        for chunk in chain.stream(state):
            # print(chunk)
            content += chunk.content
        return {"messages": AIMessage(content=content)}


    builder.add_node("model", call_model)
    builder.add_edge(START, "model")

    memory = MemorySaver()

    agent = builder.compile(checkpointer=memory)

    return agent

if __name__ == "__main__":
    agent = get_agent()
    config = {"configurable": {"thread_id": "session_1"}}

    input_dict = {
        "messages": [HumanMessage(content="你是谁")],
        "end": "---ENXXXD---",
    }

    res = agent.stream(input_dict, config)
    for chunk in res:
        print(chunk.content)  