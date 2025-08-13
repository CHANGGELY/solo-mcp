from __future__ import annotations

import os
import re
import json
import time
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple, TYPE_CHECKING
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor
import math
import heapq
from enum import Enum

from ..config import SoloConfig
from ..utils.file_utils import read_file_content, get_file_info
from ..utils.search_utils import search_files, search_content

class ContextType(Enum):
    """上下文类型枚举"""
    FILE = "file"
    FUNCTION = "function"
    CLASS = "class"
    VARIABLE = "variable"
    MODULE = "module"
    DOCUMENTATION = "documentation"
    CONFIGURATION = "configuration"
    TEST = "test"


class RelevanceLevel(Enum):
    """相关性级别枚举"""
    CRITICAL = "critical"  # 0.8-1.0
    HIGH = "high"        # 0.6-0.8
    MEDIUM = "medium"    # 0.4-0.6
    LOW = "low"          # 0.2-0.4
    MINIMAL = "minimal"  # 0.0-0.2


# 使用 TYPE_CHECKING 避免循环导入
if TYPE_CHECKING:
    from .learning import LearningEngine, UserActionType, PerformanceMetrics
    from .adaptive import AdaptiveOptimizer
    from .memory import MemoryTool


@dataclass
class ContextItem:
    """上下文项数据结构"""

    file_path: str
    content: str
    relevance_score: float
    context_type: str  # 'file', 'function', 'class', 'variable'
    line_range: Optional[Tuple[int, int]] = None
    metadata: Dict[str, Any] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ContextQuery:
    """上下文查询数据结构"""

    query: str
    query_type: str  # 'semantic', 'keyword', 'file_pattern', 'function_search'
    filters: Dict[str, Any]
    max_results: int = 10
    min_relevance: float = 0.3
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class TrimmedContext:
    """裁剪后的上下文数据结构"""

    original_items: List[ContextItem]
    trimmed_items: List[ContextItem]
    trim_ratio: float
    importance_scores: Dict[str, float]
    trim_strategy: str
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class DynamicContextTrimmer:
    """动态上下文裁剪器 - 基于重要性、访问频率和时间衰减的智能裁剪"""

    def __init__(self, max_context_size: int = 8000, target_trim_ratio: float = 0.7):
        self.max_context_size = max_context_size
        self.target_trim_ratio = target_trim_ratio

        # 权重配置
        self.importance_weight = 0.4
        self.recency_weight = 0.3
        self.relevance_weight = 0.3

        # 裁剪统计
        self.trim_stats = {
            "total_trims": 0,
            "avg_trim_ratio": 0.0,
            "content_preserved": 0.0,
            "strategy_usage": defaultdict(int),
        }

    def trim_context(
        self,
        context_items: List[ContextItem],
        target_size: Optional[int] = None,
        preserve_critical: bool = True,
    ) -> TrimmedContext:
        """智能裁剪上下文"""
        if not context_items:
            return TrimmedContext(
                original_items=[],
                trimmed_items=[],
                trim_ratio=0.0,
                importance_scores={},
                trim_strategy="none",
            )

        target_size = target_size or self.max_context_size
        current_size = self._calculate_total_size(context_items)

        # 如果当前大小已经符合要求，无需裁剪
        if current_size <= target_size:
            return TrimmedContext(
                original_items=context_items,
                trimmed_items=context_items,
                trim_ratio=0.0,
                importance_scores={item.file_path: 1.0 for item in context_items},
                trim_strategy="no_trim",
            )

        # 计算重要性分数
        importance_scores = self._calculate_importance_scores(context_items)

        # 选择裁剪策略
        strategy = self._select_trim_strategy(context_items, current_size, target_size)

        # 执行裁剪
        if strategy == "priority_based":
            trimmed_items = self._priority_based_trim(
                context_items, importance_scores, target_size, preserve_critical
            )
        elif strategy == "content_aware":
            trimmed_items = self._content_aware_trim(
                context_items, importance_scores, target_size
            )
        elif strategy == "hybrid":
            trimmed_items = self._hybrid_trim(
                context_items, importance_scores, target_size, preserve_critical
            )
        else:
            trimmed_items = self._simple_trim(context_items, target_size)

        # 计算裁剪比例
        trimmed_size = self._calculate_total_size(trimmed_items)
        trim_ratio = 1.0 - (trimmed_size / current_size) if current_size > 0 else 0.0

        # 更新统计
        self._update_trim_stats(strategy, trim_ratio)

        return TrimmedContext(
            original_items=context_items,
            trimmed_items=trimmed_items,
            trim_ratio=trim_ratio,
            importance_scores=importance_scores,
            trim_strategy=strategy,
            metadata={
                "original_size": current_size,
                "trimmed_size": trimmed_size,
                "target_size": target_size,
            },
        )

    def _calculate_importance_scores(
        self, context_items: List[ContextItem]
    ) -> Dict[str, float]:
        """计算重要性分数"""
        scores = {}
        now = datetime.now()

        for item in context_items:
            score = 0.0

            # 相关性分数
            score += item.relevance_score * self.relevance_weight

            # 时间新近性分数
            time_diff = (now - item.timestamp).total_seconds() / 3600  # 小时
            recency_score = math.exp(-time_diff / 24)  # 24小时衰减
            score += recency_score * self.recency_weight

            # 内容重要性分数
            importance_score = self._calculate_content_importance(item)
            score += importance_score * self.importance_weight

            scores[item.file_path] = min(score, 1.0)

        return scores

    def _calculate_content_importance(self, item: ContextItem) -> float:
        """计算内容重要性"""
        score = 0.0
        content = item.content.lower()

        # 基于上下文类型
        type_scores = {
            "function": 0.8,
            "class": 0.9,
            "file": 0.6,
            "content": 0.5,
            "related_file": 0.3,
        }
        score += type_scores.get(item.context_type, 0.5)

        # 基于关键词密度
        important_keywords = [
            "error",
            "exception",
            "bug",
            "critical",
            "important",
            "main",
            "init",
            "config",
            "setup",
            "core",
        ]
        keyword_count = sum(1 for keyword in important_keywords if keyword in content)
        score += min(keyword_count * 0.1, 0.3)

        # 基于代码复杂度（简化）
        if item.context_type in ["function", "class"]:
            lines = item.content.count("\n")
            if lines > 50:  # 长函数/类可能更重要
                score += 0.2
            elif lines < 5:  # 太短可能不重要
                score -= 0.1

        return min(score, 1.0)

    def _select_trim_strategy(
        self, context_items: List[ContextItem], current_size: int, target_size: int
    ) -> str:
        """选择裁剪策略"""
        trim_ratio_needed = 1.0 - (target_size / current_size)

        # 轻度裁剪
        if trim_ratio_needed < 0.3:
            return "priority_based"
        # 中度裁剪
        elif trim_ratio_needed < 0.6:
            return "content_aware"
        # 重度裁剪
        else:
            return "hybrid"

    def _priority_based_trim(
        self,
        context_items: List[ContextItem],
        importance_scores: Dict[str, float],
        target_size: int,
        preserve_critical: bool,
    ) -> List[ContextItem]:
        """基于优先级的裁剪"""
        # 按重要性排序
        sorted_items = sorted(
            context_items,
            key=lambda x: importance_scores.get(x.file_path, 0.0),
            reverse=True,
        )

        trimmed_items = []
        current_size = 0

        for item in sorted_items:
            item_size = len(item.content)

            # 保留关键项目
            if preserve_critical and importance_scores.get(item.file_path, 0.0) > 0.8:
                trimmed_items.append(item)
                current_size += item_size
            elif current_size + item_size <= target_size:
                trimmed_items.append(item)
                current_size += item_size
            else:
                break

        return trimmed_items

    def _content_aware_trim(
        self,
        context_items: List[ContextItem],
        importance_scores: Dict[str, float],
        target_size: int,
    ) -> List[ContextItem]:
        """内容感知裁剪"""
        trimmed_items = []

        for item in context_items:
            importance = importance_scores.get(item.file_path, 0.0)

            # 根据重要性决定保留比例
            if importance > 0.7:
                keep_ratio = 1.0
            elif importance > 0.5:
                keep_ratio = 0.8
            elif importance > 0.3:
                keep_ratio = 0.6
            else:
                keep_ratio = 0.4

            # 裁剪内容
            content_length = len(item.content)
            keep_length = int(content_length * keep_ratio)

            if keep_length > 0:
                trimmed_content = self._smart_content_trim(item.content, keep_length)

                trimmed_item = ContextItem(
                    file_path=item.file_path,
                    content=trimmed_content,
                    relevance_score=item.relevance_score,
                    context_type=item.context_type,
                    line_range=item.line_range,
                    metadata=item.metadata,
                    timestamp=item.timestamp,
                )
                trimmed_items.append(trimmed_item)

        # 如果还是太大，进一步裁剪
        current_size = self._calculate_total_size(trimmed_items)
        if current_size > target_size:
            return self._priority_based_trim(
                trimmed_items, importance_scores, target_size, False
            )

        return trimmed_items

    def _hybrid_trim(
        self,
        context_items: List[ContextItem],
        importance_scores: Dict[str, float],
        target_size: int,
        preserve_critical: bool,
    ) -> List[ContextItem]:
        """混合裁剪策略"""
        # 先进行内容感知裁剪
        content_trimmed = self._content_aware_trim(
            context_items, importance_scores, target_size * 1.2
        )

        # 再进行优先级裁剪
        return self._priority_based_trim(
            content_trimmed, importance_scores, target_size, preserve_critical
        )

    def _simple_trim(
        self, context_items: List[ContextItem], target_size: int
    ) -> List[ContextItem]:
        """简单裁剪（按顺序截断）"""
        trimmed_items = []
        current_size = 0

        for item in context_items:
            item_size = len(item.content)
            if current_size + item_size <= target_size:
                trimmed_items.append(item)
                current_size += item_size
            else:
                break

        return trimmed_items

    def _smart_content_trim(self, content: str, target_length: int) -> str:
        """智能内容裁剪"""
        if len(content) <= target_length:
            return content

        lines = content.split("\n")

        # 优先保留重要行
        important_lines = []
        normal_lines = []

        for i, line in enumerate(lines):
            line_lower = line.lower().strip()

            # 重要行：函数定义、类定义、注释、错误处理等
            if (
                line_lower.startswith(("def ", "class ", "import ", "from "))
                or "error" in line_lower
                or "exception" in line_lower
                or line_lower.startswith("#")
                or line_lower.startswith("//")
            ):
                important_lines.append((i, line))
            else:
                normal_lines.append((i, line))

        # 构建裁剪后的内容
        result_lines = []
        current_length = 0

        # 先添加重要行
        for _, line in important_lines:
            if current_length + len(line) + 1 <= target_length:
                result_lines.append(line)
                current_length += len(line) + 1
            else:
                break

        # 再添加普通行
        for _, line in normal_lines:
            if current_length + len(line) + 1 <= target_length:
                result_lines.append(line)
                current_length += len(line) + 1
            else:
                break

        return "\n".join(result_lines)

    def _calculate_total_size(self, context_items: List[ContextItem]) -> int:
        """计算总大小"""
        return sum(len(item.content) for item in context_items)

    def _update_trim_stats(self, strategy: str, trim_ratio: float):
        """更新裁剪统计"""
        self.trim_stats["total_trims"] += 1
        self.trim_stats["strategy_usage"][strategy] += 1

        # 更新平均裁剪比例
        current_avg = self.trim_stats["avg_trim_ratio"]
        total_trims = self.trim_stats["total_trims"]
        self.trim_stats["avg_trim_ratio"] = (
            current_avg * (total_trims - 1) + trim_ratio
        ) / total_trims

        # 更新内容保留率
        content_preserved = 1.0 - trim_ratio
        current_preserved = self.trim_stats["content_preserved"]
        self.trim_stats["content_preserved"] = (
            current_preserved * (total_trims - 1) + content_preserved
        ) / total_trims

    def get_trim_stats(self) -> Dict[str, Any]:
        """获取裁剪统计信息"""
        return {
            "total_trims": self.trim_stats["total_trims"],
            "avg_trim_ratio": self.trim_stats["avg_trim_ratio"],
            "content_preserved_rate": self.trim_stats["content_preserved"],
            "strategy_distribution": dict(self.trim_stats["strategy_usage"]),
            "efficiency_score": self._calculate_efficiency_score(),
        }

    def _calculate_efficiency_score(self) -> float:
        """计算裁剪效率分数"""
        if self.trim_stats["total_trims"] == 0:
            return 1.0

        # 基于内容保留率和裁剪一致性
        preserved_rate = self.trim_stats["content_preserved"]
        consistency = 1.0 - abs(
            self.trim_stats["avg_trim_ratio"] - self.target_trim_ratio
        )

        return preserved_rate * 0.6 + consistency * 0.4

    def optimize_parameters(self, feedback_data: Dict[str, Any]):
        """基于反馈优化参数"""
        if "user_satisfaction" in feedback_data:
            satisfaction = feedback_data["user_satisfaction"]

            # 根据用户满意度调整权重
            if satisfaction < 0.7:
                # 用户不满意，增加重要性权重
                self.importance_weight = min(0.6, self.importance_weight + 0.05)
                self.relevance_weight = max(0.2, self.relevance_weight - 0.05)
            elif satisfaction > 0.9:
                # 用户很满意，可以稍微降低保守程度
                self.target_trim_ratio = min(0.8, self.target_trim_ratio + 0.05)


