from __future__ import annotations

import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Set, Tuple, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading

from ..config import SoloConfig

# 使用 TYPE_CHECKING 避免循环导入
if TYPE_CHECKING:
    from .learning import LearningEngine, UserActionType, PerformanceMetrics
    from .adaptive import AdaptiveOptimizer
    from .memory import MemoryTool
    from .context import ContextTool
else:
    # 运行时导入
    try:
        from .learning import LearningEngine, UserActionType
        from .adaptive import AdaptiveOptimizer
    except ImportError:
        LearningEngine = None
        UserActionType = None
        AdaptiveOptimizer = None


class Priority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ResourceType(Enum):
    CPU = "cpu"
    MEMORY = "memory"
    NETWORK = "network"
    STORAGE = "storage"
    API_QUOTA = "api_quota"
    CONCURRENT_TASKS = "concurrent_tasks"


@dataclass
class Task:
    """任务数据结构"""

    id: str
    name: str
    description: str
    priority: Priority
    estimated_duration: float  # 预估执行时间（秒）
    required_resources: Dict[ResourceType, float]
    dependencies: List[str] = field(default_factory=list)  # 依赖的任务ID
    required_roles: List[str] = field(default_factory=list)  # 需要的角色能力
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    assigned_to: Optional[str] = None
    status: str = "pending"  # pending, assigned, running, completed, failed


@dataclass
class Conflict:
    """冲突数据结构"""

    conflict_type: str  # resource, dependency, priority, role_capability
    severity: str  # critical, high, medium, low
    description: str
    affected_tasks: List[str]
    suggested_resolution: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    detected_at: datetime = field(default_factory=datetime.now)


