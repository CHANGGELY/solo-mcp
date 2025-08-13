"""Solo MCP - 智能代理协作平台

基于 MCP 协议的多角色任务编排系统，支持：
- 多代理协作与任务编排
- 智能记忆与上下文管理
- 灵活的工具集成
- 分布式架构支持
"""

__version__ = "0.1.1"
__author__ = "Solo MCP Team"
__email__ = "contact@solo-mcp.dev"
__license__ = "Apache-2.0"

from .config import SoloConfig
from .mcp_server import SoloServer

# 暴露 main 函数供 console_scripts 使用
def main():
    """Solo MCP 命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Solo MCP - 智能代理协作平台")
    parser.add_argument(
        "--version", action="version", version=f"Solo MCP {__version__}"
    )
    parser.add_argument(
        "--server", action="store_true", help="启动 MCP 服务器"
    )
    parser.add_argument(
        "--config", type=str, default="solo_mcp_config.toml", 
        help="配置文件路径"
    )
    
    args = parser.parse_args()
    
    if args.server:
        # 启动 MCP 服务器
        from .mcp_server import run_server
        run_server()
    else:
        # 如果没有指定其他选项，显示帮助信息
        parser.print_help()

__all__ = ["SoloConfig", "SoloServer", "main", "__version__"]