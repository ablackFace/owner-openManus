from pydantic import BaseModel, Field


class BaseTool(BaseModel):
    name: str
    description: str
    parameters: dict


class ToolCollection:
    tools: list[BaseTool]
    tool_map: dict[str, BaseTool]

    def __init__(self, *tools: BaseTool):
        self.tools = tools
        self.tool_map = {tool.name: tool for tool in tools}

    def __iter__(self):
        return iter(self.tools)

    def to_params(self) -> list[dict]:
        return [tool.to_param() for tool in self.tools]
