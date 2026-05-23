

from agent.agent import Agent
from agent.llm_client import LLMClient
from agent.prompt import Prompt
import os
from dotenv import load_dotenv

load_dotenv()

async def test_api_key():

    client = LLMClient(
        model=os.environ["deepseek_model"],
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url=os.environ["DEEPSEEK_BASE_URL"],
    )

    agent = Agent(client, {}, "you are helpful assistant")
    response = await agent.execute("hellow world, please reply Chinese")

    print(response)