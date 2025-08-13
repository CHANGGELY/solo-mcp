# Solo MCP - Trae Solo 模式的平台

## 项目描述

Solo MCP 是一个智能多角色协作平台，专为 Trae Solo 模式设计。该平台现已支持完整的 To-Do List 任务管理功能，为开发者提供强大的任务编排和协作能力。

## 主要功能

### 🎭 智能角色系统
- 多角色协作框架
- 动态角色分配
- 角色能力评估

### 🧠 先进记忆管理
- 持久化记忆存储
- 智能记忆检索
- 上下文感知记忆

### 📋 完整的 To-Do List 功能
- ✅ 任务创建、更新、删除
- 🏷️ 任务状态管理（待办、进行中、已完成、已取消）
- ⭐ 优先级设置（低、中、高、紧急）
- 🔗 任务依赖关系
- 🏷️ 标签系统
- 📝 任务备注
- 🔍 任务搜索
- 📊 统计信息

### 🎯 智能任务编排
- 自动任务分配
- 依赖关系处理
- 优先级排序
- 冲突检测与解决

### 🔍 全面上下文分析
- 代码上下文收集
- 项目结构分析
- 智能索引构建

## 安装说明

### 使用 pip 安装
```bash
pip install solo-mcp
```

### 从源码安装
```bash
git clone https://github.com/CHANGGELY/solo-mcp.git
cd solo-mcp
pip install -e .
```

## 使用示例

### 启动 MCP 服务器
```bash
solo-mcp-server
```

### To-Do List 功能示例

#### 创建任务
```python
# 通过 MCP 客户端调用
result = await client.call_tool("todo_create", {
    "title": "实现新功能",
    "description": "为项目添加用户认证功能",
    "priority": "high",
    "tags": ["开发", "认证"]
})
```

#### 列出任务
```python
# 获取所有待办任务
tasks = await client.call_tool("todo_list", {
    "status": "pending"
})
```

#### 更新任务状态
```python
# 将任务标记为进行中
result = await client.call_tool("todo_update", {
    "task_id": "task-uuid",
    "status": "in_progress"
})
```

#### 搜索任务
```python
# 搜索包含特定关键词的任务
results = await client.call_tool("todo_search", {
    "query": "认证"
})
```

## 配置说明

### 环境变量
- `SOLO_MCP_DATA_DIR`: 数据存储目录（默认: `.memory`）
- `SOLO_MCP_LOG_LEVEL`: 日志级别（默认: `INFO`）

### 配置文件
项目支持通过 `config.json` 进行详细配置：

```json
{
  "memory": {
    "storage_path": ".memory",
    "max_entries": 1000
  },
  "roles": {
    "default_roles": ["developer", "analyst", "tester"]
  },
  "todo": {
    "data_dir": ".memory",
    "auto_save": true
  }
}
```

## 技术特性

- 🚀 **高性能**: 异步处理，支持并发操作
- 🔒 **数据安全**: 本地存储，保护隐私
- 🔧 **易于集成**: 标准 MCP 协议，兼容各种客户端
- 📱 **跨平台**: 支持 Windows、macOS、Linux
- 🎨 **可扩展**: 模块化设计，易于添加新功能

## 项目架构

```
solo-mcp/
├── solo_mcp/
│   ├── core/           # 核心功能模块
│   ├── tools/          # 工具模块
│   │   ├── todo.py     # To-Do List 功能
│   │   └── orchestrator.py  # 任务编排
│   ├── memory/         # 记忆管理
│   └── mcp_server.py   # MCP 服务器
├── tests/              # 测试文件
└── docs/               # 文档
```

## 贡献指南

我们欢迎社区贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细信息。

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 联系方式

- GitHub: [CHANGGELY/solo-mcp](https://github.com/CHANGGELY/solo-mcp)
- Issues: [GitHub Issues](https://github.com/CHANGGELY/solo-mcp/issues)

---

**Solo MCP** - 让 Trae Solo 模式更加智能和高效！