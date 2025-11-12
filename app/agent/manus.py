from pydantic import Field

from app.tool.bower_use_tool import BrowserUseTool
from app.tool.tool_collection import ToolCollection


class Manus:
    name: str = "Manus"

    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(BrowserUseTool())
    )
