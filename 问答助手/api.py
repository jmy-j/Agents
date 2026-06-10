from typing import Dict
from all import SearchState
from nodes import tavily_client
from langchain_core.messages import AIMessage
from logger import logger


def tavily_search_node(state: SearchState) -> Dict[str, object]:
    """步骤2：使用Tavily API进行真实搜索"""
    search_query = state["search_query"]
    logger.info(f"开始Tavily搜索: {search_query}")
    
    try:
        response = tavily_client.search(
            query=search_query, search_depth="basic", max_results=5, include_answer=True
        )
        
        search_results = ""
        result_count = 0
        
        if response.get("answer"):
            search_results += f"总结答案: {response['answer']}\n\n"
        
        if response.get("results"):
            search_results += "搜索结果:\n"
            for i, result in enumerate(response["results"], 1):
                search_results += f"{i}. [{result.get('title', '')}]({result.get('url', '')})\n"
                search_results += f"   {result.get('content', '')[:200]}...\n\n"
                result_count += 1
        
        logger.info(f"搜索完成，获取到 {result_count} 条结果")

        return {
            "search_results": search_results,
            "step": "searched",
            "messages": [AIMessage(content="✅ 搜索完成！正在整理答案...")]
        }
    except Exception as e:
        logger.error(f"搜索失败: {str(e)}")
        return {
            "search_results": f"搜索失败：{e}",
            "step": "search_failed",
            "messages": [AIMessage(content="❌ 搜索遇到问题...")]
        }