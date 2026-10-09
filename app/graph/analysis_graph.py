from pydantic import BaseModel,Field
from app.schemas.analysis import AnalysisResult
from app.models import CodeFile
from fastapi import HTTPException
from langgraph.graph import StateGraph,START,END
from typing import Annotated
from operator import add
from app.services.code_chunk_analysis import (
    analyses_code_chunk,
    split_code_for_analyses,
)
from langgraph.types import Send
from app.services.code_chunk_analysis import summarize_analyses

class AnalysesState(BaseModel):
    file_id: int
    file_path: str = ""
    code: str = ""
    chunks: list[str] = Field(default_factory=list)
    analyses: Annotated[
        list[AnalysisResult],
        add
    ] = Field(default_factory=list)
    result: AnalysisResult | None = None

async def empty_result_node(state: AnalysesState) -> dict:
    return {
        "result": AnalysisResult(
            summary="文件为空，无法进行代码分析。",
            issues=[],
            strengths=[],
            optimization=["请上传包含代码的文件后重试。"],
        )
    }

async def load_file(state:AnalysesState)->dict:
    code_file = await CodeFile.get_or_none(id=state.file_id)
    if code_file is None:
        raise HTTPException(
            status_code=404,
            detail="文件不存在"
        )
    return {
        "file_path":code_file.path,
        "code":code_file.content or ""
    }

async def split_node(state:AnalysesState)->dict:
    MAX_analyses_CHUNKS=3000
    if not state.code.strip():
        return {"chunks":[]}
    if len(state.code)<=MAX_analyses_CHUNKS:
        return {
            "chunks":[state.code]
        }
    return {
        "chunks":split_code_for_analyses(state.code)
    }

async def analyses_code_chunk_node(state:dict)->dict:
    "传入的是字典而非str类型的content，是因为router传入的是字典"
    one_chunk_result = await analyses_code_chunk(state["content"])
    return {
        "analyses":[one_chunk_result]
    }

def router(state: AnalysesState,) -> str | list[Send]:
    if not state.chunks:
        return "empty_result_node"
    return [
        Send(
            "analyses_code_chunk_node",
            {"content": chunk},
        )
        for chunk in state.chunks
    ]

async def summary_analyses_node(state: AnalysesState) -> dict:
    result = await summarize_analyses(
        analyses=state.analyses,
        file_path=state.file_path,
    )
    return {"result": result}


builder = StateGraph(AnalysesState)
builder.add_node("load_file",load_file)
builder.add_node("split_node",split_node)
builder.add_node("analyses_code_chunk_node",analyses_code_chunk_node)
builder.add_node("summary_analyses_node",summary_analyses_node)
builder.add_node("empty_result_node", empty_result_node)
builder.add_edge(START,"load_file")
builder.add_edge("load_file","split_node")
builder.add_conditional_edges(
    "split_node",
    router,
    path_map={
        "analyses_code_chunk_node": "analyses_code_chunk_node",
        "empty_result_node": "empty_result_node",
    },
)
builder.add_edge("analyses_code_chunk_node", "summary_analyses_node")
builder.add_edge("summary_analyses_node", END)
builder.add_edge("empty_result_node", END)
analyses_graph = builder.compile()