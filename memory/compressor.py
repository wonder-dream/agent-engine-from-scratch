from agent.llm_client import LLMClient


class Compressor:
    SYSTEM = "你是一个对话摘要助手，请用对应的语言压缩对话历史。"

    async def compress(self, to_compress: list[dict], client: LLMClient) -> str:
        text = "\n".join([f"{m['role']}: {m.get('content', '')}" for m in to_compress])
        response = await client.chat(
            messages=[
                {"role": "system", "content": self.SYSTEM},
                {"role": "user", "content": f"请压缩以下文本\n{text}"},
            ]
        )
        return response["choices"][0]["message"]["content"]

