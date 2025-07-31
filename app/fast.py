from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessage, HumanMessage
from graph import get_agent

app = FastAPI()
agent = get_agent()

@app.post("/chat")
async def chat_stream(message: str):
    input_dict = {
        "messages": [HumanMessage(content=message)],
        "end": "---ENXXXD---",
    }
    config = {"configurable": {"thread_id": "session_1"}}
    def event_generator():
        try:
            for chunk in agent.stream(input_dict, config):
                print(chunk)
        except Exception as e:
            yield f"err: {e}"

    return StreamingResponse(event_generator())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)
