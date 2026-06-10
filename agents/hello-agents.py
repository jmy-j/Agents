import re
import os
from dotenv import load_dotenv

# --- 1. 加载环境变量 ---
load_dotenv()

# --- 2. 配置LLM客户端 ---
API_KEY = os.getenv("LLM_API_KEY", "YOUR_API_KEY")
BASE_URL = os.getenv("LLM_BASE_URL", "YOUR_BASE_URL")
MODEL_ID = os.getenv("LLM_MODEL_ID", "YOUR_MODEL_ID")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "YOUR_TAVILY_API_KEY")
os.environ['TAVILY_API_KEY'] = TAVILY_API_KEY

# --- 3. 导入依赖 ---
from OpenAICompatibleClient import OpenAICompatibleClient
from available_tools import available_tools

# --- 4. 初始化LLM客户端 ---
llm = OpenAICompatibleClient(
    model=MODEL_ID,
    api_key=API_KEY,
    base_url=BASE_URL
)

# --- 5. Agent系统提示词 ---
AGENT_SYSTEM_PROMPT = """
你是一个智能助手，可以调用工具来完成任务。

可用工具：
1. get_weather(city="城市名") - 查询指定城市的天气
2. get_attraction(city="城市名", weather="天气描述") - 根据天气推荐旅游景点

当你收到用户请求时，请按照以下格式输出：
Thought: 你的思考过程，说明为什么要调用这个工具
Action: 工具调用，格式为 工具名(参数名="参数值")

当任务完成时，请输出：
Action: Finish[最终答案]

请严格按照上述格式输出，不要有多余内容。
"""

# --- 6. 初始化 ---
user_prompt = "你好，请帮我查询一下今天北京的天气，然后根据天气推荐一个合适的旅游景点。"
prompt_history = [f"用户请求: {user_prompt}"]

print(f"用户输入: {user_prompt}\n" + "=" * 40)

# --- 7. 运行主循环 ---
for i in range(5):  # 设置最大循环次数
    print(f"--- 循环 {i + 1} ---\n")

    # 7.1. 构建Prompt
    full_prompt = "\n".join(prompt_history)

    # 7.2. 调用LLM进行思考
    llm_output = llm.generate(full_prompt, system_prompt=AGENT_SYSTEM_PROMPT)
    # 模型可能会输出多余的Thought-Action，需要截断
    match = re.search(r'(Thought:.*?Action:.*?)(?=\n\s*(?:Thought:|Action:|Observation:)|\Z)', llm_output, re.DOTALL)
    if match:
        truncated = match.group(1).strip()
        if truncated != llm_output.strip():
            llm_output = truncated
            print("已截断多余的 Thought-Action 对")
    print(f"模型输出:\n{llm_output}\n")
    prompt_history.append(llm_output)

    # 7.3. 解析并执行行动
    action_match = re.search(r"Action: (.*)", llm_output, re.DOTALL)
    if not action_match:
        observation = "错误: 未能解析到 Action 字段。请确保你的回复严格遵循 'Thought: ... Action: ...' 的格式。"
        observation_str = f"Observation: {observation}"
        print(f"{observation_str}\n" + "=" * 40)
        prompt_history.append(observation_str)
        continue
    action_str = action_match.group(1).strip()

    if action_str.startswith("Finish"):
        final_answer = re.match(r"Finish\[(.*)\]", action_str).group(1)
        print(f"任务完成，最终答案: {final_answer}")
        break

    tool_name = re.search(r"(\w+)\(", action_str).group(1)
    args_str = re.search(r"\((.*)\)", action_str).group(1)
    kwargs = dict(re.findall(r'(\w+)="([^"]*)"', args_str))

    if tool_name in available_tools:
        observation = available_tools[tool_name](**kwargs)
    else:
        observation = f"错误:未定义的工具 '{tool_name}'"

    # 7.4. 记录观察结果
    observation_str = f"Observation: {observation}"
    print(f"{observation_str}\n" + "=" * 40)
    prompt_history.append(observation_str)