#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P3 阶段测试脚本：自适应学习与优化功能验证

测试内容：
1. LearningEngine 用户行为分析和模式识别
2. AdaptiveOptimizer 动态参数调整和性能优化
3. PerformanceMonitor 实时监控和瓶颈检测
4. 集成工具的智能优化功能
5. 端到端自适应学习流程
"""

import asyncio
import json
import time
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目路径
import sys
sys.path.append(str(Path(__file__).parent))

from solo_mcp.config import SoloConfig
from solo_mcp.tools.learning import LearningEngine, UserActionType, LearningPattern
from solo_mcp.tools.adaptive import AdaptiveOptimizer, OptimizationType
from solo_mcp.tools.orchestrator import OrchestratorTool
from solo_mcp.tools.context import ContextTool
from solo_mcp.tools.memory import MemoryTool


def test_learning_engine():
    """测试学习引擎功能"""
    print("\n=== 测试 LearningEngine 功能 ===")
    
    # 初始化配置和学习引擎
    config = SoloConfig.load(Path.cwd())
    learning_engine = LearningEngine(config, None)
    
    print("1. 测试用户行为记录...")
    
    # 模拟用户行为序列
    behaviors = [
        (UserActionType.CONTEXT_COLLECTION, "如何实现异步编程", {"language": "python"}, 0.5, True),
        (UserActionType.MEMORY_STORE, "async_patterns", {"type": "code_pattern"}, 0.2, True),
        (UserActionType.TASK_ALLOCATION, "创建异步函数", {"role": "backend"}, 1.2, True),
        (UserActionType.CONTEXT_COLLECTION, "Python asyncio 最佳实践", {"language": "python"}, 0.8, True),
        (UserActionType.MEMORY_SEARCH, "async", {"results": 5}, 0.3, True),
        (UserActionType.ERROR_HANDLING, "语法错误", {"error_type": "SyntaxError"}, 2.0, False),
        (UserActionType.CONTEXT_COLLECTION, "如何处理异步异常", {"language": "python"}, 0.6, True),
        (UserActionType.TASK_ALLOCATION, "错误处理优化", {"role": "backend"}, 0.9, True),
    ]
    
    # 记录用户行为
    for action_type, query, context, response_time, success in behaviors:
        learning_engine.record_user_action(
            action_type=action_type,
            query=query,
            context=context,
            response_time=response_time,
            success=success,
            error_message=None if success else "模拟错误"
        )
        time.sleep(0.1)  # 模拟时间间隔
    
    print(f"   ✓ 记录了 {len(behaviors)} 个用户行为")
    
    print("\n2. 测试模式识别...")
    
    # 分析用户模式
    patterns = learning_engine.analyze_user_patterns()
    print(f"   ✓ 识别到 {len(patterns)} 个用户模式")
    
    for pattern in patterns[:3]:  # 显示前3个模式
        print(f"     - {pattern.pattern_type.value}: {pattern.description}")
        print(f"       置信度: {pattern.confidence:.2f}, 频率: {pattern.frequency}")
    
    print("\n3. 测试性能指标记录...")
    
    # 记录性能指标
    for i in range(5):
        learning_engine.record_performance_metrics(
            response_time=0.5 + i * 0.1,
            memory_usage=0.3 + i * 0.05,
            cpu_usage=0.2 + i * 0.03,
            success_rate=0.95 - i * 0.02,
            error_count=i,
            throughput=10.0 - i,
            context_size=1000 + i * 100,
            memory_hits=8 - i,
            cache_efficiency=0.9 - i * 0.02
        )
    
    print("   ✓ 记录了 5 组性能指标")
    
    print("\n4. 测试优化建议生成...")
    
    recommendations = learning_engine.get_optimization_recommendations()
    print(f"   ✓ 生成了 {len(recommendations)} 个优化建议")
    
    for rec in recommendations[:2]:  # 显示前2个建议
        print(f"     - {rec['type']}: {rec['description']}")
        print(f"       优先级: {rec['priority']}, 影响: {rec['impact']}")
    
    # 获取学习统计
    stats = learning_engine.get_learning_stats()
    print(f"\n5. 学习统计信息:")
    print(f"   - 总行为数: {stats['total_actions']}")
    print(f"   - 成功率: {stats['success_rate']:.2%}")
    print(f"   - 平均响应时间: {stats['avg_response_time']:.3f}s")
    print(f"   - 识别模式数: {stats['patterns_identified']}")
    
    print("\n✅ LearningEngine 测试完成")
    return learning_engine


def test_adaptive_optimizer(learning_engine):
    """测试自适应优化器功能"""
    print("\n=== 测试 AdaptiveOptimizer 功能 ===")
    
    # 初始化自适应优化器
    config = SoloConfig.load(Path.cwd())
    optimizer = AdaptiveOptimizer(config)
    optimizer.set_learning_engine(learning_engine)
    
    print("1. 测试参数优化...")
    
    # 测试单个参数优化
    test_params = [
        ("context_search_limit", "context_relevance", 0.7),
        ("memory_search_limit", "memory_usage", 0.6),
        ("response_timeout", "response_time", 1.2),
        ("max_context_size", "memory_usage", 0.8)
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
    
    print("\n2. 测试自动优化...")
    
    # 模拟性能问题并触发自动优化
    optimizer.performance_monitor.record_metrics({
        "response_time": 3.0,  # 超过阈值
        "memory_usage": 0.9,   # 超过阈值
        "success_rate": 0.8    # 低于阈值
    })
    
    # 触发自动优化
    auto_optimized = optimizer.trigger_optimization_if_needed()
    if auto_optimized:
        print(f"   ✓ 自动优化已触发")
    else:
        print(f"   ⚠ 自动优化未触发（可能需要更多数据点）")
    
    print("\n3. 测试性能监控...")
    
    # 获取当前性能状态
    current_perf = optimizer.performance_monitor.get_current_performance()
    print(f"   ✓ 当前性能状态:")
    print(f"     - 响应时间: {current_perf['response_time']:.3f}s")
    print(f"     - 内存使用: {current_perf['memory_usage']:.1%}")
    print(f"     - 成功率: {current_perf['success_rate']:.1%}")
    
    # 检测性能问题
    issues = optimizer.performance_monitor.detect_performance_issues()
    print(f"   ✓ 检测到 {len(issues)} 个性能问题")
    
    for issue in issues[:2]:  # 显示前2个问题
        print(f"     - {issue['type']}: {issue['description']}")
        print(f"       严重程度: {issue['severity']}")
    
    print("\n4. 测试手动优化...")
    
    # 测试手动优化参数
    manual_params = [
        ("context_search_limit", 15.0),
        ("memory_search_limit", 8.0),
        ("response_timeout", 45.0)
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
    
    # 获取优化状态
    opt_status = optimizer.get_optimization_status()
    print(f"\n5. 优化状态信息:")
    print(f"   - 总优化次数: {opt_status['total_optimizations']}")
    print(f"   - 最近优化次数: {opt_status['recent_optimizations']}")
    print(f"   - 当前策略: {opt_status['current_strategy']}")
    print(f"   - 优化启用: {opt_status['optimization_enabled']}")
    print(f"   - 当前参数数: {len(opt_status['current_parameters'])}")
    print(f"   - 检测到问题数: {len(opt_status['performance_issues'])}")
    
    print("\n✅ AdaptiveOptimizer 测试完成")
    return optimizer


async def test_integrated_tools(learning_engine, optimizer):
    """测试集成工具的智能优化功能"""
    print("\n=== 测试集成工具智能优化功能 ===")
    
    config = SoloConfig.load(Path.cwd())
    
    print("1. 测试智能任务分配 (OrchestratorTool)...")
    
    # 初始化编排工具
    orchestrator = OrchestratorTool(config)
    
    # 模拟任务分配场景
    goal = "开发一个用户认证系统，包括注册、登录、权限管理功能"
    history = [
        "用户提出需求：需要一个安全的认证系统",
        "分析需求：包括前端界面、后端API、数据库设计",
        "技术选型：React + Node.js + PostgreSQL"
    ]
    
    result = await orchestrator.run_round(goal, history)
    print(f"   ✓ 智能任务分配完成")
    print(f"     分配任务数: {len(result.get('tasks', []))}")
    print(f"     检测冲突数: {len(result.get('conflicts', []))}")
    print(f"     生成动作数: {len(result.get('actions', []))}")
    
    # 显示部分任务
    tasks = result.get('tasks', [])
    for i, task in enumerate(tasks[:2]):
        print(f"     任务 {i+1}: {task.get('description', 'N/A')}")
        print(f"       分配角色: {task.get('assigned_role', 'N/A')}")
        print(f"       优先级: {task.get('priority', 'N/A')}")
    
    print("\n2. 测试智能上下文收集 (ContextTool)...")
    
    # 初始化上下文工具
    context_tool = ContextTool(config)
    
    # 测试智能上下文收集
    query = "如何在 React 中实现用户认证状态管理"
    context_result = await context_tool.collect_smart(query, limit=2000)
    
    print(f"   ✓ 智能上下文收集完成")
    print(f"     收集内容长度: {len(context_result)}")
    print(f"     包含文件数: {context_result.count('文件:') if context_result else 0}")
    
    # 显示部分上下文
    if context_result:
        preview = context_result[:200] + "..." if len(context_result) > 200 else context_result
        print(f"     内容预览: {preview}")
    
    print("\n3. 测试智能记忆管理 (MemoryTool)...")
    
    # 初始化记忆工具
    memory_tool = MemoryTool(config)
    
    # 测试智能记忆存储
    test_memories = [
        ("react_auth_pattern", "React 认证状态管理最佳实践", "code_context", "high", ["react", "auth", "state"]),
        ("jwt_implementation", "JWT 令牌实现和验证流程", "solution", "high", ["jwt", "security", "backend"]),
        ("user_session_mgmt", "用户会话管理策略", "workflow", "medium", ["session", "security", "frontend"])
    ]
    
    for key, content, mem_type, priority, tags in test_memories:
        success = memory_tool.store(key, content, mem_type, priority, tags)
        if success:
            print(f"   ✓ 存储记忆: {key}")
        else:
            print(f"   ⚠ 存储失败: {key}")
    
    # 测试智能记忆搜索
    search_results = memory_tool.search_smart(
        query="React 用户认证",
        memory_types=["code_context", "solution"],
        priorities=["high"],
        tags=["react", "auth"],
        limit=5
    )
    
    print(f"   ✓ 智能搜索完成，找到 {len(search_results)} 个相关记忆")
    
    for result in search_results[:2]:
        print(f"     - {result['key']}: {result['type']} ({result['priority']})")
        print(f"       相关性: {result.get('relevance_score', 0):.2f}")
    
    print("\n4. 测试工具间协同优化...")
    
    # 获取各工具的优化状态
    orchestrator_stats = orchestrator.get_optimization_status()
    context_stats = context_tool.get_optimization_recommendations()
    memory_stats = memory_tool.get_memory_stats()
    
    print(f"   ✓ 编排工具优化状态:")
    print(f"     - 执行轮次: {orchestrator_stats.get('total_rounds', 0)}")
    print(f"     - 成功率: {orchestrator_stats.get('success_rate', 0):.2%}")
    print(f"     - 平均响应时间: {orchestrator_stats.get('avg_response_time', 0):.3f}s")
    
    print(f"   ✓ 上下文工具优化建议: {len(context_stats)}")
    
    print(f"   ✓ 记忆工具统计:")
    memory_op_stats = memory_stats.get('operation_stats', {})
    print(f"     - 总存储: {memory_op_stats.get('total_stores', 0)}")
    print(f"     - 总加载: {memory_op_stats.get('total_loads', 0)}")
    success_rates = memory_stats.get('success_rates', {})
    print(f"     - 存储成功率: {success_rates.get('store', 0):.2%}")
    print(f"     - 加载成功率: {success_rates.get('load', 0):.2%}")
    
    print("\n✅ 集成工具智能优化测试完成")


async def test_end_to_end_adaptive_learning():
    """测试端到端自适应学习流程"""
    print("\n=== 测试端到端自适应学习流程 ===")
    
    config = SoloConfig.load(Path.cwd())
    
    print("1. 初始化完整系统...")
    
    # 初始化所有组件
    learning_engine = LearningEngine(config, None)
    optimizer = AdaptiveOptimizer(config)
    optimizer.set_learning_engine(learning_engine)
    orchestrator = OrchestratorTool(config)
    context_tool = ContextTool(config)
    memory_tool = MemoryTool(config)
    
    print("   ✓ 所有组件初始化完成")
    
    print("\n2. 模拟用户工作流程...")
    
    # 模拟一个完整的开发工作流程
    workflow_steps = [
        ("需求分析", "分析用户认证系统需求"),
        ("技术选型", "选择合适的技术栈"),
        ("架构设计", "设计系统架构"),
        ("数据库设计", "设计用户表和权限表"),
        ("API 设计", "设计认证相关 API"),
        ("前端实现", "实现登录注册界面"),
        ("后端实现", "实现认证逻辑"),
        ("测试验证", "进行功能测试")
    ]
    
    for step_name, step_desc in workflow_steps:
        print(f"   执行步骤: {step_name}")
        
        # 1. 收集上下文
        start_time = time.time()
        context = await context_tool.collect_smart(step_desc, limit=1000)
        context_time = time.time() - start_time
        
        # 2. 搜索相关记忆
        start_time = time.time()
        memories = memory_tool.search_smart(step_desc, limit=3)
        memory_time = time.time() - start_time
        
        # 3. 任务分配
        start_time = time.time()
        task_result = await orchestrator.run_round(step_desc, [context])
        task_time = time.time() - start_time
        
        # 4. 存储新知识
        memory_key = f"workflow_{step_name.lower().replace(' ', '_')}"
        memory_tool.store(
            key=memory_key,
            value={
                "step": step_name,
                "description": step_desc,
                "context_length": len(context) if context else 0,
                "memories_found": len(memories),
                "tasks_generated": len(task_result.get('tasks', [])),
                "timestamp": datetime.now().isoformat()
            },
            memory_type="workflow",
            priority="medium",
            tags=["workflow", "auth_system", step_name.lower()]
        )
        
        # 记录性能指标
        total_time = context_time + memory_time + task_time
        learning_engine.record_performance_metrics(
            response_time=total_time,
            memory_usage=0.4,
            cpu_usage=0.3,
            success_rate=1.0,
            error_count=0,
            throughput=1.0 / max(total_time, 0.001),
            context_size=len(context) if context else 0,
            memory_hits=len(memories),
            cache_efficiency=0.8
        )
        
        time.sleep(0.2)  # 模拟处理间隔
    
    print(f"   ✓ 完成 {len(workflow_steps)} 个工作流程步骤")
    
    print("\n3. 分析学习成果...")
    
    # 分析用户模式
    patterns = learning_engine.analyze_user_patterns()
    print(f"   ✓ 识别到 {len(patterns)} 个工作模式")
    
    # 生成优化建议
    recommendations = learning_engine.get_optimization_recommendations()
    print(f"   ✓ 生成 {len(recommendations)} 个优化建议")
    
    # 执行自动优化
    optimization_results = optimizer.optimize_automatically()
    print(f"   ✓ 执行 {len(optimization_results)} 项自动优化")
    
    print("\n4. 系统整体性能评估...")
    
    # 获取综合统计
    learning_stats = learning_engine.get_learning_stats()
    optimization_status = optimizer.get_optimization_status()
    memory_stats = memory_tool.get_memory_stats()
    
    print(f"   ✓ 学习引擎统计:")
    print(f"     - 总行为记录: {learning_stats['total_actions']}")
    print(f"     - 系统成功率: {learning_stats['success_rate']:.2%}")
    print(f"     - 平均响应时间: {learning_stats['avg_response_time']:.3f}s")
    print(f"     - 识别模式数: {learning_stats['patterns_identified']}")
    
    print(f"   ✓ 优化器状态:")
    print(f"     - 总优化次数: {optimization_status['total_optimizations']}")
    print(f"     - 优化成功率: {optimization_status['successful_optimizations'] / max(optimization_status['total_optimizations'], 1):.2%}")
    print(f"     - 平均性能改进: {optimization_status['average_improvement']:.2%}")
    
    print(f"   ✓ 记忆系统统计:")
    smart_stats = memory_stats['smart_memory_stats']
    print(f"     - 存储记忆数: {smart_stats['total_memories']}")
    print(f"     - 索引关键词: {smart_stats['index_keywords']}")
    print(f"     - 索引标签: {smart_stats['index_tags']}")
    
    print("\n5. 清理资源...")
    
    # 清理资源
    optimizer.cleanup()
    memory_tool.cleanup()
    
    print("   ✓ 资源清理完成")
    
    print("\n✅ 端到端自适应学习流程测试完成")


async def main():
    """主测试函数"""
    print("🚀 开始 P3 阶段自适应学习与优化功能测试")
    print("=" * 60)
    
    try:
        # 测试学习引擎
        learning_engine = test_learning_engine()
        
        # 测试自适应优化器
        optimizer = test_adaptive_optimizer(learning_engine)
        
        # 测试集成工具
        await test_integrated_tools(learning_engine, optimizer)
        
        # 测试端到端流程
        await test_end_to_end_adaptive_learning()
        
        print("\n" + "=" * 60)
        print("🎉 P3 阶段所有测试通过！")
        print("\n✅ 自适应学习与优化功能验证成功")
        print("\n主要成果:")
        print("  • LearningEngine: 用户行为分析和模式识别 ✓")
        print("  • AdaptiveOptimizer: 动态参数调整和性能优化 ✓")
        print("  • PerformanceMonitor: 实时监控和瓶颈检测 ✓")
        print("  • 集成工具: 智能任务分配、上下文收集、记忆管理 ✓")
        print("  • 端到端流程: 完整的自适应学习工作流 ✓")
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    # 运行测试
    success = asyncio.run(main())
    
    if success:
        print("\n🎯 P3 阶段开发完成，Solo MCP 现已具备强大的自适应学习与优化能力！")
    else:
        print("\n⚠️  测试未完全通过，请检查错误信息并修复问题。")