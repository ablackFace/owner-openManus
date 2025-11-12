from pydantic import BaseModel, Field


class BaseTool(BaseModel):
    name: str
    description: str
    parameters: dict


class ToolCollection(BaseModel):
    tools: list[BaseTool]
    tool_map: dict[str, BaseTool]

    def __init__(self, *tools: BaseTool):
        self.tools = tools
        self.tool_map = {tool.name: tool for tool in tools}
