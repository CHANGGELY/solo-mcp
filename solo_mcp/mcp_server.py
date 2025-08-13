"""
Solo MCP FastMCP Server - Full MCP integration with vector search support

Features:
- Integrates all Solo MCP tools as MCP-compatible endpoints
- Optional vector search with sentence-transformers (configurable)
- Caching and download management for large models
- Full FastMCP server compatible with Claude Desktop and MCP Inspector
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, Tool, Resource, Prompt

# 优先使用绝对导入；若运行环境未将项目根加入 sys.path，则回退注入后再导入
try:
    from solo_mcp.config import SoloConfig
    from solo_mcp.server import SoloServer
    from solo_mcp.tools.todo import TodoTool
except ModuleNotFoundError:
    root_dir = Path(__file__).resolve().parents[1]
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))
    from solo_mcp.config import SoloConfig
    from solo_mcp.server import SoloServer
    from solo_mcp.tools.todo import TodoTool


# 在配置日志前，确保日志目录存在（避免 FileNotFoundError）
Path(".ai_memory").mkdir(exist_ok=True)

# 配置日志，避免 stdout 输出（STDIO 传输必需）
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(str(Path(".ai_memory") / "mcp_server.log")),
        logging.StreamHandler(),  # stderr
    ],
)
logger = logging.getLogger(__name__)

# 创建 FastMCP 实例
mcp = FastMCP("Solo MCP Server", dependencies=["sentence-transformers", "requests"])


def get_solo_server():
    """获取 SoloServer 实例，使用项目根目录"""
    config = SoloConfig.load(enable_vector=True)  # 启用向量搜索
    return SoloServer(config)


# =============================================================================
# TOOLS - 将 SoloServer 的方法包装为 MCP 工具
# =============================================================================


@mcp.tool()
async def fs_read(path: str) -> str:
    """
    读取文件内容

    Args:
        path: 要读取的文件路径（相对于项目根目录）

    Returns:
        文件内容
    """
    try:
        server = get_solo_server()
        result = server.fs.read(path)
        return f"File: {result['path']}\n\nContent:\n{result['content']}"
    except Exception as e:
        return f"Error reading file: {str(e)}"


@mcp.tool()
async def fs_write(path: str, content: str) -> str:
    """
    写入文件内容（支持软删除备份）

    Args:
        path: 要写入的文件路径
        content: 文件内容

    Returns:
        写入结果
    """
    try:
        server = get_solo_server()
        result = server.fs.safe_write(path, content)
        return f"Successfully wrote {result['bytes']} bytes to {result['path']}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


@mcp.tool()
async def fs_list(path: Optional[str] = None) -> str:
    """
    列出目录内容

    Args:
        path: 目录路径（可选，默认为项目根目录）

    Returns:
        目录内容列表
    """
    try:
        server = get_solo_server()
        result = server.fs.list_dir(path)
        items = "\n".join(
            [f"{item['type'].upper()}: {item['name']}" for item in result["items"]]
        )
        return f"Directory: {result['path']}\n\nContents:\n{items}"
    except Exception as e:
        return f"Error listing directory: {str(e)}"


@mcp.tool()
async def memory_store(key: str, data: str) -> str:
    """
    存储数据到内存/持久化存储

    Args:
        key: 存储键名
        data: 要存储的数据（JSON 字符串）

    Returns:
        存储结果
    """
    try:
        server = get_solo_server()
        data_obj = json.loads(data) if isinstance(data, str) else data
        result = await server.memory.store(key, data_obj)
        return f"Successfully stored data for key '{key}' at {result['path']}"
    except Exception as e:
        return f"Error storing memory: {str(e)}"


@mcp.tool()
async def memory_load(key: str) -> str:
    """
    从内存/持久化存储加载数据

    Args:
        key: 存储键名

    Returns:
        存储的数据
    """
    try:
        server = get_solo_server()
        result = await server.memory.load(key)
        if result["data"] is None:
            return f"No data found for key '{key}'"
        return f"Data for key '{key}':\n{json.dumps(result['data'], ensure_ascii=False, indent=2)}"
    except Exception as e:
        return f"Error loading memory: {str(e)}"


@mcp.tool()
async def memory_summarize(key: str) -> str:
    """
    生成内存数据的摘要

    Args:
        key: 存储键名

    Returns:
        数据摘要
    """
    try:
        server = get_solo_server()
        result = await server.memory.summarize(key)
        return f"Summary for key '{key}':\n{result['summary']}"
    except Exception as e:
        return f"Error summarizing memory: {str(e)}"


@mcp.tool()
async def index_build() -> str:
    """
    构建项目文件的搜索索引（BM25 + 可选向量搜索）

    Returns:
        索引构建结果
    """
    try:
        server = get_solo_server()
        result = await server.index.build()
        return f"Successfully built index with {result['docs']} documents"
    except Exception as e:
        return f"Error building index: {str(e)}"


@mcp.tool()
async def index_search(query: str, k: int = 10) -> str:
    """
    搜索项目文件内容

    Args:
        query: 搜索查询
        k: 返回结果数量

    Returns:
        搜索结果
    """
    try:
        server = get_solo_server()
        result = await server.index.search(query, k=k)

        if not result.get("hits"):
            return f"No results found for query: '{query}'"

        hits_text = []
        for i, hit in enumerate(result["hits"], 1):
            hits_text.append(f"{i}. {hit['path']} (score: {hit.get('score', 0):.3f})")

        return (
            f"Search results for '{query}' ({len(result['hits'])} hits):\n\n"
            + "\n".join(hits_text)
        )
    except Exception as e:
        return f"Error searching index: {str(e)}"


@mcp.tool()
async def context_collect(query: str, limit: int = 8000) -> str:
    """
    收集相关上下文内容（基于搜索结果）

    Args:
        query: 上下文查询
        limit: 内容字符限制

    Returns:
        收集的上下文内容和摘要
    """
    try:
        server = get_solo_server()
        result = await server.context.collect(query, limit=limit)

        summary = f"Context Summary:\n{result['summary']}\n\n"
        content = f"Full Content ({result['tokens']} tokens):\n{result['content']}"

        return summary + content
    except Exception as e:
        return f"Error collecting context: {str(e)}"


@mcp.tool()
async def roles_evaluate(goal: str, stack: list[str] | None = None) -> str:
    """
    评估项目角色和职责分配

    Args:
        goal: 项目目标描述
        stack: 技术栈列表（如 ["python", "node"]）

    Returns:
        角色评估结果
    """
    try:
        server = get_solo_server()
        result = server.roles.evaluate(goal, stack or ["python"])

        roles_text = []
        for role in result["roles"]:
            responsibilities = ", ".join(role["responsibilities"])
            roles_text.append(f"• {role['name']}: {responsibilities}")

        return f"Goal: {result['goal']}\n\nRecommended Roles:\n" + "\n".join(roles_text)
    except Exception as e:
        return f"Error evaluating roles: {str(e)}"


@mcp.tool()
async def orchestrator_run_round(
    mode: str = "collab", state: Optional[str] = None
) -> str:
    """
    运行协作编排轮次

    Args:
        mode: 协作模式（默认 "collab"）
        state: 当前状态（JSON 字符串，可选）

    Returns:
        编排轮次结果
    """
    try:
        server = get_solo_server()
        state_obj = json.loads(state) if state else {}
        result = await server.orchestrator.run_round(mode, state_obj)

        actions_text = []
        for action in result["actions"]:
            actions_text.append(f"• {action['role']}: {action['action']}")

        conflicts_text = []
        for conflict in result.get("conflicts", []):
            conflicts_text.append(
                f"• Conflict between {', '.join(conflict['between'])}: {conflict['reason']}"
            )

        output = f"Orchestration Round Results:\n\nActions:\n" + "\n".join(actions_text)
        if conflicts_text:
            output += f"\n\nConflicts:\n" + "\n".join(conflicts_text)

        return output
    except Exception as e:
        return f"Error running orchestration: {str(e)}"


@mcp.tool()
async def proc_exec(command: str) -> str:
    """
    执行 PowerShell 命令

    Args:
        command: 要执行的 PowerShell 命令

    Returns:
        命令执行结果
    """
    try:
        server = get_solo_server()
        result = await server.proc.exec(command)

        status = "SUCCESS" if result["ok"] else "FAILED"
        return f"Command: {command}\nStatus: {status} (exit code: {result['code']})\n\nOutput:\n{result['output']}"
    except Exception as e:
        return f"Error executing command: {str(e)}"


@mcp.tool()
async def credits_get() -> str:
    """
    获取当前积分余额

    Returns:
        积分余额
    """
    try:
        server = get_solo_server()
        balance = server.credits.get_balance()
        return f"Current credits balance: {balance}"
    except Exception as e:
        return f"Error getting credits: {str(e)}"


@mcp.tool()
async def credits_add(amount: int) -> str:
    """
    添加积分

    Args:
        amount: 要添加的积分数量

    Returns:
        添加结果
    """
    try:
        server = get_solo_server()
        new_balance = server.credits.add(amount)
        return f"Added {amount} credits. New balance: {new_balance}"
    except Exception as e:
        return f"Error adding credits: {str(e)}"


# =============================================================================
# TODO TOOLS - 任务管理功能
# =============================================================================


def get_todo_tool():
    """获取 TodoTool 实例"""
    return TodoTool()


@mcp.tool()
async def todo_create(title: str, description: str = "", priority: str = "medium", 
                     due_date: Optional[str] = None, tags: Optional[str] = None) -> str:
    """
    创建新的待办任务

    Args:
        title: 任务标题
        description: 任务描述
        priority: 任务优先级 (low, medium, high, urgent)
        due_date: 截止日期 (ISO格式)
        tags: 标签列表 (逗号分隔)

    Returns:
        创建结果
    """
    try:
        todo = get_todo_tool()
        tag_list = [tag.strip() for tag in tags.split(",")] if tags else None
        task_id = todo.create_task(title, description, priority, due_date, tag_list)
        return f"Successfully created task '{title}' with ID: {task_id}"
    except Exception as e:
        return f"Error creating task: {str(e)}"


@mcp.tool()
async def todo_list(status: Optional[str] = None, priority: Optional[str] = None, 
                   tag: Optional[str] = None) -> str:
    """
    列出待办任务

    Args:
        status: 按状态过滤 (pending, in_progress, completed, cancelled)
        priority: 按优先级过滤 (low, medium, high, urgent)
        tag: 按标签过滤

    Returns:
        任务列表
    """
    try:
        todo = get_todo_tool()
        tasks = todo.list_tasks(status, priority, tag)
        
        if not tasks:
            return "No tasks found matching the criteria."
        
        task_lines = []
        for task in tasks:
            tags_str = ", ".join(task['tags']) if task['tags'] else "None"
            due_str = task['due_date'] if task['due_date'] else "No due date"
            task_lines.append(
                f"• [{task['status']}] {task['title']} (Priority: {task['priority']})\n"
                f"  ID: {task['id']}\n"
                f"  Description: {task['description'] or 'No description'}\n"
                f"  Tags: {tags_str}\n"
                f"  Due: {due_str}\n"
                f"  Created: {task['created_at']}\n"
            )
        
        return f"Found {len(tasks)} task(s):\n\n" + "\n".join(task_lines)
    except Exception as e:
        return f"Error listing tasks: {str(e)}"


@mcp.tool()
async def todo_get(task_id: str) -> str:
    """
    获取特定任务详情

    Args:
        task_id: 任务ID

    Returns:
        任务详情
    """
    try:
        todo = get_todo_tool()
        task = todo.get_task(task_id)
        
        if not task:
            return f"Task with ID '{task_id}' not found."
        
        tags_str = ", ".join(task['tags']) if task['tags'] else "None"
        deps_str = ", ".join(task['dependencies']) if task['dependencies'] else "None"
        notes_str = "\n  ".join(task['notes']) if task['notes'] else "None"
        
        return f"""Task Details:
