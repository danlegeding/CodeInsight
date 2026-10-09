from pydantic import BaseModel


class AnalysisIssue(BaseModel):
    level: str
    description: str
    suggestion: str


class AnalysisResult(BaseModel):
    summary: str
    issues: list[AnalysisIssue]
    strengths: list[str]
    optimization: list[str]

