from typing import List, Literal, override
from pydantic import Field

from app.agent.react import ReActAgent
from app.logger import logger
from app.prompt.manus import NEXT_STEP_PROMPT, SYSTEM_PROMPT
from app.tool.bower_use_tool import BrowserUseTool
from app.tool.terminate import Terminate
from app.tool.tool_collection import ToolCollection
from app.schema import Message, ToolCall


class ToolCallAgent(ReActAgent):

    name: str = "toolcall"
    description: str = "an agent that can execute tool calls."

    system_prompt: str = SYSTEM_PROMPT
    next_step_prompt: str = NEXT_STEP_PROMPT

    tool_choices: Literal["none", "auto", "required"] = "auto"
    special_tool_names: List[str] = Field(default_factory=lambda: [Terminate().name])

    tool_calls: List[ToolCall] = Field(default_factory=list)

    max_steps: int = 30

    # Function tools
    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(BrowserUseTool(), Terminate())
    )

    # Pydantic 使用非 `BaseModel` 的类时，需要使用 `arbitrary_types_allowed` 和 `extra` 配置
    class Config:
        arbitrary_types_allowed = True
        extra = "allow"

    # ReAct Agent 的思考阶段
    @override
    async def think(self) -> None:

        # 添加下一步提示
        if self.next_step_prompt:
            user_msg = Message.user_message(self.next_step_prompt)
            self.messages += [user_msg]

        response = await self.llm.ask_tool(
            messages=self.messages,
            system_msgs=(
                [Message.system_message(self.system_prompt)]
                if self.system_prompt
                else None
            ),
            tools=self.available_tools.to_params(),
            tool_choice=self.tool_choices,
        )
        self.tool_calls = response.tool_calls

        # Log response info
        logger.info(f"✨ {self.name} 思考: {response.content}")
        logger.info(f"Function Tools: 🛠️ {self.tool_calls}")

    @override
    async def act(self) -> None:
        pass

    @override
    async def step(self) -> None:
        pass
