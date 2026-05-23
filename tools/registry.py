from tools.tool import Tool


class Registry:
    def __init__(self):
        self.tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self.tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        return self.tools[name]

    def to_openai_format(self) -> list[dict]:
        tools = []
        for tool in self.tools.values():
            tools.append({"type": "function",
                          "function":
                              {"name": tool.name,
                               "description": tool.description,
                               "parameters": tool.parameters}})
        return tools