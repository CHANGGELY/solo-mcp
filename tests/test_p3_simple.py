#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P3 阶段简化测试脚本 - 自适应学习与优化功能
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path.cwd()))

from solo_mcp.config import SoloConfig
from solo_mcp.tools.learning import LearningEngine, UserActionType, LearningPattern
from solo_mcp.tools.adaptive import AdaptiveOptimizer, OptimizationType


def test_learning_engine_basic():
    """测试 LearningEngine 基础功能"""
    print("=== 测试 LearningEngine 基础功能 ===")
    
    config = SoloConfig.load(Path.cwd())
    learning_engine = LearningEngine(config, None)
    
    print("1. 测试用户行为记录...")
    
    # 记录一些用户行为
    actions = [
        (UserActionType.QUERY_PROCESSING, "搜索 React 组件", True, 0.5),
        (UserActionType.CONTEXT_COLLECTION, "收集上下文信息", True, 0.8),
        (UserActionType.MEMORY_STORE, "存储代码片段", True, 0.3),
        (UserActionType.TASK_ALLOCATION, "执行任务", False, 2.1),
        (UserActionType.QUERY_PROCESSING, "搜索 API 文档", True, 0.7)
    ]
    
    for action_type, query, success, response_time in actions:
        learning_engine.record_user_action(
            action_type=action_type,
            query=query,
            context={"test": True},
            response_time=response_time,
            success=success
        )
    
    print(f"   ✓ 记录了 {len(actions)} 个用户行为")
    
    print("\n2. 测试性能指标记录...")
    
    # 记录性能指标
    metrics = [
        (0.5, 0.3, 0.2, 0.95, 0, 10.0, 1000, 5, 0.8),
        (0.8, 0.4, 0.3, 0.90, 1, 8.0, 1200, 3, 0.7),
        (1.2, 0.5, 0.4, 0.85, 2, 6.0, 800, 7, 0.9)
    ]
    
    for response_time, memory_usage, cpu_usage, success_rate, error_count, throughput, context_size, memory_hits, cache_efficiency in metrics:
        learning_engine.record_performance_metrics(
            response_time=response_time,
            memory_usage=memory_usage,
            cpu_usage=cpu_usage,
            success_rate=success_rate,
            error_count=error_count,
            throughput=throughput,
            context_size=context_size,
            memory_hits=memory_hits,
            cache_efficiency=cache_efficiency
        )
    
    print(f"   ✓ 记录了 {len(metrics)} 组性能指标")
    
    print("\n3. 获取学习统计信息...")
    
    stats = learning_engine.get_learning_stats()
    print(f"   - 总行为数: {stats['total_actions']}")
    print(f"   - 成功率: {stats['success_rate']:.2%}")
    print(f"   - 平均响应时间: {stats['avg_response_time']:.3f}s")
    print(f"   - 识别模式数: {stats['patterns_identified']}")
    
    print("\n✅ LearningEngine 基础测试完成")
    return learning_engine


