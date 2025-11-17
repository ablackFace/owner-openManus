from app.agent.tool_call import ToolCallAgent
from app.prompt.manus import SYSTEM_PROMPT, NEXT_STEP_PROMPT


class Manus(ToolCallAgent):
    name: str = "Manus"
