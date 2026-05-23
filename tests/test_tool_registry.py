import os
from dotenv import load_dotenv

from agent.agent import Agent
from agent.llm_client import LLMClient
from tools.registry import Registry
from tools.tool import Tool

load_dotenv()

async def test_tool_registry():
    def get_weather(city: str) -> str:
        return f"{city}今天晴， 25℃"

    client = LLMClient(
        model=os.environ["deepseek_model"],
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url=os.environ["DEEPSEEK_BASE_URL"],
    )

    registry = Registry()
    registry.register(Tool(
        name="get_weather",
        description="查询指定城市的天气",
        parameters={"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]},
        fn=get_weather,
    ))
    agent = Agent(client, registry, "you are helpful assistant")
    response = await agent.execute("北京今天天气怎么样？")
    print(response)