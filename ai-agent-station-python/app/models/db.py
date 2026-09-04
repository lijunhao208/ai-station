from typing import Optional

from sqlalchemy import Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    pass


class AiAgent(Base):
    __tablename__ = "ai_agent"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    agent_id: Mapped[str] = mapped_column(String(64))
    agent_name: Mapped[str] = mapped_column(String(128))
    description: Mapped[Optional[str]] = mapped_column(Text)
    channel: Mapped[Optional[str]] = mapped_column(String(32))
    strategy: Mapped[Optional[str]] = mapped_column(String(64))
    status: Mapped[int] = mapped_column(Integer, default=1)


class AiAgentFlowConfig(Base):
    __tablename__ = "ai_agent_flow_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    agent_id: Mapped[str] = mapped_column(String(64))
    client_id: Mapped[str] = mapped_column(String(64))
    client_name: Mapped[Optional[str]] = mapped_column(String(128))
    client_type: Mapped[str] = mapped_column(String(64))
    sequence: Mapped[int] = mapped_column(Integer)
    step_prompt: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[int] = mapped_column(Integer, default=1)


class AiClient(Base):
    __tablename__ = "ai_client"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_id: Mapped[str] = mapped_column(String(64))
    client_name: Mapped[Optional[str]] = mapped_column(String(128))
    status: Mapped[int] = mapped_column(Integer, default=1)


class AiClientApi(Base):
    __tablename__ = "ai_client_api"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    api_id: Mapped[str] = mapped_column(String(64))
    base_url: Mapped[str] = mapped_column(String(256))
    api_key: Mapped[str] = mapped_column(String(256))
    completions_path: Mapped[Optional[str]] = mapped_column(String(128))
    embeddings_path: Mapped[Optional[str]] = mapped_column(String(128))
    status: Mapped[int] = mapped_column(Integer, default=1)


class AiClientModel(Base):
    __tablename__ = "ai_client_model"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    model_id: Mapped[str] = mapped_column(String(64))
    api_id: Mapped[str] = mapped_column(String(64))
    model_name: Mapped[str] = mapped_column(String(128))
    model_type: Mapped[Optional[str]] = mapped_column(String(32))
    status: Mapped[int] = mapped_column(Integer, default=1)


class AiClientSystemPrompt(Base):
    __tablename__ = "ai_client_system_prompt"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prompt_id: Mapped[str] = mapped_column(String(64))
    prompt_content: Mapped[str] = mapped_column(Text)
    status: Mapped[int] = mapped_column(Integer, default=1)


class AiClientToolMcp(Base):
    __tablename__ = "ai_client_tool_mcp"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mcp_id: Mapped[str] = mapped_column(String(64))
    transport_type: Mapped[str] = mapped_column(String(16))
    transport_config: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[int] = mapped_column(Integer, default=1)


class AiClientConfig(Base):
    __tablename__ = "ai_client_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_type: Mapped[str] = mapped_column(String(32))
    source_id: Mapped[str] = mapped_column(String(64))
    target_type: Mapped[str] = mapped_column(String(32))
    target_id: Mapped[str] = mapped_column(String(64))
    status: Mapped[int] = mapped_column(Integer, default=1)


_engine = create_engine(get_settings().mysql_url, pool_pre_ping=True, pool_size=10)
SessionLocal = sessionmaker(bind=_engine, autocommit=False, autoflush=False)
