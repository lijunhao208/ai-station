import json
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.db import (
    AiAgent,
    AiAgentFlowConfig,
    AiClient,
    AiClientApi,
    AiClientConfig,
    AiClientModel,
    AiClientSystemPrompt,
    AiClientToolMcp,
    SessionLocal,
)
from app.models.vo import (
    AiAgentClientFlowConfigVO,
    AiAgentVO,
    AiClientApiVO,
    AiClientModelVO,
    AiClientSystemPromptVO,
    AiClientToolMcpVO,
    AiClientVO,
)

AI_CLIENT = "client"
AI_CLIENT_MODEL = "model"
AI_CLIENT_SYSTEM_PROMPT = "prompt"
AI_CLIENT_TOOL_MCP = "tool_mcp"
AI_CLIENT_ADVISOR = "advisor"


class AgentRepository:
    def __init__(self, session: Optional[Session] = None):
        self._session = session

    def _get_session(self) -> Session:
        return self._session or SessionLocal()

    def _close_if_owned(self, session: Session) -> None:
        if self._session is None:
            session.close()

    def query_available_agents(self) -> list[AiAgentVO]:
        session = self._get_session()
        try:
            rows = session.scalars(select(AiAgent).where(AiAgent.status == 1)).all()
            return [
                AiAgentVO(
                    agent_id=r.agent_id,
                    agent_name=r.agent_name,
                    description=r.description,
                    channel=r.channel,
                    strategy=r.strategy,
                    status=r.status,
                )
                for r in rows
            ]
        finally:
            self._close_if_owned(session)

    def query_ai_agent_by_agent_id(self, agent_id: str) -> Optional[AiAgentVO]:
        session = self._get_session()
        try:
            row = session.scalars(select(AiAgent).where(AiAgent.agent_id == agent_id)).first()
            if not row:
                return None
            return AiAgentVO(
                agent_id=row.agent_id,
                agent_name=row.agent_name,
                description=row.description,
                channel=row.channel,
                strategy=row.strategy,
                status=row.status,
            )
        finally:
            self._close_if_owned(session)

    def query_ai_agent_clients_by_agent_id(self, agent_id: str) -> list[AiAgentClientFlowConfigVO]:
        session = self._get_session()
        try:
            rows = session.scalars(
                select(AiAgentFlowConfig)
                .where(AiAgentFlowConfig.agent_id == agent_id, AiAgentFlowConfig.status == 1)
                .order_by(AiAgentFlowConfig.sequence)
            ).all()
            return [
                AiAgentClientFlowConfigVO(
                    client_id=r.client_id,
                    client_name=r.client_name,
                    client_type=r.client_type,
                    sequence=r.sequence,
                    step_prompt=r.step_prompt,
                )
                for r in rows
            ]
        finally:
            self._close_if_owned(session)

    def query_ai_agent_client_flow_config(self, agent_id: str) -> dict[str, AiAgentClientFlowConfigVO]:
        configs = self.query_ai_agent_clients_by_agent_id(agent_id)
        return {c.client_type: c for c in configs if c.client_type}

    def query_configs_by_source(self, source_type: str, source_id: str) -> list[AiClientConfig]:
        session = self._get_session()
        try:
            return list(
                session.scalars(
                    select(AiClientConfig).where(
                        AiClientConfig.source_type == source_type,
                        AiClientConfig.source_id == source_id,
                        AiClientConfig.status == 1,
                    )
                ).all()
            )
        finally:
            self._close_if_owned(session)

    def query_client_by_id(self, client_id: str) -> Optional[AiClient]:
        session = self._get_session()
        try:
            return session.scalars(
                select(AiClient).where(AiClient.client_id == client_id, AiClient.status == 1)
            ).first()
        finally:
            self._close_if_owned(session)

    def query_api_by_id(self, api_id: str) -> Optional[AiClientApiVO]:
        session = self._get_session()
        try:
            row = session.scalars(
                select(AiClientApi).where(AiClientApi.api_id == api_id, AiClientApi.status == 1)
            ).first()
            if not row:
                return None
            return AiClientApiVO(
                api_id=row.api_id,
                base_url=row.base_url,
                api_key=row.api_key,
                completions_path=row.completions_path or "/v1/chat/completions",
                embeddings_path=row.embeddings_path or "/v1/embeddings",
            )
        finally:
            self._close_if_owned(session)

    def query_model_by_id(self, model_id: str) -> Optional[AiClientModelVO]:
        session = self._get_session()
        try:
            row = session.scalars(
                select(AiClientModel).where(AiClientModel.model_id == model_id, AiClientModel.status == 1)
            ).first()
            if not row:
                return None
            mcp_ids = [
                c.target_id
                for c in self.query_configs_by_source(AI_CLIENT_MODEL, model_id)
                if c.target_type == AI_CLIENT_TOOL_MCP
            ]
            return AiClientModelVO(
                model_id=row.model_id,
                api_id=row.api_id,
                model_name=row.model_name,
                model_type=row.model_type,
                tool_mcp_ids=mcp_ids,
            )
        finally:
            self._close_if_owned(session)

    def query_prompt_by_id(self, prompt_id: str) -> Optional[AiClientSystemPromptVO]:
        session = self._get_session()
        try:
            row = session.scalars(
                select(AiClientSystemPrompt).where(
                    AiClientSystemPrompt.prompt_id == prompt_id,
                    AiClientSystemPrompt.status == 1,
                )
            ).first()
            if not row:
                return None
            return AiClientSystemPromptVO(prompt_id=row.prompt_id, prompt_content=row.prompt_content)
        finally:
            self._close_if_owned(session)

    def query_mcp_by_id(self, mcp_id: str) -> Optional[AiClientToolMcpVO]:
        session = self._get_session()
        try:
            row = session.scalars(
                select(AiClientToolMcp).where(AiClientToolMcp.mcp_id == mcp_id, AiClientToolMcp.status == 1)
            ).first()
            if not row:
                return None
            config = {}
            if row.transport_config:
                try:
                    config = json.loads(row.transport_config)
                except json.JSONDecodeError:
                    config = {}
            return AiClientToolMcpVO(
                mcp_id=row.mcp_id,
                transport_type=row.transport_type,
                transport_config=config,
            )
        finally:
            self._close_if_owned(session)

    def build_client_vo(self, client_id: str) -> Optional[AiClientVO]:
        client = self.query_client_by_id(client_id)
        if not client:
            return None

        configs = self.query_configs_by_source(AI_CLIENT, client_id)
        model_id = next((c.target_id for c in configs if c.target_type == AI_CLIENT_MODEL), None)
        prompt_ids = [c.target_id for c in configs if c.target_type == AI_CLIENT_SYSTEM_PROMPT]
        mcp_ids = [c.target_id for c in configs if c.target_type == AI_CLIENT_TOOL_MCP]
        advisor_ids = [c.target_id for c in configs if c.target_type == AI_CLIENT_ADVISOR]

        return AiClientVO(
            client_id=client.client_id,
            client_name=client.client_name,
            model_id=model_id,
            prompt_id_list=prompt_ids,
            mcp_id_list=mcp_ids,
            advisor_id_list=advisor_ids,
        )

    def query_apis_for_clients(self, client_ids: list[str]) -> list[AiClientApiVO]:
        seen: set[str] = set()
        result: list[AiClientApiVO] = []
        for client_id in client_ids:
            vo = self.build_client_vo(client_id)
            if not vo or not vo.model_id:
                continue
            model = self.query_model_by_id(vo.model_id)
            if not model:
                continue
            api = self.query_api_by_id(model.api_id)
            if api and api.api_id not in seen:
                seen.add(api.api_id)
                result.append(api)
        return result