class SmartContextCollector:
    """智能上下文收集器"""

    def __init__(self, config: SoloConfig):
        self.config = config
        self.context_cache: Dict[str, List[ContextItem]] = {}
        self.query_history: deque = deque(maxlen=100)
        self.file_index: Dict[str, Dict[str, Any]] = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._lock = threading.Lock()

        # 构建文件索引
        self._build_file_index()

    def _build_file_index(self):
        """构建文件索引"""
        try:
            for root, dirs, files in os.walk(self.config.root):
                # 跳过隐藏目录和常见的忽略目录
                dirs[:] = [
                    d
                    for d in dirs
                    if not d.startswith(".")
                    and d not in ["node_modules", "__pycache__", "venv", "env"]
                ]

                for file in files:
                    if file.startswith("."):
                        continue

                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.config.root)

                    # 获取文件信息
                    file_info = get_file_info(file_path)
                    if file_info:
                        self.file_index[rel_path] = {
                            "full_path": file_path,
                            "size": file_info.get("size", 0),
                            "modified": file_info.get("modified", datetime.now()),
                            "extension": os.path.splitext(file)[1],
                            "keywords": self._extract_keywords_from_file(file_path),
                        }
        except Exception as e:
            print(f"Error building file index: {e}")

    def _extract_keywords_from_file(self, file_path: str) -> Set[str]:
        """从文件中提取关键词"""
        keywords = set()
        try:
            content = read_file_content(file_path)
            if content:
                # 提取函数名、类名、变量名等
                # Python
                if file_path.endswith(".py"):
                    keywords.update(re.findall(r"def\s+(\w+)", content))
                    keywords.update(re.findall(r"class\s+(\w+)", content))
                    keywords.update(re.findall(r"(\w+)\s*=", content))

                # JavaScript/TypeScript
                elif file_path.endswith((".js", ".ts", ".jsx", ".tsx")):
                    keywords.update(re.findall(r"function\s+(\w+)", content))
                    keywords.update(re.findall(r"class\s+(\w+)", content))
                    keywords.update(re.findall(r"const\s+(\w+)", content))
                    keywords.update(re.findall(r"let\s+(\w+)", content))
                    keywords.update(re.findall(r"var\s+(\w+)", content))

                # 通用关键词（大写单词、驼峰命名等）
                keywords.update(re.findall(r"\b[A-Z][a-zA-Z0-9_]*\b", content))
                keywords.update(
                    re.findall(r"\b[a-z][a-zA-Z0-9]*[A-Z][a-zA-Z0-9]*\b", content)
                )
        except Exception:
            pass

        return keywords

    def analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """分析查询意图"""
        intent = {
            "type": "general",
            "keywords": [],
            "file_patterns": [],
            "function_names": [],
            "class_names": [],
            "confidence": 0.5,
        }

        query_lower = query.lower()

        # 检测文件相关查询
        if any(word in query_lower for word in ["file", "files", "文件"]):
            intent["type"] = "file_search"
            intent["confidence"] = 0.8

        # 检测函数相关查询
        elif any(
            word in query_lower
            for word in ["function", "method", "def", "函数", "方法"]
        ):
            intent["type"] = "function_search"
            intent["confidence"] = 0.8

        # 检测类相关查询
        elif any(word in query_lower for word in ["class", "object", "类", "对象"]):
            intent["type"] = "class_search"
            intent["confidence"] = 0.8

        # 检测错误相关查询
        elif any(
            word in query_lower
            for word in ["error", "bug", "issue", "problem", "错误", "问题"]
        ):
            intent["type"] = "error_search"
            intent["confidence"] = 0.7

        # 提取关键词
        words = re.findall(r"\b\w+\b", query)
        intent["keywords"] = [
            w
            for w in words
            if len(w) > 2
            and w.lower()
            not in ["the", "and", "or", "in", "on", "at", "to", "for", "of", "with"]
        ]

        # 提取文件模式
        file_patterns = re.findall(
            r"\*\.[a-zA-Z0-9]+|[a-zA-Z0-9_-]+\.[a-zA-Z0-9]+", query
        )
        intent["file_patterns"] = file_patterns

        # 提取可能的函数名和类名
        camel_case = re.findall(r"\b[a-z][a-zA-Z0-9]*[A-Z][a-zA-Z0-9]*\b", query)
        pascal_case = re.findall(r"\b[A-Z][a-zA-Z0-9]*\b", query)
        snake_case = re.findall(r"\b[a-z][a-z0-9_]*\b", query)

        intent["function_names"] = camel_case + snake_case
        intent["class_names"] = pascal_case

        return intent

    def collect_relevant_context(
        self, query: str, max_items: int = 10
    ) -> List[ContextItem]:
        """收集相关上下文"""
        # 分析查询意图
        intent = self.analyze_query_intent(query)

        # 记录查询历史
        context_query = ContextQuery(
            query=query,
            query_type=intent["type"],
            filters={"intent": intent},
            max_results=max_items,
        )
        self.query_history.append(context_query)

        # 根据意图类型收集上下文
        context_items = []

        if intent["type"] == "file_search":
            context_items.extend(self._search_files_by_intent(intent, max_items))
        elif intent["type"] == "function_search":
            context_items.extend(self._search_functions_by_intent(intent, max_items))
        elif intent["type"] == "class_search":
            context_items.extend(self._search_classes_by_intent(intent, max_items))
        else:
            # 通用搜索
            context_items.extend(self._search_general_context(intent, max_items))

        # 按相关性排序
        context_items.sort(key=lambda x: x.relevance_score, reverse=True)

        return context_items[:max_items]

    def _search_files_by_intent(
        self, intent: Dict[str, Any], max_items: int
    ) -> List[ContextItem]:
        """根据意图搜索文件"""
        items = []
        keywords = intent.get("keywords", [])
        file_patterns = intent.get("file_patterns", [])

        for rel_path, file_info in self.file_index.items():
            relevance = 0.0

            # 文件名匹配
            file_name = os.path.basename(rel_path).lower()
            for keyword in keywords:
                if keyword.lower() in file_name:
                    relevance += 0.3

            # 文件模式匹配
            for pattern in file_patterns:
                if pattern in rel_path:
                    relevance += 0.5

            # 关键词匹配
            file_keywords = file_info.get("keywords", set())
            for keyword in keywords:
                if keyword in file_keywords:
                    relevance += 0.2

            if relevance > 0.1:
                content = read_file_content(file_info["full_path"]) or ""
                items.append(
                    ContextItem(
                        file_path=rel_path,
                        content=content[:2000],  # 限制内容长度
                        relevance_score=relevance,
                        context_type="file",
                        metadata={"full_path": file_info["full_path"]},
                    )
                )

        return sorted(items, key=lambda x: x.relevance_score, reverse=True)[:max_items]

    def _search_functions_by_intent(
        self, intent: Dict[str, Any], max_items: int
    ) -> List[ContextItem]:
        """根据意图搜索函数"""
        items = []
        keywords = intent.get("keywords", [])
        function_names = intent.get("function_names", [])

        for rel_path, file_info in self.file_index.items():
            if file_info["extension"] not in [".py", ".js", ".ts", ".jsx", ".tsx"]:
                continue

            try:
                content = read_file_content(file_info["full_path"])
                if not content:
                    continue

                # 查找函数定义
                if file_info["extension"] == ".py":
                    functions = re.finditer(r"def\s+(\w+)\s*\([^)]*\):", content)
                else:
                    functions = re.finditer(
                        r"function\s+(\w+)\s*\([^)]*\)|const\s+(\w+)\s*=\s*\([^)]*\)\s*=>",
                        content,
                    )

                for match in functions:
                    func_name = match.group(1) or match.group(2)
                    if not func_name:
                        continue

                    relevance = 0.0

                    # 函数名匹配
                    for keyword in keywords + function_names:
                        if keyword.lower() in func_name.lower():
                            relevance += 0.5

                    if relevance > 0.1:
                        # 提取函数代码
                        start_pos = match.start()
                        lines = content[:start_pos].count("\n")
                        func_content = self._extract_function_content(
                            content, start_pos
                        )

                        items.append(
                            ContextItem(
                                file_path=rel_path,
                                content=func_content,
                                relevance_score=relevance,
                                context_type="function",
                                line_range=(
                                    lines + 1,
                                    lines + func_content.count("\n") + 1,
                                ),
                                metadata={"function_name": func_name},
                            )
                        )

            except Exception:
                continue

        return sorted(items, key=lambda x: x.relevance_score, reverse=True)[:max_items]

    def _search_classes_by_intent(
        self, intent: Dict[str, Any], max_items: int
    ) -> List[ContextItem]:
        """根据意图搜索类"""
        items = []
        keywords = intent.get("keywords", [])
        class_names = intent.get("class_names", [])

        for rel_path, file_info in self.file_index.items():
            if file_info["extension"] not in [".py", ".js", ".ts", ".jsx", ".tsx"]:
                continue

            try:
                content = read_file_content(file_info["full_path"])
                if not content:
                    continue

                # 查找类定义
                classes = re.finditer(r"class\s+(\w+)", content)

                for match in classes:
                    class_name = match.group(1)
                    relevance = 0.0

                    # 类名匹配
                    for keyword in keywords + class_names:
                        if keyword.lower() in class_name.lower():
                            relevance += 0.5

                    if relevance > 0.1:
                        # 提取类代码
                        start_pos = match.start()
                        lines = content[:start_pos].count("\n")
                        class_content = self._extract_class_content(content, start_pos)

                        items.append(
                            ContextItem(
                                file_path=rel_path,
                                content=class_content,
                                relevance_score=relevance,
                                context_type="class",
                                line_range=(
                                    lines + 1,
                                    lines + class_content.count("\n") + 1,
                                ),
                                metadata={"class_name": class_name},
                            )
                        )

            except Exception:
                continue

        return sorted(items, key=lambda x: x.relevance_score, reverse=True)[:max_items]

    def _search_general_context(
        self, intent: Dict[str, Any], max_items: int
    ) -> List[ContextItem]:
        """通用上下文搜索"""
        items = []
        keywords = intent.get("keywords", [])

        if not keywords:
            return items

        # 使用搜索工具进行内容搜索
        for keyword in keywords[:3]:  # 限制关键词数量
            try:
                search_results = search_content(
                    self.config.root, keyword, max_results=max_items
                )

                for result in search_results:
                    relevance = 0.3  # 基础相关性

                    # 根据匹配次数调整相关性
                    content_lower = result.get("content", "").lower()
                    keyword_count = content_lower.count(keyword.lower())
                    relevance += min(keyword_count * 0.1, 0.5)

                    items.append(
                        ContextItem(
                            file_path=result.get("file_path", ""),
                            content=result.get("content", ""),
                            relevance_score=relevance,
                            context_type="content",
                            line_range=result.get("line_range"),
                            metadata={"search_keyword": keyword},
                        )
                    )

            except Exception:
                continue

        return sorted(items, key=lambda x: x.relevance_score, reverse=True)[:max_items]

    def _extract_function_content(self, content: str, start_pos: int) -> str:
        """提取函数内容"""
        lines = content[start_pos:].split("\n")
        function_lines = [lines[0]]  # 函数定义行

        if len(lines) > 1:
            # 检测缩进级别
            indent_level = (
                len(lines[1]) - len(lines[1].lstrip()) if lines[1].strip() else 4
            )

            for line in lines[1:]:
                if line.strip() == "":
                    function_lines.append(line)
                elif len(line) - len(line.lstrip()) > indent_level or line.startswith(
                    " " * indent_level
                ):
                    function_lines.append(line)
                else:
                    break

        return "\n".join(function_lines[:50])  # 限制行数

    def _extract_class_content(self, content: str, start_pos: int) -> str:
        """提取类内容"""
        lines = content[start_pos:].split("\n")
        class_lines = [lines[0]]  # 类定义行

        if len(lines) > 1:
            # 检测缩进级别
            indent_level = (
                len(lines[1]) - len(lines[1].lstrip()) if lines[1].strip() else 4
            )

            for line in lines[1:]:
                if line.strip() == "":
                    class_lines.append(line)
                elif len(line) - len(line.lstrip()) > indent_level or line.startswith(
                    " " * indent_level
                ):
                    class_lines.append(line)
                else:
                    break

        return "\n".join(class_lines[:100])  # 限制行数

    def get_context_summary(self, context_items: List[ContextItem]) -> str:
        """生成上下文摘要"""
        if not context_items:
            return "No relevant context found."

        summary_parts = []

        # 按类型分组
        by_type = defaultdict(list)
        for item in context_items:
            by_type[item.context_type].append(item)

        for context_type, items in by_type.items():
            if context_type == "file":
                files = [item.file_path for item in items]
                summary_parts.append(
                    f"Found {len(files)} relevant files: {', '.join(files[:3])}{'...' if len(files) > 3 else ''}"
                )

            elif context_type == "function":
                functions = [
                    item.metadata.get("function_name", "unknown") for item in items
                ]
                summary_parts.append(
                    f"Found {len(functions)} relevant functions: {', '.join(functions[:3])}{'...' if len(functions) > 3 else ''}"
                )

            elif context_type == "class":
                classes = [item.metadata.get("class_name", "unknown") for item in items]
                summary_parts.append(
                    f"Found {len(classes)} relevant classes: {', '.join(classes[:3])}{'...' if len(classes) > 3 else ''}"
                )

        return " | ".join(summary_parts)

    def cleanup(self):
        """清理资源"""
        self.executor.shutdown(wait=True)


