from typing import Any

from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client

from mcp.config import MCPConfig
from mcp.tool import MCPTool


class MCPClient:

    def __init__(self, config: MCPConfig) -> None:
        self._config = config
        self._sessions: dict[str, ClientSession] = {}

    async def connect(self, server_name: str) -> list[Any]:
        cfg = self._config.servers[server_name]

        if cfg.transport == "stdio":
            params = StdioServerParameters(
                command=cfg.command or "",
                args=cfg.args,
                env=cfg.env,
                cwd=cfg.cwd,
            )
            transport = stdio_client(params)

        else:
            transport = sse_client(
                url=cfg.url or "",
                headers=cfg.headers,
                timeout=cfg.timeout,
                sse_read_timeout=cfg.sse_read_timeout,
            )

        read, write = await transport.__aenter__()

        session = ClientSession(read, write)
        await session.__aenter__()
        self._sessions[server_name] = session

        await session.initialize()
        result = await session.list_tools()

        tools= []
        for mcp_tool in result.tools:
            tool = MCPTool(
                name=mcp_tool.name,
                description=mcp_tool.description or "",
                parameters=mcp_tool.inputSchema,
                server_name=server_name,
                mcp_tool_name=mcp_tool.name,
            )
            tool._client = self
            tools.append(tool)
        return tools