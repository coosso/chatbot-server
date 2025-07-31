from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
import asyncio

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph

checkpointer = InMemorySaver()

sessions = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in sessions:
        sessions[session_id] = ChatMessageHistory()
    return sessions[session_id]


prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessage(
            content="你的名字是文心一言, 你是一个擅长{ability}的助手。回答不超过20个字"
        ),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)

model = ChatTongyi(model="qwen-plus")

runable = prompt | model

with_message_history = RunnableWithMessageHistory(
    runable,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)


async def achat(message: str, session_id: str):
    response = with_message_history.astream(
        {"ability": "比喻回答", "input": message},
        config={"configurable": {"session_id": session_id}},
    )
    async for chunk in response:
        content = chunk.content
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
