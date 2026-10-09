from fastapi import APIRouter, UploadFile, File
import io
import zipfile
from pathlib import PurePosixPath

from app.services.embedding import  embed_texts, save_embeddings
from app.services.file_filter import SUPPORTED_EXTENTION
from app.services.chunker import chunk_code
from app.models import Project, CodeFile, CodeChunk

router = APIRouter(prefix="/projects",tags=["Projects"])
"""
注意点：1.File是用来传输长文件的
"""
# 跳过不需要分析的目录
excluded_dirs = {
    ".venv",
    "venv",
    "__pycache__",
    ".git",
    "node_modules",
    "site-packages",
    ".idea",
}

@router.post("/upload")
async def upload_project(file: UploadFile = File(...)):
    """上传 ZIP，筛选代码文件、切分代码并批量生成向量。"""

    data = await file.read()
    project = await Project.create(name=file.filename)

    files = []
    all_codechunks = []

    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for name in z.namelist():
            path = PurePosixPath(name)
            # 只处理支持的文件类型，并跳过目录

            # 跳过目录
            if name.endswith("/"):
                continue

            if any(part in excluded_dirs for part in path.parts):
                continue

            # 只处理支持的文件类型
            if path.suffix not in SUPPORTED_EXTENTION:
                continue

            try:
                content = z.read(name).decode("utf-8")
            except UnicodeDecodeError:
                continue

            code_file = await CodeFile.create(
                project=project,
                path=name,
                language=path.suffix,
                content=content,
            )

            chunks = chunk_code(
                content,
                chunk_size=500,
                overlap=50,
            )

            # 先创建代码块，暂时不逐条生成向量
            for chunk in chunks:
                codechunk = await CodeChunk.create(
                    file=code_file,
                    content=chunk["content"],
                    start_line=chunk["start_line"],
                    end_line=chunk["end_line"],
                    chunk_index=chunk["chunk_index"],
                )
                all_codechunks.append(codechunk)

            # 暂时只返回文件基本信息，避免响应携带大量源代码
            files.append({
                "path": name,
                "chunks_count": len(chunks),
            })

    # 所有文件的代码块创建完成后，再统一分批生成向量
    batch_size = 32

    for i in range(0, len(all_codechunks), batch_size):
        batch = all_codechunks[i:i + batch_size]
        texts = [chunk.content for chunk in batch]

        vectors = await embed_texts(texts)
        await save_embeddings(batch, vectors)

    return {
        "project_id": project.id,
        "filename": file.filename,
        "files_count": len(files),
        "chunks_count": len(all_codechunks),
        "files": files,
    }