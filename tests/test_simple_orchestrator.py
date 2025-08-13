#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试 OrchestratorTool 的基本功能
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """测试导入功能"""
    print("=== 测试导入 ===")
    
    try:
        from solo_mcp.tools.orchestrator import (
            Priority, ResourceType, Task, Conflict,
            TaskAllocator, ConflictDetector, OrchestratorTool
        )
        print("✓ 所有类导入成功")
        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False

def test_task_creation():
    """测试任务创建"""
    print("\n=== 测试任务创建 ===")
    
    try:
        from solo_mcp.tools.orchestrator import Task, Priority, ResourceType
        
        task = Task(
            id="test_task",
            name="Test Task",
            description="A test task",
            priority=Priority.HIGH,
            estimated_duration=60,
            required_resources={ResourceType.CPU: 0.5},
            dependencies=[],
            required_roles=["coding"]
        )
        
        print(f"✓ 任务创建成功: {task.name}")
        print(f"  ID: {task.id}")
        print(f"  优先级: {task.priority}")
        print(f"  预计时长: {task.estimated_duration}分钟")
        return True
    except Exception as e:
        print(f"✗ 任务创建失败: {e}")
        return False

def test_task_allocator():
    """测试任务分配器"""
    print("\n=== 测试任务分配器 ===")
    
    try:
        from solo_mcp.tools.orchestrator import TaskAllocator, Task, Priority, ResourceType
        
        config = {'max_rounds': 5}
        allocator = TaskAllocator(config)
        
        tasks = [
            Task(
                id="task1",
                name="Task 1",
                description="First task",
                priority=Priority.HIGH,
                estimated_duration=60,
                required_resources={ResourceType.CPU: 0.3},
                dependencies=[],
                required_roles=["coding"]
            ),
            Task(
                id="task2",
                name="Task 2",
                description="Second task",
                priority=Priority.MEDIUM,
                estimated_duration=30,
                required_resources={ResourceType.MEMORY: 0.2},
                dependencies=["task1"],
                required_roles=["testing"]
            )
        ]
        
        roles = ["developer", "tester", "analyst"]
        allocation = allocator.allocate_tasks(tasks, roles)
        
        print(f"✓ 任务分配成功，分配了 {len(allocation)} 个任务")
        for task_id, role in allocation.items():
            print(f"  {task_id} -> {role}")
        
        return True
    except Exception as e:
        print(f"✗ 任务分配器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_conflict_detector():
    """测试冲突检测器"""
    print("\n=== 测试冲突检测器 ===")
    
    try:
        from solo_mcp.tools.orchestrator import ConflictDetector, Task, Priority, ResourceType
        
        config = {'max_rounds': 5}
        detector = ConflictDetector(config)
        
        tasks = [
            Task(
                id="task1",
                name="Task 1",
                description="First task",
                priority=Priority.HIGH,
                estimated_duration=60,
                required_resources={ResourceType.CPU: 0.8},
                dependencies=[],
                required_roles=["coding"]
            ),
            Task(
                id="task2",
                name="Task 2",
                description="Second task",
                priority=Priority.HIGH,
                estimated_duration=30,
                required_resources={ResourceType.CPU: 0.7},
                dependencies=[],
                required_roles=["coding"]
            )
        ]
        
        # 将分配格式转换为角色->任务列表的映射
        allocation_dict = {"task1": "developer", "task2": "developer"}
        role_allocation = {"developer": [tasks[0], tasks[1]]}
        conflicts = detector.detect_conflicts(tasks, role_allocation)
        
        print(f"✓ 冲突检测成功，发现 {len(conflicts)} 个冲突")
        for conflict in conflicts:
            print(f"  冲突类型: {conflict.type}")
            print(f"  描述: {conflict.description}")
        
        return True
    except Exception as e:
        print(f"✗ 冲突检测器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_orchestrator_creation():
    """测试编排器创建"""
    print("\n=== 测试编排器创建 ===")
    
    try:
        from solo_mcp.tools.orchestrator import OrchestratorTool
        
        config = {
            'max_rounds': 5,
            'timeout': 300,
            'enable_learning': True,
            'enable_optimization': True
        }
        
        orchestrator = OrchestratorTool(config)
        print("✓ OrchestratorTool 创建成功")
        print(f"  可用角色: {orchestrator.roles}")
        
        # 测试优化状态
        status = orchestrator.get_optimization_status()
        print(f"  学习引擎: {'可用' if status.get('learning_engine_available') else '不可用'}")
        print(f"  自适应优化器: {'可用' if status.get('adaptive_optimizer_available') else '不可用'}")
        
        return True
    except Exception as e:
        print(f"✗ 编排器创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始测试 OrchestratorTool 组件...\n")
    
    tests = [
        test_imports,
        test_task_creation,
        test_task_allocator,
        test_conflict_detector,
        test_orchestrator_creation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        else:
            print("\n❌ 测试失败，停止后续测试")
            break
    
    print(f"\n=== 测试结果 ===")
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        return True
    else:
        print("\n❌ 部分测试失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)