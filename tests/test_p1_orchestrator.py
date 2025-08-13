#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 P1 阶段：多角色任务分配与冲突检测功能
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from solo_mcp.config import SoloConfig
from solo_mcp.tools.roles import RolesTool
from solo_mcp.tools.memory import MemoryTool
from solo_mcp.tools.orchestrator import OrchestratorTool


async def test_orchestrator_p1():
    """测试 P1 阶段的编排器功能"""
    print("=== 测试 P1 阶段：多角色任务分配与冲突检测 ===")
    
    # 初始化配置和工具
    config = SoloConfig.load(Path.cwd())
    roles_tool = RolesTool(config)
    memory_tool = MemoryTool(config)
    orchestrator = OrchestratorTool(config, roles_tool, memory_tool)
    
    # 测试场景1：Web 前端项目
    print("\n--- 测试场景1：Web 前端项目 ---")
    state1 = {
        "goal": "Build a modern web frontend application with React",
        "stack": ["javascript", "react"],
        "history": []
    }
    
    result1 = await orchestrator.run_round("collab", state1)
    print(f"✅ 角色数量: {len(result1.get('roles_used', []))}")
    print(f"✅ 动作数量: {len(result1.get('actions', []))}")
    print(f"✅ 冲突数量: {len(result1.get('conflicts', []))}")
    print(f"✅ 任务分配: {result1.get('task_allocation', {})}")
    
    # 显示详细信息
    if result1.get('actions'):
        print("\n📋 任务分配详情:")
        for action in result1['actions']:
            role = action['role']
            tasks = action.get('tasks', [])
            print(f"  {role}: {len(tasks)} 个任务")
            for task in tasks:
                print(f"    - {task['name']} (优先级: {task['priority']}, 预估: {task['estimated_time']}分钟)")
    
    if result1.get('conflicts'):
        print("\n⚠️ 检测到的冲突:")
        for conflict in result1['conflicts']:
            print(f"  类型: {conflict['type']}, 严重性: {conflict['severity']}")
            print(f"  原因: {conflict['reason']}")
            print(f"  解决方案: {conflict['resolution']}")
    
    # 测试场景2：全栈 API 项目
    print("\n--- 测试场景2：全栈 API 项目 ---")
    state2 = {
        "goal": "Develop a REST API backend with database integration",
        "stack": ["python", "fastapi"],
        "history": ["conflict detected in previous round"]
    }
    
    result2 = await orchestrator.run_round("collab", state2)
    print(f"✅ 角色数量: {len(result2.get('roles_used', []))}")
    print(f"✅ 动作数量: {len(result2.get('actions', []))}")
    print(f"✅ 冲突数量: {len(result2.get('conflicts', []))}")
    print(f"✅ 任务分配: {result2.get('task_allocation', {})}")
    
    # 测试场景3：数据库设计项目
    print("\n--- 测试场景3：数据库设计项目 ---")
    state3 = {
        "goal": "Design and implement a scalable database schema",
        "stack": ["python", "postgresql"],
        "history": []
    }
    
    result3 = await orchestrator.run_round("collab", state3)
    print(f"✅ 角色数量: {len(result3.get('roles_used', []))}")
    print(f"✅ 动作数量: {len(result3.get('actions', []))}")
    print(f"✅ 冲突数量: {len(result3.get('conflicts', []))}")
    print(f"✅ 任务分配: {result3.get('task_allocation', {})}")
    
    # 验证核心功能
    print("\n=== P1 功能验证 ===")
    
    # 验证1：智能任务分配
    has_task_allocation = all(result.get('task_allocation') for result in [result1, result2, result3])
    print(f"✅ 智能任务分配: {'通过' if has_task_allocation else '失败'}")
    
    # 验证2：冲突检测
    has_conflict_detection = any(result.get('conflicts') for result in [result1, result2, result3])
    print(f"✅ 冲突检测机制: {'通过' if has_conflict_detection else '失败'}")
    
    # 验证3：任务优先级处理
    has_priority_tasks = any(
        any(task.get('priority') for task in action.get('tasks', []))
        for result in [result1, result2, result3]
        for action in result.get('actions', [])
    )
    print(f"✅ 任务优先级处理: {'通过' if has_priority_tasks else '失败'}")
    
    # 验证4：角色能力匹配
    has_role_matching = all(
        len(result.get('actions', [])) > 0 for result in [result1, result2, result3]
    )
    print(f"✅ 角色能力匹配: {'通过' if has_role_matching else '失败'}")
    
    print("\n🎉 P1 阶段测试完成！")
    return True


if __name__ == "__main__":
    asyncio.run(test_orchestrator_p1())