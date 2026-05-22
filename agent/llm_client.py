import httpx
from httpx import AsyncClient

class LLMClient:

    def __init__(self,
                 model: str,
                 api_key: str,
                 default_system_prompt: str | None = None,
                 timeout: int = 60,
                 extra_headers: dict | None = None,
                 temperature: float = 0.7,
                 max_tokens: int = 2000,
                 base_url: str = "https://api.openai.com/v1",
                 ):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.default_system_prompt = default_system_prompt
        self.timeout = timeout
        self.extra_headers = extra_headers
        self.temperature = temperature
        self.max_tokens = max_tokens

    async def chat(self, messages: list[dict]) -> dict:
        header ={
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.extra_headers:
            header.update(self.extra_headers)

        if self.default_system_prompt:
            messages = [{"role": "system", "content": self.default_system_prompt}] + messages

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(f"{self.base_url}/chat/completions",
                                         headers=header,
                                         json={
                                             "model": self.model,
                                             "messages": messages,
                                             "temperature": self.temperature,
                                             "max_tokens": self.max_tokens,
                                         })
        response.raise_for_status()
        json_response = response.json()

        return json_response