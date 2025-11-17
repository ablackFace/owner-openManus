from typing import List, Literal, Optional
from pydantic import BaseModel, Field

from app.logger import logger
from app.schema import Memory, Message


class BaseAgent(BaseModel):
    max_steps: int = Field(default=30, description="Maximum steps before termination")
    current_step: int = Field(default=0, description="Current step in execution")

    memory: Memory = Field(default_factory=Memory, description="Agent's memory store")

    @property
    def messages(self) -> List[Message]:
        """Retrieve a list of messages from the agent's memory."""
        return self.memory.messages

    @messages.setter
    def messages(self, value: List[Message]):
        """Set the list of messages in the agent's memory."""
        self.memory.messages = value

    async def run(self, request: Optional[str] = None) -> None:

        if request:
            self.update_memory("user", request)

        await self.think()

    def update_memory(
        self,
        role: Literal["user", "system", "assistant", "tool"],
        content: str,
        **kwargs,
    ) -> None:
        """Add a message to the agent's memory.

        Args:
            role: The role of the message sender (user, system, assistant, tool).
            content: The message content.
            **kwargs: Additional arguments (e.g., tool_call_id for tool messages).

        Raises:
            ValueError: If the role is unsupported.
        """
        message_map = {
            "user": Message.user_message,
            "system": Message.system_message,
            "assistant": Message.assistant_message,
            "tool": lambda content, **kw: Message.tool_message(content, **kw),
        }

        if role not in message_map:
            raise ValueError(f"Unsupported message role: {role}")

        msg_factory = message_map[role]
        msg = msg_factory(content, **kwargs) if role == "tool" else msg_factory(content)
        self.memory.add_message(msg)
