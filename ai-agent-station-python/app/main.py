from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import get_settings
from app.services.armory.builder import ArmoryService
from app.services.execute.dispatch import AgentDispatchService
from app.routers import agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    armory = ArmoryService()
    if settings.auto_armory_enabled:
        logger.info("Auto armory enabled, loading all agents...")
        try:
            armory.accept_armory_all_available_agents()
            logger.info("Auto armory completed")
        except Exception as e:
            logger.warning("Auto armory failed (check MySQL connection): {}", e)
    app.state.armory = armory
    app.state.dispatch = AgentDispatchService()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Agent Station Study",
        description="Python + LangChain 版 AI Agent 平台",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(agent.router, prefix="/api/v1/agent", tags=["Agent"])
    return app


app = create_app()
