from typing import Any

from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client

from mcp_client.config import MCPConfig
from mcp_client.tool import MCPTool
from tools.registry import Registry


class MCPClient:

    def __init__(self, config: MCPConfig) -> None:
        self._config = config
        self._sessions: dict[str, ClientSession] = {}
        self._transports: dict[str, Any] = {}

    async def connect(self, server_name: str) -> list[MCPTool]:
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
        self._transports[server_name] = transport

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

    async def call_tool(self, server_name: str, tool_name: str, arguments: dict[str, Any] | None = None) -> str:
        session = self._sessions[server_name]
        call_result = await session.call_tool(tool_name, arguments)
        result = ""
        for block in call_result.content:
            if hasattr(block, "text"):
                result += block.text

        return result

    async def disconnect(self, server_name: str) -> None:
        session = self._sessions.pop(server_name, None)
        transport = self._transports.pop(server_name, None)
        if session:
            await session.__aexit__(None, None, None)
        if transport:
            await transport.__aexit__(None, None, None)

    async def discover_and_register(self, registry: Registry) -> None:
        for server_name in self._config.servers:
            tools = await self.connect(server_name)
            for tool in tools:
                registry.register(tool)

    async def disconnect_all(self) -> None:
        for server_name in self._config.servers:
            await self.disconnect(server_name)

