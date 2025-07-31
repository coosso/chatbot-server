from tabnanny import verbose
from langchain import memory
from langchain_community.chat_models import ChatTongyi
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory


chat_model = ChatTongyi(model="qwen-plus")

conversation = ConversationChain(
    llm=chat_model,
    verbose=True,
    memory=ConversationBufferMemory()
)
conversation.predict(input="Write a blog outline on cricket with only 3 topics")
