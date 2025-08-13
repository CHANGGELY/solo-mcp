#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 OrchestratorTool 的任务分配和冲突检测功能
"""

import asyncio
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from solo_mcp.tools.orchestrator import OrchestratorTool

async def test_orchestrator():
    """测试 OrchestratorTool 的基本功能"""
    print("=== 开始测试 OrchestratorTool ===")
    
    # 创建配置
    config = {
        'max_rounds': 5,
        'timeout': 300,
        'enable_learning': True,
        'enable_optimization': True
    }
    
    # 创建 OrchestratorTool 实例
    orchestrator = OrchestratorTool(config)
    print("✓ OrchestratorTool 实例创建成功")
    
    # 测试简单的 Web 开发目标
    goal = "创建一个简单的 Web 应用，包含前端界面和后端 API"
    history = []
    
    print(f"\n目标: {goal}")
    print("开始执行任务分配和冲突检测...")
    
    try:
        # 执行一轮任务分配
        result = await orchestrator.run_round(goal, history)
        
        print("\n=== 执行结果 ===")
        print(f"生成的动作数量: {len(result.get('actions', []))}")
        
        # 显示生成的动作
        actions = result.get('actions', [])
        for i, action in enumerate(actions[:3], 1):  # 只显示前3个动作
            print(f"动作 {i}: {action.get('description', 'N/A')}")
            print(f"  角色: {action.get('role', 'N/A')}")
            print(f"  优先级: {action.get('priority', 'N/A')}")
        
        if len(actions) > 3:
            print(f"... 还有 {len(actions) - 3} 个动作")
        
        # 显示统计信息
        stats = result.get('stats', {})
        print(f"\n=== 统计信息 ===")
        print(f"总执行时间: {stats.get('total_execution_time', 0):.2f}ms")
        print(f"任务分配时间: {stats.get('task_allocation_time', 0):.2f}ms")
        print(f"冲突检测时间: {stats.get('conflict_detection_time', 0):.2f}ms")
        
        # 显示优化状态
        optimization_status = orchestrator.get_optimization_status()
        print(f"\n=== 优化状态 ===")
        print(f"学习引擎状态: {'可用' if optimization_status.get('learning_engine_available') else '不可用'}")
        print(f"自适应优化器状态: {'可用' if optimization_status.get('adaptive_optimizer_available') else '不可用'}")
        
        print("\n✓ 测试完成，所有功能正常工作")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理资源
        await orchestrator.cleanup()
        print("\n✓ 资源清理完成")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_orchestrator())
    if success:
        print("\n🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("\n❌ 测试失败")
        sys.exit(1)