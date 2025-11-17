from typing import Dict, List, Literal, Optional, Self, Union

from loguru import logger
from openai import (
    APIError,
    AsyncOpenAI,
    AuthenticationError,
    OpenAIError,
    RateLimitError,
)

from app.config import DEFAULT_LLM_NAME, LLMSettings, config
from app.schema import Message
from tenacity import retry, stop_after_attempt, wait_random_exponential


class LLM:
    _instances: Dict[str, "LLM"] = {}

    model: str = ""
    base_url: str = ""
    api_key: str = ""
    max_tokens: int = 0
    temperature: float = 0.0

    # 单例
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

    # 初始化、获取 LLM config、设置模型配置、设置 OpenAI 客户端
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

    async def ask(self, messages: List[Union[dict, Message]]) -> str:
        messages = self.format_messages(messages)

        completion = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            stream=True,
        )

        collected_messages = []
        async for chunk in completion:
            chunk_message = chunk.choices[0].delta.content or ""
            collected_messages.append(chunk_message)
            print(chunk_message, end="", flush=True)

    # 格式化消息
    def format_messages(self, messages: List[Union[dict, Message]]) -> List[Message]:
        """
        Format messages for LLM by converting them to OpenAI message format.

        Args:
            messages: List of messages that can be either dict or Message objects

        Returns:
            List[dict]: List of formatted messages in OpenAI format

        Raises:
            ValueError: If messages are invalid or missing required fields
            TypeError: If unsupported message types are provided

        Examples:
            >>> msgs = [
            ...     Message.system_message("You are a helpful assistant"),
            ...     {"role": "user", "content": "Hello"},
            ...     Message.user_message("How are you?")
            ... ]
            >>> formatted = LLM.format_messages(msgs)
        """

        formatted_messages = []

        for message in messages:
            if isinstance(message, dict):
                if "role" not in message:
                    raise ValueError("Message dict must contain 'role' field")
                formatted_messages.append(message)

            elif isinstance(message, Message):
                formatted_messages.append(message.to_dict())

            else:
                raise TypeError(f"Unsupported message type: {type(message)}")

        # 检测消息格式是否正确
        for msg in formatted_messages:
            if msg["role"] not in ["system", "user", "assistant", "tool"]:
                raise ValueError(f"Invalid role: {msg['role']}")
            if "content" not in msg and "tool_calls" not in msg:
                raise ValueError(
                    "Message must contain either 'content' or 'tool_calls'"
                )

        return formatted_messages

    @retry(
        wait=wait_random_exponential(min=1, max=60),
        stop=stop_after_attempt(6),
    )
    async def ask_tool(
        self,
        messages: List[Union[dict, Message]],
        system_msgs: Optional[List[Union[dict, Message]]] = None,
        timeout: int = 60,
        tools: Optional[List[dict]] = None,
        tool_choice: Literal["none", "auto", "required"] = "auto",
        temperature: Optional[float] = None,
        **kwargs,
    ):
        """
        使用函数/工具向LLM询问并返回响应。

        参数:
            messages: 对话消息列表
            system_msgs: 可选的系统消息，将添加到前面
            timeout: 请求超时时间（秒）
            tools: 要使用的工具列表
            tool_choice: 工具选择策略
            temperature: 响应的采样温度
            **kwargs: 其他完成参数

        返回:
            ChatCompletionMessage: 模型的响应

        异常:
            ValueError: 如果工具、工具选择或消息无效
            OpenAIError: 如果API调用重试后失败
            Exception: 对于意外错误
        """
        try:
            # Validate tool_choice
            if tool_choice not in ["none", "auto", "required"]:
                raise ValueError(f"Invalid tool_choice: {tool_choice}")

            # Format messages
            if system_msgs:
                system_msgs = self.format_messages(system_msgs)
                messages = system_msgs + self.format_messages(messages)
            else:
                messages = self.format_messages(messages)

            logger.info(f"ask_tool messages: {messages}")

            # Validate tools if provided
            if tools:
                for tool in tools:
                    if not isinstance(tool, dict) or "type" not in tool:
                        raise ValueError("Each tool must be a dict with 'type' field")

            # Set up the completion request
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=self.max_tokens,
                tools=tools,
                tool_choice=tool_choice,
                timeout=timeout,
                **kwargs,
            )

            # Check if response is valid
            if not response.choices or not response.choices[0].message:
                print(response)
                raise ValueError("Invalid or empty response from LLM")

            return response.choices[0].message

        except ValueError as ve:
            logger.error(f"Validation error in ask_tool: {ve}")
            raise
        except OpenAIError as oe:
            if isinstance(oe, AuthenticationError):
                logger.error("Authentication failed. Check API key.")
            elif isinstance(oe, RateLimitError):
                logger.error("Rate limit exceeded. Consider increasing retry attempts.")
            elif isinstance(oe, APIError):
                logger.error(f"API error: {oe}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in ask_tool: {e}")
            raise
