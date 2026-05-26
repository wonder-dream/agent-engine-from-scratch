import importlib
import pkgutil

from tools.tool import Tool


class Registry:
    """工具注册中心，管理所有 Tool 的注册、查找和格式转换。"""

    def __init__(self):
        self.tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """手动注册单个工具。同名工具会被覆盖。"""
        self.tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        """按名称获取工具，不存在时抛 KeyError。"""
        return self.tools[name]

    def to_openai_format(self) -> list[dict]:
        """将所有已注册工具转为 OpenAI tools 格式。"""
        tools = []
        for tool in self.tools.values():
            tools.append({"type": "function",
                          "function":
                              {"name": tool.name,
                               "description": tool.description,
                               "parameters": tool.parameters}})
        return tools

    def discover(self, module_path: str) -> None:
        """扫描指定模块路径，自动注册其中所有 Tool 实例。

        Example: registry.discover("tools.builtin")
        """
        module = importlib.import_module(module_path)

        if hasattr(module, "__path__"):
            # 包：遍历所有子模块
            for _, name, _ in pkgutil.iter_modules(
                    module.__path__,
                    prefix=module.__name__ + ".",
            ):
                sub = importlib.import_module(name)
                for obj in vars(sub).values():
                    if isinstance(obj, Tool):
                        self.register(obj)
        else:
            # 单模块：直接扫
            for obj in vars(module).values():
                if isinstance(obj, Tool):
                    self.register(obj)