class TaskAllocator:
    """智能任务分配器"""

    def __init__(self, config: SoloConfig):
        self.config = config
        self.allocation_history: deque = deque(maxlen=1000)
        self.role_capabilities: Dict[str, Set[str]] = {
            "analyst": {"analysis", "research", "data_processing", "reporting"},
            "developer": {
                "coding",
                "debugging",
                "testing",
                "deployment",
                "architecture",
            },
            "designer": {"ui_design", "ux_design", "prototyping", "visual_design"},
            "manager": {
                "planning",
                "coordination",
                "resource_management",
                "decision_making",
            },
            "qa": {"testing", "quality_assurance", "bug_tracking", "validation"},
        }
        self.role_workload: Dict[str, float] = defaultdict(float)
        self.role_performance: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {
                "success_rate": 1.0,
                "avg_completion_time": 1.0,
                "quality_score": 1.0,
            }
        )

    def allocate_tasks(
        self, tasks: List[Task], available_roles: List[str]
    ) -> Dict[str, List[Task]]:
        """分配任务到角色"""
        allocation = defaultdict(list)

        # 按优先级和依赖关系排序任务
        sorted_tasks = self._sort_tasks_by_priority_and_dependencies(tasks)

        for task in sorted_tasks:
            best_role = self._find_best_role_for_task(task, available_roles)
            if best_role:
                allocation[best_role].append(task)
                task.assigned_to = best_role
                task.status = "assigned"

                # 更新角色工作负载
                self.role_workload[best_role] += task.estimated_duration

                # 记录分配历史
                self.allocation_history.append(
                    {
                        "task_id": task.id,
                        "role": best_role,
                        "timestamp": datetime.now(),
                        "priority": task.priority.value,
                        "estimated_duration": task.estimated_duration,
                    }
                )

        return dict(allocation)

    def _create_role_evaluator(self):
        """创建角色评估器"""

        class SimpleRoleEvaluator:
            def evaluate(self, goal: str, stack: List[str]) -> Dict[str, Any]:
                """评估并返回适合的角色列表"""
                available_roles = [
                    {
                        "name": "analyst",
                        "capabilities": ["analysis", "research", "planning"],
                    },
                    {
                        "name": "developer",
                        "capabilities": ["coding", "implementation", "debugging"],
                    },
                    {
                        "name": "designer",
                        "capabilities": ["ui_design", "ux_design", "prototyping"],
                    },
                    {
                        "name": "tester",
                        "capabilities": ["testing", "quality_assurance", "validation"],
                    },
                    {
                        "name": "manager",
                        "capabilities": [
                            "coordination",
                            "planning",
                            "resource_management",
                        ],
                    },
                ]

                # 根据目标和技术栈筛选角色
                if goal:
                    goal_lower = goal.lower()
                    if "design" in goal_lower or "ui" in goal_lower:
                        available_roles = [
                            r
                            for r in available_roles
                            if r["name"] in ["designer", "developer"]
                        ]
                    elif "test" in goal_lower:
                        available_roles = [
                            r
                            for r in available_roles
                            if r["name"] in ["tester", "developer"]
                        ]
                    elif "api" in goal_lower or "backend" in goal_lower:
                        available_roles = [
                            r
                            for r in available_roles
                            if r["name"] in ["developer", "analyst"]
                        ]

                return {"ok": True, "roles": available_roles}

        return SimpleRoleEvaluator()

    def _sort_tasks_by_priority_and_dependencies(self, tasks: List[Task]) -> List[Task]:
        """按优先级和依赖关系排序任务"""
        # 创建任务映射
        task_map = {task.id: task for task in tasks}

        # 拓扑排序处理依赖关系
        sorted_tasks = []
        visited = set()
        temp_visited = set()

        def dfs(task: Task):
            if task.id in temp_visited:
                # 检测到循环依赖，跳过
                return
            if task.id in visited:
                return

            temp_visited.add(task.id)

            # 先处理依赖的任务
            for dep_id in task.dependencies:
                if dep_id in task_map:
                    dfs(task_map[dep_id])

            temp_visited.remove(task.id)
            visited.add(task.id)
            sorted_tasks.append(task)

        # 按优先级分组
        priority_groups = {
            Priority.CRITICAL: [],
            Priority.HIGH: [],
            Priority.MEDIUM: [],
            Priority.LOW: [],
        }

        for task in tasks:
            priority_groups[task.priority].append(task)

        # 按优先级顺序处理每组任务
        final_sorted = []
        for priority in [
            Priority.CRITICAL,
            Priority.HIGH,
            Priority.MEDIUM,
            Priority.LOW,
        ]:
            group_tasks = priority_groups[priority]
            group_sorted = []
            group_visited = set()

            for task in group_tasks:
                if task.id not in group_visited:
                    temp_sorted_tasks = []
                    temp_visited_set = set()

                    def group_dfs(t: Task):
                        if t.id in temp_visited_set or t.id in group_visited:
                            return
                        temp_visited_set.add(t.id)

                        for dep_id in t.dependencies:
                            if dep_id in task_map and task_map[dep_id] in group_tasks:
                                group_dfs(task_map[dep_id])

                        temp_sorted_tasks.append(t)
                        group_visited.add(t.id)

                    group_dfs(task)
                    group_sorted.extend(temp_sorted_tasks)

            final_sorted.extend(group_sorted)

        return final_sorted

    def _find_best_role_for_task(
        self, task: Task, available_roles: List[str]
    ) -> Optional[str]:
        """为任务找到最佳角色"""
        suitable_roles = []

        for role in available_roles:
            if self._is_role_suitable_for_task(role, task):
                score = self._calculate_role_suitability_score(role, task)
                suitable_roles.append((role, score))

        if not suitable_roles:
            # 如果没有完全匹配的角色，选择最通用的角色
            return self._get_fallback_role(available_roles)

        # 按适合度分数排序，选择最佳角色
        suitable_roles.sort(key=lambda x: x[1], reverse=True)
        return suitable_roles[0][0]

    def _is_role_suitable_for_task(self, role: str, task: Task) -> bool:
        """检查角色是否适合任务"""
        role_caps = self.role_capabilities.get(role, set())
        required_caps = set(task.required_roles)

        if not required_caps:
            return True  # 没有特定要求，任何角色都可以

        # 检查是否有交集
        return bool(role_caps.intersection(required_caps))

    def _calculate_role_suitability_score(self, role: str, task: Task) -> float:
        """计算角色对任务的适合度分数"""
        score = 0.0

        # 能力匹配分数
        role_caps = self.role_capabilities.get(role, set())
        required_caps = set(task.required_roles)

        if required_caps:
            capability_match = len(role_caps.intersection(required_caps)) / len(
                required_caps
            )
            score += capability_match * 0.4
        else:
            score += 0.4  # 没有特定要求时给基础分

        # 工作负载分数（负载越低分数越高）
        current_workload = self.role_workload.get(role, 0)
        max_workload = 8 * 3600  # 假设最大工作负载为8小时
        workload_score = max(0, (max_workload - current_workload) / max_workload)
        score += workload_score * 0.3

        # 历史性能分数
        performance = self.role_performance.get(role, {})
        performance_score = (
            performance.get("success_rate", 1.0) * 0.4
            + (2.0 - performance.get("avg_completion_time", 1.0)) * 0.3
            + performance.get("quality_score", 1.0) * 0.3
        ) / 3
        score += max(0, performance_score) * 0.3

        return min(score, 1.0)

    def _get_fallback_role(self, available_roles: List[str]) -> Optional[str]:
        """获取备用角色"""
        # 优先选择开发者角色作为备用
        if "developer" in available_roles:
            return "developer"
        elif "manager" in available_roles:
            return "manager"
        elif available_roles:
            return available_roles[0]
        return None

    def update_role_performance(
        self,
        role: str,
        task_id: str,
        success: bool,
        completion_time: float,
        quality_score: float = 1.0,
    ):
        """更新角色性能数据"""
        perf = self.role_performance[role]

        # 使用指数移动平均更新性能指标
        alpha = 0.1  # 学习率

        perf["success_rate"] = (1 - alpha) * perf["success_rate"] + alpha * (
            1.0 if success else 0.0
        )
        perf["avg_completion_time"] = (1 - alpha) * perf[
            "avg_completion_time"
        ] + alpha * completion_time
        perf["quality_score"] = (1 - alpha) * perf[
            "quality_score"
        ] + alpha * quality_score

        # 更新工作负载
        if role in self.role_workload:
            self.role_workload[role] = max(
                0, self.role_workload[role] - completion_time
            )

    def get_allocation_stats(self) -> Dict[str, Any]:
        """获取分配统计信息"""
        return {
            "role_workload": dict(self.role_workload),
            "role_performance": dict(self.role_performance),
            "total_allocations": len(self.allocation_history),
            "recent_allocations": list(self.allocation_history)[-10:],
        }


