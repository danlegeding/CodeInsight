from pydantic import BaseModel
from langgraph.graph import START,END,StateGraph
from app.services.embedding import retrieve
from app.services.deepseek_llm import llm_model

class OverAllState(BaseModel):
    question:str
    mid_context:str
    answer:str
    project_id:int

async def retrieve_node(state:OverAllState)->OverAllState:
    context = await retrieve(
        state.question,
        state.project_id
    )
    mid_context = f"""
        上下文：
        {context}
        """
    return {
        "mid_context":mid_context
    }

async def generate_node(state: OverAllState) -> OverAllState:
    prompt = f"""
你是一个严谨的代码分析助手，负责回答用户关于指定项目的问题。

请严格遵守以下规则：

1. 先直接回答问题，不要先写冗长的背景介绍。
2. 只根据提供的代码上下文回答，不要把猜测当作事实。
3. 如果问题询问执行流程，按照实际执行顺序解释。
4. 如果问题询问某个功能，说明相关文件、关键逻辑及其作用。
5. 如果上下文不足以回答，明确指出缺少什么信息。
6. 使用清晰的中文，优先使用分点说明，避免重复和空泛的评价。
7. 只有在上下文能够支持时，才引用文件路径和行号。
8. 对于上下文中未展示的分支、函数实现或调用关系，
不得依据常见编程模式补全其行为。
9.可以提出待验证的可能性，但必须明确标记为假设，
不得将假设写入已确认的执行流程。

建议的回答结构：
- **结论**：先用一两句话回答问题。
- **具体依据**：结合检索到的代码解释原因或执行过程。
- **补充说明**：仅在必要时指出限制或尚无法确定的部分。

用户问题：
{state.question}

检索到的代码上下文：
{state.mid_context}
"""

    response = await llm_model.ainvoke(prompt)

    return {
        "answer": response.content
    }

builder = StateGraph(state_schema=OverAllState)
builder.add_node("retrieve_node",retrieve_node)
builder.add_node("generate_node",generate_node)
builder.add_edge(START,"retrieve_node")
builder.add_edge("retrieve_node","generate_node")
builder.add_edge("generate_node",END)

graph = builder.compile()
