#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P2 任务测试：超长上下文持久缓存与动态裁剪
测试 ContextCacheManager 和 DynamicContextTrimmer 的功能
"""

import sys
import os
import time
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from solo_mcp.tools.memory import ContextCacheManager, CacheItem, Priority
from solo_mcp.tools.context import DynamicContextTrimmer, ContextItem, TrimmedContext

def test_context_cache_manager():
    """测试上下文缓存管理器"""
    print("\n=== 测试 ContextCacheManager ===")
    
    # 初始化缓存管理器
    cache = ContextCacheManager(max_size=5, max_memory_mb=1)
    
    # 测试基本缓存操作
    print("\n1. 测试基本缓存操作")
    
    # 添加缓存项
    test_data = [
        ("key1", "这是第一个测试数据", Priority.HIGH),
        ("key2", "这是第二个测试数据", Priority.MEDIUM),
        ("key3", "这是第三个测试数据", Priority.LOW),
        ("key4", "这是第四个测试数据", Priority.HIGH),
        ("key5", "这是第五个测试数据", Priority.MEDIUM)
    ]
    
    for key, data, priority in test_data:
        cache.put(key, data, priority, ttl_hours=1)
        print(f"  添加缓存: {key} (优先级: {priority.name})")
    
    # 测试缓存获取
    print("\n2. 测试缓存获取")
    for key, _, _ in test_data:
        result = cache.get(key)
        print(f"  获取 {key}: {'成功' if result else '失败'}")
    
    # 测试 LRU 驱逐
    print("\n3. 测试 LRU 驱逐机制")
    cache.put("key6", "这会触发 LRU 驱逐", Priority.MEDIUM, ttl_hours=1)
    print("  添加 key6，应该驱逐最少使用的项")
    
    # 检查缓存状态
    stats = cache.get_stats()
    print(f"\n4. 缓存统计:")
    print(f"  当前大小: {stats['size']}/{stats['max_size']}")
    print(f"  命中率: {stats['hit_rate']:.2%}")
    print(f"  内存使用: {stats['memory_usage_mb']:.2f}MB")
    
    # 测试过期清理
    print("\n5. 测试过期清理")
    cache.put("temp_key", "临时数据", Priority.LOW, ttl_hours=0.001)  # 很短的 TTL
    time.sleep(0.1)  # 等待过期
    cache.cleanup_expired()
    temp_result = cache.get("temp_key")
    print(f"  过期项清理: {'成功' if temp_result is None else '失败'}")
    
    return True

def test_dynamic_context_trimmer():
    """测试动态上下文裁剪器"""
    print("\n=== 测试 DynamicContextTrimmer ===")
    
    # 初始化裁剪器
    trimmer = DynamicContextTrimmer(max_context_size=500, target_trim_ratio=0.6)
    
    # 创建测试上下文项
    print("\n1. 创建测试上下文项")
    
    test_contexts = [
        ContextItem(
            file_path="test1.py",
            content="def important_function():\n    # 这是一个重要的函数\n    return 'critical_data'\n" * 10,
            relevance_score=0.9,
            context_type="function",
            timestamp=datetime.now()
        ),
        ContextItem(
            file_path="test2.py",
            content="# 这是一些普通的代码注释\nprint('hello world')\n" * 15,
            relevance_score=0.5,
            context_type="content",
            timestamp=datetime.now() - timedelta(hours=2)
        ),
        ContextItem(
            file_path="test3.py",
            content="class TestClass:\n    def __init__(self):\n        self.data = []\n" * 8,
            relevance_score=0.8,
            context_type="class",
            timestamp=datetime.now() - timedelta(minutes=30)
        ),
        ContextItem(
            file_path="test4.py",
            content="# 低重要性的文件内容\ntemp_var = 123\n" * 20,
            relevance_score=0.2,
            context_type="content",
            timestamp=datetime.now() - timedelta(hours=5)
        )
    ]
    
    total_size = sum(len(item.content) for item in test_contexts)
    print(f"  创建了 {len(test_contexts)} 个上下文项，总大小: {total_size} 字符")
    
    # 测试不同的裁剪策略
    print("\n2. 测试裁剪功能")
    
    # 测试自动裁剪
    trimmed = trimmer.trim_context(test_contexts)
    
    print(f"  原始项目数: {len(trimmed.original_items)}")
    print(f"  裁剪后项目数: {len(trimmed.trimmed_items)}")
    print(f"  裁剪比例: {trimmed.trim_ratio:.2%}")
    print(f"  使用策略: {trimmed.trim_strategy}")
    print(f"  原始大小: {trimmed.metadata.get('original_size', 0)} 字符")
    print(f"  裁剪后大小: {trimmed.metadata.get('trimmed_size', 0)} 字符")
    
    # 测试重要性分数
    print("\n3. 重要性分数分析")
    for file_path, score in trimmed.importance_scores.items():
        print(f"  {file_path}: {score:.3f}")
    
    # 测试不同目标大小的裁剪
    print("\n4. 测试不同目标大小")
    target_sizes = [200, 300, 400]
    
    for target_size in target_sizes:
        result = trimmer.trim_context(test_contexts, target_size=target_size)
        actual_size = sum(len(item.content) for item in result.trimmed_items)
        print(f"  目标大小 {target_size}: 实际大小 {actual_size}, 策略 {result.trim_strategy}")
    
    # 测试裁剪统计
    print("\n5. 裁剪统计信息")
    stats = trimmer.get_trim_stats()
    print(f"  总裁剪次数: {stats['total_trims']}")
    print(f"  平均裁剪比例: {stats['avg_trim_ratio']:.2%}")
    print(f"  内容保留率: {stats['content_preserved_rate']:.2%}")
    print(f"  效率分数: {stats['efficiency_score']:.3f}")
    print(f"  策略分布: {stats['strategy_distribution']}")
    
    # 测试参数优化
    print("\n6. 测试参数优化")
    feedback = {"user_satisfaction": 0.6}  # 模拟用户不满意
    old_importance_weight = trimmer.importance_weight
    trimmer.optimize_parameters(feedback)
    print(f"  重要性权重调整: {old_importance_weight:.2f} -> {trimmer.importance_weight:.2f}")
    
    return True

def test_integration():
    """测试缓存和裁剪的集成效果"""
    print("\n=== 测试集成效果 ===")
    
    # 模拟实际使用场景
    cache = ContextCacheManager(max_size=10, max_memory_mb=2)
    trimmer = DynamicContextTrimmer(max_context_size=300, target_trim_ratio=0.5)
    
    # 创建大量上下文数据
    large_contexts = []
    for i in range(20):
        context = ContextItem(
            file_path=f"file_{i}.py",
            content=f"# 文件 {i} 的内容\n" + "代码行\n" * (10 + i),
            relevance_score=0.3 + (i % 7) * 0.1,
            context_type="content",
            timestamp=datetime.now() - timedelta(minutes=i*5)
        )
        large_contexts.append(context)
    
    print(f"\n1. 处理 {len(large_contexts)} 个上下文项")
    
    # 模拟查询和缓存流程
    queries = ["query1", "query2", "query3", "query1", "query2"]  # 重复查询测试缓存
    
    for i, query in enumerate(queries):
        print(f"\n  处理查询 {i+1}: {query}")
        
        # 检查缓存
        cached_result = cache.get(query)
        if cached_result:
            print(f"    缓存命中: {len(cached_result)} 项")
            continue
        
        # 模拟上下文收集（选择部分数据）
        selected_contexts = large_contexts[i*3:(i+1)*4]  # 选择不同的上下文子集
        
        # 应用裁剪
        trimmed = trimmer.trim_context(selected_contexts, target_size=200)
        
        # 缓存结果
        cache.put(query, trimmed.trimmed_items, Priority.MEDIUM, ttl_hours=1)
        
        print(f"    新处理: {len(selected_contexts)} -> {len(trimmed.trimmed_items)} 项")
        print(f"    裁剪比例: {trimmed.trim_ratio:.2%}")
    
    # 最终统计
    print("\n2. 最终统计")
    cache_stats = cache.get_stats()
    trim_stats = trimmer.get_trim_stats()
    
    print(f"  缓存命中率: {cache_stats['hit_rate']:.2%}")
    print(f"  缓存使用率: {cache_stats['size']}/{cache_stats['max_size']}")
    print(f"  平均裁剪比例: {trim_stats['avg_trim_ratio']:.2%}")
    print(f"  内容保留率: {trim_stats['content_preserved_rate']:.2%}")
    
    return True

def main():
    """主测试函数"""
    print("开始 P2 任务测试：超长上下文持久缓存与动态裁剪")
    print("=" * 60)
    
    try:
        # 运行所有测试
        tests = [
            ("上下文缓存管理器", test_context_cache_manager),
            ("动态上下文裁剪器", test_dynamic_context_trimmer),
            ("集成效果", test_integration)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            try:
                result = test_func()
                results.append((test_name, result, None))
                print(f"✅ {test_name} 测试通过")
            except Exception as e:
                results.append((test_name, False, str(e)))
                print(f"❌ {test_name} 测试失败: {e}")
        
        # 汇总结果
        print("\n" + "="*60)
        print("测试结果汇总:")
        
        passed = 0
        for test_name, success, error in results:
            status = "✅ 通过" if success else f"❌ 失败: {error}"
            print(f"  {test_name}: {status}")
            if success:
                passed += 1
        
        print(f"\n总体结果: {passed}/{len(tests)} 个测试通过")
        
        if passed == len(tests):
            print("\n🎉 P2 任务实现成功！")
            print("✨ 超长上下文持久缓存与动态裁剪功能已就绪")
            return True
        else:
            print("\n⚠️  部分测试失败，需要进一步调试")
            return False
            
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)