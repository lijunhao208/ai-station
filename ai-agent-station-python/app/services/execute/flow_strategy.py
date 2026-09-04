import re
import time
from typing import Callable

from loguru import logger

from app.repository.agent_repository import AgentRepository
from app.schemas.agent_result import AgentExecuteResult
from app.schemas.requests import ExecuteCommand
from app.services.armory.builder import get_chat_client
from app.services.execute.auto_strategy import EXECUTOR, PLANNING, TOOL_MCP


class FlowAgentStrategy:
    def __init__(self, repository: AgentRepository | None = None):
        self.repository = repository or AgentRepository()

    def execute(self, command: ExecuteCommand, send: Callable[[AgentExecuteResult], None]) -> None:
        flow_map = self.repository.query_ai_agent_client_flow_config(command.ai_agent_id)
        if not flow_map:
            send(AgentExecuteResult.error("未找到 Flow Agent 配置", command.session_id))
            return

        max_step = command.max_step or 4
        mcp_analysis = ""

        # Step 1: MCP 工具分析
        mcp_config = flow_map.get(TOOL_MCP)
        if mcp_config and mcp_config.step_prompt:
            client = get_chat_client(mcp_config.client_id)
            prompt = mcp_config.step_prompt % command.message
            mcp_analysis = client.invoke(prompt, command.session_id)
            send(AgentExecuteResult.analysis_sub(1, "analysis_strategy", mcp_analysis, command.session_id))

        # Step 2: 规划
        plan_config = flow_map.get(PLANNING)
        plan_text = ""
        if plan_config and plan_config.step_prompt:
            client = get_chat_client(plan_config.client_id)
            prompt = plan_config.step_prompt % (command.message, mcp_analysis)
            plan_text = client.invoke(prompt, command.session_id)
            send(AgentExecuteResult.analysis_sub(2, "analysis_strategy", plan_text, command.session_id))

        # Step 3: 解析步骤
        steps = self._parse_steps(plan_text)
        if not steps:
            steps = {"step_1": plan_text or command.message}

        # Step 4: 逐步执行
        exec_config = flow_map.get(EXECUTOR)
        if not exec_config:
            send(AgentExecuteResult.summary(plan_text, command.session_id))
            send(AgentExecuteResult.complete(command.session_id))
            return

        client = get_chat_client(exec_config.client_id)
        for i, (step_key, step_content) in enumerate(steps.items(), 1):
            if i > max_step:
                break
            exec_prompt = (
                f"用户原始需求: {command.message}\n"
                f"当前步骤: {step_key}\n"
                f"步骤内容: {step_content}\n"
                f"请执行此步骤并给出详细结果。"
            )
            if exec_config.step_prompt:
                try:
                    exec_prompt = exec_config.step_prompt % (step_content, command.message)
                except TypeError:
                    pass

            result = client.invoke(exec_prompt, command.session_id)
            send(
                AgentExecuteResult.execution_sub(
                    i, "execution_result", f"{step_key} 执行完成: {result[:500]}", command.session_id
                )
            )
            logger.info("Flow step {} done: {}", step_key, result[:100])
            time.sleep(0.5)

        send(AgentExecuteResult.summary("Flow Agent 执行完成", command.session_id))
        send(AgentExecuteResult.complete(command.session_id))

    def _parse_steps(self, plan_text: str) -> dict[str, str]:
        steps: dict[str, str] = {}
        if not plan_text:
            return steps

        pattern = re.compile(r"(?:步骤|Step)\s*(\d+)[:：]\s*(.+?)(?=(?:步骤|Step)\s*\d+[:：]|$)", re.S | re.I)
        matches = pattern.findall(plan_text)
        for num, content in matches:
            steps[f"step_{num}"] = content.strip()

        if not steps:
            for i, line in enumerate(plan_text.split("\n"), 1):
                line = line.strip()
                if line and len(line) > 5:
                    steps[f"step_{i}"] = line

        return steps
