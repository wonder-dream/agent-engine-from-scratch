import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class MCPServerConfig(BaseModel):
    transport: Literal["stdio", "sse"]
    command: str | None = None
    args: list[str] = Field(default_factory=list)
    env: dict | None = None
    cwd: str | None = None
    url: str | None = None
    headers: dict[str, str] | None = None
    timeout: float = 5
    sse_read_timeout: float = 300

class MCPConfig(BaseModel):
    servers: dict[str, MCPServerConfig]

    @classmethod
    def from_json(cls, path: str | Path) -> "MCPConfig":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.model_validate(data)