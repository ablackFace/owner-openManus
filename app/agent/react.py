from abc import ABC, abstractmethod
from typing import Optional

from pydantic import Field, ConfigDict

from app.agent.base import BaseAgent
from app.llm import LLM


class ReActAgent(ABC, BaseAgent):

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    llm: Optional[LLM] = Field(default_factory=LLM)

    @abstractmethod
    async def think(self) -> None:
        """
        思考阶段：分析当前状态，决定是否需要行动

        这是 ReAct 模式的核心思考环节，Agent 在此阶段需要：
        1. 分析当前的状态和上下文
        2. 评估是否需要执行工具或行动
        3. 决定下一步的策略
        """
        pass

    @abstractmethod
    async def act(self) -> None:
        """
        行动阶段：执行具体行动

        这是 ReAct 模式的核心行动环节，Agent 在此阶段需要：
        1. 执行具体行动
        2. 返回行动结果
        """
        pass

    @abstractmethod
    async def step(self) -> None:
        """
        执行阶段：执行思考和行动

        这是 ReAct 模式的核心执行环节，Agent 在此阶段需要：
        1. 执行思考阶段
        2. 执行行动阶段
        3. 返回行动结果
        """
        should_act = await self.think()
        if not should_act:
            return "Thinking complete - no action needed"
        return await self.act()
