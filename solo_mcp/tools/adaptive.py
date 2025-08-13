from __future__ import annotations

import time
import statistics
from typing import Dict, List, Any, Optional, TYPE_CHECKING
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
import json
from pathlib import Path

from ..config import SoloConfig

# 使用 TYPE_CHECKING 避免循环导入
if TYPE_CHECKING:
    from .learning import LearningEngine
    from .memory import MemoryTool
    from .context import ContextTool
    from .orchestrator import OrchestratorTool


class OptimizationType(Enum):
    RESPONSE_TIME = "response_time"
    MEMORY_USAGE = "memory_usage"
    CPU_USAGE = "cpu_usage"
    SUCCESS_RATE = "success_rate"
    THROUGHPUT = "throughput"
    CONTEXT_RELEVANCE = "context_relevance"
    MEMORY_EFFICIENCY = "memory_efficiency"
    RESOURCE_ALLOCATION = "resource_allocation"


class AdaptationStrategy(Enum):
    CONSERVATIVE = "conservative"  # 小幅调整
    MODERATE = "moderate"  # 中等调整
    AGGRESSIVE = "aggressive"  # 大幅调整
    EXPERIMENTAL = "experimental"  # 实验性调整


@dataclass
class OptimizationParameter:
    name: str
    current_value: float
    min_value: float
    max_value: float
    step_size: float
    optimization_type: OptimizationType
    last_updated: datetime
    performance_impact: float = 0.0
    adjustment_count: int = 0


@dataclass
class OptimizationResult:
    parameter_name: str
    old_value: float
    new_value: float
    performance_before: float
    performance_after: float
    improvement: float
    timestamp: datetime
    strategy_used: AdaptationStrategy
    success: bool
    notes: str = ""


