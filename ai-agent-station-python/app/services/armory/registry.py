from typing import Any


class AgentRegistry:
    """运行时 Bean 注册表，对应 Java Spring 容器中的动态 Bean。"""

    _store: dict[str, Any] = {}

    @classmethod
    def register(cls, name: str, instance: Any) -> None:
        cls._store[name] = instance

    @classmethod
    def get(cls, name: str) -> Any:
        if name not in cls._store:
            raise KeyError(f"Bean not found: {name}")
        return cls._store[name]

    @classmethod
    def contains(cls, name: str) -> bool:
        return name in cls._store

    @classmethod
    def remove(cls, name: str) -> None:
        cls._store.pop(name, None)

    @classmethod
    def clear(cls) -> None:
        cls._store.clear()


def client_bean_name(client_id: str) -> str:
    return f"ai_client_{client_id}"


def api_bean_name(api_id: str) -> str:
    return f"ai_client_api_{api_id}"


def model_bean_name(model_id: str) -> str:
    return f"ai_client_model_{model_id}"


def mcp_bean_name(mcp_id: str) -> str:
    return f"ai_client_tool_mcp_{mcp_id}"
