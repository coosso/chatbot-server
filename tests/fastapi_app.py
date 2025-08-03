from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from typing import AsyncGenerator
from langgraph_agent import graph
from langchain_core.messages import HumanMessage

app = FastAPI(title="LangGraph Chat API", version="1.0.0")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat_endpoint(request: Request):
    """
    聊天端点，返回流式响应
    """
    try:
        # 解析请求体
        body = await request.json()
        user_message = body.get("message", "")
        thread_id = body.get("thread_id", "default_thread")
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # 配置检查点
        config = {"configurable": {"thread_id": thread_id}}
        
        # 定义异步生成器函数
        async def generate_response() -> AsyncGenerator[str, None]:
            try:
                # 使用图进行调用
                input_state = {"messages": [HumanMessage(content=user_message)]}
                
                # 流式获取响应
                async for chunk in graph.astream_events(
                    input_state, 
                    config=config, 
                    version="v2"
                ):
                    # 只处理on_chain_stream事件中的LLM输出
                    if chunk["event"] == "on_chat_model_stream":
                        content = chunk["data"]["chunk"].content
                        if content:
                            # 以SSE格式发送数据
                            yield f"data: {json.dumps({'content': content})}\n\n"
                
                # 发送结束标记
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                # 发送错误信息
                error_data = {"error": str(e)}
                yield f"data: {json.dumps(error_data)}\n\n"
        
        # 返回流式响应
        return StreamingResponse(
            generate_response(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}

@app.get("/history/{thread_id}")
async def get_history(thread_id: str):
    """获取对话历史"""
    try:
        config = {"configurable": {"thread_id": thread_id}}
        state = graph.get_state(config)
        return {"messages": [str(msg) for msg in state.values.get("messages", [])]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)