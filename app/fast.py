from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessage, HumanMessage
from graph import get_agent

app = FastAPI()
agent = get_agent()

@app.post("/chat")
async def chat_stream(message: str):
    config = {"configurable": {"thread_id": "session_1"}}

    input_dict = {
        "messages": [HumanMessage(content=message)],
        "end": "---ENXXXD---",
    }
    
    def event_generator():
        for event in agent.stream(input_dict, config, stream_mode="messages"):
          content = event[0].content
          if content == "":
             break
          yield content
    return StreamingResponse(event_generator())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fast:app", port=8000, reload=True)
