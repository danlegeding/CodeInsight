from typing import Dict
import os

from dotenv import load_dotenv

load_dotenv(override=True)

DB_URL = os.getenv("DB_URL")

if not DB_URL:
    raise RuntimeError(
        "未找到 DB_URL，请检查项目根目录下的 .env 文件"
    )

TORTOISE_ORM: Dict = {
    "connections": {
        "default": DB_URL,
    },
    "apps": {
        "models": {
            "models": ["app.models"],
            "default_connection": "default",
        }
    },
    "use_tz": False,
    "timezone": "UTC",
    "db_pool": {
        "max_size": 10,
        "min_size": 1,
        "idle_timeout": 30,
    },
}