class ContextTool:
    """上下文工具主类"""

    def __init__(
        self,
        config: SoloConfig,
        enable_trimming: bool = True,
        max_context_size: int = 8000,
    ):
        self.config = config
        self.collector = SmartContextCollector(config)

        # 初始化裁剪器
        self.enable_trimming = enable_trimming
        if enable_trimming:
            self.trimmer = DynamicContextTrimmer(
                max_context_size=max_context_size, target_trim_ratio=0.7
            )
        else:
            self.trimmer = None

        # 学习和优化组件（延迟初始化）
        self.learning_engine: Optional[Any] = None
        self.adaptive_optimizer: Optional[Any] = None

        # 性能统计
        self.collection_stats = {
            "total_queries": 0,
            "successful_queries": 0,
            "avg_response_time": 0.0,
            "cache_hits": 0,
            "cache_misses": 0,
            "trim_operations": 0,
            "avg_trim_ratio": 0.0,
        }

        # 上下文缓存
        self.context_cache: Dict[str, Tuple[List[ContextItem], datetime]] = {}
        self.cache_ttl = timedelta(minutes=10)

        # 线程锁
        self._lock = threading.Lock()

    def set_learning_engine(self, learning_engine: Any):
        """设置学习引擎"""
        self.learning_engine = learning_engine

    def set_adaptive_optimizer(self, optimizer: Any):
        """设置自适应优化器"""
        self.adaptive_optimizer = optimizer

    async def collect_context(
        self, query: str, max_items: int = 10, use_cache: bool = True
    ) -> Dict[str, Any]:
        """收集上下文信息"""
        start_time = time.time()

        try:
            # 记录用户行为
            if self.learning_engine:
                from .learning import UserActionType

                self.learning_engine.record_user_action(
                    action_type=UserActionType.CONTEXT_QUERY,
                    details={"query": query, "max_items": max_items},
                )

            # 应用自适应参数
            if self.adaptive_optimizer:
                params = self.adaptive_optimizer.get_current_parameters()
                max_items = min(
                    max_items, int(params.get("context_search_limit", max_items))
                )
                min_relevance = params.get("context_relevance_threshold", 0.3)
            else:
                min_relevance = 0.3

            # 检查缓存
            cache_key = f"{query}:{max_items}:{min_relevance}"
            if use_cache and cache_key in self.context_cache:
                cached_items, cached_time = self.context_cache[cache_key]
                if datetime.now() - cached_time < self.cache_ttl:
                    self.collection_stats["cache_hits"] += 1
                    return self._format_context_result(
                        cached_items, query, time.time() - start_time, True
                    )

            self.collection_stats["cache_misses"] += 1

            # 确定收集策略
            strategy = self._determine_collection_strategy(query)

            # 收集上下文
            if strategy == "focused":
                context_items = await self._focused_collection(
                    query, max_items, min_relevance
                )
            elif strategy == "comprehensive":
                context_items = await self._comprehensive_collection(
                    query, max_items, min_relevance
                )
            else:
                context_items = await self._standard_collection(
                    query, max_items, min_relevance
                )

            # 过滤低相关性项目
            context_items = [
                item for item in context_items if item.relevance_score >= min_relevance
            ]

            # 应用动态裁剪
            trimmed_context = None
            if self.enable_trimming and self.trimmer and context_items:
                trimmed_context = self.trimmer.trim_context(context_items)
                context_items = trimmed_context.trimmed_items

                # 更新裁剪统计
                with self._lock:
                    self.collection_stats["trim_operations"] += 1
                    current_avg = self.collection_stats["avg_trim_ratio"]
                    total_trims = self.collection_stats["trim_operations"]
                    self.collection_stats["avg_trim_ratio"] = (
                        current_avg * (total_trims - 1) + trimmed_context.trim_ratio
                    ) / total_trims

            # 缓存结果
            if use_cache:
                self.context_cache[cache_key] = (context_items, datetime.now())

            # 记录性能指标
            response_time = time.time() - start_time
            self._record_collection_metrics(
                query, len(context_items), response_time, True
            )

            return self._format_context_result(
                context_items, query, response_time, False, trimmed_context
            )

        except Exception as e:
            response_time = time.time() - start_time
            self._record_collection_metrics(query, 0, response_time, False)

            return {
                "success": False,
                "error": str(e),
                "context_items": [],
                "summary": "Error occurred during context collection",
                "response_time": response_time,
            }

    def _determine_collection_strategy(self, query: str) -> str:
        """确定收集策略"""
        # 基于学习数据调整策略
        if self.learning_engine:
            insights = self.learning_engine.get_learning_insights()
            for insight in insights:
                if insight.insight_type == "context_preferences":
                    evidence = insight.evidence
                    if evidence.get("prefers_comprehensive", False):
                        return "comprehensive"
                    elif evidence.get("prefers_focused", False):
                        return "focused"

        # 基于查询特征确定策略
        query_lower = query.lower()

        # 复杂查询使用综合策略
        if len(query.split()) > 5 or any(
            word in query_lower
            for word in ["complex", "detailed", "comprehensive", "详细", "全面"]
        ):
            return "comprehensive"

        # 简单查询使用聚焦策略
        elif len(query.split()) <= 2 or any(
            word in query_lower for word in ["quick", "simple", "brief", "快速", "简单"]
        ):
            return "focused"

        return "standard"

    async def _focused_collection(
        self, query: str, max_items: int, min_relevance: float
    ) -> List[ContextItem]:
        """聚焦式收集 - 精确匹配"""
        return self.collector.collect_relevant_context(query, max_items // 2)

    async def _comprehensive_collection(
        self, query: str, max_items: int, min_relevance: float
    ) -> List[ContextItem]:
        """综合式收集 - 广泛搜索"""
        context_items = self.collector.collect_relevant_context(query, max_items * 2)

        # 添加相关文件的上下文
        related_files = set()
        for item in context_items[:5]:  # 取前5个最相关的项目
            file_dir = os.path.dirname(item.file_path)
            try:
                for file in os.listdir(
                    os.path.join(self.config.root, file_dir)
                ):
                    if file.endswith((".py", ".js", ".ts", ".jsx", ".tsx")):
                        related_files.add(os.path.join(file_dir, file))
            except Exception:
                continue

        # 添加相关文件内容
        for file_path in list(related_files)[: max_items // 2]:
            full_path = os.path.join(self.config.root, file_path)
            content = read_file_content(full_path)
            if content:
                context_items.append(
                    ContextItem(
                        file_path=file_path,
                        content=content[:1000],
                        relevance_score=0.2,
                        context_type="related_file",
                    )
                )

        return context_items[:max_items]

    async def _standard_collection(
        self, query: str, max_items: int, min_relevance: float
    ) -> List[ContextItem]:
        """标准收集策略"""
        return self.collector.collect_relevant_context(query, max_items)

    def _format_context_result(
        self,
        context_items: List[ContextItem],
        query: str,
        response_time: float,
        from_cache: bool,
        trimmed_context: Optional[TrimmedContext] = None,
    ) -> Dict[str, Any]:
        """格式化上下文结果"""
        result = {
            "success": True,
            "context_items": [
                {
                    "file_path": item.file_path,
                    "content": item.content,
                    "relevance_score": item.relevance_score,
                    "context_type": item.context_type,
                    "line_range": item.line_range,
                    "metadata": item.metadata,
                }
                for item in context_items
            ],
            "summary": self.collector.get_context_summary(context_items),
            "query": query,
            "total_items": len(context_items),
            "response_time": response_time,
            "from_cache": from_cache,
            "collection_strategy": self._determine_collection_strategy(query),
        }

        # 添加裁剪信息
        if trimmed_context:
            result["trim_info"] = {
                "was_trimmed": trimmed_context.trim_ratio > 0,
                "trim_ratio": trimmed_context.trim_ratio,
                "trim_strategy": trimmed_context.trim_strategy,
                "original_items_count": len(trimmed_context.original_items),
                "trimmed_items_count": len(trimmed_context.trimmed_items),
                "metadata": trimmed_context.metadata,
            }

        return result

    def _record_collection_metrics(
        self, query: str, items_count: int, response_time: float, success: bool
    ):
        """记录收集指标"""
        with self._lock:
            self.collection_stats["total_queries"] += 1
            if success:
                self.collection_stats["successful_queries"] += 1

            # 更新平均响应时间
            current_avg = self.collection_stats["avg_response_time"]
            total_queries = self.collection_stats["total_queries"]
            self.collection_stats["avg_response_time"] = (
                current_avg * (total_queries - 1) + response_time
            ) / total_queries

        # 记录到学习引擎
        if self.learning_engine:
            from .learning import PerformanceMetrics

            metrics = PerformanceMetrics(
                response_time=response_time,
                success_rate=1.0 if success else 0.0,
                throughput=items_count / response_time if response_time > 0 else 0,
                resource_usage=0.5,  # 估算值
                error_count=0 if success else 1,
            )
            self.learning_engine.record_performance_metrics(metrics)

        # 触发自适应优化
        if self.adaptive_optimizer:
            self.adaptive_optimizer.trigger_optimization_if_needed()

    def get_collection_stats(self) -> Dict[str, Any]:
        """获取收集统计信息"""
        with self._lock:
            stats = self.collection_stats.copy()

            # 计算成功率
            if stats["total_queries"] > 0:
                stats["success_rate"] = (
                    stats["successful_queries"] / stats["total_queries"]
                )
            else:
                stats["success_rate"] = 0.0

            # 计算缓存命中率
            total_cache_requests = stats["cache_hits"] + stats["cache_misses"]
            if total_cache_requests > 0:
                stats["cache_hit_rate"] = stats["cache_hits"] / total_cache_requests
            else:
                stats["cache_hit_rate"] = 0.0

            # 添加裁剪统计
            if self.trimmer:
                trim_stats = self.trimmer.get_trim_stats()
                stats["trimmer_stats"] = trim_stats

            return stats

    def clear_cache(self):
        """清理缓存"""
        with self._lock:
            self.context_cache.clear()

    def cleanup(self):
        """清理资源"""
        self.collector.cleanup()
        self.clear_cache()

    def optimize_trimming(self, feedback_data: Dict[str, Any]):
        """优化裁剪参数"""
        if self.trimmer:
            self.trimmer.optimize_parameters(feedback_data)

    def get_trimmer_stats(self) -> Dict[str, Any]:
        """获取裁剪器统计信息"""
        if self.trimmer:
            return self.trimmer.get_trim_stats()
        return {}
