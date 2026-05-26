from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from mcp_client import MCPServerConfig, MCPConfig, MCPClient, MCPTool
from tools.registry import Registry


@pytest.fixture
def stdio_config():
    return MCPConfig(servers={"test": MCPServerConfig(transport="stdio", command="echo")})

@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.__aenter__.return_value = session
    session.__aexit__.return_value = session
    session.initialize.return_value = session
    session.list_tools.return_value = session
    return session

@pytest.fixture
def mock_transport():
    transport = AsyncMock()
    transport.__aenter__.return_value = (MagicMock(), MagicMock())
    transport.__aexit__.return_value = transport
    return transport

@pytest.mark.asyncio
async def test_connect(mock_session, mock_transport, stdio_config):
    fake_tool = MagicMock()
    fake_tool.name = "fake_tool"
    fake_tool.description = "fake_tool_description"
    fake_tool.inputSchema = "fake_tool_inputSchema"

    result = MagicMock()
    result.tools = [fake_tool]
    mock_session.list_tools.return_value = result

    with patch("mcp_client.client.stdio_client", return_value=mock_transport):
        with patch("mcp_client.client.ClientSession", return_value=mock_session):
            client = MCPClient(stdio_config)
            tools = await client.connect("test")
            assert len(tools) == 1
            assert isinstance(tools[0], MCPTool)
            assert tools[0].name == "fake_tool"
            assert tools[0]._client is client


@pytest.mark.asyncio
async def test_call_tool(mock_session, mock_transport, stdio_config):
    fake_block = MagicMock()
    fake_block.text = "hello world"
    fake_call_result = MagicMock()
    fake_call_result.content = [fake_block]
    mock_session.call_tool = AsyncMock(return_value=fake_call_result)
    mock_session.list_tools.return_value = MagicMock(tools=[])

    with patch("mcp_client.client.stdio_client", return_value=mock_transport):
        with patch("mcp_client.client.ClientSession", return_value=mock_session):
            client = MCPClient(stdio_config)
            await client.connect("test")
            result = await client.call_tool("test", "echo", {"msg": "hi"})

            assert result == "hello world"
            mock_session.call_tool.assert_called_once_with("echo", {"msg": "hi"})


@pytest.mark.asyncio
async def test_disconnect(mock_session, mock_transport, stdio_config):
    mock_session.list_tools.return_value = MagicMock(tools=[])

    with patch("mcp_client.client.stdio_client", return_value=mock_transport):
        with patch("mcp_client.client.ClientSession", return_value=mock_session):
            client = MCPClient(stdio_config)
            await client.connect("test")
            await client.disconnect("test")

            mock_session.__aexit__.assert_called_once()
            mock_transport.__aexit__.assert_called_once()
            assert "test" not in client._sessions
            assert "test" not in client._transports


@pytest.mark.asyncio
async def test_discover_and_register(stdio_config):
    client = MCPClient(stdio_config)
    fake_tool = MCPTool(
        name="remote_tool",
        description="a remote tool",
        parameters={},
        server_name="test",
        mcp_tool_name="remote_tool",
    )
    client.connect = AsyncMock(return_value=[fake_tool])

    registry = Registry()
    await client.discover_and_register(registry)

    assert registry.get("remote_tool") is fake_tool
    client.connect.assert_called_once_with("test")

