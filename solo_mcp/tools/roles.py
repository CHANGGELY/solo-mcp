from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..config import SoloConfig


@dataclass
class Role:
    name: str
    responsibilities: list[str]


DEFAULT_ROLES = {
    "python": [
        Role(
            "Architect",
            ["Define modules", "Decide storage/indexing", "Error handling policies"],
        ),
        Role("Planner", ["Break down tasks", "Define milestones", "Prioritize"]),
        Role("Coder", ["Implement tools", "Write tests", "Optimize"]),
        Role("Reviewer", ["Code review", "Enforce style", "Find edge cases"]),
        Role("QA", ["Test scenarios", "Coverage gaps", "Regression tests"]),
    ],
    "node": [
        Role("Architect", ["Define modules", "API design", "Dev server strategy"]),
        Role("Planner", ["Break down tasks", "Define milestones", "Prioritize"]),
        Role("Coder", ["Implement features", "Write tests", "Optimize"]),
        Role("Reviewer", ["Code review", "Enforce style", "Find edge cases"]),
        Role("QA", ["Test scenarios", "Coverage gaps", "Regression tests"]),
    ],
}


class RolePlanner:
    """根据项目目标和技术栈自动规划角色列表。"""

    def __init__(self, default_roles: dict[str, list[Role]] | None = None):
        self.default_roles = default_roles or DEFAULT_ROLES

    def plan(self, goal: str | None, stack: list[str] | None) -> list[Role]:
        """根据关键字和技术栈生成去重后的角色集合。"""
        stack = [s.lower() for s in (stack or ["python"])]
        roles: list[Role] = []
        # 技术栈驱动
        if "python" in stack:
            roles.extend(self.default_roles["python"])
        if any(s in stack for s in ["node", "js", "ts"]):
            roles.extend(self.default_roles["node"])
        # 目标关键字驱动（简单 Heuristic，可后续扩展）
        kw = (goal or "").lower()
        if any(k in kw for k in ["frontend", "web ui", "dashboard"]):
            roles.append(
                Role(
                    "Frontend", ["Build UI", "Integrate APIs", "Ensure responsiveness"]
                )
            )
        if "data" in kw or "etl" in kw:
            roles.append(
                Role(
                    "DataEngineer",
                    ["Build pipelines", "Optimize queries", "Manage storage"],
                )
            )
        # 去重
        unique: dict[str, Role] = {}
        for r in roles:
            if r.name not in unique:
                unique[r.name] = r
        return list(unique.values())


class RolesTool:
    def __init__(self, config: SoloConfig):
        self.config = config
        self.planner = RolePlanner()

    def evaluate(self, goal: str | None, stack: list[str] | None) -> dict[str, Any]:
        roles = self.planner.plan(goal, stack)
        res = [{"name": r.name, "responsibilities": r.responsibilities} for r in roles]
        return {"ok": True, "goal": goal or "", "roles": res}
