import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from tortoise.contrib.fastapi import register_tortoise

from config import TORTOISE_ORM
from routers import project
from app.routers import chat
from app.routers import code_analyzer


# 1. 日志基础配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


# 2. 创建应用
app = FastAPI(
    title="CodeInsight",
    description="AI-powered code analysis and project Q&A assistant",
    version="0.1.0",
)

@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start_time = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        logger.exception(
            "Request failed | request_id=%s | method=%s | path=%s | elapsed_ms=%.2f",
            request_id,
            request.method,
            request.url.path,
            elapsed_ms,
        )
        raise

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    response.headers["X-Request-ID"] = request_id

    logger.info(
        "Request completed | request_id=%s | method=%s | path=%s | status=%s | elapsed_ms=%.2f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )

    return response

# 3. 注册路由
app.include_router(project.router)
app.include_router(chat.router)
app.include_router(code_analyzer.router)


# 4. 处理 HTTP 异常，例如 404、400
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
):
    logger.warning(
        "HTTP error | method=%s | path=%s | status=%s",
        request.method,
        request.url.path,
        exc.status_code,
    )

    return JSONResponse(
        # 就是404之类的
        status_code=exc.status_code,
        content={
            "code": "HTTP_ERROR",
            "message": (
                exc.detail
                if isinstance(exc.detail, str)
                else "请求处理失败"
            ),
        },
        headers=exc.headers,
    )


# 5. 处理请求参数校验异常
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    logger.warning(
        "Validation error | method=%s | path=%s",
        request.method,
        request.url.path,
    )

    return JSONResponse(
        status_code=422,
        content={
            "code": "VALIDATION_ERROR",
            "message": "请求参数不符合要求，请检查输入。",
        },
    )


# 6. 处理未预期的服务端异常
@app.exception_handler(Exception)
async def unexpected_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.exception(
        "Unexpected error | method=%s | path=%s",
        request.method,
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "code": "INTERNAL_SERVER_ERROR",
            "message": "服务器内部错误，请稍后重试。",
        },
    )


# 7. 注册 Tortoise ORM
register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True,
)


# 8. 启动应用
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
