from fastapi import FastAPI, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from agent import achat
import uvicorn

app = FastAPI(title="Chatbot Service")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境建议指定具体域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有HTTP头
)


@app.get("/")
def root():
    return {"message": "Hello XXX"}


class ChatRequest(BaseModel):
    session_id: str | None = Field(
        default=None, title="聊天会话ID", example="session_id_123"
    )
    message: str = Field(
        ..., min_length=1, max_length=100, title="用户消息", example="你好"
    )


class ChatResponse(BaseModel):
    session_id: str
    message: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    处理用户聊天请求并返回流式响应
    - **session_id**: 可选，用于关联多轮对话
    - **message**: 必填，用户的提问内容
    """
    return StreamingResponse(achat(request.message, request.session_id), media_type="text/plain")


@app.get("/session/{session_id}")
async def get_session_by_id(
    session_id: str = Path(..., example="session_1", description="聊天会话ID")
):
    """
    获取指定会话ID的聊天记录
    - **session_id**: 必填，聊天会话ID
    """
    return {"session_id": session_id, "message": "这是之前的对话记录"}


if __name__ == "__main__":
    uvicorn.run("server:app", port=8000, reload=True)
