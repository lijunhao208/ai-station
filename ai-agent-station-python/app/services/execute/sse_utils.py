import asyncio
import json
from typing import AsyncGenerator, Callable, Optional

from app.schemas.agent_result import AgentExecuteResult


class SseQueue:
    """异步 SSE 事件队列。"""

    def __init__(self):
        self._queue: asyncio.Queue[Optional[str]] = asyncio.Queue()
        self._closed = False

    async def send(self, result: AgentExecuteResult) -> None:
        if not self._closed:
            await self._queue.put(result.to_sse())

    async def send_raw(self, data: str) -> None:
        if not self._closed:
            await self._queue.put(data)

    async def close(self) -> None:
        self._closed = True
        await self._queue.put(None)

    async def stream(self) -> AsyncGenerator[str, None]:
        while True:
            item = await self._queue.get()
            if item is None:
                break
            yield item


SendFn = Callable[[AgentExecuteResult], None]


def parse_sections(
    text: str,
    section_markers: dict[str, str],
    send_fn: SendFn,
    step: int,
    session_id: str,
    result_type: str,
) -> None:
    """解析 LLM 结构化输出并发送 SSE 子类型事件。"""
    lines = text.split("\n")
    current_section = ""
    section_content: list[str] = []

    def flush():
        nonlocal current_section, section_content
        if current_section and section_content:
            content = "\n".join(section_content).strip()
            if content:
                if result_type == "analysis":
                    send_fn(AgentExecuteResult.analysis_sub(step, current_section, content, session_id))
                elif result_type == "execution":
                    send_fn(AgentExecuteResult.execution_sub(step, current_section, content, session_id))
                elif result_type == "supervision":
                    send_fn(AgentExecuteResult.supervision_sub(step, current_section, content, session_id))
                elif result_type == "summary":
                    send_fn(AgentExecuteResult.summary_sub(current_section, content, session_id))
        section_content = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        matched = False
        for marker, sub_type in section_markers.items():
            if marker in line:
                flush()
                current_section = sub_type
                matched = True
                break

        if not matched and current_section:
            section_content.append(line)

    flush()
