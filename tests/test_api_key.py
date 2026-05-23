from agent.agent import Agent
from agent.llm_client import LLMClient
import os
from dotenv import load_dotenv

from tools.registry import Registry

load_dotenv()

async def test_api_key():
    """验证 Agent 无工具场景：DeepSeek API 直接回复。"""

    client = LLMClient(
        model=os.environ["deepseek_model"],
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url=os.environ["DEEPSEEK_BASE_URL"],
    )

    agent = Agent(client, Registry(), "you are helpful assistant")
    response = await agent.execute("hellow world, please reply Chinese")

    print(response)

