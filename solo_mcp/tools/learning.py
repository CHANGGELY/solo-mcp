from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics
import re

from ..config import SoloConfig

# 使用 TYPE_CHECKING 避免循环导入
if TYPE_CHECKING:
    from .memory import MemoryTool
    from .context import ContextTool
    from .orchestrator import OrchestratorTool


class UserActionType(Enum):
    CONTEXT_COLLECTION = "context_collection"
    MEMORY_STORE = "memory_store"
    MEMORY_LOAD = "memory_load"
    MEMORY_SEARCH = "memory_search"
    TASK_ALLOCATION = "task_allocation"
    CONFLICT_DETECTION = "conflict_detection"
    ERROR_HANDLING = "error_handling"
    OPTIMIZATION = "optimization"
    QUERY_PROCESSING = "query_processing"
    RESPONSE_GENERATION = "response_generation"


class LearningPattern(Enum):
    QUERY_FREQUENCY = "query_frequency"
    ERROR_RECOVERY = "error_recovery"
    CONTEXT_PREFERENCE = "context_preference"
    MEMORY_ACCESS = "memory_access"
    TASK_COMPLEXITY = "task_complexity"
    RESPONSE_TIME = "response_time"
    SUCCESS_RATE = "success_rate"
    WORKFLOW_SEQUENCE = "workflow_sequence"
    RESOURCE_USAGE = "resource_usage"
    USER_BEHAVIOR = "user_behavior"


@dataclass
class UserAction:
    action_type: UserActionType
    timestamp: datetime
    query: str
    context: Dict[str, Any]
    response_time: float
    success: bool
    error_message: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class PerformanceMetrics:
    timestamp: datetime
    response_time: float
    memory_usage: float
    cpu_usage: float
    success_rate: float
    error_count: int
    throughput: float
    context_size: int
    memory_hits: int
    cache_efficiency: float


@dataclass
class LearningInsight:
    pattern_type: LearningPattern
    description: str
    confidence: float
    frequency: int
    impact_score: float
    evidence: Dict[str, Any]
    timestamp: datetime
    recommendations: List[str]


