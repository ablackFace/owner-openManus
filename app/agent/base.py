from typing import List, Optional
from pydantic import BaseModel, Field

from app.logger import logger
from app.schema import Message


class BaseAgent(BaseModel):
    max_steps: int = Field(default=30, description="Maximum steps before termination")
    current_step: int = Field(default=0, description="Current step in execution")

    memory: Memory = Field(default_factory=Memory, description="Agent's memory store")

    def __init__(self) -> None:
        pass

    async def run(self, message: Optional[str] = None) -> None:

        results: List[str] = []

        Message.user_message(message)

        await self.think()
