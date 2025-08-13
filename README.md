# Solo MCP - 智能多角色协作平台

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

一个基于 Model Context Protocol (MCP) 的智能多角色协作系统，通过模拟不同专业角色的协作来提升项目开发效率。Solo MCP 让单人开发者能够获得团队协作的智慧，实现更高质量的软件开发。

## ✨ 核心特性

### 🎭 智能角色系统
- **多角色模拟**: 智能模拟产品经理、架构师、开发者、测试工程师等专业角色
- **动态角色分配**: 根据任务类型自动选择最适合的角色组合
- **角色协作**: 不同角色间的智能对话和决策协商

### 🧠 先进记忆管理
- **持久化存储**: 项目知识的长期记忆和快速检索
- **上下文感知**: 基于当前任务智能推荐相关历史信息
- **学习能力**: 从项目历史中学习最佳实践和常见模式

### 🔄 智能任务编排
- **自动任务分解**: 将复杂项目分解为可管理的子任务
- **冲突检测**: 识别和解决任务间的潜在冲突
- **优先级管理**: 基于项目目标智能排序任务优先级

### 📊 全面上下文分析
- **代码理解**: 深度分析项目结构、依赖关系和代码质量
- **文档解析**: 自动提取和整理项目文档信息
- **环境感知**: 识别开发环境、工具链和配置

### 🚀 标准化集成
- **MCP 协议**: 基于 Model Context Protocol 标准，确保兼容性
- **插件架构**: 支持自定义工具和扩展
- **API 友好**: 提供完整的 REST API 和 Python SDK

## 🚀 快速开始

### 环境要求

- Python 3.11+
- 8GB+ RAM (推荐)
- 支持的操作系统: Windows, macOS, Linux

### 安装

```bash
# 克隆项目
git clone https://github.com/your-username/solo-mcp.git
cd solo-mcp

# 创建虚拟环境 (推荐使用 Python 3.11)
python -m venv venv311

# 激活虚拟环境
# Windows
venv311\Scripts\activate
# macOS/Linux
source venv311/bin/activate

# 升级 pip
python -m pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
# 安装交互式反馈增强 MCP
pip install mcp-feedback-enhanced

# 验证安装
python -m pytest tests/test_basic.py
```

### 基本使用

```bash
# 启动 Solo MCP 服务
python -m solo_mcp

# 或者直接运行主模块
python solo_mcp/main.py

# 运行交互式示例
python examples/demo.py
```

## 📖 使用示例

### 1. 角色规划示例

```python
from solo_mcp.tools.roles import RolesTool

# 创建角色工具
roles_tool = RolesTool()

# 评估项目需要的角色
result = roles_tool.evaluate(
    goal="开发一个电商网站",
    stack="Python, FastAPI, React, PostgreSQL"
)

print(result)  # 输出推荐的角色列表
```

### 2. 任务分配示例

```python
from solo_mcp.config import SoloConfig
from solo_mcp.tools.orchestrator import OrchestratorTool

# 加载配置
config = SoloConfig.load()

# 创建编排工具
orchestrator = OrchestratorTool(config)

# 运行一轮协作
result = orchestrator.run_round(
    goal="实现用户认证功能",
    stack="Python, FastAPI, JWT"
)

print(result)  # 输出任务分配和执行结果
```

### 3. 记忆管理示例

```python
from solo_mcp.config import SoloConfig
from solo_mcp.tools.memory import MemoryTool

# 加载配置
config = SoloConfig.load()

# 创建记忆工具
memory_tool = MemoryTool(config)

# 存储项目信息
memory_id = memory_tool.store(
    content="用户认证采用JWT token机制",
    memory_type="technical",
    context={"module": "authentication", "priority": "high"}
)

# 检索相关信息
result = memory_tool.load(
    query="JWT认证",
    memory_type="technical"
)

print(f"找到 {len(result)} 条相关记忆")
```

## 🏗️ 项目架构

```
solo_mcp/
├── tools/                  # 核心工具模块
│   ├── roles.py           # 角色规划与管理
│   ├── orchestrator.py    # 多角色任务编排
│   ├── memory.py          # 智能记忆管理
│   ├── context.py         # 上下文收集与处理
│   ├── learning.py        # 学习引擎
│   ├── adaptive.py        # 自适应优化器
│   └── __init__.py
├── config.py              # 配置管理
├── server.py              # MCP 服务器
├── main.py                # 主入口文件
└── __init__.py

tests/                     # 测试文件
├── test_basic.py          # 基础功能测试
├── test_roles.py          # 角色系统测试
├── test_orchestrator.py   # 编排系统测试
├── test_memory.py         # 记忆系统测试
└── test_context.py        # 上下文系统测试

memory/                    # 持久化记忆存储
├── memories/              # 记忆数据文件
├── cache/                 # 缓存文件
└── index/                 # 索引文件

examples/                  # 使用示例
├── demo.py               # 基础演示
├── advanced_usage.py     # 高级用法
└── integration_test.py   # 集成测试

docs/                      # 文档
├── api.md                # API 文档
├── architecture.md       # 架构说明
└── deployment.md         # 部署指南
```

## 🧪 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_roles.py

