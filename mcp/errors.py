class MCPError(Exception):
    """MCP 客户端通用异常"""
    pass


class MCPConnectionError(MCPError):
    """连接失败或断开"""
    pass


class MCPToolNotFoundError(MCPError):
    """请求的工具在服务器上不存在"""
    pass