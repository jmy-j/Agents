from typing import Dict
from all import SearchState
from nodes import llm
from langchain_core.messages import SystemMessage, AIMessage
from logger import logger


def generate_answer_node(state: SearchState) -> Dict[str, object]:
    """步骤3：基于搜索结果生成最终答案"""
    logger.info(f"开始生成答案，步骤状态: {state['step']}")
    
    if state["step"] == "search_failed":
        logger.warning("搜索失败，使用回退策略")
        fallback_prompt = f"搜索API暂时不可用，请基于您的知识回答用户的问题：\n用户问题：{state['user_query']}"
        response = llm.invoke([SystemMessage(content=fallback_prompt)])
    else:
        answer_prompt = f"""基于以下搜索结果为用户提供完整、准确的答案：
用户问题：{state['user_query']}
搜索结果：\n{state['search_results']}
请综合搜索结果，提供准确、有用的回答..."""
        response = llm.invoke([SystemMessage(content=answer_prompt)])

    logger.info(f"答案生成完成，长度: {len(response.content)} 字符")

    return {
        "final_answer": response.content,
        "step": "completed",
        "messages": [AIMessage(content=response.content)]
    }