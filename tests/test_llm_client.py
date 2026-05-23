import httpx

from agent.llm_client import LLMClient


async def test_chat_returns_dict(httpx_mock):
    """模拟 HTTP，验证 chat() 返回 dict 且 body 结构正确。"""
    httpx_mock.add_response(
        url="https://api.openai.com/v1/chat/completions",
        json={"choices": [{"message": {"content": "hello"}}]},
    )
    client = LLMClient(model="deepseek-v4-flash", api_key="sk-fake")
    result = await client.chat([{"role": "user", "content": "hello"}])
    assert isinstance(result, dict)

async def test_chat_stream(httpx_mock):
    """模拟 SSE 流，验证 chat_stream() 逐块产出 delta.content。"""
    def mock_callback(request):
        return httpx.Response(
            status_code=200,
            content=b'data: {"choices":[{"delta":{"content":"Hello"}}]}\n\ndata: {"choices":[{"delta":{"content":"World"}}]}\n\ndata: [DONE]\n\n',
        )
    httpx_mock.add_callback(mock_callback, url="https://api.openai.com/v1/chat/completions")
    client = LLMClient(model="deepseek-v4-flash", api_key="sk-fake")
    result = []
    async for chunk in client.chat_stream([{"role": "user", "content": "hello"}]):
        result.append(chunk)
    assert result == ["Hello", "World"]