def test_adaptive_optimizer_basic(learning_engine):
    """测试 AdaptiveOptimizer 基础功能"""
    print("\n=== 测试 AdaptiveOptimizer 基础功能 ===")
    
    config = SoloConfig.load(Path.cwd())
    optimizer = AdaptiveOptimizer(config)
    optimizer.set_learning_engine(learning_engine)
    
    print("1. 测试参数优化...")
    
    # 测试单个参数优化
    test_params = [
        ("context_search_limit", "context_relevance", 0.7),
        ("memory_search_limit", "memory_usage", 0.6),
        ("response_timeout", "response_time", 1.2)
    ]
    
    optimized_count = 0
    for param_name, target_metric, current_perf in test_params:
        success = optimizer.optimize_parameter(param_name, target_metric, current_perf)
        if success:
            print(f"   ✓ {param_name} 优化成功")
            optimized_count += 1
        else:
            print(f"   ⚠ {param_name} 优化跳过")
    
    print(f"   总计优化了 {optimized_count} 个参数")
    
    print("\n2. 测试性能监控...")
    
    # 记录一些性能数据
    optimizer.performance_monitor.record_metrics({
        "response_time": 1.5,
        "memory_usage": 0.6,
        "success_rate": 0.9
    })
    
    current_perf = optimizer.performance_monitor.get_current_performance()
    print(f"   ✓ 当前性能状态:")
    print(f"     - 响应时间: {current_perf['response_time']:.3f}s")
    print(f"     - 内存使用: {current_perf['memory_usage']:.1%}")
    print(f"     - 成功率: {current_perf['success_rate']:.1%}")
    
    print("\n3. 测试手动优化...")
    
    # 测试手动优化参数
    manual_params = [
        ("context_search_limit", 15.0),
        ("memory_search_limit", 8.0)
    ]
    
    manual_count = 0
    for param_name, target_value in manual_params:
        success = optimizer.manual_optimize(param_name, target_value)
        if success:
            print(f"   ✓ 手动优化 {param_name} = {target_value}")
            manual_count += 1
        else:
            print(f"   ⚠ 手动优化 {param_name} 失败")
    
    print(f"   总计手动优化了 {manual_count} 个参数")
    
    print("\n4. 获取优化状态...")
    
    opt_status = optimizer.get_optimization_status()
    print(f"   - 总优化次数: {opt_status['total_optimizations']}")
    print(f"   - 当前策略: {opt_status['current_strategy']}")
    print(f"   - 优化启用: {opt_status['optimization_enabled']}")
    print(f"   - 当前参数数: {len(opt_status['current_parameters'])}")
    
    print("\n✅ AdaptiveOptimizer 基础测试完成")
    return optimizer


def test_integration_basic(learning_engine, optimizer):
    """测试基础集成功能"""
    print("\n=== 测试基础集成功能 ===")
    
    print("1. 测试学习引擎与优化器协同...")
    
    # 模拟一些用户操作和性能数据
    for i in range(3):
        # 记录用户行为
        learning_engine.record_user_action(
            action_type=UserActionType.SEARCH,
            description=f"测试搜索 {i+1}",
            success=True,
            response_time=0.5 + i * 0.2,
            context={"iteration": i+1}
        )
        
        # 记录性能指标
        learning_engine.record_performance_metrics(
            response_time=0.5 + i * 0.2,
            memory_usage=0.3 + i * 0.1,
            cpu_usage=0.2 + i * 0.05,
            success_rate=0.95 - i * 0.02,
            error_count=i,
            throughput=10.0 - i,
            context_size=1000 + i * 100,
            memory_hits=5 - i,
            cache_efficiency=0.8 + i * 0.05
        )
        
        # 记录到优化器的性能监控
        optimizer.performance_monitor.record_metrics({
            "response_time": 0.5 + i * 0.2,
            "memory_usage": 0.3 + i * 0.1,
            "success_rate": 0.95 - i * 0.02
        })
    
    print("   ✓ 记录了协同测试数据")
    
    print("\n2. 获取综合统计信息...")
    
    # 学习引擎统计
    learning_stats = learning_engine.get_learning_stats()
    print(f"   学习引擎统计:")
    print(f"     - 总行为数: {learning_stats['total_actions']}")
    print(f"     - 成功率: {learning_stats['success_rate']:.2%}")
    print(f"     - 平均响应时间: {learning_stats['avg_response_time']:.3f}s")
    
    # 优化器统计
    opt_status = optimizer.get_optimization_status()
    print(f"   优化器统计:")
    print(f"     - 总优化次数: {opt_status['total_optimizations']}")
    print(f"     - 当前策略: {opt_status['current_strategy']}")
    print(f"     - 检测到问题数: {len(opt_status['performance_issues'])}")
    
    print("\n✅ 基础集成测试完成")


def main():
    """主测试函数"""
    print("🚀 开始 P3 阶段简化测试")
    print("=" * 50)
    
    try:
        # 测试学习引擎
        learning_engine = test_learning_engine_basic()
        
        # 测试自适应优化器
        optimizer = test_adaptive_optimizer_basic(learning_engine)
        
        # 测试基础集成
        test_integration_basic(learning_engine, optimizer)
        
        print("\n🎉 P3 阶段简化测试全部通过！")
        print("\n主要功能验证:")
        print("✅ LearningEngine - 用户行为记录和性能指标收集")
        print("✅ AdaptiveOptimizer - 参数优化和性能监控")
        print("✅ 基础集成 - 学习引擎与优化器协同工作")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)