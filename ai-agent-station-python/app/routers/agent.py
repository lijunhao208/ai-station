import asyncio

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from loguru import logger

from app.schemas.requests import (
    AiAgentResponse,
    ArmoryAgentRequest,
    ArmoryApiRequest,
    AutoAgentRequest,
    ExecuteCommand,
    Response,
)
from app.services.execute.sse_utils import SseQueue

router = APIRouter()


@router.post("/auto_agent")
async def auto_agent(request: AutoAgentRequest, req: Request):
    logger.info("Auto agent request: agentId={}, sessionId={}", request.aiAgentId, request.sessionId)

    command = ExecuteCommand(
        ai_agent_id=request.aiAgentId,
        message=request.message,
        session_id=request.sessionId,
        max_step=request.maxStep,
    )

    sse = SseQueue()
    dispatch = req.app.state.dispatch

    async def event_generator():
        task = asyncio.create_task(dispatch.dispatch(command, sse))
        async for chunk in sse.stream():
            yield chunk
        await task

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/armory_agent")
async def armory_agent(request: ArmoryAgentRequest, req: Request):
    if not request.agentId:
        return Response(code="0002", info="agentId不能为空", data=False)

    try:
        req.app.state.armory.accept_armory_agent(request.agentId)
        return Response(code="0000", info="装配成功", data=True)
    except Exception as e:
        logger.exception("Armory agent failed")
        return Response(code="0001", info=f"装配失败：{e}", data=False)


@router.get("/query_available_agents")
async def query_available_agents(req: Request):
    try:
        agents = req.app.state.armory.query_available_agents()
        data = [
            AiAgentResponse(
                agentId=a.agent_id,
                agentName=a.agent_name,
                description=a.description,
                channel=a.channel,
                strategy=a.strategy,
                status=a.status,
            )
            for a in agents
        ]
        return Response(code="0000", info="查询成功", data=data)
    except Exception as e:
        logger.exception("Query agents failed")
        return Response(code="0001", info=f"查询失败：{e}", data=[])


@router.post("/armory_api")
async def armory_api(request: ArmoryApiRequest, req: Request):
    if not request.apiId:
        return Response(code="0002", info="apiId不能为空", data=False)

    try:
        req.app.state.armory.accept_armory_api(request.apiId)
        return Response(code="0000", info="装配成功", data=True)
    except Exception as e:
        logger.exception("Armory api failed")
        return Response(code="0001", info=f"装配失败：{e}", data=False)
