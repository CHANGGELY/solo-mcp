#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 Todo 功能的完整性
"""

from solo_mcp.tools.todo import TodoTool
import json

def test_todo_functionality():
    """测试 Todo 功能"""
    print("=== 测试 Todo 功能 ===")
    
    # 初始化 TodoTool
    todo = TodoTool()
    
    # 测试创建任务
    print("\n1. 创建任务测试")
    task1_id = todo.create_task(
        title="完成项目文档",
        description="编写项目的 README 和 API 文档",
        priority="high",
        tags=["文档", "重要"]
    )
    print(f"创建任务1: {task1_id}")
    
    task2_id = todo.create_task(
        title="代码重构",
        description="重构核心模块代码",
        priority="medium",
        tags=["代码", "重构"]
    )
    print(f"创建任务2: {task2_id}")
    
    # 测试列出任务
    print("\n2. 列出所有任务")
    tasks = todo.list_tasks()
    print(f"总任务数: {len(tasks)}")
    for task in tasks:
        print(f"- {task['title']} ({task['status']}) - 优先级: {task['priority']}")
    
    # 测试更新任务
    print("\n3. 更新任务状态")
    todo.update_task(task1_id, status="in_progress")
    updated_task = todo.get_task(task1_id)
    print(f"任务1状态更新为: {updated_task['status']}")
    
    # 测试添加依赖
    print("\n4. 添加任务依赖")
    todo.add_dependency(task2_id, task1_id)
    task2 = todo.get_task(task2_id)
    print(f"任务2的依赖: {task2['dependencies']}")
    
    # 测试搜索
    print("\n5. 搜索任务")
    search_results = todo.search_tasks("文档")
    print(f"搜索'文档'的结果: {len(search_results)}个任务")
    
    # 测试统计
    print("\n6. 获取统计信息")
    stats = todo.get_statistics()
    print(f"统计信息: {json.dumps(stats, indent=2, ensure_ascii=False)}")
    
    # 测试添加备注
    print("\n7. 添加任务备注")
    todo.add_note(task1_id, "已开始编写 README 文件")
    task1 = todo.get_task(task1_id)
    print(f"任务1的备注: {task1['notes']}")
    
    print("\n=== Todo 功能测试完成 ===")
    return True

if __name__ == "__main__":
    try:
        test_todo_functionality()
        print("\n✅ 所有测试通过！")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()