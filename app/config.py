"""
配置管理模块、解析 toml 配置文件
"""

import threading
from pathlib import Path
import tomllib
from typing import Dict, Optional

from pydantic import BaseModel, Field

GET_PROJECT_ROOT = lambda: Path(__file__).resolve().parent.parent


PROJECT_ROOT = GET_PROJECT_ROOT()
WORKSPACE_ROOT = PROJECT_ROOT / "workspace"

DEFAULT_LLM_NAME = "default"


def get_config_path() -> Path:
    """获取配置文件路径"""
    config_path = PROJECT_ROOT / "config" / "config.toml"

    # exists 判断文件是否存在
    if config_path.exists():
        return config_path
    example_path = PROJECT_ROOT / "config" / "config.example.toml"
    if example_path.exists():
        return example_path
    else:
        raise FileNotFoundError("Configuration file not found")


class LLMSettings(BaseModel):
    """
    LLM 模型配置
    """

    model: str = Field(..., description="Model name")
    base_url: str = Field(..., description="API base URL")
    api_key: str = Field(..., description="API key")
    max_tokens: int = Field(4096, description="Maximum number of tokens per request")
    temperature: float = Field(1.0, description="Sampling temperature")


class AppConfig(BaseModel):
    """
    LLM 模型配置字典
    """

    llm: Dict[str, LLMSettings]


class Config:
    """
    获取 llm 模型配置
    """

    _instance = None
    _lock = threading.Lock()
    _initialized = False
    _config: Optional[AppConfig] = None

    @property
    def llm(self) -> Dict[str, LLMSettings]:
        return self._config.llm

    # 单例模式
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    # 初始化
    def __init__(self):
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    self._config = None
                    self._load_config()
                    self._initialized = True

    def _load_config(self):
        config_path = get_config_path()

        # 读取 toml 配置文件
        with config_path.open("rb") as f:
            raw_config = tomllib.load(f)

        base_llm = raw_config.get("llm", {})

        # 读取 llm 配置
        llm_overrides = {k: v for k, v in base_llm.items() if isinstance(v, dict)}

        # 读取默认配置
        default_settings = {
            "model": base_llm.get("model"),
            "base_url": base_llm.get("base_url"),
            "api_key": base_llm.get("api_key"),
            "max_tokens": base_llm.get("max_tokens", 4096),
            "temperature": base_llm.get("temperature", 1.0),
        }

        config_dict = {
            "llm": {
                DEFAULT_LLM_NAME: default_settings,
                **{
                    name: {**default_settings, **override_config}
                    for name, override_config in llm_overrides.items()
                },
            }
        }

        self._config = AppConfig(**config_dict)


config = Config()
