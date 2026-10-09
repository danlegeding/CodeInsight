import asyncio
import os
import logging
import time
from loguru import logger
from dotenv import load_dotenv
from langchain.embeddings import init_embeddings
from tortoise import connections

load_dotenv(override=True)

embedding_model = init_embeddings(
    model="openai:text-embedding-3-small",
    api_key=os.getenv("CLOSEAI_API_KEY"),
    base_url=os.getenv("CLOSEAI_BASE_URL"),
)


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """在线程中批量生成文本向量，避免阻塞 FastAPI 事件循环。"""
    if not texts:
        return []

    return await asyncio.to_thread(
        embedding_model.embed_documents,
        texts,
    )


async def save_embeddings(chunks, vectors):
    """将生成的向量写入对应的 CodeChunk 记录。"""
    if len(chunks) != len(vectors):
        raise ValueError("代码块数量与向量数量不一致")

    connection = connections.get("default")

    for chunk, vector in zip(chunks, vectors):
        await connection.execute_query(
            """
            UPDATE codechunk
            SET embedding = $1::vector
            WHERE id = $2
            """,
            [str(vector), chunk.id],
        )


async def embed_code_chunk(chunk):
    """兼容原有单个代码块的调用方式。"""
    vectors = await embed_texts([chunk.content])
    await save_embeddings([chunk], vectors)


async def retrieve(query: str, project_id: int = 1, limit: int = 5):
    """检索相关代码，并记录数据库检索耗时。"""
    connection = connections.get("default")

    # 生成查询向量：单独计时，便于区分模型耗时和数据库耗时
    embedding_start = time.perf_counter()

    query_vector = await asyncio.to_thread(
        embedding_model.embed_query,
        query,
    )

    embedding_elapsed_ms = (
        time.perf_counter() - embedding_start
    ) * 1000

    # 执行数据库检索
    retrieval_start = time.perf_counter()

    _, result = await connection.execute_query(
        """
        SELECT
            codechunk.id AS chunk_id,
            codefile.path AS file_path,
            codechunk.content AS chunk_content,
            codechunk.start_line AS chunk_start_line,
            codechunk.end_line AS chunk_end_line,
            codechunk.embedding <=> $1::vector AS distance
        FROM codechunk
        JOIN codefile ON codechunk.file_id = codefile.id
        WHERE codechunk.embedding IS NOT NULL
          AND codefile.project_id = $2
        ORDER BY codechunk.embedding <=> $1::vector
        LIMIT $3
        """,
        [str(query_vector), project_id, limit],
    )

    retrieval_elapsed_ms = (
        time.perf_counter() - retrieval_start
    ) * 1000

    logger.info(
        "Code retrieval completed | project_id=%s | "
        "result_count=%s | embedding_ms=%.2f | db_query_ms=%.2f",
        project_id,
        len(result),
        embedding_elapsed_ms,
        retrieval_elapsed_ms,
    )

    if not result:
        return "没有检索到相关代码。"

    contexts = []

    for row in result:
        contexts.append(
            f"""
文件：{row["file_path"]}
行号：{row["chunk_start_line"]}-{row["chunk_end_line"]}
相关代码：
{row["chunk_content"]}
""".strip()
        )

    return "\n\n--- 相关代码片段 ---\n\n".join(contexts)
