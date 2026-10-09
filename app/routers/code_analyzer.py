from fastapi import APIRouter
from pydantic import BaseModel
from app.graph.analysis_graph import analyses_graph

router = APIRouter(
    prefix="/analysis",
    tags=["analysis"]
)

class AnalysisRequest(BaseModel):
    file_id : int
    # analysis_type:str = "quality"

@router.post("/")
async def analyze(request: AnalysisRequest):
    final_result = await analyses_graph.ainvoke(
        {"file_id": request.file_id}
    )
    return final_result["result"]
# @router.post("/")
# async def analyze(request:AnalysisRequest):
#     code_file = await CodeFile.get_or_none(id=request.file_id)
#     final_result = analyses_graph.invoke(
#         {
#             "file_id": code_file.id,
#             "file_path":code_file.path,
#             "code":code_file.content or "",
#         }
#     )
#     return final_result.result
