#!/usr/bin/env python3
"""
独立测试 Solo MCP 服务器的 STDIO 传输
无需 MCP Inspector 即可验证基本功能
"""

import sys
import asyncio
import json
from pathlib import Path

# 确保能导入 solo_mcp
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from solo_mcp.mcp_server import run_server


async def test_basic_functionality():
    """基础功能测试（不需要 STDIO 通信）"""
    print("=== Solo MCP 基础功能测试 ===")
    
    try:
        from solo_mcp.config import SoloConfig
        from solo_mcp.server import SoloServer
        
        config = SoloConfig.load(enable_vector=False)  # 禁用向量搜索避免模型下载
        server = SoloServer(config)
        
        print(f"✓ 配置加载成功：根目录 {config.root}")
        print(f"✓ 服务器初始化成功")
        
        # 测试积分功能
        balance = server.credits.get_balance()
        print(f"✓ 积分余额：{balance}")
        
        # 测试文件系统
        fs_result = server.fs.list_dir(None)
        print(f"✓ 文件系统：项目根目录包含 {len(fs_result['items'])} 个项目")
        
        # 测试内存功能
        await server.memory.store("test_key", {"message": "Hello Solo MCP"})
        memory_result = await server.memory.load("test_key")
        print(f"✓ 内存存储：{memory_result['data']['message']}")
        
        print("\n=== 基础功能测试通过 ===")
        return True
        
    except Exception as e:
        print(f"✗ 测试失败：{e}")
        return False


if __name__ == "__main__":
    print("Solo MCP 服务器测试脚本")
    print("1. 基础功能测试")
    print("2. STDIO 服务器启动")
    
    choice = input("\n请选择测试模式 (1/2): ").strip()
    
    if choice == "1":
        success = asyncio.run(test_basic_functionality())
        sys.exit(0 if success else 1)
    elif choice == "2":
        print("\n启动 STDIO MCP 服务器...")
        print("(可使用 Claude Desktop 或其他 MCP 客户端连接)")
        run_server()
    else:
        print("无效选择")
        sys.exit(1)