from fastapi import FastAPI, Path, Query,Body
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional

app = FastAPI(title="sever API docs", version="0.1.0")

class ItemType(str, Enum):
    BOOK = "book"
    ELECTRONIC = "electronic"
    CLOTHING = "clothing"

class Item(BaseModel):
    name: str
    price: float
    type: ItemType
    is_offer: Optional[bool]


# 定义响应模型（不包含敏感字段）
class ItemResponse(BaseModel):    
    id: int = Field(..., example=1)
    name: str = Field(..., example="Python编程入门")
    price: float = Field(..., example=59.99)
    type: ItemType = Field(..., example=ItemType.BOOK)
    is_offer: Optional[bool] = Field(None, example=False)
    tax: Optional[float] = Field(None, example=5.99)
    
    class Config:
        orm_mode = True  # 支持从ORM对象转换


@app.get("/type/{type_id}")
async def root(type:ItemType=Query(description="类型了"),type_id:ItemType = Path(description="路径")):
    """根路径端点"""
    return {"message": "Hello, FastAPI!"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    """带路径参数的端点"""
    return {"item_id": item_id}

@app.get(
        "/items-query/{item_id}",
        response_model=ItemResponse,
        response_description="返回物品的完整信息"
        )
def read_item(
    item_id: int = Path(..., gt=0, le=1000, example=100, description="物品ID，范围1-1000"),
    skip: int = 0,
    limit: int = 0
    ):
    """带路径和query参数的端点"""
    return {"item_id": item_id, "skip":skip,"limit": limit}    

@app.post("/items/")
async def create_item(item: Item = Body(
    ...,
    examples={
            "normal": {
                "summary": "一个正常的物品",
                "description": "一个符合预期结构的物品示例",
                "value": {
                    "name": "无线鼠标",
                    "price": 29.99,
                    "type": ItemType.ELECTRONIC,
                    "is_offer": True
                }
            },
            "clothing": {
                "summary": "一件衣物",
                "description": "一件衣物类型的物品示例",
                "value": {
                    "name": "牛仔裤",
                    "price": 89.99,
                    "type": ItemType.CLOTHING
                }
            }
        }
)):
    """使用请求体创建物品"""
    item_dict = item.model_dump()
    if item.price:
        item_dict.update({"tax": item.price * 0.1})
    return item_dict


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fastapi_base:app", reload=True)