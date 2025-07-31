from audioop import mul
from langchain_community.chat_models import ChatTongyi
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

@tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@tool
def multiple(a: int, b: int) -> int:
    """Multiplies a and b"""
    return a * b


tools = [add, multiple]
model = ChatTongyi()
model_with_tools = model.bind_tools(tools)
query = "what is 11 + 49? And what is 3 * 12?"
messages = [HumanMessage(query)]
res = model_with_tools.invoke(messages)

messages.append(res)
print(res.tool_calls)

for tool_call in res.tool_calls:
    seleted_tool = {"add": add, "multiple": multiple}[tool_call["name"]]
    tool_msg = seleted_tool.invoke(tool_call)
    messages.append(tool_msg)

print(messages)
