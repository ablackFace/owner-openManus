from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class BaseTool(ABC, BaseModel):

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """FunctionCall 的执行方法"""
        pass

    def to_param(self) -> dict:
        """转换为LLM函数调用格式"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }
