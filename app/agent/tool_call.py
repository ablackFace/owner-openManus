from typing import override
from pydantic import Field

from app.agent.react import ReActAgent
from app.tool.bower_use_tool import BrowserUseTool
from app.tool.terminate import Terminate
from app.tool.tool_collection import ToolCollection


class ToolCallAgent(ReActAgent):

    # 构建工具工厂
    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(BrowserUseTool(), Terminate())
    )

    # Pydantic 使用非 `BaseModel` 的类时，需要使用 `arbitrary_types_allowed` 和 `extra` 配置
    class Config:
        arbitrary_types_allowed = True
        extra = "allow"

    def __init__(self) -> None:
        pass

    # ReAct Agent 的思考阶段
    @override
    async def think(self) -> None:

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

        pass
