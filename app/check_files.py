import asyncio
from tortoise import Tortoise
from app.models import CodeFile
from app.config import TORTOISE_ORM  # 按实际路径修改


async def main():
    await Tortoise.init(config=TORTOISE_ORM)

    try:
        files = await CodeFile.all().order_by("-id").limit(100)

        for file in files:
            print(
                f"id={file.id}, "
                f"path={file.path}, "
                f"project_id={file.project_id}"
            )
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())