from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
# from langchain.memory import ConversationBufferMemory
# from langchain.chains import ConversationChain
# from typing import TypedDict, Annotated, List, Any, Dict
# from langgraph.graph.message import add_messages

# import asyncio

# # Memory
# memory = ConversationBufferMemory()


sessions = {
    "session_1": [
        SystemMessage(content="You are helpful assitant."),
        HumanMessage(content="我是Jack"),
    ]
}


async def achat(message: str, session_id: str):
    if session_id not in sessions:
        sessions[session_id] = []
    sessions[session_id].append(HumanMessage(content=message))
    llm = ChatTongyi(model="qwen-plus")
    response = llm.astream(sessions[session_id])
    full_content = ""
    async for chunk in response:
        content = chunk.content
        full_content += content
        if content == "":
            sessions[session_id].append(AIMessage(content=full_content))
        yield content


async def main():
    user_input = input("Enter:")
    while user_input != "exit":
        async for chunk in achat(user_input, "session_1"):
            print(chunk)
        user_input = input("Enter:")


if __name__ == "__main__":
    asyncio.run(main())
    ...
