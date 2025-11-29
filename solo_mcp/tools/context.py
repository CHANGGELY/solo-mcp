# 这个模块管理运行时上下文，提供键值存取与序列化
from __future__ import annotations
from typing import Any, Dict

class Context:
    def __init__(self) -> None:
        self._data: Dict[str, Any] = {}

    # 中文接口，帮助学习
    def 设置(self, 键: str, 值: Any) -> None:
        self._data[键] = 值

    def 读取(self, 键: str, 默认: Any | None = None) -> Any | None:
        return self._data.get(键, 默认)

    # 英文接口，兼容现有测试
    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def get(self, key: str, default: Any | None = None) -> Any | None:
        return self._data.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data)
