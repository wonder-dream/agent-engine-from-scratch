import asyncio
import json
from typing import AsyncGenerator

from agent.llm_client import LLMClient
from agent.state import AgentState
from memory.manager import MemoryManager
from tools.registry import Registry

from mcp_client.client import MCPClient


class Agent:
    def __init__(self, client: LLMClient, tools: Registry, system_prompt: str,  mcp_client: MCPClient | None = None):
        self.client = client
        self.tools = tools
        self.state = AgentState.IDLE
        self.system_prompt = system_prompt
        self.memory = MemoryManager(self.client)
        self.mcp_client = mcp_client


    async def execute_stream(self, user_input: str) -> AsyncGenerator[dict, None]:
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

                    if self.mcp_client is not None:
                        await self.mcp_client.discover_and_register(self.tools)

                    self.state = AgentState.THOUGHT
                    print(self.state)
                    yield {"state": "idle"}

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

                    yield {"state": "thinking"}

                case AgentState.ACTION:
                    # 从 tool_calls 里取函数名和参数，执行本地函数
                    tc = tool_calls[0]
                    tool_name = tc["function"]["name"]
                    args = tc["function"]["arguments"]  # JSON 字符串
                    parsed_args = json.loads(args)
                    tool = self.tools.get(tool_name)
                    fn = tool.fn
                    results = fn(**parsed_args)
                    if asyncio.iscoroutine(results):
                        results = await results
                    self.state = AgentState.OBSERVATION
                    print(self.state)

                    yield {"state": "action", "tool": tool_name, "args": parsed_args}

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

                    yield {"state": "observation", "results": results}

                case _:
                    raise ValueError("Unknown state")
        await self.memory.finalize()

        if self.mcp_client is not None:
            await self.mcp_client.disconnect_all()

        yield {"state": "final", "answer": final_answer}

    async def execute(self, user_input: str) -> str:
        async for event in self.execute_stream(user_input):
            if event["state"] == "final":
                return event["answer"]
        return ""