import asyncio
from typing import Callable

from loguru import logger

from app.repository.agent_repository import AgentRepository
from app.schemas.agent_result import AgentExecuteResult
from app.schemas.requests import ExecuteCommand
from app.services.execute.auto_strategy import AutoAgentStrategy
from app.services.execute.fixed_strategy import FixedAgentStrategy
from app.services.execute.flow_strategy import FlowAgentStrategy
from app.services.execute.sse_utils import SseQueue

STRATEGY_MAP = {
    "autoAgentExecuteStrategy": AutoAgentStrategy,
    "flowAgentExecuteStrategy": FlowAgentStrategy,
    "fixedAgentExecuteStrategy": FixedAgentStrategy,
}


class AgentDispatchService:
    def __init__(self, repository: AgentRepository | None = None):
        self.repository = repository or AgentRepository()

    async def dispatch(self, command: ExecuteCommand, sse: SseQueue) -> None:
        agent = self.repository.query_ai_agent_by_agent_id(command.ai_agent_id)
        if not agent:
            await sse.send(AgentExecuteResult.error(f"Agent 不存在: {command.ai_agent_id}", command.session_id))
            await sse.close()
            return

        strategy_name = agent.strategy or "autoAgentExecuteStrategy"
        strategy_cls = STRATEGY_MAP.get(strategy_name)
        if not strategy_cls:
            await sse.send(AgentExecuteResult.error(f"未知策略: {strategy_name}", command.session_id))
            await sse.close()
            return

        loop = asyncio.get_event_loop()

        def send(result: AgentExecuteResult) -> None:
            asyncio.run_coroutine_threadsafe(sse.send(result), loop)

        def run_strategy() -> None:
            try:
                strategy = strategy_cls(self.repository)
                strategy.execute(command, send)
            except Exception as e:
                logger.exception("Agent execution failed")
                asyncio.run_coroutine_threadsafe(
                    sse.send(AgentExecuteResult.error(str(e), command.session_id)), loop
                )
            finally:
                asyncio.run_coroutine_threadsafe(sse.close(), loop)

        await asyncio.to_thread(run_strategy)
