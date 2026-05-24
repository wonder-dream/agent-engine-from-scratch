

class Prompt:
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt

    def build(self, user_input: str, facts: list[str] | None = None) -> list[dict[str, str]]:
        content = self.system_prompt
        if facts:
            content += "\n\n你已知晓以下用户相关信息：\n" + "\n".join(f"- {f}" for f in facts)
        return [
            {"role": "system", "content": content},
            {"role": "user", "content": user_input},
        ]