class ConflictDetector:
    """多维度冲突检测器"""

    def __init__(self, config: SoloConfig):
        self.config = config
        self.conflict_history: deque = deque(maxlen=500)
        self.resource_limits: Dict[ResourceType, float] = {
            ResourceType.CPU: 0.8,  # 80% CPU使用率限制
            ResourceType.MEMORY: 0.9,  # 90% 内存使用率限制
            ResourceType.NETWORK: 100.0,  # 100 Mbps
            ResourceType.STORAGE: 0.95,  # 95% 存储使用率限制
            ResourceType.API_QUOTA: 1000.0,  # 每小时1000次API调用
            ResourceType.CONCURRENT_TASKS: 10.0,  # 最多10个并发任务
        }

    def detect_conflicts(
        self, tasks: List[Task], allocation: Dict[str, List[Task]]
    ) -> List[Conflict]:
        """检测多维度冲突"""
        conflicts = []

        # 检测资源冲突
        conflicts.extend(self._detect_resource_conflicts(tasks))

        # 检测依赖冲突
        conflicts.extend(self._detect_dependency_conflicts(tasks))

        # 检测优先级冲突
        conflicts.extend(self._detect_priority_conflicts(tasks, allocation))

        # 检测角色能力冲突
        conflicts.extend(self._detect_role_capability_conflicts(tasks, allocation))

        # 记录冲突历史
        for conflict in conflicts:
            self.conflict_history.append(
                {"conflict": conflict, "timestamp": datetime.now()}
            )

        return conflicts

    def _detect_resource_conflicts(self, tasks: List[Task]) -> List[Conflict]:
        """检测资源冲突"""
        conflicts = []
        resource_usage = defaultdict(float)

        # 计算总资源使用量
        for task in tasks:
            if task.status in ["assigned", "running"]:
                for resource_type, usage in task.required_resources.items():
                    resource_usage[resource_type] += usage

        # 检查是否超过限制
        for resource_type, total_usage in resource_usage.items():
            limit = self.resource_limits.get(resource_type, float("inf"))
            if total_usage > limit:
                affected_tasks = [
                    task.id
                    for task in tasks
                    if task.status in ["assigned", "running"]
                    and resource_type in task.required_resources
                ]

                conflicts.append(
                    Conflict(
                        conflict_type="resource",
                        severity="high" if total_usage > limit * 1.2 else "medium",
                        description=f"Resource {resource_type.value} usage ({total_usage:.2f}) exceeds limit ({limit:.2f})",
                        affected_tasks=affected_tasks,
                        suggested_resolution=f"Reduce {resource_type.value} usage or increase resource limits",
                        metadata={
                            "resource_type": resource_type.value,
                            "current_usage": total_usage,
                            "limit": limit,
                            "overflow": total_usage - limit,
                        },
                    )
                )

        return conflicts

    def _detect_dependency_conflicts(self, tasks: List[Task]) -> List[Conflict]:
        """检测依赖冲突"""
        conflicts = []
        task_map = {task.id: task for task in tasks}

        # 检测循环依赖
        visited = set()
        rec_stack = set()

        def has_cycle(task_id: str) -> bool:
            if task_id in rec_stack:
                return True
            if task_id in visited:
                return False

            visited.add(task_id)
            rec_stack.add(task_id)

            task = task_map.get(task_id)
            if task:
                for dep_id in task.dependencies:
                    if has_cycle(dep_id):
                        return True

            rec_stack.remove(task_id)
            return False

        for task in tasks:
            if task.id not in visited and has_cycle(task.id):
                conflicts.append(
                    Conflict(
                        conflict_type="dependency",
                        severity="critical",
                        description=f"Circular dependency detected involving task {task.id}",
                        affected_tasks=[task.id],
                        suggested_resolution="Remove circular dependencies or restructure task dependencies",
                        metadata={"cycle_root": task.id},
                    )
                )

        # 检测缺失依赖
        for task in tasks:
            for dep_id in task.dependencies:
                if dep_id not in task_map:
                    conflicts.append(
                        Conflict(
                            conflict_type="dependency",
                            severity="high",
                            description=f"Task {task.id} depends on missing task {dep_id}",
                            affected_tasks=[task.id],
                            suggested_resolution=f"Create missing task {dep_id} or remove dependency",
                            metadata={"missing_dependency": dep_id},
                        )
                    )

        return conflicts

    def _detect_priority_conflicts(
        self, tasks: List[Task], allocation: Dict[str, List[Task]]
    ) -> List[Conflict]:
        """检测优先级冲突"""
        conflicts = []

        # 检查每个角色的任务优先级分布
        for role, role_tasks in allocation.items():
            if len(role_tasks) <= 1:
                continue

            # 按优先级分组
            priority_groups = defaultdict(list)
            for task in role_tasks:
                priority_groups[task.priority].append(task)

            # 检查是否有低优先级任务阻塞高优先级任务
            high_priority_tasks = (
                priority_groups[Priority.CRITICAL] + priority_groups[Priority.HIGH]
            )
            low_priority_tasks = (
                priority_groups[Priority.MEDIUM] + priority_groups[Priority.LOW]
            )

            for high_task in high_priority_tasks:
                for low_task in low_priority_tasks:
                    # 检查低优先级任务是否会延迟高优先级任务
                    if (
                        low_task.estimated_duration > high_task.estimated_duration * 2
                        and low_task.status == "assigned"
                        and high_task.status == "pending"
                    ):

                        conflicts.append(
                            Conflict(
                                conflict_type="priority",
                                severity="medium",
                                description=f"Low priority task {low_task.id} may delay high priority task {high_task.id}",
                                affected_tasks=[high_task.id, low_task.id],
                                suggested_resolution="Reorder tasks or reassign to different roles",
                                metadata={
                                    "high_priority_task": high_task.id,
                                    "low_priority_task": low_task.id,
                                    "role": role,
                                },
                            )
                        )

        return conflicts

    def _detect_role_capability_conflicts(
        self, tasks: List[Task], allocation: Dict[str, List[Task]]
    ) -> List[Conflict]:
        """检测角色能力冲突"""
        conflicts = []

        role_capabilities = {
            "analyst": {"analysis", "research", "data_processing", "reporting"},
            "developer": {
                "coding",
                "debugging",
                "testing",
                "deployment",
                "architecture",
            },
            "designer": {"ui_design", "ux_design", "prototyping", "visual_design"},
            "manager": {
                "planning",
                "coordination",
                "resource_management",
                "decision_making",
            },
            "qa": {"testing", "quality_assurance", "bug_tracking", "validation"},
        }

        for role, role_tasks in allocation.items():
            role_caps = role_capabilities.get(role, set())

            for task in role_tasks:
                required_caps = set(task.required_roles)
                if required_caps and not role_caps.intersection(required_caps):
                    conflicts.append(
                        Conflict(
                            conflict_type="role_capability",
                            severity="high",
                            description=f"Role {role} lacks required capabilities for task {task.id}",
                            affected_tasks=[task.id],
                            suggested_resolution=f"Reassign task to role with capabilities: {', '.join(required_caps)}",
                            metadata={
                                "role": role,
                                "role_capabilities": list(role_caps),
                                "required_capabilities": list(required_caps),
                                "missing_capabilities": list(required_caps - role_caps),
                            },
                        )
                    )

        return conflicts

    def get_conflict_stats(self) -> Dict[str, Any]:
        """获取冲突统计信息"""
        if not self.conflict_history:
            return {"total_conflicts": 0, "conflict_types": {}, "recent_conflicts": []}

        conflict_types = defaultdict(int)
        for entry in self.conflict_history:
            conflict_types[entry["conflict"].conflict_type] += 1

        return {
            "total_conflicts": len(self.conflict_history),
            "conflict_types": dict(conflict_types),
            "recent_conflicts": [
                entry["conflict"] for entry in list(self.conflict_history)[-5:]
            ],
        }


