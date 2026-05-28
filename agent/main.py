import json
import os
import uuid
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from sse_starlette import EventSourceResponse
from fastapi.middleware.cors import CORSMiddleware

from agent.agent import Agent
from agent.llm_client import LLMClient
from agent.schemas import ChatRequest
from tools.registry import Registry

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()
    client = LLMClient(
        model=os.environ["deepseek_model"],
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url=os.environ["DEEPSEEK_BASE_URL"],
    )
    app.state.client = client

    registry = Registry()
    registry.discover("tools.builtin")
    app.state.registry = registry

    app.state.sessions = {}
    yield



app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,         # type: ignore[arg-type]
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"],
)

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())

    # 拿到或者创建该 session 的 Agent
    if session_id not in app.state.sessions:
        registry = Registry()
        for tool in app.state.registry.tools.values():
            registry.register(tool)
        agent = Agent(
            client=app.state.client,
            tools=registry,
            system_prompt="你是一个有用的AI助手，可以使用工具来帮助用户解决问题。",
        )
        app.state.sessions[session_id] = agent

    agent = app.state.sessions[session_id]

    # 用 SSE 流式返回 execute_stream 的结果
    async def _gen():
        async for event in agent.execute_stream(request.message):
            event["session_id"] = session_id
            yield {"event": event["state"], "data": json.dumps(event, ensure_ascii=False)}

    return EventSourceResponse(_gen())

@app.get("/health")
async def health():
    return {"status": "ok"}