@dataclass
class ResourceUsage:
    cpu_percent: float
    memory_mb: float
    response_time_ms: float
    throughput_ops_per_sec: float
    error_rate: float
    timestamp: datetime


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self, config: SoloConfig):
        self.config = config
        self.metrics_history: deque = deque(maxlen=1000)
        self.alert_thresholds = {
            "response_time": 2.0,  # 秒
            "memory_usage": 0.8,  # 80%
            "cpu_usage": 0.7,  # 70%
            "error_rate": 0.1,  # 10%
            "success_rate": 0.9,  # 90%
        }
        self.performance_baseline = {
            "response_time": 0.5,
            "memory_usage": 0.3,
            "cpu_usage": 0.2,
            "success_rate": 0.95,
            "throughput": 10.0,
        }
        self.monitoring_active = True
        self._lock = threading.Lock()

    def record_metrics(self, metrics: Dict[str, float]):
        """记录性能指标"""
        with self._lock:
            timestamp = datetime.now()
            self.metrics_history.append(
                {"timestamp": timestamp, "metrics": metrics.copy()}
            )

    def get_current_performance(self) -> Dict[str, float]:
        """获取当前性能状态"""
        with self._lock:
            if not self.metrics_history:
                return self.performance_baseline.copy()

            # 计算最近10个记录的平均值
            recent_metrics = list(self.metrics_history)[-10:]
            avg_metrics = {}

            for key in self.performance_baseline.keys():
                values = [
                    m["metrics"].get(key, 0)
                    for m in recent_metrics
                    if key in m["metrics"]
                ]
                if values:
                    avg_metrics[key] = statistics.mean(values)
                else:
                    avg_metrics[key] = self.performance_baseline[key]

            return avg_metrics

    def detect_performance_issues(self) -> List[Dict[str, Any]]:
        """检测性能问题"""
        current_perf = self.get_current_performance()
        issues = []

        # 检查响应时间
        if current_perf["response_time"] > self.alert_thresholds["response_time"]:
            issues.append(
                {
                    "type": "high_response_time",
                    "severity": "high",
                    "current_value": current_perf["response_time"],
                    "threshold": self.alert_thresholds["response_time"],
                    "description": f"响应时间 {current_perf['response_time']:.2f}s 超过阈值 {self.alert_thresholds['response_time']}s",
                }
            )

        # 检查内存使用
        if current_perf["memory_usage"] > self.alert_thresholds["memory_usage"]:
            issues.append(
                {
                    "type": "high_memory_usage",
                    "severity": "medium",
                    "current_value": current_perf["memory_usage"],
                    "threshold": self.alert_thresholds["memory_usage"],
                    "description": f"内存使用率 {current_perf['memory_usage']:.1%} 超过阈值 {self.alert_thresholds['memory_usage']:.1%}",
                }
            )

        # 检查CPU使用
        if current_perf["cpu_usage"] > self.alert_thresholds["cpu_usage"]:
            issues.append(
                {
                    "type": "high_cpu_usage",
                    "severity": "medium",
                    "current_value": current_perf["cpu_usage"],
                    "threshold": self.alert_thresholds["cpu_usage"],
                    "description": f"CPU使用率 {current_perf['cpu_usage']:.1%} 超过阈值 {self.alert_thresholds['cpu_usage']:.1%}",
                }
            )

        # 检查成功率
        if current_perf["success_rate"] < self.alert_thresholds["success_rate"]:
            issues.append(
                {
                    "type": "low_success_rate",
                    "severity": "high",
                    "current_value": current_perf["success_rate"],
                    "threshold": self.alert_thresholds["success_rate"],
                    "description": f"成功率 {current_perf['success_rate']:.1%} 低于阈值 {self.alert_thresholds['success_rate']:.1%}",
                }
            )

        return issues

    def get_performance_trend(self, metric: str, hours: int = 1) -> Dict[str, Any]:
        """获取性能趋势"""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        with self._lock:
            recent_data = [
                record
                for record in self.metrics_history
                if record["timestamp"] >= cutoff_time and metric in record["metrics"]
            ]

        if len(recent_data) < 2:
            return {
                "trend": "insufficient_data",
                "change": 0.0,
                "data_points": len(recent_data),
            }

        values = [record["metrics"][metric] for record in recent_data]

        # 计算趋势
        first_half = values[: len(values) // 2]
        second_half = values[len(values) // 2 :]

        avg_first = statistics.mean(first_half)
        avg_second = statistics.mean(second_half)

        change_percent = (
            ((avg_second - avg_first) / avg_first) * 100 if avg_first > 0 else 0
        )

        if abs(change_percent) < 5:
            trend = "stable"
        elif change_percent > 0:
            trend = "increasing"
        else:
            trend = "decreasing"

        return {
            "trend": trend,
            "change": change_percent,
            "data_points": len(recent_data),
            "current_avg": statistics.mean(values),
            "min_value": min(values),
            "max_value": max(values),
        }


class AdaptiveOptimizer:
    """自适应优化器"""

    def __init__(self, config: SoloConfig, parent_tool: Any = None):
        self.config = config
        self.parent_tool = parent_tool

        # 性能监控器
        self.performance_monitor = PerformanceMonitor(config)

        # 优化参数
        self.parameters: Dict[str, OptimizationParameter] = {}
        self._init_default_parameters()

        # 优化历史
        self.optimization_history: List[OptimizationResult] = []

        # 自适应策略
        self.current_strategy = AdaptationStrategy.MODERATE
        self.strategy_performance: Dict[AdaptationStrategy, List[float]] = defaultdict(
            list
        )

        # 优化控制
        self.optimization_enabled = True
        self.last_optimization = datetime.now()
        self.optimization_interval = timedelta(minutes=5)  # 5分钟优化一次
        self.min_data_points = 10  # 最少数据点才开始优化

        # 学习引擎引用（延迟初始化）
        self.learning_engine: Optional[Any] = None

        # 线程锁
        self._lock = threading.Lock()

    def _init_default_parameters(self):
        """初始化默认优化参数"""
        default_params = [
            (
                "context_search_limit",
                10.0,
                5.0,
                50.0,
                1.0,
                OptimizationType.CONTEXT_RELEVANCE,
            ),
            (
                "memory_search_limit",
                5.0,
                3.0,
                20.0,
                1.0,
                OptimizationType.MEMORY_EFFICIENCY,
            ),
            (
                "response_timeout",
                30.0,
                10.0,
                120.0,
                5.0,
                OptimizationType.RESPONSE_TIME,
            ),
            (
                "max_context_size",
                5000.0,
                1000.0,
                20000.0,
                500.0,
                OptimizationType.MEMORY_USAGE,
            ),
            (
                "memory_priority_boost",
                0.0,
                -2.0,
                2.0,
                0.5,
                OptimizationType.MEMORY_EFFICIENCY,
            ),
            (
                "context_relevance_threshold",
                0.3,
                0.1,
                0.8,
                0.05,
                OptimizationType.CONTEXT_RELEVANCE,
            ),
            (
                "task_allocation_weight",
                1.0,
                0.5,
                2.0,
                0.1,
                OptimizationType.RESOURCE_ALLOCATION,
            ),
            (
                "conflict_detection_sensitivity",
                0.7,
                0.3,
                1.0,
                0.1,
                OptimizationType.SUCCESS_RATE,
            ),
        ]

        for name, current, min_val, max_val, step, opt_type in default_params:
            self.parameters[name] = OptimizationParameter(
                name=name,
                current_value=current,
                min_value=min_val,
                max_value=max_val,
                step_size=step,
                optimization_type=opt_type,
                last_updated=datetime.now(),
            )

    def set_learning_engine(self, learning_engine: Any):
        """设置学习引擎引用"""
        self.learning_engine = learning_engine

    def get_current_parameters(self) -> Dict[str, Any]:
        """获取当前优化参数"""
        with self._lock:
            return {
                name: param.current_value for name, param in self.parameters.items()
            }

    def optimize_parameter(
        self, parameter_name: str, target_metric: str, current_performance: float
    ) -> bool:
        """优化单个参数"""
        if parameter_name not in self.parameters:
            return False

        param = self.parameters[parameter_name]

        # 记录优化前性能
        performance_before = current_performance

        # 根据当前策略确定调整方向和幅度
        adjustment = self._calculate_adjustment(
            param, target_metric, current_performance
        )

        # 应用调整
        old_value = param.current_value
        new_value = max(param.min_value, min(param.max_value, old_value + adjustment))

        if abs(new_value - old_value) < param.step_size * 0.1:
            return False  # 调整太小，跳过

        param.current_value = new_value
        param.last_updated = datetime.now()
        param.adjustment_count += 1

        # 记录优化结果
        result = OptimizationResult(
            parameter_name=parameter_name,
            old_value=old_value,
            new_value=new_value,
            performance_before=performance_before,
            performance_after=0.0,  # 将在后续更新
            improvement=0.0,
            timestamp=datetime.now(),
            strategy_used=self.current_strategy,
            success=True,
        )

        self.optimization_history.append(result)

        return True

    def _calculate_adjustment(
        self,
        param: OptimizationParameter,
        target_metric: str,
        current_performance: float,
    ) -> float:
        """计算参数调整量"""
        baseline = self.performance_monitor.performance_baseline.get(target_metric, 1.0)

        # 性能差异
        performance_gap = baseline - current_performance

        # 根据策略确定调整幅度
        strategy_multipliers = {
            AdaptationStrategy.CONSERVATIVE: 0.5,
            AdaptationStrategy.MODERATE: 1.0,
            AdaptationStrategy.AGGRESSIVE: 2.0,
            AdaptationStrategy.EXPERIMENTAL: 3.0,
        }

        base_adjustment = param.step_size * strategy_multipliers[self.current_strategy]

        # 根据性能差异调整方向
        if performance_gap > 0:  # 性能低于基线，需要改进
            if param.optimization_type == OptimizationType.RESPONSE_TIME:
                # 响应时间类参数：减少值来改善性能
                return -base_adjustment
            else:
                # 其他类参数：增加值来改善性能
                return base_adjustment
        else:  # 性能高于基线，可以适度调整
            return base_adjustment * 0.5 if performance_gap < -0.1 else 0

    def trigger_optimization_if_needed(self) -> bool:
        """根据条件触发优化"""
        if not self.optimization_enabled:
            return False

        # 检查时间间隔
        if datetime.now() - self.last_optimization < self.optimization_interval:
            return False

        # 检查数据点数量
        if len(self.performance_monitor.metrics_history) < self.min_data_points:
            return False

        # 检查是否有性能问题
        issues = self.performance_monitor.detect_performance_issues()
        if not issues:
            return False

        # 执行优化
        return self._execute_optimization(issues)

    def _execute_optimization(self, issues: List[Dict[str, Any]]) -> bool:
        """执行优化"""
        optimized_count = 0
        current_perf = self.performance_monitor.get_current_performance()

        for issue in issues:
            issue_type = issue["type"]

            # 根据问题类型选择优化参数
            if issue_type == "high_response_time":
                params_to_optimize = [
                    "response_timeout",
                    "context_search_limit",
                    "max_context_size",
                ]
            elif issue_type == "high_memory_usage":
                params_to_optimize = ["max_context_size", "memory_search_limit"]
            elif issue_type == "low_success_rate":
                params_to_optimize = [
                    "conflict_detection_sensitivity",
                    "context_relevance_threshold",
                ]
            else:
                continue

            # 优化相关参数
            for param_name in params_to_optimize:
                if param_name in self.parameters:
                    target_metric = self._get_target_metric_for_issue(issue_type)
                    if self.optimize_parameter(
                        param_name, target_metric, current_perf.get(target_metric, 0)
                    ):
                        optimized_count += 1

        self.last_optimization = datetime.now()

        # 更新策略性能记录
        if optimized_count > 0:
            self.strategy_performance[self.current_strategy].append(optimized_count)
            self._update_strategy()

        return optimized_count > 0

    def _get_target_metric_for_issue(self, issue_type: str) -> str:
        """根据问题类型获取目标指标"""
        mapping = {
            "high_response_time": "response_time",
            "high_memory_usage": "memory_usage",
            "high_cpu_usage": "cpu_usage",
            "low_success_rate": "success_rate",
        }
        return mapping.get(issue_type, "response_time")

    def _update_strategy(self):
        """更新自适应策略"""
        # 计算各策略的平均性能
        strategy_scores = {}
        for strategy, performances in self.strategy_performance.items():
            if performances:
                strategy_scores[strategy] = statistics.mean(
                    performances[-10:]
                )  # 最近10次的平均

        if len(strategy_scores) >= 2:
            # 选择表现最好的策略
            best_strategy = max(strategy_scores.items(), key=lambda x: x[1])[0]
            if best_strategy != self.current_strategy:
                self.current_strategy = best_strategy

    def get_optimization_status(self) -> Dict[str, Any]:
        """获取优化状态"""
        with self._lock:
            recent_optimizations = [
                opt
                for opt in self.optimization_history
                if opt.timestamp >= datetime.now() - timedelta(hours=1)
            ]

            return {
                "optimization_enabled": self.optimization_enabled,
                "current_strategy": self.current_strategy.value,
                "last_optimization": self.last_optimization.isoformat(),
                "total_optimizations": len(self.optimization_history),
                "recent_optimizations": len(recent_optimizations),
                "current_parameters": self.get_current_parameters(),
                "performance_issues": self.performance_monitor.detect_performance_issues(),
                "strategy_performance": {
                    strategy.value: statistics.mean(perfs[-5:]) if perfs else 0
                    for strategy, perfs in self.strategy_performance.items()
                },
            }

    def manual_optimize(self, parameter_name: str, target_value: float) -> bool:
        """手动优化参数"""
        if parameter_name not in self.parameters:
            return False

        param = self.parameters[parameter_name]

        # 验证目标值
        if not (param.min_value <= target_value <= param.max_value):
            return False

        old_value = param.current_value
        param.current_value = target_value
        param.last_updated = datetime.now()
        param.adjustment_count += 1

        # 记录手动优化
        result = OptimizationResult(
            parameter_name=parameter_name,
            old_value=old_value,
            new_value=target_value,
            performance_before=0.0,
            performance_after=0.0,
            improvement=0.0,
            timestamp=datetime.now(),
            strategy_used=AdaptationStrategy.EXPERIMENTAL,
            success=True,
            notes="Manual optimization",
        )

        self.optimization_history.append(result)

        return True

    def reset_parameters(self):
        """重置所有参数到默认值"""
        with self._lock:
            self._init_default_parameters()
            self.optimization_history.clear()
            self.strategy_performance.clear()
            self.current_strategy = AdaptationStrategy.MODERATE

    def export_optimization_data(self) -> Dict[str, Any]:
        """导出优化数据"""
        return {
            "parameters": {
                name: {
                    "current_value": param.current_value,
                    "min_value": param.min_value,
                    "max_value": param.max_value,
                    "step_size": param.step_size,
                    "optimization_type": param.optimization_type.value,
                    "last_updated": param.last_updated.isoformat(),
                    "adjustment_count": param.adjustment_count,
                }
                for name, param in self.parameters.items()
            },
            "optimization_history": [
                {
                    "parameter_name": opt.parameter_name,
                    "old_value": opt.old_value,
                    "new_value": opt.new_value,
                    "improvement": opt.improvement,
                    "timestamp": opt.timestamp.isoformat(),
                    "strategy_used": opt.strategy_used.value,
                    "success": opt.success,
                }
                for opt in self.optimization_history
            ],
            "performance_metrics": [
                {
                    "timestamp": record["timestamp"].isoformat(),
                    "metrics": record["metrics"],
                }
                for record in list(self.performance_monitor.metrics_history)
            ],
        }

    def save_optimization_state(self, file_path: Optional[Path] = None):
        """保存优化状态到文件"""
        if file_path is None:
            file_path = self.config.ai_memory_dir / "optimization_state.json"

        try:
            data = self.export_optimization_data()
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving optimization state: {e}")

    def load_optimization_state(self, file_path: Optional[Path] = None):
        """从文件加载优化状态"""
        if file_path is None:
            file_path = self.config.ai_memory_dir / "optimization_state.json"

        if not file_path.exists():
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 恢复参数
            for name, param_data in data.get("parameters", {}).items():
                if name in self.parameters:
                    param = self.parameters[name]
                    param.current_value = param_data["current_value"]
                    param.last_updated = datetime.fromisoformat(
                        param_data["last_updated"]
                    )
                    param.adjustment_count = param_data["adjustment_count"]

            # 恢复优化历史（最近100条）
            history_data = data.get("optimization_history", [])[-100:]
            self.optimization_history = [
                OptimizationResult(
                    parameter_name=opt["parameter_name"],
                    old_value=opt["old_value"],
                    new_value=opt["new_value"],
                    performance_before=0.0,
                    performance_after=0.0,
                    improvement=opt["improvement"],
                    timestamp=datetime.fromisoformat(opt["timestamp"]),
                    strategy_used=AdaptationStrategy(opt["strategy_used"]),
                    success=opt["success"],
                )
                for opt in history_data
            ]

        except Exception as e:
            print(f"Error loading optimization state: {e}")

    def cleanup(self):
        """清理资源"""
        self.save_optimization_state()
        self.performance_monitor.monitoring_active = False
