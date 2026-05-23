

class Prompt:
    def __init__(self, system_prompt: str, ):
        self.system_prompt = system_prompt

    def build(self, user_prompt: str, tool_list: list | None = None) -> list[dict[str, str]]:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        return messages