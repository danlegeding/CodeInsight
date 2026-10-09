from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
import os

load_dotenv(override=True)

llm_model = ChatDeepSeek(
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
    extra_body={
        "thinking":{
            "type":"disabled"
        }
    }
)
