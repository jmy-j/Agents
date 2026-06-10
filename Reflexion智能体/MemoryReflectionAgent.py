from INITIAL_PROMPT_TEMPLATE import INITIAL_PROMPT_TEMPLATE
from REFLECT_PROMPT_TEMPLATE import REFLECT_PROMPT_TEMPLATE
from REFINE_PROMPT_TEMPLATE import REFINE_PROMPT_TEMPLATE
from Memory import Memory


class ReflectionAgent:
    def __init__(self, llm_client, max_iterations=3):
        self.llm_client = llm_client
        self.memory = Memory()
        self.max_iterations = max_iterations

    def run(self, task: str):
        print(f"\n--- 开始处理任务 ---\n任务: {task}")

        # --- 1. 初始执行 ---
        print("\n--- 正在进行初始尝试 ---")
        initial_prompt = INITIAL_PROMPT_TEMPLATE.format(task=task)
        initial_code = self._get_llm_response(initial_prompt)
        self.memory.add_record("execution", initial_code)
        self.memory.debug_print("初始执行后")

        # --- 2. 迭代循环:反思与优化 ---
        for i in range(self.max_iterations):
            print(f"\n--- 第 {i + 1}/{self.max_iterations} 轮迭代 ---")

            # a. 反思
            print("\n-> 正在进行反思...")
            last_code = self.memory.get_last_execution()
            reflect_prompt = REFLECT_PROMPT_TEMPLATE.format(
                task=task,
                code=last_code,
                trajectory=self.memory.get_past_trajectory(),
            )
            feedback = self._get_llm_response(reflect_prompt)
            self.memory.add_record("reflection", feedback)
            self.memory.debug_print(f"第 {i + 1} 轮反思后")

            # b. 检查是否需要停止
            if "无需改进" in feedback:
                print("\n✅ 反思认为代码已无需改进，任务完成。")
                break

            # c. 优化
            print("\n-> 正在进行优化...")
            refine_prompt = REFINE_PROMPT_TEMPLATE.format(
                task=task,
                last_code_attempt=last_code,
                feedback=feedback,
                trajectory=self.memory.get_past_trajectory(exclude_last_reflection=True),
            )
            refined_code = self._get_llm_response(refine_prompt)
            self.memory.add_record("execution", refined_code)
            self.memory.debug_print(f"第 {i + 1} 轮优化后")

        final_code = self.memory.get_last_execution()
        self.memory.debug_print("任务完成")
        print(f"\n--- 任务完成 ---\n最终生成的代码:\n```python\n{final_code}\n```")
        return final_code

    def _get_llm_response(self, prompt: str) -> str:
        """一个辅助方法，用于调用LLM并获取完整的流式响应。"""
        messages = [{"role": "user", "content": prompt}]
        response_text = self.llm_client.think(messages=messages)
        if not response_text:
            raise ValueError("LLM 未返回有效响应，请检查 API 配置或网络连接。")
        return response_text
