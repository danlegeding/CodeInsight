from app.schemas.analysis import AnalysisResult
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import os

load_dotenv(override=True)

gdp_model = init_chat_model(
    model="gpt-5.4-mini",
    api_key=os.getenv("CLOSEAI_API_KEY"),
    base_url=os.getenv("CLOSEAI_BASE_URL")
)
structured_llm = gdp_model.with_structured_output(AnalysisResult)

def split_code_for_analyses(content: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=300,
        separators=[
            "\nclass ",
            "\nasync def ",
            "\ndef ",
            "\n\n",
            "\n",
            " ",
            "",
        ]
    )
    return splitter.split_text(content)

async def analyses_code_chunk(content: str) -> AnalysisResult:
    prompt = f"""
        你是一名经验丰富的代码审查工程师。

        请分析下面的代码。

        分析要求：
        1. 总结代码的主要功能。
        2. 找出潜在的问题，包括逻辑错误、异常处理、代码质量、安全性等。
        3. 给出具体的优化建议。
        4. 指出代码中做得比较好的地方。
        5. 不要凭空猜测代码不存在的问题。
        6. 如果没有发现明显问题，明确说明。

        代码：
        {content}
        """
    analyses_result = await structured_llm.ainvoke(prompt)
    return analyses_result

async def summarize_analyses(
    analyses: list[AnalysisResult],
    file_path: str,
) -> AnalysisResult:
    analyses_text = "\n\n".join(
        item.model_dump_json()
        for item in analyses
    )

    prompt = f"""
    你是一名高级代码审查工程师。

    文件：{file_path}

    以下是同一文件不同代码片段的分析结果：
    {analyses_text}

    请综合生成最终代码审查报告。
    1. 合并重复问题。
    2. 总结整份文件的主要功能。
    3. 整合代码优点和优化建议。
    4. 不要凭空增加问题。
    """

    return await structured_llm.ainvoke(prompt)