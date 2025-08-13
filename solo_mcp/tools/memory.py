from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque, OrderedDict
import statistics
import hashlib
import re
import threading
from typing import Union

from ..config import SoloConfig

# 使用 TYPE_CHECKING 避免循环导入
if TYPE_CHECKING:
    from .learning import LearningEngine
    from .adaptive import AdaptiveOptimizer


class MemoryType(Enum):
    CONTEXT = "context"
    CONVERSATION = "conversation"
    LEARNING = "learning"
    SYSTEM = "system"
    USER_PREFERENCE = "user_preference"
    ERROR_LOG = "error_log"
    OPTIMIZATION = "optimization"
    WORKFLOW = "workflow"


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class MemoryItem:
    id: str
    content: str
    memory_type: MemoryType
    priority: Priority
    tags: List[str]
    context: Dict[str, Any]
    created_at: datetime
    last_accessed: datetime
    access_count: int
    relevance_score: float = 0.0
    expiry_date: Optional[datetime] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class MemoryIndex:
    """记忆索引系统"""

    def __init__(self):
        self.keyword_index: Dict[str, List[str]] = defaultdict(list)
        self.tag_index: Dict[str, List[str]] = defaultdict(list)
        self.type_index: Dict[MemoryType, List[str]] = defaultdict(list)
        self.priority_index: Dict[Priority, List[str]] = defaultdict(list)
        self.date_index: Dict[str, List[str]] = defaultdict(list)  # YYYY-MM-DD format

    def add_memory(self, memory: MemoryItem):
        """添加记忆到索引"""
        memory_id = memory.id

        # 关键词索引
        keywords = self._extract_keywords(memory.content)
        for keyword in keywords:
            self.keyword_index[keyword].append(memory_id)

        # 标签索引
        for tag in memory.tags:
            self.tag_index[tag].append(memory_id)

        # 类型索引
        self.type_index[memory.memory_type].append(memory_id)

        # 优先级索引
        self.priority_index[memory.priority].append(memory_id)

        # 日期索引
        date_key = memory.created_at.strftime("%Y-%m-%d")
        self.date_index[date_key].append(memory_id)

    def remove_memory(self, memory_id: str, memory: MemoryItem):
        """从索引中移除记忆"""
        # 从关键词索引移除
        keywords = self._extract_keywords(memory.content)
        for keyword in keywords:
            if memory_id in self.keyword_index[keyword]:
                self.keyword_index[keyword].remove(memory_id)

        # 从标签索引移除
        for tag in memory.tags:
            if memory_id in self.tag_index[tag]:
                self.tag_index[tag].remove(memory_id)

        # 从类型索引移除
        if memory_id in self.type_index[memory.memory_type]:
            self.type_index[memory.memory_type].remove(memory_id)

        # 从优先级索引移除
        if memory_id in self.priority_index[memory.priority]:
            self.priority_index[memory.priority].remove(memory_id)

        # 从日期索引移除
        date_key = memory.created_at.strftime("%Y-%m-%d")
        if memory_id in self.date_index[date_key]:
            self.date_index[date_key].remove(memory_id)

    def search_by_keywords(self, keywords: List[str]) -> List[str]:
        """通过关键词搜索"""
        result_sets = []
        for keyword in keywords:
            if keyword in self.keyword_index:
                result_sets.append(set(self.keyword_index[keyword]))

        if not result_sets:
            return []

        # 取交集
        result = result_sets[0]
        for result_set in result_sets[1:]:
            result = result.intersection(result_set)

        return list(result)

    def search_by_tags(self, tags: List[str]) -> List[str]:
        """通过标签搜索"""
        result_sets = []
        for tag in tags:
            if tag in self.tag_index:
                result_sets.append(set(self.tag_index[tag]))

        if not result_sets:
            return []

        # 取并集
        result = result_sets[0]
        for result_set in result_sets[1:]:
            result = result.union(result_set)

        return list(result)

    def search_by_type(self, memory_type: MemoryType) -> List[str]:
        """通过类型搜索"""
        return list(self.type_index[memory_type])

    def search_by_priority(self, priority: Priority) -> List[str]:
        """通过优先级搜索"""
        return list(self.priority_index[priority])

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
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
        }
        return [word for word in words if word not in stop_words and len(word) > 2][:20]