class PatternAnalyzer:
    """模式分析器"""

    def __init__(self):
        self.min_pattern_frequency = 3
        self.confidence_threshold = 0.7

    def analyze_query_patterns(
        self, actions: List[UserAction]
    ) -> List[LearningInsight]:
        """分析查询模式"""
        insights = []

        # 分析查询频率模式
        query_freq = defaultdict(int)
        query_contexts = defaultdict(list)

        for action in actions:
            if action.action_type in [
                UserActionType.CONTEXT_COLLECTION,
                UserActionType.QUERY_PROCESSING,
            ]:
                # 提取关键词
                keywords = self._extract_keywords(action.query)
                for keyword in keywords:
                    query_freq[keyword] += 1
                    query_contexts[keyword].append(action.context)

        # 识别高频查询模式
        for keyword, freq in query_freq.items():
            if freq >= self.min_pattern_frequency:
                confidence = min(freq / 10.0, 1.0)
                if confidence >= self.confidence_threshold:
                    insights.append(
                        LearningInsight(
                            pattern_type=LearningPattern.QUERY_FREQUENCY,
                            description=f"用户经常查询关于 '{keyword}' 的内容",
                            confidence=confidence,
                            frequency=freq,
                            impact_score=confidence * 0.8,
                            evidence={
                                "keyword": keyword,
                                "contexts": query_contexts[keyword][:5],
                            },
                            timestamp=datetime.now(),
                            recommendations=[
                                f"预加载 {keyword} 相关的上下文",
                                f"优化 {keyword} 相关的搜索算法",
                                f"缓存 {keyword} 的常用结果",
                            ],
                        )
                    )

        return insights

    def analyze_context_patterns(
        self, actions: List[UserAction]
    ) -> List[LearningInsight]:
        """分析上下文模式"""
        insights = []

        # 分析上下文偏好
        context_types = defaultdict(int)
        context_success = defaultdict(list)

        for action in actions:
            if action.action_type == UserActionType.CONTEXT_COLLECTION:
                ctx_type = action.context.get("collection_strategy", "standard")
                context_types[ctx_type] += 1
                context_success[ctx_type].append(action.success)

        # 识别最佳上下文策略
        for ctx_type, count in context_types.items():
            if count >= self.min_pattern_frequency:
                success_rate = sum(context_success[ctx_type]) / len(
                    context_success[ctx_type]
                )
                confidence = min(count / 10.0, 1.0) * success_rate

                if confidence >= self.confidence_threshold:
                    insights.append(
                        LearningInsight(
                            pattern_type=LearningPattern.CONTEXT_PREFERENCE,
                            description=f"'{ctx_type}' 上下文收集策略效果最佳",
                            confidence=confidence,
                            frequency=count,
                            impact_score=success_rate * 0.9,
                            evidence={
                                "strategy": ctx_type,
                                "success_rate": success_rate,
                            },
                            timestamp=datetime.now(),
                            recommendations=[
                                f"优先使用 {ctx_type} 策略",
                                f"为 {ctx_type} 策略分配更多资源",
                                "调整其他策略的参数",
                            ],
                        )
                    )

        return insights

    def analyze_performance_patterns(
        self, metrics: List[PerformanceMetrics]
    ) -> List[LearningInsight]:
        """分析性能模式"""
        insights = []

        if len(metrics) < 5:
            return insights

        # 分析响应时间趋势
        response_times = [m.response_time for m in metrics[-20:]]  # 最近20个指标
        avg_response_time = statistics.mean(response_times)

        if len(response_times) >= 10:
            recent_avg = statistics.mean(response_times[-5:])
            earlier_avg = statistics.mean(response_times[-10:-5])

            if recent_avg > earlier_avg * 1.2:  # 响应时间增加20%以上
                insights.append(
                    LearningInsight(
                        pattern_type=LearningPattern.RESPONSE_TIME,
                        description="系统响应时间呈上升趋势，可能存在性能瓶颈",
                        confidence=0.8,
                        frequency=len(response_times),
                        impact_score=0.9,
                        evidence={
                            "recent_avg": recent_avg,
                            "earlier_avg": earlier_avg,
                            "increase_ratio": recent_avg / earlier_avg,
                        },
                        timestamp=datetime.now(),
                        recommendations=[
                            "检查系统资源使用情况",
                            "优化慢查询和算法",
                            "考虑增加缓存机制",
                            "分析内存泄漏问题",
                        ],
                    )
                )

        # 分析成功率模式
        success_rates = [m.success_rate for m in metrics[-10:]]
        if success_rates:
            avg_success_rate = statistics.mean(success_rates)
            if avg_success_rate < 0.9:  # 成功率低于90%
                insights.append(
                    LearningInsight(
                        pattern_type=LearningPattern.SUCCESS_RATE,
                        description=f"系统成功率偏低 ({avg_success_rate:.1%})，需要改进错误处理",
                        confidence=0.9,
                        frequency=len(success_rates),
                        impact_score=1.0 - avg_success_rate,
                        evidence={
                            "avg_success_rate": avg_success_rate,
                            "recent_rates": success_rates,
                        },
                        timestamp=datetime.now(),
                        recommendations=[
                            "加强错误处理机制",
                            "改进输入验证",
                            "增加重试逻辑",
                            "优化异常恢复策略",
                        ],
                    )
                )

        return insights

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简化的关键词提取
        words = re.findall(r"\b[a-zA-Z_][a-zA-Z0-9_]*\b", text.lower())
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "have",
            "has",
            "had",
            "do",
            "does",
            "did",
            "will",
            "would",
            "could",
            "should",
            "how",
            "what",
            "when",
            "where",
            "why",
            "who",
            "which",
        }
        return [word for word in words if word not in stop_words and len(word) > 2][:10]


