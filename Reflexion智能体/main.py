import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from MemoryReflectionAgent import ReflectionAgent
from llm_client import HelloAgentsLLM


def main():
    task = "编写一个Python函数，找出1到n之间所有的素数 (prime numbers)。"

    try:
        agent = ReflectionAgent(HelloAgentsLLM(), max_iterations=2)
        agent.run(task)
    except ValueError as e:
        print(e)


if __name__ == "__main__":
    main()