@dataclass
class CacheItem:
    """缓存项数据结构"""

    key: str
    value: Any
    priority: Priority
    access_count: int
    last_accessed: datetime
    size: int  # 缓存项大小（字节）
    ttl: Optional[datetime] = None  # 生存时间

    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = datetime.now()


class ContextCacheManager:
    """上下文缓存管理器 - 实现 LRU+优先级的缓存策略"""

    def __init__(self, max_size: int = 1000, max_memory_mb: int = 100):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.cache: OrderedDict[str, CacheItem] = OrderedDict()
        self.priority_index: Dict[Priority, Set[str]] = {
            Priority.LOW: set(),
            Priority.MEDIUM: set(),
            Priority.HIGH: set(),
            Priority.CRITICAL: set(),
        }
        self.current_memory_usage = 0
        self._lock = threading.RLock()

        # 缓存统计
        self.stats = {"hits": 0, "misses": 0, "evictions": 0, "total_requests": 0}

    def get(self, key: str) -> Optional[Any]:
        """获取缓存项"""
        with self._lock:
            self.stats["total_requests"] += 1

            if key not in self.cache:
                self.stats["misses"] += 1
                return None

            # 命中缓存
            self.stats["hits"] += 1
            item = self.cache[key]

            # 检查TTL
            if item.ttl and datetime.now() > item.ttl:
                self._remove_item(key)
                self.stats["misses"] += 1
                return None

            # 更新访问信息
            item.access_count += 1
            item.last_accessed = datetime.now()

            # 移动到末尾（LRU策略）
            self.cache.move_to_end(key)

            return item.value

    def put(
        self,
        key: str,
        value: Any,
        priority: Priority = Priority.MEDIUM,
        ttl_hours: Optional[int] = None,
    ) -> bool:
        """存储缓存项"""
        with self._lock:
            # 计算大小
            size = self._calculate_size(value)

            # 检查是否需要清理空间
            if not self._ensure_space(size, priority):
                return False

            # 设置TTL
            ttl = None
            if ttl_hours:
                ttl = datetime.now() + timedelta(hours=ttl_hours)

            # 如果key已存在，先移除旧的
            if key in self.cache:
                self._remove_item(key)

            # 创建新的缓存项
            item = CacheItem(
                key=key,
                value=value,
                priority=priority,
                access_count=1,
                last_accessed=datetime.now(),
                size=size,
                ttl=ttl,
            )

            # 添加到缓存
            self.cache[key] = item
            self.priority_index[priority].add(key)
            self.current_memory_usage += size

            return True

    def remove(self, key: str) -> bool:
        """移除缓存项"""
        with self._lock:
            if key in self.cache:
                self._remove_item(key)
                return True
            return False

    def clear(self):
        """清空缓存"""
        with self._lock:
            self.cache.clear()
            for priority_set in self.priority_index.values():
                priority_set.clear()
            self.current_memory_usage = 0

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self._lock:
            total_requests = self.stats["total_requests"]
            hit_rate = self.stats["hits"] / max(total_requests, 1)

            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "memory_usage_mb": self.current_memory_usage / (1024 * 1024),
                "max_memory_mb": self.max_memory_bytes / (1024 * 1024),
                "hit_rate": hit_rate,
                "total_requests": total_requests,
                "hits": self.stats["hits"],
                "misses": self.stats["misses"],
                "evictions": self.stats["evictions"],
                "priority_distribution": {
                    priority.name: len(keys)
                    for priority, keys in self.priority_index.items()
                },
            }

    def _ensure_space(self, required_size: int, new_priority: Priority) -> bool:
        """确保有足够空间"""
        # 检查内存限制
        if self.current_memory_usage + required_size > self.max_memory_bytes:
            if not self._evict_by_memory(required_size, new_priority):
                return False

        # 检查数量限制
        if len(self.cache) >= self.max_size:
            if not self._evict_by_count(new_priority):
                return False

        return True

    def _evict_by_memory(self, required_size: int, new_priority: Priority) -> bool:
        """基于内存使用进行驱逐"""
        freed_memory = 0
        candidates = self._get_eviction_candidates(new_priority)

        for key in candidates:
            if freed_memory >= required_size:
                break

            item = self.cache[key]
            freed_memory += item.size
            self._remove_item(key)
            self.stats["evictions"] += 1

        return freed_memory >= required_size

    def _evict_by_count(self, new_priority: Priority) -> bool:
        """基于数量进行驱逐"""
        candidates = self._get_eviction_candidates(new_priority)

        if candidates:
            key = candidates[0]
            self._remove_item(key)
            self.stats["evictions"] += 1
            return True

        return False

    def _get_eviction_candidates(self, new_priority: Priority) -> List[str]:
        """获取驱逐候选项（优先级+LRU策略）"""
        candidates = []

        # 按优先级从低到高排序
        for priority in [
            Priority.LOW,
            Priority.MEDIUM,
            Priority.HIGH,
            Priority.CRITICAL,
        ]:
            if priority.value >= new_priority.value:
                break

            # 在同一优先级内按LRU排序（最少使用的在前）
            priority_keys = list(self.priority_index[priority])
            priority_items = [
                (key, self.cache[key]) for key in priority_keys if key in self.cache
            ]

            # 按访问时间和访问次数排序
            priority_items.sort(
                key=lambda x: (
                    x[1].last_accessed,  # 最后访问时间
                    x[1].access_count,  # 访问次数
                )
            )

            candidates.extend([key for key, _ in priority_items])

        return candidates

    def _remove_item(self, key: str):
        """移除缓存项"""
        if key in self.cache:
            item = self.cache[key]
            del self.cache[key]
            self.priority_index[item.priority].discard(key)
            self.current_memory_usage -= item.size

    def _calculate_size(self, value: Any) -> int:
        """计算值的大小（简化实现）"""
        if isinstance(value, str):
            return len(value.encode("utf-8"))
        elif isinstance(value, (list, tuple)):
            return sum(self._calculate_size(item) for item in value)
        elif isinstance(value, dict):
            return sum(
                self._calculate_size(k) + self._calculate_size(v)
                for k, v in value.items()
            )
        else:
            # 对于其他类型，使用字符串表示的长度作为近似
            return len(str(value).encode("utf-8"))

    def cleanup_expired(self):
        """清理过期项"""
        with self._lock:
            now = datetime.now()
            expired_keys = []

            for key, item in self.cache.items():
                if item.ttl and now > item.ttl:
                    expired_keys.append(key)

            for key in expired_keys:
                self._remove_item(key)


