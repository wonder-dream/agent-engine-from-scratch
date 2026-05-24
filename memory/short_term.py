import collections

from agent.llm_client import LLMClient
from memory.compressor import Compressor


class ShortTermMemory:
    def __init__(self, max_window: int = 20):
        self._system: dict | None = None
        self._messages = collections.deque(maxlen=max_window)
        self.compressor = Compressor()
        self._summary: str | None = None

    def set_system(self, system: dict) -> None:
        self._system = system

    def add(self, msg: dict) -> None:
        self._messages.append(msg)

    async def get_messages(self) -> list[dict]:
        result = []
        if self._system:
            result.append(self._system)
        if self._summary:
            result.append({"role": "system", "content": f"对话历史摘要：{self._summary}"})
        result.extend(self._messages)
        return result

    async def compress(self, client: LLMClient) -> None:
        if len(self._messages) >= 16:
            to_compress = self.left_messages()
            self._summary = await self.compressor.compress(to_compress, client)

    def left_messages(self) -> list[dict]:
        to_compress = []
        while len(self._messages) > 4:
            to_compress.append(self._messages.popleft())
        return to_compress
