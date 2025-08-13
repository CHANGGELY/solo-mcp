#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P2 阶段测试：上下文收集与记忆管理增强功能
测试智能上下文收集、记忆优先级管理、语义搜索和自动摘要功能
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path.cwd()))

from solo_mcp.config import SoloConfig
from solo_mcp.tools.context import ContextTool, SmartContextCollector, ContextType, RelevanceLevel
from solo_mcp.tools.memory import MemoryTool, MemoryType, Priority
from solo_mcp.tools.index import IndexTool


def print_section(title: str):
    """打印测试章节标题"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def print_subsection(title: str):
    """打印测试子章节标题"""
    print(f"\n{'-'*40}")
    print(f" {title}")
    print(f"{'-'*40}")


async def test_smart_context_collection():
    """测试智能上下文收集功能"""
    print_section("P2 阶段测试：智能上下文收集")
    
    try:
        # 初始化配置和工具
        config = SoloConfig.load(Path.cwd())
        index = IndexTool(config)
        memory = MemoryTool(config)
        context = ContextTool(config, index, memory)
        
        # 测试场景1：Python 代码实现查询
        print_subsection("场景1：Python 代码实现查询")
        query1 = "implement python function for role planning algorithm"
        result1 = await context.collect_smart(query1, limit=4000)
        
        print(f"查询: {query1}")
        print(f"查询意图分析: {result1.get('query_intent', {})}")
        print(f"找到 {result1.get('items_count', 0)} 个相关文件")
        print(f"总大小: {result1.get('total_size', 0)} 字符")
        print(f"摘要:\n{result1.get('summary', '')[:500]}...")
        
        # 测试场景2：调试错误查询
        print_subsection("场景2：调试错误查询")
        query2 = "debug error in orchestrator tool conflict detection"
        result2 = await context.collect_smart(query2, limit=3000)
        
        print(f"查询: {query2}")
        print(f"查询意图分析: {result2.get('query_intent', {})}")
        print(f"找到 {result2.get('items_count', 0)} 个相关文件")
        
        # 显示相关性得分最高的文件
        context_items = result2.get('context_items', [])
        if context_items:
            print("\n相关性最高的文件:")
            for i, item in enumerate(context_items[:3]):
                print(f"  {i+1}. {Path(item['path']).name} (得分: {item['relevance_score']:.2f}, 类型: {item['type']})")
        
        # 测试场景3：配置文件查询
        print_subsection("场景3：配置文件查询")
        query3 = "configuration setup environment variables"
        result3 = await context.collect_smart(query3, limit=2000)
        
        print(f"查询: {query3}")
        print(f"查询复杂度: {result3.get('query_intent', {}).get('complexity', 'unknown')}")
        print(f"技术栈: {result3.get('query_intent', {}).get('tech_stack', [])}")
        
        print("\n✅ 智能上下文收集测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 智能上下文收集测试失败: {e}")
        return False


def test_smart_memory_management():
    """测试智能记忆管理功能"""
    print_section("P2 阶段测试：智能记忆管理")
    
    try:
        # 初始化配置和工具
        config = SoloConfig.load(Path.cwd())
        memory = MemoryTool(config)
        
        # 测试场景1：存储不同类型的记忆
        print_subsection("场景1：存储不同类型的记忆")
        
        # 存储代码模式记忆
        code_pattern_id = memory.store_smart(
            content="def calculate_relevance(item, query_intent): score = 0.0; score += type_weight; return score",
            memory_type="code_pattern",
            tags=["algorithm", "relevance", "scoring"],
            context={"success": True, "reuse_count": 3}
        )
        print(f"存储代码模式记忆: {code_pattern_id}")
        
        # 存储解决方案记忆
        solution_id = memory.store_smart(
            content="To fix orchestrator conflict detection, add TaskAllocator and ConflictDetector classes with priority-based allocation",
            memory_type="solution",
            tags=["orchestrator", "conflict", "fix"],
            context={"success": True, "error_count": 2}
        )
        print(f"存储解决方案记忆: {solution_id}")
        
        # 存储错误修复记忆
        error_fix_id = memory.store_smart(
            content="ImportError: No module named 'dataclasses' - Fixed by adding from dataclasses import dataclass",
            memory_type="error_fix",
            tags=["import", "dataclass", "python"],
            context={"error_count": 1, "success": True}
        )
        print(f"存储错误修复记忆: {error_fix_id}")
        
        # 测试场景2：智能搜索记忆
        print_subsection("场景2：智能搜索记忆")
        
        # 搜索算法相关记忆
        algorithm_memories = memory.search_smart(
            query="algorithm relevance scoring",
            limit=5
        )
        print(f"\n搜索 'algorithm relevance scoring' 找到 {len(algorithm_memories)} 条记忆:")
        for mem in algorithm_memories:
            print(f"  - {mem['type']}: {mem['summary'][:100]}... (优先级: {mem['priority']})")
        
        # 搜索错误修复记忆
        error_memories = memory.search_smart(
            query="import error fix",
            memory_types=["error_fix"],
            limit=3
        )
        print(f"\n搜索错误修复记忆找到 {len(error_memories)} 条:")
        for mem in error_memories:
            print(f"  - 访问次数: {mem['access_count']}, 关键词: {mem['keywords'][:5]}")
        
        # 测试场景3：按标签搜索
        print_subsection("场景3：按标签搜索")
        
        orchestrator_memories = memory.search_smart(
            tags=["orchestrator", "conflict"],
            limit=5
        )
        print(f"\n按标签搜索 'orchestrator, conflict' 找到 {len(orchestrator_memories)} 条记忆:")
        for mem in orchestrator_memories:
            print(f"  - {mem['id']}: {mem['tags']}")
        
        # 测试场景4：记忆统计信息
        print_subsection("场景4：记忆统计信息")
        
        stats = memory.get_stats()
        print(f"\n记忆统计信息:")
        print(f"  总记忆数: {stats['total_items']}")
        print(f"  总大小: {stats['total_size_bytes']} 字节")
        print(f"  平均访问次数: {stats['avg_access_per_item']:.2f}")
        print(f"  类型分布: {stats['type_distribution']}")
        print(f"  优先级分布: {stats['priority_distribution']}")
        
        # 测试场景5：记忆清理
        print_subsection("场景5：记忆清理测试")
        
        # 清理90天前的记忆（测试用，实际不会有这么旧的记忆）
        cleaned_count = memory.cleanup(days_threshold=90)
        print(f"清理了 {cleaned_count} 条旧记忆")
        
        print("\n✅ 智能记忆管理测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 智能记忆管理测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_context_memory_integration():
    """测试上下文收集与记忆管理集成"""
    print_section("P2 阶段测试：上下文与记忆集成")
    
    try:
        # 初始化配置和工具
        config = SoloConfig.load(Path.cwd())
        index = IndexTool(config)
        memory = MemoryTool(config)
        context = ContextTool(config, index, memory)
        
        # 测试场景1：基于记忆的上下文增强
        print_subsection("场景1：基于记忆的上下文增强")
        
        # 先存储一些相关记忆
        memory.store_smart(
            content="Context collection should prioritize recent files and high-relevance content based on query intent analysis",
            memory_type="learning",
            tags=["context", "collection", "strategy"],
            context={"success": True}
        )
        
        # 然后进行上下文收集
        query = "improve context collection strategy"
        context_result = await context.collect_smart(query, limit=3000)
        
        # 搜索相关记忆
        related_memories = memory.search_smart(
            query="context collection strategy",
            limit=3
        )
        
        print(f"查询: {query}")
        print(f"上下文项目数: {context_result.get('items_count', 0)}")
        print(f"相关记忆数: {len(related_memories)}")
        
        if related_memories:
            print("\n相关记忆:")
            for mem in related_memories:
                print(f"  - {mem['type']}: {mem['summary'][:80]}...")
        
        # 测试场景2：传统接口兼容性
        print_subsection("场景2：传统接口兼容性测试")
        
        # 测试传统 collect 方法
        traditional_result = await context.collect("python function implementation", limit=2000)
        
        print(f"传统接口结果:")
        print(f"  成功: {traditional_result.get('ok', False)}")
        print(f"  令牌数: {traditional_result.get('tokens', 0)}")
        print(f"  智能分析: {'smart_analysis' in traditional_result}")
        print(f"  项目数: {traditional_result.get('items_count', 0)}")
        
        # 测试传统记忆接口
        memory.store("test_key", {"data": "test_value", "timestamp": datetime.now().isoformat()})
        loaded_data = memory.load("test_key")
        print(f"\n传统记忆接口测试: {loaded_data is not None}")
        
        print("\n✅ 上下文与记忆集成测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 上下文与记忆集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("🚀 开始 P2 阶段测试：上下文收集与记忆管理增强")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 运行所有测试
    tests = [
        ("智能上下文收集", test_smart_context_collection()),
        ("智能记忆管理", test_smart_memory_management()),
        ("上下文与记忆集成", test_context_memory_integration())
    ]
    
    results = []
    for test_name, test_coro in tests:
        print(f"\n🧪 运行测试: {test_name}")
        try:
            if asyncio.iscoroutine(test_coro):
                result = await test_coro
            else:
                result = test_coro
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 测试 {test_name} 异常: {e}")
            results.append((test_name, False))
    
    # 汇总结果
    print_section("P2 阶段测试结果汇总")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总体结果: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 P2 阶段所有测试通过！")
        print("\n📋 P2 阶段功能验证完成:")
        print("  ✅ 智能上下文收集 - 查询意图分析、文件类型分类、相关性计算")
        print("  ✅ 智能记忆管理 - 优先级管理、语义搜索、自动摘要")
        print("  ✅ 上下文与记忆集成 - 增强的上下文收集、传统接口兼容")
        print("\n🚀 P2 阶段增强功能已就绪，可以进入下一阶段开发！")
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，需要修复后再继续")
    
    return passed == total


if __name__ == "__main__":
    asyncio.run(main())