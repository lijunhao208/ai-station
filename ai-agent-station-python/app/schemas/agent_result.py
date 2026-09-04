import time
from typing import Optional

from pydantic import BaseModel, Field


class AgentExecuteResult(BaseModel):
    type: str
    subType: Optional[str] = None
    step: Optional[int] = None
    content: str
    completed: bool = False
    timestamp: int = Field(default_factory=lambda: int(time.time() * 1000))
    sessionId: str

    @classmethod
    def analysis_sub(cls, step: int, sub_type: str, content: str, session_id: str) -> "AgentExecuteResult":
        return cls(type="analysis", subType=sub_type, step=step, content=content, sessionId=session_id)

    @classmethod
    def execution_sub(cls, step: int, sub_type: str, content: str, session_id: str) -> "AgentExecuteResult":
        return cls(type="execution", subType=sub_type, step=step, content=content, sessionId=session_id)

    @classmethod
    def supervision(cls, step: int, content: str, session_id: str) -> "AgentExecuteResult":
        return cls(type="supervision", step=step, content=content, sessionId=session_id)

    @classmethod
    def supervision_sub(cls, step: int, sub_type: str, content: str, session_id: str) -> "AgentExecuteResult":
        return cls(type="supervision", subType=sub_type, step=step, content=content, sessionId=session_id)

    @classmethod
    def summary_sub(cls, sub_type: str, content: str, session_id: str) -> "AgentExecuteResult":
        return cls(type="summary", subType=sub_type, step=4, content=content, sessionId=session_id)

    @classmethod
    def summary(cls, content: str, session_id: str) -> "AgentExecuteResult":
        return cls(type="summary", content=content, completed=True, sessionId=session_id)

    @classmethod
    def error(cls, content: str, session_id: str) -> "AgentExecuteResult":
        return cls(type="error", content=content, completed=True, sessionId=session_id)

    @classmethod
    def complete(cls, session_id: str) -> "AgentExecuteResult":
        return cls(type="complete", content="执行完成", completed=True, sessionId=session_id)

    def to_sse(self) -> str:
        return f"data: {self.model_dump_json(by_alias=True)}\n\n"