class SmartMemoryManager:
    """智能记忆管理器"""

    def __init__(self, max_memories: int = 10000):
        self.max_memories = max_memories
        self.memories: Dict[str, MemoryItem] = {}
        self.index = MemoryIndex()

        # 智能管理参数
        self.relevance_threshold = 0.3
        self.access_weight = 0.4
        self.recency_weight = 0.3
        self.priority_weight = 0.3

    def store_memory(self, memory: MemoryItem) -> bool:
        """存储记忆"""
        # 检查是否需要清理空间
        if len(self.memories) >= self.max_memories:
            self._cleanup_memories()

        # 存储记忆
        self.memories[memory.id] = memory
        self.index.add_memory(memory)

        return True

    def retrieve_memory(self, memory_id: str) -> Optional[MemoryItem]:
        """检索记忆"""
        if memory_id in self.memories:
            memory = self.memories[memory_id]
            # 更新访问信息
            memory.last_accessed = datetime.now()
            memory.access_count += 1
            return memory
        return None

    def search_memories(
        self,
        query: str,
        memory_type: Optional[MemoryType] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[MemoryItem]:
        """智能搜索记忆"""
        candidate_ids = set()

        # 关键词搜索
        keywords = self.index._extract_keywords(query)
        if keywords:
            keyword_results = self.index.search_by_keywords(keywords)
            candidate_ids.update(keyword_results)

        # 标签搜索
        if tags:
            tag_results = self.index.search_by_tags(tags)
            candidate_ids.update(tag_results)

        # 类型过滤
        if memory_type:
            type_results = self.index.search_by_type(memory_type)
            if candidate_ids:
                candidate_ids = candidate_ids.intersection(set(type_results))
            else:
                candidate_ids = set(type_results)

        # 获取候选记忆
        candidates = []
        for memory_id in candidate_ids:
            if memory_id in self.memories:
                memory = self.memories[memory_id]
                # 计算相关性分数
                relevance = self._calculate_relevance(memory, query, keywords)
                if relevance >= self.relevance_threshold:
                    memory.relevance_score = relevance
                    candidates.append(memory)

        # 按相关性排序
        candidates.sort(key=lambda m: m.relevance_score, reverse=True)

        # 更新访问信息
        for memory in candidates[:limit]:
            memory.last_accessed = datetime.now()
            memory.access_count += 1

        return candidates[:limit]

    def get_summary(
        self, memory_type: Optional[MemoryType] = None, days: int = 7
    ) -> Dict[str, Any]:
        """获取记忆摘要"""
        cutoff_date = datetime.now() - timedelta(days=days)

        recent_memories = []
        for memory in self.memories.values():
            if memory.created_at >= cutoff_date:
                if memory_type is None or memory.memory_type == memory_type:
                    recent_memories.append(memory)

        # 统计信息
        type_counts = defaultdict(int)
        priority_counts = defaultdict(int)
        tag_counts = defaultdict(int)

        for memory in recent_memories:
            type_counts[memory.memory_type.value] += 1
            priority_counts[memory.priority.value] += 1
            for tag in memory.tags:
                tag_counts[tag] += 1

        # 最常访问的记忆
        most_accessed = sorted(
            recent_memories, key=lambda m: m.access_count, reverse=True
        )[:5]

        return {
            "total_memories": len(self.memories),
            "recent_memories": len(recent_memories),
            "type_distribution": dict(type_counts),
            "priority_distribution": dict(priority_counts),
            "top_tags": dict(
                sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            ),
            "most_accessed": [
                {
                    "id": m.id,
                    "content": (
                        m.content[:100] + "..." if len(m.content) > 100 else m.content
                    ),
                    "access_count": m.access_count,
                    "type": m.memory_type.value,
                }
                for m in most_accessed
            ],
        }

    def _calculate_relevance(
        self, memory: MemoryItem, query: str, keywords: List[str]
    ) -> float:
        """计算记忆相关性"""
        score = 0.0

        # 关键词匹配分数
        content_lower = memory.content.lower()
        query_lower = query.lower()

        # 直接匹配
        if query_lower in content_lower:
            score += 0.5

        # 关键词匹配
        keyword_matches = sum(1 for keyword in keywords if keyword in content_lower)
        if keywords:
            score += (keyword_matches / len(keywords)) * 0.3

        # 访问频率分数
        access_score = min(memory.access_count / 10.0, 1.0) * self.access_weight
        score += access_score

        # 时间新近性分数
        days_old = (datetime.now() - memory.created_at).days
        recency_score = max(0, 1 - days_old / 30.0) * self.recency_weight
        score += recency_score

        # 优先级分数
        priority_score = (memory.priority.value / 4.0) * self.priority_weight
        score += priority_score

        return min(score, 1.0)

    def _cleanup_memories(self):
        """清理记忆空间"""
        # 移除过期的记忆
        expired_ids = []
        for memory_id, memory in self.memories.items():
            if memory.expiry_date and memory.expiry_date < datetime.now():
                expired_ids.append(memory_id)

        for memory_id in expired_ids:
            memory = self.memories[memory_id]
            self.index.remove_memory(memory_id, memory)
            del self.memories[memory_id]

        # 如果还是太多，移除最不重要的记忆
        if len(self.memories) >= self.max_memories:
            # 计算重要性分数
            memory_scores = []
            for memory_id, memory in self.memories.items():
                importance = self._calculate_importance(memory)
                memory_scores.append((memory_id, importance))

            # 按重要性排序，移除最不重要的20%
            memory_scores.sort(key=lambda x: x[1])
            remove_count = int(len(memory_scores) * 0.2)

            for memory_id, _ in memory_scores[:remove_count]:
                memory = self.memories[memory_id]
                self.index.remove_memory(memory_id, memory)
                del self.memories[memory_id]

    def _calculate_importance(self, memory: MemoryItem) -> float:
        """计算记忆重要性"""
        score = 0.0

        # 优先级权重
        score += memory.priority.value * 0.4

        # 访问频率权重
        score += min(memory.access_count / 10.0, 1.0) * 0.3

        # 时间新近性权重
        days_old = (datetime.now() - memory.created_at).days
        score += max(0, 1 - days_old / 30.0) * 0.3

        return score


class MemoryTool:
    """记忆工具"""

    def __init__(
        self, config: SoloConfig, enable_cache: bool = True, cache_size: int = 100
    ):
        self.config = config
        self.memory_dir = config.ai_memory_dir / "memories"
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        self.memory_file = self.memory_dir / "memories.json"
        self.index_file = self.memory_dir / "index.json"

        # 智能记忆管理器
        self.smart_manager = SmartMemoryManager()

        # 初始化缓存管理器
        self.enable_cache = enable_cache
        if enable_cache:
            self.cache_manager = ContextCacheManager(
                max_size=cache_size, max_memory_mb=50  # 50MB 缓存限制
            )
        else:
            self.cache_manager = None

        # 学习和自适应组件（延迟初始化避免循环导入）
        self.learning_engine: Optional[Any] = None
        self.adaptive_optimizer: Optional[Any] = None

        # 性能统计
        self.operation_stats = {
            "store_count": 0,
            "load_count": 0,
            "search_count": 0,
            "total_response_time": 0.0,
            "successful_operations": 0,
            "failed_operations": 0,
        }

        # 加载现有记忆
        self._load_memories()

        # 延迟初始化学习组件
        self._init_learning_components()

    def _init_learning_components(self):
        """延迟初始化学习组件"""
        try:
            from .learning import LearningEngine
            from .adaptive import AdaptiveOptimizer

            self.learning_engine = LearningEngine(self.config, self)
            self.adaptive_optimizer = AdaptiveOptimizer(self.config, self)
        except ImportError:
            # 如果导入失败，继续运行但不使用学习功能
            pass

    def store(
        self,
        content: str,
        memory_type: str = "context",
        tags: List[str] = None,
        context: Dict[str, Any] = None,
        priority: str = "medium",
        expiry_hours: Optional[int] = None,
    ) -> str:
        """存储记忆"""
        start_time = time.time()

        try:
            # 记录用户行为
            if self.learning_engine:
                from .learning import UserActionType

                self.learning_engine.record_user_action(
                    action_type=UserActionType.MEMORY_STORE,
                    query=content[:100],
                    context=context or {},
                    response_time=0.0,  # 将在最后更新
                    success=False,  # 将在成功时更新
                )

            # 应用自适应参数
            if self.adaptive_optimizer:
                adaptive_params = self.adaptive_optimizer.get_current_parameters()
                priority = self._apply_adaptive_priority(priority, adaptive_params)

            # 创建记忆项
            memory_id = self._generate_memory_id(content)

            # 转换枚举类型
            try:
                mem_type = MemoryType(memory_type.lower())
            except ValueError:
                mem_type = MemoryType.CONTEXT

            try:
                mem_priority = Priority[priority.upper()]
            except (KeyError, AttributeError):
                mem_priority = Priority.MEDIUM

            # 设置过期时间
            expiry_date = None
            if expiry_hours:
                expiry_date = datetime.now() + timedelta(hours=expiry_hours)

            memory = MemoryItem(
                id=memory_id,
                content=content,
                memory_type=mem_type,
                priority=mem_priority,
                tags=tags or [],
                context=context or {},
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=0,
                expiry_date=expiry_date,
            )

            # 存储到智能管理器
            success = self.smart_manager.store_memory(memory)

            if success:
                # 保存到文件
                self._save_memories()

                # 记录性能指标
                response_time = time.time() - start_time
                self._record_operation_metrics("store", response_time, True)

                # 更新学习引擎
                if self.learning_engine:
                    # 更新用户行为记录
                    actions = list(self.learning_engine.user_actions)
                    if actions:
                        actions[-1].response_time = response_time
                        actions[-1].success = True

                # 触发自动优化
                if self.adaptive_optimizer:
                    self.adaptive_optimizer.trigger_optimization_if_needed()

                return memory_id
            else:
                self._record_operation_metrics("store", time.time() - start_time, False)
                return ""

        except Exception as e:
            self._record_operation_metrics("store", time.time() - start_time, False)
            if self.learning_engine:
                # 记录失败
                actions = list(self.learning_engine.user_actions)
                if actions:
                    actions[-1].response_time = time.time() - start_time
                    actions[-1].success = False
                    actions[-1].error_message = str(e)
            raise e

    def load(
        self,
        query: str,
        memory_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """加载记忆"""
        start_time = time.time()

        try:
            # 检查缓存
            cache_key = None
            if self.cache_manager:
                cache_key = self._generate_cache_key(query, memory_type, tags, limit)
                cached_result = self.cache_manager.get(cache_key)
                if cached_result is not None:
                    return cached_result

            # 记录用户行为
            if self.learning_engine:
                from .learning import UserActionType

                self.learning_engine.record_user_action(
                    action_type=UserActionType.MEMORY_LOAD,
                    query=query,
                    context={"memory_type": memory_type, "tags": tags, "limit": limit},
                    response_time=0.0,
                    success=False,
                )

            # 应用自适应参数
            if self.adaptive_optimizer:
                adaptive_params = self.adaptive_optimizer.get_current_parameters()
                limit = adaptive_params.get("memory_search_limit", limit)
            
            # 确保limit是整数
            limit = int(limit)

            # 转换类型
            mem_type = None
            if memory_type:
                try:
                    mem_type = MemoryType(memory_type.lower())
                except ValueError:
                    pass

            # 搜索记忆
            memories = self.smart_manager.search_memories(
                query=query, memory_type=mem_type, tags=tags, limit=limit
            )

            # 转换为字典格式
            result = []
            for memory in memories:
                result.append(
                    {
                        "id": memory.id,
                        "content": memory.content,
                        "type": memory.memory_type.value,
                        "priority": memory.priority.name.lower(),
                        "tags": memory.tags,
                        "context": memory.context,
                        "created_at": memory.created_at.isoformat(),
                        "relevance_score": memory.relevance_score,
                        "access_count": memory.access_count,
                    }
                )

            # 记录性能指标
            response_time = time.time() - start_time
            self._record_operation_metrics("load", response_time, True)

            # 更新学习引擎
            if self.learning_engine:
                actions = list(self.learning_engine.user_actions)
                if actions:
                    actions[-1].response_time = response_time
                    actions[-1].success = True

            # 缓存结果
            if self.cache_manager and cache_key:
                priority = Priority.MEDIUM
                if len(result) > 0:
                    priority = Priority.HIGH
                self.cache_manager.put(cache_key, result, priority, ttl_hours=1)

            return result

        except Exception as e:
            self._record_operation_metrics("load", time.time() - start_time, False)
            if self.learning_engine:
                actions = list(self.learning_engine.user_actions)
                if actions:
                    actions[-1].response_time = time.time() - start_time
                    actions[-1].success = False
                    actions[-1].error_message = str(e)
            raise e

    def store_smart(
        self,
        content: str,
        memory_type: str = "context",
        tags: List[str] = None,
        context: Dict[str, Any] = None,
        auto_priority: bool = True,
        auto_expiry: bool = True,
    ) -> str:
        """智能存储记忆"""
        # 自动确定优先级
        priority = "medium"
        if auto_priority:
            priority = self._determine_smart_priority(content, memory_type, context)

        # 自动确定过期时间
        expiry_hours = None
        if auto_expiry:
            expiry_hours = self._determine_smart_expiry(memory_type, priority)

        # 自动生成标签
        if not tags:
            tags = self._generate_smart_tags(content, memory_type)

        return self.store(
            content=content,
            memory_type=memory_type,
            tags=tags,
            context=context,
            priority=priority,
            expiry_hours=expiry_hours,
        )

    def get_memory_summary(self, days: int = 7) -> Dict[str, Any]:
        """获取记忆摘要"""
        return self.smart_manager.get_summary(days=days)

    def _apply_adaptive_priority(
        self, priority: str, adaptive_params: Dict[str, Any]
    ) -> str:
        """应用自适应优先级调整"""
        priority_boost = adaptive_params.get("memory_priority_boost", 0)

        priority_map = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        reverse_map = {1: "low", 2: "medium", 3: "high", 4: "critical"}

        current_level = priority_map.get(priority.lower(), 2)
        new_level = max(1, min(4, current_level + priority_boost))

        return reverse_map[new_level]

    def _record_operation_metrics(
        self, operation: str, response_time: float, success: bool
    ):
        """记录操作指标"""
        self.operation_stats[f"{operation}_count"] += 1
        self.operation_stats["total_response_time"] += response_time

        if success:
            self.operation_stats["successful_operations"] += 1
        else:
            self.operation_stats["failed_operations"] += 1

        # 记录到学习引擎
        if self.learning_engine:
            total_ops = (
                self.operation_stats["successful_operations"]
                + self.operation_stats["failed_operations"]
            )
            success_rate = self.operation_stats["successful_operations"] / max(
                total_ops, 1
            )

            self.learning_engine.record_performance_metrics(
                response_time=response_time,
                memory_usage=0.5,  # 简化的内存使用率
                cpu_usage=0.3,  # 简化的CPU使用率
                success_rate=success_rate,
                error_count=self.operation_stats["failed_operations"],
                throughput=1.0 / max(response_time, 0.001),
                context_size=len(self.smart_manager.memories),
                memory_hits=self.operation_stats["successful_operations"],
                cache_efficiency=success_rate,
            )

    def _load_existing_memories(self) -> List[MemoryItem]:
        """加载现有记忆"""
        return list(self.smart_manager.memories.values())

    def get_memory_stats(self) -> Dict[str, Any]:
        """获取记忆统计信息"""
        total_ops = (
            self.operation_stats["successful_operations"]
            + self.operation_stats["failed_operations"]
        )
        avg_response_time = self.operation_stats["total_response_time"] / max(
            total_ops, 1
        )
        success_rate = self.operation_stats["successful_operations"] / max(total_ops, 1)

        stats = {
            "total_memories": len(self.smart_manager.memories),
            "total_operations": total_ops,
            "success_rate": success_rate,
            "avg_response_time": avg_response_time,
            "operation_breakdown": {
                "store": self.operation_stats["store_count"],
                "load": self.operation_stats["load_count"],
                "search": self.operation_stats["search_count"],
            },
        }

        # 添加缓存统计
        if self.cache_manager:
            stats["cache_stats"] = self.cache_manager.get_stats()

        return stats

    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """获取优化建议"""
        recommendations = []

        # 基于统计数据生成建议
        total_ops = (
            self.operation_stats["successful_operations"]
            + self.operation_stats["failed_operations"]
        )
        if total_ops > 0:
            success_rate = self.operation_stats["successful_operations"] / total_ops
            avg_response_time = self.operation_stats["total_response_time"] / total_ops

            if success_rate < 0.9:
                recommendations.append(
                    {
                        "type": "reliability_improvement",
                        "description": f"记忆操作成功率 {success_rate:.1%} 偏低，建议检查存储机制",
                        "priority": "high",
                        "impact": 1.0 - success_rate,
                    }
                )

            if avg_response_time > 0.5:
                recommendations.append(
                    {
                        "type": "performance_optimization",
                        "description": f"记忆操作平均响应时间 {avg_response_time:.2f}s 偏高，建议优化索引",
                        "priority": "medium",
                        "impact": min(avg_response_time / 2.0, 1.0),
                    }
                )

        # 基于记忆数量生成建议
        memory_count = len(self.smart_manager.memories)
        if memory_count > 8000:
            recommendations.append(
                {
                    "type": "memory_cleanup",
                    "description": f"记忆数量 {memory_count} 较多，建议清理过期记忆",
                    "priority": "medium",
                    "impact": 0.6,
                }
            )

        return recommendations

    def _determine_smart_priority(
        self, content: str, memory_type: str, context: Dict[str, Any]
    ) -> str:
        """智能确定优先级"""
        # 基于内容长度
        if len(content) > 1000:
            return "high"

        # 基于类型
        if memory_type in ["system", "error_log"]:
            return "high"
        elif memory_type in ["learning", "optimization"]:
            return "medium"

        # 基于上下文
        if context and context.get("importance") == "critical":
            return "critical"

        return "medium"

    def _determine_smart_expiry(self, memory_type: str, priority: str) -> Optional[int]:
        """智能确定过期时间"""
        if memory_type == "conversation":
            return 24 * 7  # 7天
        elif memory_type == "context":
            return 24 * 3  # 3天
        elif memory_type == "error_log":
            return 24 * 30  # 30天
        elif priority == "low":
            return 24  # 1天

        return None  # 不过期

    def _generate_smart_tags(self, content: str, memory_type: str) -> List[str]:
        """智能生成标签"""
        tags = [memory_type]

        # 基于内容提取关键词作为标签
        keywords = self.smart_manager.index._extract_keywords(content)
        tags.extend(keywords[:3])  # 最多3个关键词标签

        # 基于内容特征添加标签
        if "error" in content.lower() or "exception" in content.lower():
            tags.append("error")
        if "optimization" in content.lower() or "performance" in content.lower():
            tags.append("optimization")
        if "user" in content.lower():
            tags.append("user_related")

        return list(set(tags))  # 去重

    def _generate_memory_id(self, content: str) -> str:
        """生成记忆ID"""
        timestamp = datetime.now().isoformat()
        content_hash = hashlib.md5(f"{content}_{timestamp}".encode()).hexdigest()
        return f"mem_{content_hash[:12]}"

    def _generate_cache_key(
        self,
        query: str,
        memory_type: Optional[str],
        tags: Optional[List[str]],
        limit: int,
    ) -> str:
        """生成缓存键"""
        key_parts = [query, str(memory_type), str(sorted(tags or [])), str(limit)]
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()

    def clear_cache(self):
        """清空缓存"""
        if self.cache_manager:
            self.cache_manager.clear()

    def cleanup_expired_cache(self):
        """清理过期缓存"""
        if self.cache_manager:
            self.cache_manager.cleanup_expired()

    def _save_memories(self):
        """保存记忆到文件"""
        try:
            memories_data = []
            for memory in self.smart_manager.memories.values():
                memory_dict = asdict(memory)
                memory_dict["created_at"] = memory.created_at.isoformat()
                memory_dict["last_accessed"] = memory.last_accessed.isoformat()
                memory_dict["memory_type"] = memory.memory_type.value
                memory_dict["priority"] = memory.priority.value
                if memory.expiry_date:
                    memory_dict["expiry_date"] = memory.expiry_date.isoformat()
                memories_data.append(memory_dict)

            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(memories_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving memories: {e}")

    def _load_memories(self):
        """从文件加载记忆"""
        if not self.memory_file.exists():
            return

        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                memories_data = json.load(f)

            for memory_dict in memories_data:
                # 转换时间字段
                memory_dict["created_at"] = datetime.fromisoformat(
                    memory_dict["created_at"]
                )
                memory_dict["last_accessed"] = datetime.fromisoformat(
                    memory_dict["last_accessed"]
                )
                if memory_dict.get("expiry_date"):
                    memory_dict["expiry_date"] = datetime.fromisoformat(
                        memory_dict["expiry_date"]
                    )

                # 转换枚举字段
                memory_dict["memory_type"] = MemoryType(memory_dict["memory_type"])
                memory_dict["priority"] = Priority(memory_dict["priority"])

                # 创建记忆对象
                memory = MemoryItem(**memory_dict)
                self.smart_manager.memories[memory.id] = memory
                self.smart_manager.index.add_memory(memory)

        except Exception as e:
            print(f"Error loading memories: {e}")
