from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from loguru import logger

from app.models.vo import AiAgentClientFlowConfigVO
from app.repository.agent_repository import AgentRepository
from app.schemas.agent_result import AgentExecuteResult
from app.schemas.requests import ExecuteCommand
from app.services.armory.builder import get_chat_client
from app.services.execute.sse_utils import parse_sections

# Client type constants (match Java AiClientTypeEnumVO)
TASK_ANALYZER = "TASK_ANALYZER_CLIENT"
PRECISION_EXECUTOR = "PRECISION_EXECUTOR_CLIENT"
QUALITY_SUPERVISOR = "QUALITY_SUPERVISOR_CLIENT"
RESPONSE_ASSISTANT = "RESPONSE_ASSISTANT"
TOOL_MCP = "TOOL_MCP_CLIENT"
PLANNING = "PLANNING_CLIENT"
EXECUTOR = "EXECUTOR_CLIENT"


@dataclass
class DynamicContext:
    step: int = 1
    max_step: int = 3
    execution_history: str = ""
    current_task: str = ""
    is_completed: bool = False
    flow_config_map: dict[str, AiAgentClientFlowConfigVO] = field(default_factory=dict)
    data: dict[str, Any] = field(default_factory=dict)


class AutoAgentStrategy:
    ANALYSIS_MARKERS = {
        "任务状态分析:": "analysis_status",
        "执行历史评估:": "analysis_history",
        "下一步策略:": "analysis_strategy",
        "完成度评估:": "analysis_progress",
        "任务状态:": "analysis_task_status",
    }

    EXECUTION_MARKERS = {
        "执行目标:": "execution_target",
        "执行过程:": "execution_process",
        "执行结果:": "execution_result",
        "质量检查:": "execution_quality",
    }

    SUPERVISION_MARKERS = {
        "质量评估:": "assessment",
        "问题识别:": "issues",
        "改进建议:": "suggestions",
        "质量评分:": "score",
        "是否通过:": "pass",
    }

    def __init__(self, repository: AgentRepository | None = None):
        self.repository = repository or AgentRepository()

    def execute(self, command: ExecuteCommand, send: Callable[[AgentExecuteResult], None]) -> None:
        ctx = DynamicContext(
            max_step=command.max_step or 3,
            current_task=command.message,
        )
        ctx.flow_config_map = self.repository.query_ai_agent_client_flow_config(command.ai_agent_id)

        if not ctx.flow_config_map:
            send(AgentExecuteResult.error("未找到 Agent 流程配置", command.session_id))
            return

        logger.info("Auto Agent start: agent={}, maxStep={}", command.ai_agent_id, ctx.max_step)

        while ctx.step <= ctx.max_step and not ctx.is_completed:
            self._step_analyze(command, ctx, send)
            if ctx.is_completed or ctx.step > ctx.max_step:
                break
            self._step_execute(command, ctx, send)
            self._step_supervise(command, ctx, send)

        self._step_summary(command, ctx, send)
        send(AgentExecuteResult.complete(command.session_id))

    def _step_analyze(self, command: ExecuteCommand, ctx: DynamicContext, send: Callable) -> None:
        config = ctx.flow_config_map.get(TASK_ANALYZER)
        if not config or not config.step_prompt:
            return

        history = ctx.execution_history if ctx.execution_history else "[首次执行]"
        prompt = config.step_prompt % (
            command.message,
            ctx.step,
            ctx.max_step,
            history,
            ctx.current_task,
        )

        client = get_chat_client(config.client_id)
        result = client.invoke(prompt, command.session_id)

        parse_sections(result, self.ANALYSIS_MARKERS, send, ctx.step, command.session_id, "analysis")
        ctx.data["analysisResult"] = result

        if "任务状态: COMPLETED" in result or "完成度评估: 100%" in result:
            ctx.is_completed = True

    def _step_execute(self, command: ExecuteCommand, ctx: DynamicContext, send: Callable) -> None:
        config = ctx.flow_config_map.get(PRECISION_EXECUTOR)
        if not config or not config.step_prompt:
            return

        analysis = ctx.data.get("analysisResult", "执行当前任务步骤")
        prompt = config.step_prompt % (command.message, analysis)

        client = get_chat_client(config.client_id)
        result = client.invoke(prompt, command.session_id)

        parse_sections(result, self.EXECUTION_MARKERS, send, ctx.step, command.session_id, "execution")
        ctx.data["executionResult"] = result

        ctx.execution_history += (
            f"\n=== 第 {ctx.step} 步执行记录 ===\n"
            f"【分析阶段】{ctx.data.get('analysisResult', '')}\n"
            f"【执行阶段】{result}\n"
        )

    def _step_supervise(self, command: ExecuteCommand, ctx: DynamicContext, send: Callable) -> None:
        config = ctx.flow_config_map.get(QUALITY_SUPERVISOR)
        execution = ctx.data.get("executionResult", "")
        if not config or not config.step_prompt or not execution:
            ctx.step += 1
            return

        prompt = config.step_prompt % (command.message, execution)
        client = get_chat_client(config.client_id)
        result = client.invoke(prompt, command.session_id)

        parse_sections(result, self.SUPERVISION_MARKERS, send, ctx.step, command.session_id, "supervision")
        send(AgentExecuteResult.supervision(ctx.step, result, command.session_id))
        ctx.data["supervisionResult"] = result

        if "是否通过: FAIL" in result:
            ctx.current_task = "根据质量监督的建议重新执行任务"
        elif "是否通过: OPTIMIZE" in result:
            ctx.current_task = "根据质量监督的建议优化执行结果"
        else:
            ctx.is_completed = True

        ctx.execution_history += (
            f"\n=== 第 {ctx.step} 步完整记录 ===\n"
            f"【分析阶段】{ctx.data.get('analysisResult', '')}\n"
            f"【执行阶段】{execution}\n"
            f"【监督阶段】{result}\n"
        )
        ctx.step += 1

    def _step_summary(self, command: ExecuteCommand, ctx: DynamicContext, send: Callable) -> None:
        config = ctx.flow_config_map.get(RESPONSE_ASSISTANT)
        if not config or not config.step_prompt:
            send(AgentExecuteResult.summary(ctx.execution_history or "任务执行完成", command.session_id))
            return

        status = "已完成" if ctx.is_completed else "未完成（达到最大步数）"
        prompt = config.step_prompt % (
            command.message,
            ctx.execution_history,
            status,
            ctx.step - 1,
            ctx.max_step,
        )

        client = get_chat_client(config.client_id)
        result = client.invoke(prompt, f"{command.session_id}-summary", memory_size=50)

        summary_sections = {
            "已完成工作:": "completed_work",
            "未完成原因:": "incomplete_reasons",
            "执行效果评估:": "evaluation",
            "总结概述:": "summary_overview",
        }
        parse_sections(result, summary_sections, send, 4, command.session_id, "summary")
        send(AgentExecuteResult.summary(result, command.session_id))
