from fastapi import FastAPI
import uvicorn

app = FastAPI(
    title="CodeInsight",
    description="AI-powered code analysis and project Q&A assistant",
    version="0.1.0",
)



if __name__=="__main__":
    uvicorn.run("app.main:app",host="127.0.0.1",port=8000,reload=True)