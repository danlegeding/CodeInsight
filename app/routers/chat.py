from fastapi import APIRouter
from pydantic import BaseModel
from app.graph.code_graph import graph

class ChatRequest(BaseModel):
    question:str
    project_id:int

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

@router.post("/")
async def chat(request: ChatRequest):
    response = await graph.ainvoke({
        "question": request.question,
        "mid_context": "",
        "answer": "",
        "project_id": request.project_id
    })

    return {
        "answer": response["answer"]
    }