# 运行测试并显示覆盖率
pytest --cov=solo_mcp
```

## 🔧 配置

项目支持通过环境变量和配置文件进行配置:

### 环境变量配置

```bash
# 设置记忆存储路径
export SOLO_MCP_MEMORY_PATH="./custom_memory"

# 设置日志级别
export SOLO_MCP_LOG_LEVEL="DEBUG"

# 设置缓存大小
export SOLO_MCP_CACHE_SIZE="1000"

# 设置最大记忆数量
export SOLO_MCP_MAX_MEMORIES="10000"

# 设置学习引擎开关
export SOLO_MCP_ENABLE_LEARNING="true"
```

### 配置文件

创建 `config.json` 文件进行详细配置:

```json
{
  "memory": {
    "max_memories": 10000,
    "cache_size": 1000,
    "enable_learning": true,
    "relevance_threshold": 0.3
  },
  "orchestrator": {
    "max_concurrent_tasks": 5,
    "conflict_detection": true,
    "auto_optimization": true
  },
  "roles": {
    "default_roles": ["analyst", "developer", "designer", "tester"],
    "enable_dynamic_roles": true
  }
}
```

#### 集成交互式反馈增强 MCP

在 `config.json` 中新增 `mcpServers` 配置以启用交互式反馈增强 MCP：

```json
  "mcpServers": {
    "mcp-feedback-enhanced": {
      "command": "uvx",
      "args": ["mcp-feedback-enhanced@latest"],
      "timeout": 600,
      "autoApprove": ["interactive_feedback"]
    }
  }
```

> 提示：`autoApprove` 可根据需求调整自动批准的工具列表。

## 🤝 贡献指南

我们欢迎所有形式的贡献！无论是报告 bug、提出新功能建议，还是提交代码改进。

### 开发环境设置

1. **Fork 并克隆仓库**
   ```bash
   git clone https://github.com/your-username/solo-mcp.git
   cd solo-mcp
   ```

2. **设置开发环境**
   ```bash
   # 创建虚拟环境
   python -m venv venv311
   source venv311/bin/activate  # Linux/macOS
   # 或 venv311\Scripts\activate  # Windows
   
   # 安装开发依赖
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # 如果存在
   
   # 安装预提交钩子
   pre-commit install
   ```

3. **运行测试**
   ```bash
   # 运行所有测试
   python -m pytest
   
   # 运行特定测试
   python -m pytest tests/test_basic.py
   
   # 生成覆盖率报告
   python -m pytest --cov=solo_mcp --cov-report=html
   ```

### 贡献流程

1. **创建 Issue**
   - 报告 bug 或提出新功能建议
   - 使用相应的 Issue 模板
   - 提供详细的描述和复现步骤

2. **开发流程**
   ```bash
   # 创建特性分支
   git checkout -b feature/amazing-feature
   
   # 进行开发...
   
   # 运行测试确保代码质量
   python -m pytest
   
   # 提交更改
   git add .
   git commit -m "feat: add amazing feature"
   
   # 推送到你的 fork
   git push origin feature/amazing-feature
   ```

3. **提交 Pull Request**
   - 使用清晰的标题和描述
   - 关联相关的 Issue
   - 确保所有测试通过
   - 请求代码审查

### 代码规范

- **代码风格**: 遵循 PEP 8 标准
- **类型注解**: 使用 Python 类型提示
- **文档字符串**: 使用 Google 风格的 docstring
- **测试**: 新功能必须包含相应的测试
- **提交信息**: 使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式

### 提交信息格式

```
type(scope): description

[optional body]

[optional footer]
```

类型包括：
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式化
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

### 开发规范

- 使用 [Black](https://github.com/psf/black) 进行代码格式化
- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 编码规范
- 为新功能添加相应的测试
- 更新相关文档

### 代码格式化

```bash
# 格式化代码
black solo_mcp/ tests/

# 检查代码风格
black --check solo_mcp/ tests/
```

## 🗺️ 路线图

### 近期目标 (v1.1)
- [ ] 添加更多预定义角色类型
- [ ] 实现记忆系统的向量化搜索
- [ ] 优化任务调度算法
- [ ] 添加性能监控和指标
- [ ] 完善 API 文档

### 中期目标 (v1.5)
- [ ] 实现分布式记忆存储
- [ ] 添加 Web 管理界面
- [ ] 支持插件系统
- [ ] 集成更多 AI 模型
- [ ] 添加实时协作功能

### 长期目标 (v2.0)
- [ ] 支持多语言 SDK
- [ ] 云端部署方案
- [ ] 企业级安全特性
- [ ] 高级分析和报告
- [ ] 自动化 DevOps 集成

## 🐛 问题反馈

如果您发现任何问题或有改进建议，请:

1. 查看 [Issues](https://github.com/your-username/solo-mcp/issues) 是否已有相关问题
2. 如果没有，请创建新的 Issue 并提供详细信息:
   - 问题描述
   - 复现步骤
   - 期望行为
   - 系统环境信息

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [Model Context Protocol](https://github.com/modelcontextprotocol) - 提供了强大的上下文协议基础
- [sentence-transformers](https://github.com/UKPLab/sentence-transformers) - 提供了优秀的文本嵌入能力
- 所有贡献者和使用者的支持

---

**Solo MCP** - 让AI协作开发变得简单而强大 🚀