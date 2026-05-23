from agent import agent
from agent.agent import Agent
from agent.llm_client import LLMClient
import os
from dotenv import load_dotenv

from tools.registry import Registry
from tools.tool import Tool

load_dotenv()

async def test_api_key():

    client = LLMClient(
        model=os.environ["deepseek_model"],
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url=os.environ["DEEPSEEK_BASE_URL"],
    )

    agent = Agent(client, Registry(), "you are helpful assistant")
    response = await agent.execute("hellow world, please reply Chinese")

    print(response)

