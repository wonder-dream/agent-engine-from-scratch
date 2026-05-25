from dataclasses import dataclass, field

from mcp.errors import MCPError
from tools.tool import Tool


@dataclass
class MCPTool(Tool):
    server_name: str
    mcp_tool_name: str
    _client: "MCPClient | None" = field(default=None, repr=False)

    def __post_init__(self):
        self.fn = self._call_mcp

    async def _call_mcp(self, **kwargs):
        if self._client is None:
            raise MCPError()
        return await self._client.call_tool(self.server_name, self.mcp_tool_name, kwargs)