from typing import Annotated, List, TypedDict
from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph, add_messages
import asyncio

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

    chat_model = ChatTongyi(model="qwen-plus")

    chain = prompt | chat_model


    class State(TypedDict):
        messages: Annotated[List[BaseMessage], add_messages]
        end: str


    builder = StateGraph(State)


    def call_model(state: State):
        return {"messages": [chain.invoke(state)]}
      

    builder.add_node("model_node", call_model)
    builder.add_edge(START, "model_node")

    memory = MemorySaver()

    agent = builder.compile(checkpointer=memory)

    return agent

async def main():
    agent = get_agent()
    config = {"configurable": {"thread_id": "session_1"}}

    input_dict = {
        "messages": [HumanMessage(content="你是谁")],
        "end": "---ENXXXD---",
    }
    for event in agent.stream(input_dict, config, stream_mode="messages"):
       content = event[0].content
       if content == "":
          break
       print(event[0].content)
       

if __name__ == "__main__":
   asyncio.run(main())