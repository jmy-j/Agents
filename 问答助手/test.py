"""问答助手测试文件"""
import unittest
from unittest.mock import Mock, patch
from all import SearchState
from search_query import understand_query_node
from api import tavily_search_node
from answer import generate_answer_node
from langchain_core.messages import HumanMessage


class TestSearchQuery(unittest.TestCase):
    """测试搜索查询理解节点"""

    @patch('search_query.llm')
    def test_understand_query_node(self, mock_llm):
        """测试理解用户查询"""
        mock_response = Mock()
        mock_response.content = "理解：用户想了解Python\n搜索词：Python programming"
        mock_llm.invoke.return_value = mock_response

        state = SearchState(
            messages=[HumanMessage(content="什么是Python？")],
            user_query="",
            search_query="",
            search_results="",
            final_answer="",
            step=""
        )

        result = understand_query_node(state)

        self.assertEqual(result["step"], "understood")
        self.assertEqual(result["search_query"], "Python programming")
        self.assertIn("我将为您搜索：Python programming", str(result["messages"]))


class TestApi(unittest.TestCase):
    """测试搜索API节点"""

    @patch('api.tavily_client')
    def test_tavily_search_success(self, mock_tavily):
        """测试搜索成功"""
        mock_response = {
            "answer": "Python是一种编程语言",
            "results": [
                {"title": "Python官网", "url": "https://python.org", "content": "Python介绍"}
            ]
        }
        mock_tavily.search.return_value = mock_response

        state = SearchState(
            messages=[],
            user_query="",
            search_query="Python",
            search_results="",
            final_answer="",
            step="understood"
        )

        result = tavily_search_node(state)

        self.assertEqual(result["step"], "searched")
        self.assertIn("Python官网", result["search_results"])

    @patch('api.tavily_client')
    def test_tavily_search_failure(self, mock_tavily):
        """测试搜索失败"""
        mock_tavily.search.side_effect = Exception("网络错误")

        state = SearchState(
            messages=[],
            user_query="",
            search_query="Python",
            search_results="",
            final_answer="",
            step="understood"
        )

        result = tavily_search_node(state)

        self.assertEqual(result["step"], "search_failed")


class TestAnswer(unittest.TestCase):
    """测试答案生成节点"""

    @patch('answer.llm')
    def test_generate_answer_with_search(self, mock_llm):
        """测试基于搜索结果生成答案"""
        mock_response = Mock()
        mock_response.content = "Python是一种高级编程语言"
        mock_llm.invoke.return_value = mock_response

        state = SearchState(
            messages=[],
            user_query="什么是Python",
            search_query="",
            search_results="搜索结果内容",
            final_answer="",
            step="searched"
        )

        result = generate_answer_node(state)

        self.assertEqual(result["step"], "completed")
        self.assertEqual(result["final_answer"], "Python是一种高级编程语言")

    @patch('answer.llm')
    def test_generate_answer_fallback(self, mock_llm):
        """测试回退策略"""
        mock_response = Mock()
        mock_response.content = "基于知识的回答"
        mock_llm.invoke.return_value = mock_response

        state = SearchState(
            messages=[],
            user_query="什么是Python",
            search_query="",
            search_results="",
            final_answer="",
            step="search_failed"
        )

        result = generate_answer_node(state)

        self.assertEqual(result["step"], "completed")


if __name__ == "__main__":
    unittest.main(verbosity=2)