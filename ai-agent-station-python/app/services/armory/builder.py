from loguru import logger

from app.config import get_settings
from app.models.vo import AiClientApiVO
from app.repository.agent_repository import AgentRepository
from app.services.armory.chat_client import GLOBAL_MEMORY, AgentChatClient, build_chat_openai
from app.services.armory.registry import AgentRegistry, api_bean_name, client_bean_name, model_bean_name


class ArmoryService:
    def __init__(self, repository: AgentRepository | None = None):
        self.repository = repository or AgentRepository()

    def accept_armory_all_available_agents(self) -> None:
        agents = self.repository.query_available_agents()
        for agent in agents:
            try:
                self.accept_armory_agent(agent.agent_id)
            except Exception as e:
                logger.error("Armory agent {} failed: {}", agent.agent_id, e)

    def accept_armory_agent(self, agent_id: str) -> None:
        flow_configs = self.repository.query_ai_agent_clients_by_agent_id(agent_id)
        if not flow_configs:
            logger.warning("No flow config for agent {}", agent_id)
            return

        client_ids = list({c.client_id for c in flow_configs})
        self._armory_clients(client_ids)

    def accept_armory_api(self, api_id: str) -> None:
        api_vo = self.repository.query_api_by_id(api_id)
        if not api_vo:
            raise ValueError(f"API not found: {api_id}")
        self._register_api(api_vo)

    def query_available_agents(self):
        return self.repository.query_available_agents()

    def _armory_clients(self, client_ids: list[str]) -> None:
        apis = self.repository.query_apis_for_clients(client_ids)
        settings = get_settings()

        for api_vo in apis:
            self._register_api(api_vo)

        for client_id in client_ids:
            client_vo = self.repository.build_client_vo(client_id)
            if not client_vo or not client_vo.model_id:
                logger.warning("Skip client {} - no model config", client_id)
                continue

            model_vo = self.repository.query_model_by_id(client_vo.model_id)
            if not model_vo:
                continue

            api_vo = self.repository.query_api_by_id(model_vo.api_id)
            if not api_vo:
                if settings.openai_api_key:
                    api_vo = AiClientApiVO(
                        api_id=model_vo.api_id,
                        base_url=settings.openai_base_url,
                        api_key=settings.openai_api_key,
                    )
                else:
                    logger.warning("No API config for model {}", model_vo.model_id)
                    continue

            if not AgentRegistry.contains(model_bean_name(model_vo.model_id)):
                llm = build_chat_openai(api_vo, model_vo.model_name)
                AgentRegistry.register(model_bean_name(model_vo.model_id), llm)

            system_parts = ["Ai 智能体\n"]
            for prompt_id in client_vo.prompt_id_list:
                prompt_vo = self.repository.query_prompt_by_id(prompt_id)
                if prompt_vo:
                    system_parts.append(prompt_vo.prompt_content)

            llm = AgentRegistry.get(model_bean_name(model_vo.model_id))
            chat_client = AgentChatClient(
                llm=llm,
                system_prompt="".join(system_parts),
                memory_store=GLOBAL_MEMORY,
            )
            AgentRegistry.register(client_bean_name(client_id), chat_client)
            logger.info("Registered chat client: {}", client_bean_name(client_id))

    def _register_api(self, api_vo) -> None:
        name = api_bean_name(api_vo.api_id)
        if not AgentRegistry.contains(name):
            AgentRegistry.register(name, api_vo)
            logger.info("Registered API: {}", name)


def get_chat_client(client_id: str) -> AgentChatClient:
    return AgentRegistry.get(client_bean_name(client_id))
