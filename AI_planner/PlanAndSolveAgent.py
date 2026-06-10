from Executor import Executor
from Planner import Planner


class PlanAndSolveAgent:
    def __init__(self, llm_client):
        """初始化智能体，同时创建规划器和执行器实例。"""
        self.llm_client = llm_client
        self.planner = Planner(self.llm_client)
        self.executor = Executor(self.llm_client)

    def run(self, question: str):
        """运行智能体的完整流程：先规划，后执行。"""
        print(f"\n--- 开始处理问题 ---\n问题: {question}")

        plan = self.planner.plan(question)
        if not plan:
            print("\n--- 任务终止 --- \n无法生成有效的行动计划。")
            return

        final_answer = self.executor.execute(question, plan)
        print(f"\n--- 任务完成 ---\n最终答案: {final_answer}")
