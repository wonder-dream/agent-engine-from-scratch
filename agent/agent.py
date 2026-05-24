import json

from agent.llm_client import LLMClient
from agent.state import AgentState
from memory.manager import MemoryManager
from tools.registry import Registry


class Agent:
    def __init__(self, client: LLMClient, tools: Registry, system_prompt: str):
        self.client = client
        self.tools = tools
        self.state = AgentState.IDLE
        self.system_prompt = system_prompt
        self.memory = MemoryManager(self.client)


    async def execute(self, user_input: str) -> str:
        self.state = AgentState.IDLE
        print(self.state)

        # msg:      LLM 返回的当前轮 message（含 content 或 tool_calls）
        # tool_calls: 本轮解析出的工具调用列表，每个元素含 id/type/function
        # results:    工具函数的返回值
        # final_answer: 最终给用户的文本回复
        msg: dict = {}
        tool_calls: list[dict] = []
        results: list = []
        final_answer: str = ""
        messages: list = []

        while self.state != AgentState.FINAL_ANSWER:
            match self.state:
                case AgentState.IDLE:
                    # 用 Prompt 组装 system + user 消息，初始化 messages
                    messages = await self.memory.build_context(self.system_prompt, user_input)
                    self.state = AgentState.THOUGHT
                    print(self.state)

                case AgentState.THOUGHT:
                    # 调 LLM，传入工具列表。LLM 决定返回文本还是 tool_calls
                    response = await self.client.chat(
                        messages=messages,
                        tool_list=self.tools.to_openai_format(),
                    )
                    msg = response["choices"][0]["message"]
                    tool_calls = msg.get("tool_calls", [])
                    if tool_calls:
                        self.state = AgentState.ACTION
                        print(self.state)
                    else:
                        # 没有 tool_calls 就是最终回答
                        final_answer = msg.get("content", "")
                        self.state = AgentState.FINAL_ANSWER
                        print(self.state)

                case AgentState.ACTION:
                    # 从 tool_calls 里取函数名和参数，执行本地函数
                    tc = tool_calls[0]
                    tool_name = tc["function"]["name"]
                    args = tc["function"]["arguments"]  # JSON 字符串
                    parsed_args = json.loads(args)
                    results = self.tools.get(tool_name).fn(**parsed_args)
                    self.state = AgentState.OBSERVATION
                    print(self.state)

                case AgentState.OBSERVATION:
                    # 把模型的 tool_calls 响应和工具结果追加回 messages，
                    # 然后跳回 THOUGHT 让 LLM 基于结果继续推理
                    self.memory.add_message(msg)
                    self.memory.add_message({
                        "role": "tool",
                        "tool_call_id": tool_calls[0]["id"],
                        "content": json.dumps(results, ensure_ascii=False),
                    })
                    messages = await self.memory.get_messages()
                    self.state = AgentState.THOUGHT
                    print(self.state)

                case _:
                    raise ValueError("Unknown state")
        await self.memory.finalize()
        return final_answer