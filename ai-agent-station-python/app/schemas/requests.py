from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    code: str = "0000"
    info: str = "成功"
    data: Optional[T] = None


class AutoAgentRequest(BaseModel):
    aiAgentId: str
    message: str = Field(max_length=1000)
    sessionId: str
    maxStep: int = 5


class ArmoryAgentRequest(BaseModel):
    agentId: str


class ArmoryApiRequest(BaseModel):
    apiId: str


class AiAgentResponse(BaseModel):
    agentId: str
    agentName: str
    description: Optional[str] = None
    channel: Optional[str] = None
    strategy: Optional[str] = None
    status: Optional[int] = None


class ExecuteCommand(BaseModel):
    ai_agent_id: str
    message: str
    session_id: str
    max_step: int = 5