class OrchestratorTool:
    """编排工具主类"""

    def __init__(self, config: SoloConfig):
        self.config = config
        self.task_allocator = TaskAllocator(config)
        self.conflict_detector = ConflictDetector(config)

        # 初始化角色评估器
        from .roles import RolesTool
        self.roles = RolesTool(config)
        self.role_evaluator = self._create_simple_role_evaluator()

        # 学习和自适应优化（可选）
        if LearningEngine and AdaptiveOptimizer:
            self.learning_engine = LearningEngine(config)
            self.adaptive_optimizer = AdaptiveOptimizer(config)
            self.adaptive_optimizer.set_learning_engine(self.learning_engine)
        else:
            self.learning_engine = None
            self.adaptive_optimizer = None

        # 性能统计
        self.execution_stats = {
            "total_rounds": 0,
            "successful_rounds": 0,
            "avg_response_time": 0.0,
            "conflict_resolution_rate": 0.0,
        }

    async def run_round(
        self, mode: str, state: dict[str, Any] | None
    ) -> dict[str, Any]:
        start_time = time.time()
        mode = mode or "collab"
        state = state or {}
        history = state.get("history", [])
        goal = state.get("goal")
        stack = state.get("stack", ["python"])

        try:
            # 记录用户行为（如果学习引擎可用）
            if self.learning_engine and UserActionType:
                self.learning_engine.record_user_action(
                    action_type=UserActionType.TASK_ALLOCATION,
                    query=goal or "No specific goal",
                    context={
                        "mode": mode,
                        "stack": stack,
                        "history_length": len(history),
                    },
                    response_time=0.0,  # 将在最后更新
                    success=False,  # 将在最后更新
                )

            # 动态生成角色列表
            roles_result = self.roles.evaluate(goal, stack)
            if not roles_result.get("ok"):
                self._record_failure(start_time, "Failed to evaluate roles")
                return {"ok": False, "error": "Failed to evaluate roles"}

            # 从目标和历史中提取任务
            tasks = self._extract_tasks_from_goal_and_history(goal, history)

            # 应用自适应优化参数
            self._apply_adaptive_parameters()

            # 智能任务分配（集成学习优化）
            allocation = self._smart_task_allocation(tasks, roles_result["roles"], goal)

            # 冲突检测（集成学习优化）
            conflicts = self._smart_conflict_detection(
                allocation, roles_result["roles"]
            )

            # 生成动作列表
            actions = self._generate_optimized_actions(allocation, conflicts)

            # 记录性能指标
            response_time = time.time() - start_time
            self._record_performance_metrics(response_time, len(tasks), len(conflicts))

            # 更新统计信息
            self._update_execution_stats(response_time, True)

            # 触发自动优化（如果可用）
            optimization_results = []
            if self.adaptive_optimizer:
                try:
                    optimization_results = (
                        self.adaptive_optimizer.trigger_optimization_if_needed()
                    )
                except Exception:
                    optimization_results = []

            result = {
                "ok": True,
                "actions": actions,
                "conflicts": [
                    {
                        "type": c.type,
                        "severity": c.severity,
                        "reason": c.reason,
                        "resolution": c.resolution,
                        "involved_roles": c.involved_roles,
                    }
                    for c in conflicts
                ],
                "roles_used": roles_result["roles"],
                "task_allocation": {
                    role: len(tasks) for role, tasks in allocation.items()
                },
                "performance_metrics": {
                    "response_time": response_time,
                    "tasks_processed": len(tasks),
                    "conflicts_detected": len(conflicts),
                    "optimization_applied": len(optimization_results) > 0,
                },
                "learning_insights": self._get_learning_insights(),
            }

            # 记录成功的用户行为（如果学习引擎可用）
            if self.learning_engine and UserActionType:
                self.learning_engine.record_user_action(
                    action_type=UserActionType.TASK_ALLOCATION,
                    query=f"Allocated {len(tasks)} tasks to {len(allocation)} roles",
                    context={
                        "tasks_count": len(tasks),
                        "roles_count": len(allocation),
                        "conflicts_count": len(conflicts),
                    },
                    response_time=response_time,
                    success=True,
                )

            return result

        except Exception as e:
            self._record_failure(start_time, str(e))
            return {"ok": False, "error": str(e)}

    def _smart_task_allocation(
        self, tasks: List[Task], available_roles: List[Dict], goal: str
    ) -> Dict[str, List[Task]]:
        """智能任务分配，集成学习优化"""
        # 获取学习建议
        recommendations = self.learning_engine.get_optimization_recommendations()

        # 基于历史数据调整分配策略
        allocation_strategy = self._determine_allocation_strategy(recommendations, goal)

        # 应用优化的任务分配
        if allocation_strategy == "performance_optimized":
            return self._performance_optimized_allocation(tasks, available_roles)
        elif allocation_strategy == "load_balanced":
            return self._load_balanced_allocation(tasks, available_roles)
        else:
            return self.task_allocator.allocate_tasks(tasks, available_roles)

    def _smart_conflict_detection(
        self, allocation: Dict[str, List[Task]], available_roles: List[Dict]
    ) -> List[Conflict]:
        """智能冲突检测，集成学习优化"""
        # 基础冲突检测
        conflicts = self.conflict_detector.detect_conflicts(allocation, available_roles)

        # 基于学习数据的高级冲突预测
        predicted_conflicts = self._predict_conflicts_from_history(allocation)
        conflicts.extend(predicted_conflicts)

        # 冲突优先级重排
        conflicts = self._rerank_conflicts_by_impact(conflicts)

        return conflicts

    def _determine_allocation_strategy(
        self, recommendations: List[Dict], goal: str
    ) -> str:
        """基于学习建议确定分配策略"""
        performance_issues = any(
            "performance" in rec.get("type", "")
            or "bottleneck" in rec.get("description", "")
            for rec in recommendations
        )

        if performance_issues:
            return "performance_optimized"
        elif "complex" in goal.lower() or "large" in goal.lower():
            return "load_balanced"
        else:
            return "standard"

    def _performance_optimized_allocation(
        self, tasks: List[Task], available_roles: List[Dict]
    ) -> Dict[str, List[Task]]:
        """性能优化的任务分配"""
        allocation = {role["name"]: [] for role in available_roles}

        # 优先分配高优先级任务给最适合的角色
        high_priority_tasks = [
            t for t in tasks if t.priority in [Priority.CRITICAL, Priority.HIGH]
        ]
        other_tasks = [
            t for t in tasks if t.priority not in [Priority.CRITICAL, Priority.HIGH]
        ]

        # 先分配高优先级任务
        for task in high_priority_tasks:
            best_role = self._find_optimal_role(task, available_roles, allocation)
            if best_role:
                allocation[best_role].append(task)
                task.assigned_role = best_role

        # 再分配其他任务
        for task in other_tasks:
            best_role = self._find_optimal_role(task, available_roles, allocation)
            if best_role:
                allocation[best_role].append(task)
                task.assigned_role = best_role

        return allocation

    def _load_balanced_allocation(
        self, tasks: List[Task], available_roles: List[Dict]
    ) -> Dict[str, List[Task]]:
        """负载均衡的任务分配"""
        allocation = {role["name"]: [] for role in available_roles}

        # 按估计时间排序任务
        sorted_tasks = sorted(tasks, key=lambda t: t.estimated_time, reverse=True)

        for task in sorted_tasks:
            # 找到当前工作负载最轻的合适角色
            suitable_roles = self._get_suitable_roles(task, available_roles)
            if suitable_roles:
                # 选择工作负载最轻的角色
                lightest_role = min(
                    suitable_roles,
                    key=lambda r: sum(t.estimated_time for t in allocation[r]),
                )
                allocation[lightest_role].append(task)
                task.assigned_role = lightest_role

        return allocation

    def _find_optimal_role(
        self,
        task: Task,
        available_roles: List[Dict],
        current_allocation: Dict[str, List[Task]],
    ) -> str:
        """找到最优角色"""
        role_scores = {}

        for role in available_roles:
            role_name = role["name"]

            # 基础兼容性得分
            compatibility_score = (
                self.task_allocator._calculate_role_task_compatibility(task, role)
            )

            # 工作负载惩罚
            current_workload = sum(
                t.estimated_time for t in current_allocation[role_name]
            )
            workload_penalty = current_workload / 200  # 调整惩罚系数

            role_scores[role_name] = final_score

        return max(role_scores, key=role_scores.get) if role_scores else None

    def _get_suitable_roles(self, task: Task, available_roles: List[Dict]) -> List[str]:
        """获取适合的角色列表"""
        suitable_roles = []

        for role in available_roles:
            compatibility = self.task_allocator._calculate_role_task_compatibility(
                task, role
            )
            if compatibility > 0.5:  # 兼容性阈值
                suitable_roles.append(role["name"])

        return suitable_roles

    def _get_role_historical_success(
        self, role_name: str, task_description: str
    ) -> float:
        """获取角色历史成功率"""
        # 从学习引擎获取历史数据
        stats = self.learning_engine.get_learning_stats()

        # 简化的成功率计算
        base_success_rate = stats.get("success_rate", 0.8)

        # 基于角色名称的调整
        role_adjustments = {
            "architect": 0.1 if "design" in task_description.lower() else 0.0,
            "coder": 0.1 if "implement" in task_description.lower() else 0.0,
            "tester": 0.1 if "test" in task_description.lower() else 0.0,
        }

        adjustment = role_adjustments.get(role_name.lower(), 0.0)
        return base_success_rate + adjustment

    def _predict_conflicts_from_history(
        self, allocation: Dict[str, List[Task]]
    ) -> List[Conflict]:
        """基于历史数据预测冲突"""
        predicted_conflicts = []

        # 获取学习洞察
        insights = self.learning_engine.analyze_patterns()

        for insight in insights:
            if "bottleneck" in insight.description.lower():
                # 预测性能瓶颈冲突
                predicted_conflicts.append(
                    Conflict(
                        type="predicted_bottleneck",
                        involved_tasks=[],
                        involved_roles=list(allocation.keys()),
                        severity="medium",
                        reason=f"Predicted bottleneck based on pattern: {insight.description}",
                        resolution="Consider load balancing or resource optimization",
                    )
                )

        return predicted_conflicts

    def _rerank_conflicts_by_impact(self, conflicts: List[Conflict]) -> List[Conflict]:
        """按影响重新排序冲突"""
        severity_order = {"high": 3, "medium": 2, "low": 1}

        return sorted(
            conflicts,
            key=lambda c: (severity_order.get(c.severity, 0), len(c.involved_tasks)),
            reverse=True,
        )

    def _generate_optimized_actions(
        self, allocation: Dict[str, List[Task]], conflicts: List[Conflict]
    ) -> List[Dict]:
        """生成优化的动作列表"""
        actions = []

        # 获取优化参数
        max_concurrent_tasks = (
            self.adaptive_optimizer.get_parameter_value("thread_pool_size") or 4
        )

        for role_name, assigned_tasks in allocation.items():
            if assigned_tasks:
                # 限制并发任务数量
                task_batches = [
                    assigned_tasks[i : i + max_concurrent_tasks]
                    for i in range(0, len(assigned_tasks), max_concurrent_tasks)
                ]

                for batch_idx, task_batch in enumerate(task_batches):
                    task_names = [task.name for task in task_batch]
                    action_name = (
                        f"Execute batch {batch_idx + 1}: {', '.join(task_names)}"
                    )

                    actions.append(
                        {
                            "role": role_name,
                            "action": action_name,
                            "batch_id": batch_idx + 1,
                            "tasks": [
                                {
                                    "id": task.id,
                                    "name": task.name,
                                    "priority": task.priority.name,
                                    "estimated_time": task.estimated_time,
                                }
                                for task in task_batch
                            ],
                            "conflicts": [
                                c.reason
                                for c in conflicts
                                if role_name in c.involved_roles
                            ],
                        }
                    )

        return actions

    def _apply_adaptive_parameters(self):
        """应用自适应参数"""
        # 获取并应用优化参数
        context_limit = self.adaptive_optimizer.get_parameter_value(
            "context_size_limit"
        )
        if context_limit:
            # 这里可以调整上下文收集的限制
            pass

        timeout = self.adaptive_optimizer.get_parameter_value("query_timeout")
        if timeout:
            # 这里可以调整查询超时时间
            pass

    def _record_performance_metrics(
        self, response_time: float, tasks_count: int, conflicts_count: int
    ):
        """记录性能指标"""
        self.learning_engine.record_performance_metrics(
            response_time=response_time,
            memory_usage=0.5,  # 简化的内存使用率
            cpu_usage=0.3,  # 简化的CPU使用率
            success_rate=1.0,  # 成功率
            error_count=0,
            throughput=tasks_count / max(response_time, 0.1),
            context_size=tasks_count * 100,  # 估算的上下文大小
            memory_hits=0,
            cache_efficiency=0.8,
        )

    def _update_execution_stats(self, response_time: float, success: bool):
        """更新执行统计"""
        self.execution_stats["total_rounds"] += 1
        if success:
            self.execution_stats["successful_rounds"] += 1

        # 更新平均响应时间
        total_rounds = self.execution_stats["total_rounds"]
        current_avg = self.execution_stats["avg_response_time"]
        self.execution_stats["avg_response_time"] = (
            current_avg * (total_rounds - 1) + response_time
        ) / total_rounds

    def _record_failure(self, start_time: float, error_message: str):
        """记录失败"""
        response_time = time.time() - start_time

        self.learning_engine.record_user_action(
            action_type=UserActionType.ERROR_HANDLING,
            query="Orchestrator execution failed",
            context={"error": error_message},
            response_time=response_time,
            success=False,
            error_message=error_message,
        )

        self._update_execution_stats(response_time, False)

    def _get_learning_insights(self) -> List[Dict]:
        """获取学习洞察"""
        insights = self.learning_engine.analyze_patterns()
        return [
            {
                "type": insight.pattern_type.value,
                "confidence": insight.confidence,
                "description": insight.description,
                "recommendations": insight.recommendations[:3],  # 只返回前3个建议
                "impact_score": insight.impact_score,
            }
            for insight in insights[-5:]
        ]  # 只返回最近5个洞察

    def get_optimization_status(self) -> Dict[str, Any]:
        """获取优化状态"""
        return {
            "execution_stats": self.execution_stats,
            "learning_stats": self.learning_engine.get_learning_stats(),
            "optimization_status": self.adaptive_optimizer.get_optimization_status(),
            "current_parameters": {
                name: param.current_value
                for name, param in self.adaptive_optimizer.parameters.items()
            },
        }

    def cleanup(self):
        """清理资源"""
        if hasattr(self, "adaptive_optimizer"):
            self.adaptive_optimizer.cleanup()

    def _extract_tasks_from_goal_and_history(
        self, goal: str, history: List
    ) -> List[Task]:
        """从目标和历史中提取任务"""
        tasks = []

        if not goal:
            return tasks

    def _create_simple_role_evaluator(self):
        """创建简单的角色评估器"""

        class SimpleRoleEvaluator:
            def evaluate(self, goal: str, stack: List[str]) -> Dict[str, Any]:
                """评估并返回适合的角色列表"""
                available_roles = [
                    {
                        "name": "analyst",
                        "capabilities": ["analysis", "research", "planning"],
                    },
                    {
                        "name": "developer",
                        "capabilities": ["coding", "implementation", "debugging"],
                    },
                    {
                        "name": "designer",
                        "capabilities": ["ui_design", "ux_design", "prototyping"],
                    },
                    {
                        "name": "tester",
                        "capabilities": ["testing", "quality_assurance", "validation"],
                    },
                    {
                        "name": "manager",
                        "capabilities": [
                            "coordination",
                            "planning",
                            "resource_management",
                        ],
                    },
                ]

                # 根据目标和技术栈筛选角色
                if goal:
                    goal_lower = goal.lower()
                    if "design" in goal_lower or "ui" in goal_lower:
                        available_roles = [
                            r
                            for r in available_roles
                            if r["name"] in ["designer", "developer"]
                        ]
                    elif "test" in goal_lower:
                        available_roles = [
                            r
                            for r in available_roles
                            if r["name"] in ["tester", "developer"]
                        ]
                    elif "api" in goal_lower or "backend" in goal_lower:
                        available_roles = [
                            r
                            for r in available_roles
                            if r["name"] in ["developer", "analyst"]
                        ]

                return {"ok": True, "roles": available_roles}

        return SimpleRoleEvaluator()

        # 基于目标生成基础任务
        goal_lower = goal.lower()

        if "web" in goal_lower or "frontend" in goal_lower:
            tasks.extend(
                [
                    Task(
                        id="design_ui",
                        name="Design UI",
                        description="Design user interface components",
                        priority=Priority.HIGH,
                        estimated_duration=120,
                        required_resources={ResourceType.MEMORY: 0.3},
                        dependencies=[],
                        required_roles=["ui_design"],
                    ),
                    Task(
                        id="implement_frontend",
                        name="Implement Frontend",
                        description="Implement frontend components",
                        priority=Priority.HIGH,
                        estimated_duration=240,
                        required_resources={
                            ResourceType.CPU: 0.5,
                            ResourceType.MEMORY: 0.4,
                        },
                        dependencies=["design_ui"],
                        required_roles=["coding"],
                    ),
                    Task(
                        id="test_frontend",
                        name="Test Frontend",
                        description="Test frontend functionality",
                        priority=Priority.MEDIUM,
                        estimated_duration=60,
                        required_resources={ResourceType.CPU: 0.3},
                        dependencies=["implement_frontend"],
                        required_roles=["testing"],
                    ),
                ]
            )

        if "api" in goal_lower or "backend" in goal_lower:
            tasks.extend(
                [
                    Task(
                        id="design_api",
                        name="Design API",
                        description="Design API endpoints and data models",
                        priority=Priority.HIGH,
                        estimated_duration=90,
                        required_resources={
                            ResourceType.MEMORY: 0.2,
                            ResourceType.API_QUOTA: 10,
                        },
                        dependencies=[],
                        required_roles=["analysis", "architecture"],
                    ),
                    Task(
                        id="implement_api",
                        name="Implement API",
                        description="Implement API endpoints",
                        priority=Priority.HIGH,
                        estimated_duration=180,
                        required_resources={
                            ResourceType.CPU: 0.6,
                            ResourceType.MEMORY: 0.5,
                            ResourceType.API_QUOTA: 20,
                        },
                        dependencies=["design_api"],
                        required_roles=["coding"],
                    ),
                    Task(
                        id="test_api",
                        name="Test API",
                        description="Test API functionality",
                        priority=Priority.MEDIUM,
                        estimated_duration=60,
                        required_resources={ResourceType.API_QUOTA: 15},
                        dependencies=["implement_api"],
                        required_roles=["testing"],
                    ),
                ]
            )

        if "database" in goal_lower or "data" in goal_lower:
            tasks.extend(
                [
                    Task(
                        id="design_schema",
                        name="Design Database Schema",
                        description="Design database schema",
                        priority=Priority.HIGH,
                        estimated_duration=60,
                        required_resources={
                            ResourceType.MEMORY: 0.2,
                            ResourceType.STORAGE: 0.1,
                        },
                        dependencies=[],
                        required_roles=["analysis", "data_processing"],
                    ),
                    Task(
                        id="setup_database",
                        name="Setup Database",
                        description="Setup and configure database",
                        priority=Priority.HIGH,
                        estimated_duration=90,
                        required_resources={
                            ResourceType.STORAGE: 0.3,
                            ResourceType.MEMORY: 0.3,
                        },
                        dependencies=["design_schema"],
                        required_roles=["coding"],
                    ),
                ]
            )

        # 如果没有特定任务，生成通用任务
        if not tasks:
            tasks.append(
                Task(
                    id="analyze_goal",
                    name="Analyze Goal",
                    description=f"Analyze and break down: {goal}",
                    priority=Priority.HIGH,
                    estimated_duration=30,
                    required_resources={ResourceType.MEMORY: 0.1},
                    dependencies=[],
                    required_roles=["analysis"],
                )
            )

        return tasks
