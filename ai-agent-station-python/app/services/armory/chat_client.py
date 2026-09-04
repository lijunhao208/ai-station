from typing import Callable, Optional

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from loguru import logger


class AgentChatClient:
    """封装 LangChain ChatOpenAI，对应 Java 版 ChatClient。"""

    def __init__(
        self,
        llm: ChatOpenAI,
        system_prompt: str = "",
        memory_store: Optional[dict[str, list[BaseMessage]]] = None,
    ):
        self._llm = llm
        self._system_prompt = system_prompt
        self._memory_store = memory_store if memory_store is not None else {}

    def invoke(self, prompt: str, session_id: Optional[str] = None, memory_size: int = 1024) -> str:
        messages: list[BaseMessage] = []
        if self._system_prompt:
            messages.append(SystemMessage(content=self._system_prompt))

        if session_id and session_id in self._memory_store:
            history = self._memory_store[session_id][-memory_size:]
            messages.extend(history)

        messages.append(HumanMessage(content=prompt))

        try:
            response = self._llm.invoke(messages)
            content = response.content if isinstance(response.content, str) else str(response.content)

            if session_id:
                if session_id not in self._memory_store:
                    self._memory_store[session_id] = []
                self._memory_store[session_id].append(HumanMessage(content=prompt))
                self._memory_store[session_id].append(AIMessage(content=content))

            return content
        except Exception as e:
            logger.error("LLM invoke failed: {}", e)
            raise


# 全局会话记忆
GLOBAL_MEMORY: dict[str, list[BaseMessage]] = {}


def build_chat_openai(api_vo, model_name: str) -> ChatOpenAI:
    base_url = api_vo.base_url.rstrip("/")
    if not base_url.endswith("/v1"):
        if "/v1" not in base_url:
            base_url = f"{base_url}/v1"

    return ChatOpenAI(
        model=model_name,
        api_key=api_vo.api_key,
        base_url=base_url,
        temperature=0.7,
        max_tokens=4096,
    )
