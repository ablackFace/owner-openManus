from typing import Dict, Optional, Self

from app.config import DEFAULT_LLM_NAME, LLMSettings, config
from openai import AsyncOpenAI


class LLM:
    _instances: Dict[str, "LLM"] = {}

    model: str = ""
    base_url: str = ""
    api_key: str = ""
    max_tokens: int = 0
    temperature: float = 0.0

    def __new__(
        cls,
        config_name: str = DEFAULT_LLM_NAME,
        llm_config: Optional[LLMSettings] = None,
    ) -> Self:
        if config_name not in cls._instances:
            instance = super().__new__(cls)
            instance.__init__(config_name, llm_config)
            cls._instances[config_name] = instance
        return cls._instances[config_name]

    def __init__(
        self,
        config_name: str = DEFAULT_LLM_NAME,
        llm_config: Optional[LLMSettings] = None,
    ) -> None:
        if not hasattr(self, "client"):
            # 获取 config 中的 llm 配置
            llm_config = llm_config or config.llm
            llm_config = llm_config.get(config_name, llm_config[DEFAULT_LLM_NAME])

            # 设置模型配置
            self.model = llm_config.model
            self.base_url = llm_config.base_url
            self.api_key = llm_config.api_key
            self.max_tokens = llm_config.max_tokens
            self.temperature = llm_config.temperature

            # 设置 OpenAI 客户端
            self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)

    async def ask(self, messages: str) -> str:
        completion = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "你是谁？,你必须使用 markdown 格式回答"},
                {"role": "user", "content": "给我画一个如何学习 AI 的流程图"},
            ],
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            stream=True,
        )

        collected_messages = []
        async for chunk in completion:
            chunk_message = chunk.choices[0].delta.content or ""
            collected_messages.append(chunk_message)
            print(chunk_message, end="", flush=True)
