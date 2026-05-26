from dataclasses import dataclass
from typing import Any, Callable

@dataclass
class Tool:
    """一个可被 Agent 调用的工具。

    name 和 description 供 LLM 理解用途，
    parameters 是 JSON Schema（发给 API），
    fn 是实际执行的 Python 函数。
    """
    name: str
    description: str
    parameters: dict    # JSON Schema，如 {"type": "object", "properties": {...}}
    fn: Callable[..., Any] | None = None    # 可调用对象，接收 **kwargs