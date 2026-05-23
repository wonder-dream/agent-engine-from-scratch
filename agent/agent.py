from typing import Callable, Any

from agent.llm_client import LLMClient
from agent.prompt import Prompt
from agent.state import AgentState


class Agent:
    def __init__(self, client: LLMClient, tools: dict[str, Callable], system_prompt: str):
        self.client = client
        self.tools = tools
        self.state = AgentState.IDLE
        self.system_prompt = system_prompt
        self.messages: list[dict] = []
        self.prompt = Prompt(system_prompt)


    async def execute(self, user_input: str) -> str:
        self.state = AgentState.IDLE
        print(self.state)

        msg = {}
        tool_calls = []
        results = []
        final_answer = ""

        while self.state != AgentState.FINAL_ANSWER:
            match self.state:
                case AgentState.IDLE:
                    self.messages = self.prompt.build(user_input)
                    self.state = AgentState.THOUGHT
                    print(self.state)

                case AgentState.THOUGHT:
                    response = await self.client.chat(messages=self.messages)
                    msg = response["choices"][0]["message"]
                    tool_calls = msg.get("tool_calls", [])
                    if tool_calls:
                        self.state = AgentState.ACTION
                        print(self.state)
                    else:
                        final_answer = msg.get("content")
                        self.state = AgentState.FINAL_ANSWER
                        print(self.state)

                case AgentState.ACTION:
                    raise NotImplementedError

                case AgentState.OBSERVATION:
                    raise NotImplementedError

                case _:
                    raise ValueError("Unknown state")

        return final_answer