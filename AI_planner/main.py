import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from PlanAndSolveAgent import PlanAndSolveAgent
from llm_client import HelloAgentsLLM


def main():
    question = (
        "一个水果店周一卖出了15个苹果。周二卖出的苹果数量是周一的两倍。"
        "周三卖出的数量比周二少了5个。请问这三天总共卖出了多少个苹果？"
    )

    try:
        agent = PlanAndSolveAgent(HelloAgentsLLM())
        agent.run(question)
    except ValueError as e:
        print(e)


if __name__ == "__main__":
    main()
