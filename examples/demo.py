#!/usr/bin/env python3
"""
Solo MCP 基础演示

这个示例展示了如何使用 Solo MCP 进行基本的多角色协作开发。
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from solo_mcp.config import SoloConfig
from solo_mcp.tools.orchestrator import OrchestratorTool
from solo_mcp.tools.memory import MemoryTool
from solo_mcp.tools.context import ContextTool


async def basic_demo():
    """基础演示：展示 Solo MCP 的核心功能"""
    print("🚀 Solo MCP 基础演示")
    print("=" * 50)
    
    # 1. 初始化配置
    print("\n📋 1. 初始化配置...")
    config = SoloConfig.load(root=project_root)
    print(f"✅ 配置加载完成，项目根目录: {config.root}")
    
    # 2. 创建工具实例
    print("\n🛠️ 2. 创建工具实例...")
    orchestrator = OrchestratorTool(config)
    memory_tool = MemoryTool(config)
    context_tool = ContextTool(config)
    
    print("✅ 工具实例创建完成")
    
    # 3. 存储一些示例记忆
    print("\n🧠 3. 存储项目记忆...")
    
    memories = [
        {
            "content": "项目使用 Python 3.11+ 开发，基于 MCP 协议",
            "memory_type": "technical",
            "context": {"category": "architecture", "priority": "high"}
        },
        {
            "content": "采用多角色协作模式：产品经理、架构师、开发者、测试工程师",
            "memory_type": "process",
            "context": {"category": "workflow", "priority": "high"}
        },
        {
            "content": "使用智能记忆系统进行知识管理和上下文感知",
            "memory_type": "feature",
            "context": {"category": "capability", "priority": "medium"}
        }
    ]
    
    for i, memory in enumerate(memories, 1):
        memory_id = memory_tool.store(**memory)
        print(f"  📝 记忆 {i} 已存储 (ID: {memory_id[:8]}...)")
    
    # 4. 检索相关记忆
    print("\n🔍 4. 检索相关记忆...")
    
    queries = [
        "Python 开发",
        "角色协作",
        "记忆系统"
    ]
    
    for query in queries:
        results = memory_tool.load(query=query, memory_type="technical")
        print(f"  🔎 查询 '{query}': 找到 {len(results)} 条相关记忆")
    
    # 5. 收集项目上下文
    print("\n📊 5. 收集项目上下文...")
    
    try:
        # 构建项目索引
        context_tool.index.build()
        print("  ✅ 项目索引构建完成")
        
        # 搜索相关文件
        search_results = context_tool.search("config memory tool")
        print(f"  🔍 搜索结果: 找到 {len(search_results)} 个相关文件")
        
        for result in search_results[:3]:  # 显示前3个结果
            print(f"    📄 {result['file']} (相关度: {result['score']:.2f})")
            
    except Exception as e:
        print(f"  ⚠️ 上下文收集遇到问题: {e}")
    
    # 6. 模拟任务编排
    print("\n🎭 6. 模拟任务编排...")
    
    try:
        # 运行一轮协作
        result = orchestrator.run_round(
            goal="优化项目的记忆管理系统",
            stack="Python, MCP, 智能记忆"
        )
        
        print("  ✅ 任务编排完成")
        print(f"  📋 生成的任务数量: {len(result.get('tasks', []))}")
        print(f"  👥 参与的角色: {', '.join(result.get('roles', []))}")
        
        # 显示部分任务
        tasks = result.get('tasks', [])
        for i, task in enumerate(tasks[:3], 1):
            print(f"    {i}. {task.get('title', 'Unknown Task')}")
            
    except Exception as e:
        print(f"  ⚠️ 任务编排遇到问题: {e}")
    
    print("\n🎉 演示完成！")
    print("\n💡 提示:")
    print("  - 查看 README.md 了解更多功能")
    print("  - 运行测试: python -m pytest tests/")
    print("  - 查看 examples/ 目录获取更多示例")


def main():
    """主函数"""
    try:
        asyncio.run(basic_demo())
    except KeyboardInterrupt:
        print("\n\n👋 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()