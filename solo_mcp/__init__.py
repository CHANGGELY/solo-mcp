"""
Solo MCP - 智能代理协作平台

基于 MCP 协议的多角色任务编排系统，为 AI 代理提供记忆、索引、协作等核心能力。
"""

__version__ = "0.1.1"
__all__ = ["SoloConfig", "SoloServer", "main"]

from .config import SoloConfig
from .server import SoloServer


def main():
    """solo-mcp 命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="Solo MCP - 智能代理协作平台")
    parser.add_argument("--version", action="version", version=f"Solo MCP {__version__}")
    parser.add_argument("--server", action="store_true", help="启动 MCP 服务器")
    parser.add_argument("--config", type=str, help="配置文件路径")

    args = parser.parse_args()

    if args.server:
        # 启动 MCP 服务器
        from .mcp_server import run_server

        run_server()
    else:
        print(f"Solo MCP v{__version__}")
        print("使用 --server 启动 MCP 服务器")
        print("使用 --help 查看更多选项")