class LearningEngine:
    """学习引擎 - 用户行为分析和模式识别"""

    def __init__(self, config: SoloConfig, tool_instance: Optional[Any] = None):
        self.config = config
        self.tool_instance = tool_instance

        # 数据存储
        self.user_actions: deque = deque(maxlen=1000)  # 最多保存1000个行为
        self.performance_metrics: deque = deque(maxlen=500)  # 最多保存500个指标
        self.learning_insights: List[LearningInsight] = []

        # 分析器
        self.pattern_analyzer = PatternAnalyzer()

        # 学习参数
        self.learning_rate = 0.1
        self.adaptation_threshold = 0.8
        self.insight_expiry_hours = 24

        # 统计信息
        self.stats = {
            "total_actions": 0,
            "successful_actions": 0,
            "total_metrics": 0,
            "patterns_identified": 0,
            "optimizations_applied": 0,
        }

    def record_user_action(
        self,
        action_type: UserActionType,
        query: str,
        context: Dict[str, Any],
        response_time: float,
        success: bool,
        error_message: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
        """记录用户行为"""
        action = UserAction(
            action_type=action_type,
            timestamp=datetime.now(),
            query=query,
            context=context,
            response_time=response_time,
            success=success,
            error_message=error_message,
            session_id=session_id,
        )

        self.user_actions.append(action)

        # 更新统计
        self.stats["total_actions"] += 1
        if success:
            self.stats["successful_actions"] += 1

    def record_performance_metrics(
        self,
        response_time: float,
        memory_usage: float,
        cpu_usage: float,
        success_rate: float,
        error_count: int,
        throughput: float,
        context_size: int,
        memory_hits: int,
        cache_efficiency: float,
    ):
        """记录性能指标"""
        metrics = PerformanceMetrics(
            timestamp=datetime.now(),
            response_time=response_time,
            memory_usage=memory_usage,
            cpu_usage=cpu_usage,
            success_rate=success_rate,
            error_count=error_count,
            throughput=throughput,
            context_size=context_size,
            memory_hits=memory_hits,
            cache_efficiency=cache_efficiency,
        )

        self.performance_metrics.append(metrics)
        self.stats["total_metrics"] += 1

    def analyze_user_patterns(self) -> List[LearningInsight]:
        """分析用户模式"""
        all_insights = []

        # 清理过期的洞察
        self._cleanup_expired_insights()

        # 分析不同类型的模式
        actions_list = list(self.user_actions)
        metrics_list = list(self.performance_metrics)

        # 查询模式分析
        query_insights = self.pattern_analyzer.analyze_query_patterns(actions_list)
        all_insights.extend(query_insights)

        # 上下文模式分析
        context_insights = self.pattern_analyzer.analyze_context_patterns(actions_list)
        all_insights.extend(context_insights)

        # 性能模式分析
        performance_insights = self.pattern_analyzer.analyze_performance_patterns(
            metrics_list
        )
        all_insights.extend(performance_insights)

        # 更新洞察列表
        self.learning_insights.extend(all_insights)
        self.stats["patterns_identified"] += len(all_insights)

        return all_insights

    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """获取优化建议"""
        recommendations = []

        # 基于最新的洞察生成建议
        recent_insights = [
            insight
            for insight in self.learning_insights
            if (datetime.now() - insight.timestamp).hours < self.insight_expiry_hours
        ]

        for insight in recent_insights:
            if insight.confidence >= self.adaptation_threshold:
                rec = {
                    "type": f"{insight.pattern_type.value}_optimization",
                    "description": insight.description,
                    "priority": (
                        "high"
                        if insight.impact_score > 0.8
                        else "medium" if insight.impact_score > 0.5 else "low"
                    ),
                    "impact": insight.impact_score,
                    "confidence": insight.confidence,
                    "evidence": insight.evidence,
                    "recommendations": insight.recommendations,
                    "timestamp": insight.timestamp.isoformat(),
                }
                recommendations.append(rec)

        # 基于性能指标生成通用建议
        if self.performance_metrics:
            recent_metrics = list(self.performance_metrics)[-10:]
            avg_response_time = statistics.mean(
                [m.response_time for m in recent_metrics]
            )
            avg_memory_usage = statistics.mean([m.memory_usage for m in recent_metrics])
            avg_success_rate = statistics.mean([m.success_rate for m in recent_metrics])

            if avg_response_time > 1.0:  # 响应时间超过1秒
                recommendations.append(
                    {
                        "type": "response_time_optimization",
                        "description": f"平均响应时间 {avg_response_time:.2f}s 偏高，建议优化",
                        "priority": "high",
                        "impact": 0.8,
                        "confidence": 0.9,
                        "evidence": {"avg_response_time": avg_response_time},
                        "recommendations": [
                            "优化算法复杂度",
                            "增加缓存机制",
                            "并行处理优化",
                        ],
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            if avg_memory_usage > 0.8:  # 内存使用率超过80%
                recommendations.append(
                    {
                        "type": "memory_usage_optimization",
                        "description": f"内存使用率 {avg_memory_usage:.1%} 偏高，建议优化",
                        "priority": "medium",
                        "impact": 0.7,
                        "confidence": 0.8,
                        "evidence": {"avg_memory_usage": avg_memory_usage},
                        "recommendations": [
                            "清理无用数据",
                            "优化数据结构",
                            "实现内存池",
                        ],
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        # 按优先级和影响排序
        priority_order = {"high": 3, "medium": 2, "low": 1}
        recommendations.sort(
            key=lambda x: (priority_order.get(x["priority"], 0), x["impact"]),
            reverse=True,
        )

        return recommendations[:10]  # 返回前10个建议

    def get_learning_stats(self) -> Dict[str, Any]:
        """获取学习统计信息"""
        success_rate = self.stats["successful_actions"] / max(
            self.stats["total_actions"], 1
        )

        avg_response_time = 0.0
        if self.user_actions:
            response_times = [
                action.response_time
                for action in self.user_actions
                if action.response_time > 0
            ]
            if response_times:
                avg_response_time = statistics.mean(response_times)

        return {
            "total_actions": self.stats["total_actions"],
            "successful_actions": self.stats["successful_actions"],
            "success_rate": success_rate,
            "avg_response_time": avg_response_time,
            "total_metrics": self.stats["total_metrics"],
            "patterns_identified": self.stats["patterns_identified"],
            "optimizations_applied": self.stats["optimizations_applied"],
            "active_insights": len(
                [
                    insight
                    for insight in self.learning_insights
                    if (datetime.now() - insight.timestamp).hours
                    < self.insight_expiry_hours
                ]
            ),
            "learning_rate": self.learning_rate,
            "adaptation_threshold": self.adaptation_threshold,
        }

    def _cleanup_expired_insights(self):
        """清理过期的洞察"""
        cutoff_time = datetime.now() - timedelta(hours=self.insight_expiry_hours)
        self.learning_insights = [
            insight
            for insight in self.learning_insights
            if insight.timestamp > cutoff_time
        ]

    def apply_optimization(
        self, optimization_type: str, parameters: Dict[str, Any]
    ) -> bool:
        """应用优化"""
        try:
            # 这里可以根据优化类型应用具体的优化策略
            # 目前只是记录优化应用
            self.stats["optimizations_applied"] += 1
            return True
        except Exception:
            return False

    def export_learning_data(self) -> Dict[str, Any]:
        """导出学习数据"""
        return {
            "actions": [asdict(action) for action in list(self.user_actions)],
            "metrics": [asdict(metric) for metric in list(self.performance_metrics)],
            "insights": [asdict(insight) for insight in self.learning_insights],
            "stats": self.stats,
            "export_timestamp": datetime.now().isoformat(),
        }

    def import_learning_data(self, data: Dict[str, Any]) -> bool:
        """导入学习数据"""
        try:
            # 导入行为数据
            if "actions" in data:
                for action_data in data["actions"]:
                    action_data["timestamp"] = datetime.fromisoformat(
                        action_data["timestamp"]
                    )
                    action_data["action_type"] = UserActionType(
                        action_data["action_type"]
                    )
                    action = UserAction(**action_data)
                    self.user_actions.append(action)

            # 导入指标数据
            if "metrics" in data:
                for metric_data in data["metrics"]:
                    metric_data["timestamp"] = datetime.fromisoformat(
                        metric_data["timestamp"]
                    )
                    metric = PerformanceMetrics(**metric_data)
                    self.performance_metrics.append(metric)

            # 导入洞察数据
            if "insights" in data:
                for insight_data in data["insights"]:
                    insight_data["timestamp"] = datetime.fromisoformat(
                        insight_data["timestamp"]
                    )
                    insight_data["pattern_type"] = LearningPattern(
                        insight_data["pattern_type"]
                    )
                    insight = LearningInsight(**insight_data)
                    self.learning_insights.append(insight)

            # 导入统计数据
            if "stats" in data:
                self.stats.update(data["stats"])

            return True
        except Exception:
            return False
