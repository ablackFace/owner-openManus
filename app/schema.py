from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    id: str = Field(..., description="工具调用 ID")
    type: Literal["function"] = Field(..., description="工具调用类型")
    function: dict = Field(..., description="工具调用函数")


class Message(BaseModel):

    role: Literal["system", "user", "assistant", "tool"] = Field(
        ..., description="消息角色"
    )
    content: str = Field(..., description="消息内容")
    tool_calls: List[ToolCall] = Field(default_factory=list, description="工具调用")
    name: str = Field(default=None, description="工具名称")
    tool_call_id: str = Field(default=None, description="工具调用 ID")

    def __add__(self, other: "Message") -> "Message":
        """支持 Message + list 或 Message + Message 的操作"""
        if isinstance(other, list):
            return [self] + other
        elif isinstance(other, Message):
            return [self, other]
        else:
            raise TypeError(
                f"unsupported operand type(s) for +: '{type(self).__name__}' and '{type(other).__name__}'"
            )

    def __radd__(self, other: list) -> list["Message"]:
        """支持 list + Message 的操作"""
        if isinstance(other, list):
            return other + [self]
        else:
            raise TypeError(
                f"unsupported operand type(s) for +: '{type(other).__name__}' and '{type(self).__name__}'"
            )

    def to_dict(self) -> dict:
        """将 Message 对象转换为字典"""
        message = {"role": self.role}
        if self.content is not None:
            message["content"] = self.content
        if self.tool_calls:  # 检查列表是否非空
            message["tool_calls"] = [tool_call.dict() for tool_call in self.tool_calls]
        if self.name is not None:
            message["name"] = self.name
        if self.tool_call_id is not None:
            message["tool_call_id"] = self.tool_call_id
        return message

    @classmethod
    def user_message(cls, content: str) -> "Message":
        """创建用户消息"""
        return cls(role="user", content=content)

    @classmethod
    def system_message(cls, content: str) -> "Message":
        """创建系统消息"""
        return cls(role="system", content=content)

    @classmethod
    def tool_message(cls, content: str, name, tool_call_id: str) -> "Message":
        """Create a tool message"""
        return cls(role="tool", content=content, name=name, tool_call_id=tool_call_id)

    @classmethod
    def assistant_message(cls, content: Optional[str] = None) -> "Message":
        """Create an assistant message"""
        return cls(role="assistant", content=content)


# 记忆、上下文管理
class Memory(BaseModel):
    messages: List[Message] = Field(default_factory=list)
    max_messages: int = Field(default=100)

    def add_message(self, message: Message) -> None:
        """添加消息到记忆"""
        self.messages.append(message)
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages :]

    def add_messages(self, messages: List[Message]) -> None:
        """添加多条消息到记忆"""
        self.messages.extend(messages)

    def clear(self) -> None:
        """清空所有消息"""
        self.messages.clear()

    def get_recent_messages(self, n: int) -> List[Message]:
        """获取最近的n条消息"""
        return self.messages[-n:]

    def to_dict_list(self) -> List[dict]:
        """将消息转换为字典列表"""
        return [msg.to_dict() for msg in self.messages]
