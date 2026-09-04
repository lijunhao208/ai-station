from datetime import date
from typing import Callable

from loguru import logger

from app.repository.agent_repository import AgentRepository
from app.schemas.agent_result import AgentExecuteResult
from app.schemas.requests import ExecuteCommand
from app.services.armory.builder import get_chat_client


class FixedAgentStrategy:
    def __init__(self, repository: AgentRepository | None = None):
        self.repository = repository or AgentRepository()

    def execute(self, command: ExecuteCommand, send: Callable[[AgentExecuteResult], None]) -> None:
        configs = self.repository.query_ai_agent_clients_by_agent_id(command.ai_agent_id)
        if not configs:
            send(AgentExecuteResult.error("未找到 Agent 客户端配置", command.session_id))
            return

        content = ""
        for config in configs:
            client = get_chat_client(config.client_id)
            prompt = f"{command.message}，{content}" if content else command.message
            prompt += f"\n当前日期: {date.today()}"
            content = client.invoke(prompt, command.session_id, memory_size=100)
            logger.info("Fixed agent client {} done", config.client_id)

        if content:
            send(AgentExecuteResult.summary(content, command.session_id))
        send(AgentExecuteResult.complete(command.session_id))