ID: {task['id']}
Title: {task['title']}
Description: {task['description'] or 'No description'}
Status: {task['status']}
Priority: {task['priority']}
Tags: {tags_str}
Dependencies: {deps_str}
Due Date: {task['due_date'] or 'No due date'}
Created: {task['created_at']}
Updated: {task['updated_at']}

Notes:
  {notes_str}"""
    except Exception as e:
        return f"Error getting task: {str(e)}"


@mcp.tool()
async def todo_update(task_id: str, title: Optional[str] = None, 
                     description: Optional[str] = None, status: Optional[str] = None,
                     priority: Optional[str] = None, due_date: Optional[str] = None,
                     tags: Optional[str] = None) -> str:
    """
    更新任务

    Args:
        task_id: 任务ID
        title: 新标题
        description: 新描述
        status: 新状态 (pending, in_progress, completed, cancelled)
        priority: 新优先级 (low, medium, high, urgent)
        due_date: 新截止日期
        tags: 新标签列表 (逗号分隔)

    Returns:
        更新结果
    """
    try:
        todo = get_todo_tool()
        
        update_data = {}
        if title is not None:
            update_data['title'] = title
        if description is not None:
            update_data['description'] = description
        if status is not None:
            update_data['status'] = status
        if priority is not None:
            update_data['priority'] = priority
        if due_date is not None:
            update_data['due_date'] = due_date
        if tags is not None:
            update_data['tags'] = [tag.strip() for tag in tags.split(",")] if tags else []
        
        if not update_data:
            return "No fields specified for update."
        
        success = todo.update_task(task_id, **update_data)
        if success:
            return f"Successfully updated task '{task_id}'."
        else:
            return f"Task with ID '{task_id}' not found."
    except Exception as e:
        return f"Error updating task: {str(e)}"


@mcp.tool()
async def todo_delete(task_id: str) -> str:
    """
    删除任务

    Args:
        task_id: 任务ID

    Returns:
        删除结果
    """
    try:
        todo = get_todo_tool()
        success = todo.delete_task(task_id)
        if success:
            return f"Successfully deleted task '{task_id}'."
        else:
            return f"Task with ID '{task_id}' not found."
    except Exception as e:
        return f"Error deleting task: {str(e)}"


@mcp.tool()
async def todo_search(query: str) -> str:
    """
    搜索任务

    Args:
        query: 搜索关键词

    Returns:
        搜索结果
    """
    try:
        todo = get_todo_tool()
        tasks = todo.search_tasks(query)
        
        if not tasks:
            return f"No tasks found matching '{query}'."
        
        task_lines = []
        for task in tasks:
            task_lines.append(
                f"• [{task['status']}] {task['title']} (Priority: {task['priority']})\n"
                f"  ID: {task['id']}\n"
                f"  Description: {task['description'] or 'No description'}\n"
            )
        
        return f"Found {len(tasks)} task(s) matching '{query}':\n\n" + "\n".join(task_lines)
    except Exception as e:
        return f"Error searching tasks: {str(e)}"


@mcp.tool()
async def todo_stats() -> str:
    """
    获取任务统计信息

    Returns:
        统计信息
    """
    try:
        todo = get_todo_tool()
        stats = todo.get_statistics()
        
        status_lines = []
        for status, count in stats['status_breakdown'].items():
            status_lines.append(f"  {status}: {count}")
        
        priority_lines = []
        for priority, count in stats['priority_breakdown'].items():
            priority_lines.append(f"  {priority}: {count}")
        
        return f"""Todo Statistics:
Total Tasks: {stats['total_tasks']}

By Status:
{chr(10).join(status_lines)}

By Priority:
{chr(10).join(priority_lines)}"""
    except Exception as e:
        return f"Error getting statistics: {str(e)}"


@mcp.tool()
async def todo_add_note(task_id: str, note: str) -> str:
    """
    为任务添加备注

    Args:
        task_id: 任务ID
        note: 备注内容

    Returns:
        添加结果
    """
    try:
        todo = get_todo_tool()
        success = todo.add_note(task_id, note)
        if success:
            return f"Successfully added note to task '{task_id}'."
        else:
            return f"Task with ID '{task_id}' not found."
    except Exception as e:
        return f"Error adding note: {str(e)}"


@mcp.tool()
async def todo_add_dependency(task_id: str, dependency_id: str) -> str:
    """
    为任务添加依赖关系

    Args:
        task_id: 任务ID
        dependency_id: 依赖任务ID

    Returns:
        添加结果
    """
    try:
        todo = get_todo_tool()
        success = todo.add_dependency(task_id, dependency_id)
        if success:
            return f"Successfully added dependency '{dependency_id}' to task '{task_id}'."
        else:
            return f"Failed to add dependency. Check that both tasks exist."
    except Exception as e:
        return f"Error adding dependency: {str(e)}"


# =============================================================================
# RESOURCES - 暴露项目信息为 MCP 资源
# =============================================================================


@mcp.resource("project://config")
async def get_project_config() -> str:
    """获取项目配置信息"""
    try:
        config = SoloConfig.load()
        return f"""Project Configuration:
Root: {config.root}
AI Memory: {config.ai_memory_dir}
Vector Search: {config.enable_vector_search}
Model: {config.model_name}
Max Context Tokens: {config.max_context_tokens}
Credits Path: {config.credits_path}
"""
    except Exception as e:
        return f"Error getting config: {str(e)}"


@mcp.resource("project://structure")
async def get_project_structure() -> str:
    """获取项目结构概览"""
    try:
        server = get_solo_server()
        result = server.fs.list_dir(None)

        structure = ["Project Structure:"]
        for item in result["items"]:
            structure.append(f"  {item['type'].upper()}: {item['name']}")

        return "\n".join(structure)
    except Exception as e:
        return f"Error getting project structure: {str(e)}"


# =============================================================================
# PROMPTS - 预定义提示模板
# =============================================================================


@mcp.prompt()
async def code_review_prompt(file_path: str) -> list:
    """代码审查提示模板"""
    try:
        server = get_solo_server()
        file_content = server.fs.read(file_path)

        prompt_text = f"""Please review this code file for:

1. Code quality and best practices
2. Potential bugs or issues
3. Performance optimizations
4. Security considerations
5. Documentation improvements

File: {file_content['path']}

```
{file_content['content']}
```

Please provide detailed feedback and suggestions."""

        return [TextContent(type="text", text=prompt_text)]
    except Exception as e:
        return [
            TextContent(type="text", text=f"Error loading file for review: {str(e)}")
        ]


@mcp.prompt()
async def project_planning_prompt(goal: str, stack: str = "python") -> list:
    """项目规划提示模板"""
    try:
        server = get_solo_server()
        roles_result = server.roles.evaluate(goal, [stack])

        roles_text = []
        for role in roles_result["roles"]:
            responsibilities = ", ".join(role["responsibilities"])
            roles_text.append(f"• {role['name']}: {responsibilities}")

        prompt_text = f"""Project Planning Session

Goal: {goal}
Technology Stack: {stack}

Based on the goal and stack, here are the recommended roles and responsibilities:

{chr(10).join(roles_text)}

Please create a detailed project plan including:
1. Project phases and milestones
2. Task breakdown for each role
3. Dependencies and critical path
4. Resource requirements
5. Risk assessment and mitigation strategies

Consider the multi-role collaboration approach for optimal results."""

        return [TextContent(type="text", text=prompt_text)]
    except Exception as e:
        return [
            TextContent(type="text", text=f"Error generating planning prompt: {str(e)}")
        ]


# =============================================================================
# SERVER STARTUP
# =============================================================================


def run_server():
    """启动 MCP 服务器"""
    logger.info("Starting Solo MCP Server with FastMCP")

    # 确保 .ai_memory 目录存在
    Path(".ai_memory").mkdir(exist_ok=True)

    # 运行服务器（STDIO transport，兼容 Claude Desktop）
    mcp.run(transport="stdio")


if __name__ == "__main__":
    run_server()
