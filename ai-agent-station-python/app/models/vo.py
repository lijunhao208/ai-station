from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class AiAgentVO:
    agent_id: str
    agent_name: str
    description: Optional[str] = None
    channel: Optional[str] = None
    strategy: Optional[str] = None
    status: Optional[int] = None


@dataclass
class AiAgentClientFlowConfigVO:
    client_id: str
    client_name: Optional[str] = None
    client_type: Optional[str] = None
    sequence: Optional[int] = None
    step_prompt: Optional[str] = None


@dataclass
class AiClientApiVO:
    api_id: str
    base_url: str
    api_key: str
    completions_path: str = "/v1/chat/completions"
    embeddings_path: str = "/v1/embeddings"


@dataclass
class AiClientModelVO:
    model_id: str
    api_id: str
    model_name: str
    model_type: Optional[str] = None
    tool_mcp_ids: list[str] = field(default_factory=list)


@dataclass
class AiClientSystemPromptVO:
    prompt_id: str
    prompt_content: str


@dataclass
class AiClientToolMcpVO:
    mcp_id: str
    transport_type: str
    transport_config: dict[str, Any] = field(default_factory=dict)


@dataclass
class AiClientVO:
    client_id: str
    client_name: Optional[str] = None
    model_id: Optional[str] = None
    prompt_id_list: list[str] = field(default_factory=list)
    mcp_id_list: list[str] = field(default_factory=list)
    advisor_id_list: list[str] = field(default_factory=list)
