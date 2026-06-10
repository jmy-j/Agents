import ast
import json
import re

from PLANNER_PROMPT_TEMPLATE import PLANNER_PROMPT_TEMPLATE


class Planner:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    def _parse_plan(self, response_text: str) -> list[str]:
        """从 LLM 响应中解析步骤列表。"""
        candidates = []

        for pattern in (r"```python\s*(.*?)```", r"```json\s*(.*?)```", r"```\s*(.*?)```"):
            match = re.search(pattern, response_text, re.DOTALL)
            if match:
                candidates.append(match.group(1).strip())

        candidates.append(response_text.strip())

        for candidate in candidates:
            for parser in (ast.literal_eval, json.loads):
                try:
                    plan = parser(candidate)
                    if isinstance(plan, list) and plan:
                        return [str(item) for item in plan]
                except (ValueError, SyntaxError, json.JSONDecodeError, TypeError):
                    continue

        return []

    def plan(self, question: str) -> list[str]:
        """根据用户问题生成一个行动计划。"""
        prompt = PLANNER_PROMPT_TEMPLATE.format(question=question)
        messages = [{"role": "user", "content": prompt}]

        print("--- 正在生成计划 ---")
        response_text = self.llm_client.think(messages=messages) or ""

        print(f"✅ 计划已生成:\n{response_text}")

        try:
            plan = self._parse_plan(response_text)
            if not plan:
                print("❌ 解析计划时出错: 未能从响应中提取有效列表")
                print(f"原始响应: {response_text}")
            return plan
        except Exception as e:
            print(f"❌ 解析计划时发生未知错误: {e}")
            print(f"原始响应: {response_text}")
            return []
