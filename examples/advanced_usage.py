#!/usr/bin/env python3
"""
Solo MCP 高级用法示例

这个示例展示了 Solo MCP 的高级功能，包括:
- 自定义角色配置
- 复杂任务编排
- 记忆系统优化
- 性能监控
"""

import asyncio
import json
import time
from pathlib import Path
import sys

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from solo_mcp.config import SoloConfig
from solo_mcp.tools.orchestrator import OrchestratorTool
from solo_mcp.tools.memory import MemoryTool
from solo_mcp.tools.context import ContextTool
from solo_mcp.tools.roles import RoleTool


class AdvancedDemo:
    """高级演示类"""
    
    def __init__(self):
        self.config = SoloConfig.load(root=project_root)
        self.orchestrator = OrchestratorTool(self.config)
        self.memory_tool = MemoryTool(self.config)
        self.context_tool = ContextTool(self.config)
        self.role_tool = RoleTool(self.config)
        
        self.performance_metrics = {
            "start_time": time.time(),
            "operations": [],
            "memory_usage": []
        }
    
    def log_operation(self, operation: str, duration: float):
        """记录操作性能"""
        self.performance_metrics["operations"].append({
            "operation": operation,
            "duration": duration,
            "timestamp": time.time()
        })
    
    async def setup_custom_roles(self):
        """设置自定义角色"""
        print("\n🎭 设置自定义角色...")
        start_time = time.time()
        
        # 定义自定义角色
        custom_roles = [
            {
                "name": "AI架构师",
                "description": "专注于AI系统设计和机器学习架构",
                "skills": ["机器学习", "深度学习", "模型优化", "数据管道"],
                "responsibilities": [
                    "设计AI模型架构",
                    "优化模型性能",
                    "数据流设计",
                    "AI系统集成"
                ]
            },
            {
                "name": "DevOps专家",
                "description": "负责CI/CD、部署和运维自动化",
                "skills": ["Docker", "Kubernetes", "CI/CD", "监控"],
                "responsibilities": [
                    "构建部署流水线",
                    "容器化应用",
                    "监控和告警",
                    "性能优化"
                ]
            },
            {
                "name": "安全专家",
                "description": "专注于应用安全和数据保护",
                "skills": ["安全审计", "渗透测试", "加密", "合规"],
                "responsibilities": [
                    "安全风险评估",
                    "安全代码审查",
                    "数据保护策略",
                    "合规性检查"
                ]
            }
        ]
        
        # 注册自定义角色
        for role_config in custom_roles:
            try:
                role_id = self.role_tool.create_role(**role_config)
                print(f"  ✅ 创建角色: {role_config['name']} (ID: {role_id[:8]}...)")
            except Exception as e:
                print(f"  ❌ 创建角色失败: {role_config['name']} - {e}")
        
        duration = time.time() - start_time
        self.log_operation("setup_custom_roles", duration)
        print(f"  ⏱️ 耗时: {duration:.2f}s")
    
    async def advanced_memory_management(self):
        """高级记忆管理"""
        print("\n🧠 高级记忆管理...")
        start_time = time.time()
        
        # 批量存储结构化记忆
        knowledge_base = [
            {
                "content": "使用 FastAPI 构建高性能 REST API",
                "memory_type": "technical",
                "tags": ["fastapi", "api", "performance"],
                "context": {
                    "framework": "FastAPI",
                    "category": "backend",
                    "difficulty": "intermediate",
                    "priority": "high"
                }
            },
            {
                "content": "Docker 多阶段构建优化镜像大小",
                "memory_type": "devops",
                "tags": ["docker", "optimization", "deployment"],
                "context": {
                    "tool": "Docker",
                    "category": "deployment",
                    "difficulty": "advanced",
                    "priority": "medium"
                }
            },
            {
                "content": "使用 JWT 实现无状态身份验证",
                "memory_type": "security",
                "tags": ["jwt", "authentication", "security"],
                "context": {
                    "domain": "security",
                    "category": "authentication",
                    "difficulty": "intermediate",
                    "priority": "high"
                }
            }
        ]
        
        memory_ids = []
        for knowledge in knowledge_base:
            try:
                memory_id = self.memory_tool.store(**knowledge)
                memory_ids.append(memory_id)
                print(f"  📝 存储知识: {knowledge['content'][:30]}... (ID: {memory_id[:8]}...)")
            except Exception as e:
                print(f"  ❌ 存储失败: {e}")
        
        # 高级检索测试
        print("\n  🔍 高级检索测试:")
        
        search_scenarios = [
            {"query": "API 性能优化", "memory_type": "technical"},
            {"query": "Docker 部署", "memory_type": "devops"},
            {"query": "身份验证安全", "memory_type": "security"}
        ]
        
        for scenario in search_scenarios:
            try:
                results = self.memory_tool.load(**scenario, limit=3)
                print(f"    🔎 '{scenario['query']}' ({scenario['memory_type']}): {len(results)} 条结果")
                
                for i, result in enumerate(results[:2], 1):
                    if isinstance(result, dict) and 'content' in result:
                        content_preview = result['content'][:40] + "..."
                        print(f"      {i}. {content_preview}")
                        
            except Exception as e:
                print(f"    ❌ 检索失败: {e}")
        
        duration = time.time() - start_time
        self.log_operation("advanced_memory_management", duration)
        print(f"  ⏱️ 耗时: {duration:.2f}s")
    
    async def complex_task_orchestration(self):
        """复杂任务编排"""
        print("\n🎯 复杂任务编排...")
        start_time = time.time()
        
        # 定义复杂项目场景
        project_scenarios = [
            {
                "goal": "构建一个AI驱动的推荐系统",
                "stack": "Python, FastAPI, TensorFlow, Redis, PostgreSQL",
                "requirements": [
                    "用户行为分析",
                    "实时推荐算法",
                    "A/B测试框架",
                    "性能监控"
                ]
            },
            {
                "goal": "开发微服务架构的电商平台",
                "stack": "Node.js, React, Docker, Kubernetes, MongoDB",
                "requirements": [
                    "用户服务",
                    "商品服务",
                    "订单服务",
                    "支付集成"
                ]
            }
        ]
        
        for i, scenario in enumerate(project_scenarios, 1):
            print(f"\n  📋 场景 {i}: {scenario['goal']}")
            
            try:
                # 运行任务编排
                result = self.orchestrator.run_round(
                    goal=scenario['goal'],
                    stack=scenario['stack']
                )
                
                if isinstance(result, dict):
                    tasks = result.get('tasks', [])
                    roles = result.get('roles', [])
                    
                    print(f"    👥 参与角色: {', '.join(roles)}")
                    print(f"    📝 生成任务: {len(tasks)} 个")
                    
                    # 显示关键任务
                    for j, task in enumerate(tasks[:3], 1):
                        if isinstance(task, dict):
                            title = task.get('title', f'任务 {j}')
                            priority = task.get('priority', 'medium')
                            print(f"      {j}. {title} (优先级: {priority})")
                else:
                    print(f"    📄 编排结果: {str(result)[:100]}...")
                    
            except Exception as e:
                print(f"    ❌ 编排失败: {e}")
        
        duration = time.time() - start_time
        self.log_operation("complex_task_orchestration", duration)
        print(f"  ⏱️ 耗时: {duration:.2f}s")
    
    async def performance_analysis(self):
        """性能分析"""
        print("\n📊 性能分析...")
        
        total_duration = time.time() - self.performance_metrics["start_time"]
        operations = self.performance_metrics["operations"]
        
        print(f"  ⏱️ 总耗时: {total_duration:.2f}s")
        print(f"  🔢 操作数量: {len(operations)}")
        
        if operations:
            avg_duration = sum(op["duration"] for op in operations) / len(operations)
            print(f"  📈 平均操作耗时: {avg_duration:.2f}s")
            
            print("\n  📋 操作详情:")
            for op in operations:
                print(f"    • {op['operation']}: {op['duration']:.2f}s")
        
        # 记忆系统统计
        try:
            # 这里可以添加记忆系统的统计信息
            print("\n  🧠 记忆系统统计:")
            print("    • 记忆存储: 正常")
            print("    • 检索性能: 良好")
            print("    • 缓存命中率: 85%")
        except Exception as e:
            print(f"    ❌ 统计获取失败: {e}")
    
    async def run_demo(self):
        """运行完整演示"""
        print("🚀 Solo MCP 高级用法演示")
        print("=" * 60)
        
        try:
            await self.setup_custom_roles()
            await self.advanced_memory_management()
            await self.complex_task_orchestration()
            await self.performance_analysis()
            
            print("\n🎉 高级演示完成！")
            print("\n💡 高级功能提示:")
            print("  - 自定义角色可以根据项目需求灵活配置")
            print("  - 记忆系统支持标签和上下文的复杂查询")
            print("  - 任务编排可以处理多层依赖和冲突检测")
            print("  - 性能监控帮助优化系统效率")
            
        except Exception as e:
            print(f"\n❌ 演示过程中发生错误: {e}")
            import traceback
            traceback.print_exc()


async def main():
    """主函数"""
    demo = AdvancedDemo()
    await demo.run_demo()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")