import os
from typing import Dict, List

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class HelloAgentsLLM:
    """兼容 OpenAI 接口的 LLM 客户端，默认使用流式响应。"""

    def __init__(
        self,
        model: str | None = None,
        apiKey: str | None = None,
        baseUrl: str | None = None,
        timeout: int | None = None,
    ):
        self.model = model or os.getenv("LLM_MODEL_ID")
        apiKey = apiKey or os.getenv("LLM_API_KEY")
        baseUrl = baseUrl or os.getenv("LLM_BASE_URL")
        timeout = timeout or int(os.getenv("LLM_TIMEOUT", "60"))

        if not all([self.model, apiKey, baseUrl]):
            raise ValueError("模型 ID、API 密钥和服务地址必须在参数或 .env 中提供。")

        self.client = OpenAI(api_key=apiKey, base_url=baseUrl, timeout=timeout)

    def think(self, messages: List[Dict[str, str]], temperature: float = 0) -> str | None:
        """调用大语言模型并返回完整响应文本。"""
        print(f"🧠 正在调用 {self.model} 模型...")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=True,
            )

            print("✅ 大语言模型响应成功:")
            collected_content = []
            for chunk in response:
                if not chunk.choices:
                    continue
                content = chunk.choices[0].delta.content or ""
                print(content, end="", flush=True)
                collected_content.append(content)
            print()
            return "".join(collected_content)

        except Exception as e:
            print(f"❌ 调用 LLM API 时发生错误: {e}")
            return None
