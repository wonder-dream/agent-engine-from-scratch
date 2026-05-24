import json

from agent.llm_client import LLMClient
from agent.prompt import Prompt
from memory.long_term import LongTermMemory
from memory.short_term import ShortTermMemory


class MemoryManager:
    def __init__(self, client: LLMClient):
        self.long_term_memory = LongTermMemory()
        self.short_term_memory = ShortTermMemory()
        self.client = client

    async def build_context(self, system_prompt: str, user_input: str) -> list[dict]:
        facts = await self.long_term_memory.retrieve(user_input)
        prompt = Prompt(system_prompt)
        messages = prompt.build(user_input, facts=facts)

        self.short_term_memory.set_system(messages[0])
        for msg in messages[1:]:
            self.short_term_memory.add(msg)

        return messages

    def add_message(self, message: dict) -> None:
        self.short_term_memory.add(message)

    async def get_messages(self) -> list[dict]:
        await self.short_term_memory.compress(self.client)
        return await self.short_term_memory.get_messages()

    async def finalize(self) -> None:
        messages = await self.short_term_memory.get_messages()
        text = "\n".join([message.get("content", "") for message in messages])

        response = await self.client.chat(
            messages=[{"role": "user", "content": f"请从以下对话记录中提取关键事实，返回JSON数组：\n\n{text}"}],
        )
        raw = response["choices"][0]["message"]["content"]
        raw = raw.strip().removeprefix("```json").removesuffix("```").strip()
        try:
            facts = json.loads(raw)
        except json.JSONDecodeError:
            facts = [raw]

        facts = [str(f) if not isinstance(f, str) else f for f in facts]

        await self.long_term_memory.store(facts)