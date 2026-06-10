from typing import Dict
from all import SearchState
from nodes import llm
from langchain_core.messages import SystemMessage, AIMessage
from logger import logger


def understand_query_node(state: SearchState) -> Dict[str, object]:
    """步骤1：理解用户查询并生成搜索关键词"""
    user_message = state["messages"][-1].content
    logger.info(f"开始理解用户查询: {user_message[:50]}...")

    understand_prompt = f"""分析用户的查询："{user_message}"
请完成两个任务：
1. 简洁总结用户想要了解什么
2. 生成最适合搜索引擎的关键词（中英文均可，要精准）

格式：
理解：[用户需求总结]
搜索词：[最佳搜索关键词]"""

    response = llm.invoke([SystemMessage(content=understand_prompt)])
    response_text = response.content

    search_query = user_message
    if "搜索词：" in response_text:
        search_query = response_text.split("搜索词：")[1].strip()

    logger.info(f"生成搜索关键词: {search_query}")

    return {
        "user_query": response_text,
        "search_query": search_query,
        "step": "understood",
        "messages": [AIMessage(content=f"我将为您搜索：{search_query}")]
    }