from typing import AsyncGenerator
import json
import httpx


class LLMClient:

    def __init__(self,
                 model: str,
                 api_key: str,
                 timeout: int = 60,
                 extra_headers: dict | None = None,
                 temperature: float = 0.7,
                 max_tokens: int = 2000,
                 base_url: str = "https://api.openai.com/v1",
                 ):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.timeout = timeout
        self.extra_headers = extra_headers
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def chat(self, messages: list[dict], tool_list: list | None = None) -> dict:
        """发送非流式请求，返回完整响应 JSON。

        Args:
            messages: 对话消息列表，每个元素含 role 和 content。
            tool_list: 可选工具定义列表，不为空时注入 tools 字段。

        Returns:
            API 完整响应字典，choices[0].message 中取 content 或 tool_calls。
        """
        header = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.extra_headers:
            header.update(self.extra_headers)

        json_body = self.build_body(messages, tool_list)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=header,
                json=json_body,
            )
        response.raise_for_status()
        return response.json()

    async def chat_stream(self, messages: list[dict], tool_list: list | None = None) -> AsyncGenerator[str, None]:
        """发送流式请求，异步生成器逐块产出 delta.content 文本。

        Args:
            messages: 对话消息列表，每个元素含 role 和 content。
            tool_list: 可选工具定义列表，不为空时注入 tools 字段。

        Yields:
            每个 chunk 中 delta.content 的文本片段。
        """
        header = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.extra_headers:
            header.update(self.extra_headers)

        json_body = self.build_body(messages, tool_list)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(f"{self.base_url}/chat/completions",
                                         headers=header,
                                         json=json_body,)
            response.raise_for_status()
            # SSE 格式: 每行以 "data: " 开头，以 "[DONE]" 结束
            chunk_response = response.aiter_lines()
            async for line in chunk_response:
                if not line.startswith("data: "):
                    continue
                data = line.removeprefix("data: ")
                if data == "[DONE]":
                    break
                chunk = json.loads(data)
                # delta.content 只在模型输出文本时有值，tool_call 时不在此字段
                content = chunk["choices"][0]["delta"].get("content")
                if content:
                    yield content

    def build_body(self, messages: list[dict], tool_list: list | None = None) -> dict:
        """构建请求体，有 tool_list 时注入 tools 字段。

        Args:
            messages: 对话消息列表。
            tool_list: 可选工具定义列表。

        Returns:
            请求体字典，含 model、messages、temperature、max_tokens 及可选的 tools。
        """
        body_json = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        if tool_list:
            body_json["tools"] = tool_list

        return body_json