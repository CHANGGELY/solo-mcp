# 贡献指南

感谢您对 Solo MCP 项目的关注！我们欢迎所有形式的贡献，包括但不限于：

- 🐛 报告 Bug
- 💡 提出新功能建议
- 📝 改进文档
- 🔧 提交代码修复
- ✨ 添加新功能
- 🧪 编写测试

## 🚀 快速开始

### 环境准备

1. **Fork 仓库**
   ```bash
   # 在 GitHub 上 Fork 项目
   # 然后克隆你的 Fork
   git clone https://github.com/your-username/solo-mcp.git
   cd solo-mcp
   ```

2. **设置开发环境**
   ```bash
   # 创建虚拟环境 (推荐 Python 3.11+)
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
   
   # 安装开发依赖 (如果存在)
   pip install -r requirements-dev.txt
   ```

3. **验证环境**
   ```bash
   # 运行测试确保环境正常
   python -m pytest tests/test_basic.py
   
   # 运行演示确保功能正常
   python examples/demo.py
   ```

## 📋 开发流程

### 1. 创建 Issue

在开始开发之前，请先创建一个 Issue 来描述你要解决的问题或添加的功能：

- **Bug 报告**: 使用 Bug 报告模板，提供详细的复现步骤
- **功能请求**: 使用功能请求模板，描述需求和预期行为
- **文档改进**: 描述需要改进的文档部分

### 2. 开发分支

```bash
# 创建并切换到新分支
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/your-bug-fix
# 或
git checkout -b docs/your-doc-improvement
```

分支命名规范：
- `feature/功能名称`: 新功能开发
- `fix/问题描述`: Bug 修复
- `docs/文档内容`: 文档改进
- `refactor/重构内容`: 代码重构
- `test/测试内容`: 测试相关

### 3. 代码开发

#### 代码规范

- **Python 版本**: 使用 Python 3.11+
- **代码风格**: 遵循 PEP 8 标准
- **类型注解**: 使用 Python 类型提示
- **文档字符串**: 使用 Google 风格的 docstring

#### 示例代码风格

```python
from typing import List, Dict, Optional

def process_memories(
    memories: List[Dict[str, str]], 
    filter_type: Optional[str] = None
) -> List[Dict[str, str]]:
    """处理记忆数据。
    
    Args:
        memories: 记忆数据列表
        filter_type: 可选的过滤类型
        
    Returns:
        处理后的记忆数据列表
        
    Raises:
        ValueError: 当输入数据格式不正确时
    """
    if not memories:
        return []
    
    # 实现逻辑...
    return processed_memories
```

#### 测试要求

- **测试覆盖率**: 新功能必须包含相应的测试
- **测试命名**: 使用描述性的测试函数名
- **测试结构**: 遵循 AAA 模式 (Arrange, Act, Assert)

```python
def test_memory_tool_store_and_load():
    """测试记忆工具的存储和加载功能"""
    # Arrange
    config = SoloConfig.load()
    memory_tool = MemoryTool(config)
    test_content = "测试记忆内容"
    
    # Act
    memory_id = memory_tool.store(
        content=test_content,
        memory_type="test"
    )
    results = memory_tool.load(query="测试", memory_type="test")
    
    # Assert
    assert memory_id is not None
    assert len(results) > 0
    assert any(test_content in str(result) for result in results)
```

### 4. 提交代码

#### 提交信息格式

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
type(scope): description

[optional body]

[optional footer]
```

**类型 (type)**:
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式化（不影响功能）
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动
- `perf`: 性能优化

**范围 (scope)** (可选):
- `memory`: 记忆系统
- `orchestrator`: 任务编排
- `roles`: 角色系统
- `context`: 上下文管理
- `config`: 配置管理

**示例**:
```bash
git commit -m "feat(memory): add vector search capability"
git commit -m "fix(orchestrator): resolve task conflict detection issue"
git commit -m "docs: update installation guide"
```

### 5. 运行测试

提交前务必运行完整的测试套件：

```bash
# 运行所有测试
python -m pytest

# 运行特定模块测试
python -m pytest tests/test_memory.py

# 生成覆盖率报告
python -m pytest --cov=solo_mcp --cov-report=html

# 查看覆盖率报告
# Windows
start htmlcov/index.html
# macOS
open htmlcov/index.html
# Linux
xdg-open htmlcov/index.html
```

### 6. 提交 Pull Request

1. **推送分支**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **创建 Pull Request**
   - 在 GitHub 上创建 Pull Request
   - 使用清晰的标题和描述
   - 关联相关的 Issue
   - 添加适当的标签

3. **PR 描述模板**
   ```markdown
   ## 变更描述
   简要描述这个 PR 的变更内容
   
   ## 变更类型
   - [ ] Bug 修复
   - [ ] 新功能
   - [ ] 文档更新
   - [ ] 代码重构
   - [ ] 性能优化
   
   ## 测试
   - [ ] 已添加相应的测试
   - [ ] 所有测试通过
   - [ ] 手动测试通过
   
   ## 关联 Issue
   Closes #issue_number
   
   ## 其他说明
   任何其他需要说明的内容
   ```

## 🔍 代码审查

### 审查标准

- **功能正确性**: 代码是否正确实现了预期功能
- **代码质量**: 是否遵循项目的代码规范
- **测试覆盖**: 是否包含充分的测试
- **文档完整性**: 是否包含必要的文档和注释
- **性能影响**: 是否对系统性能产生负面影响
- **安全性**: 是否存在安全隐患

### 审查流程

1. **自动检查**: CI/CD 流水线会自动运行测试和代码质量检查
2. **人工审查**: 项目维护者会进行代码审查
3. **反馈处理**: 根据审查意见修改代码
4. **最终批准**: 审查通过后合并到主分支

## 📚 开发指南

### 项目结构

```
solo_mcp/
├── tools/              # 核心工具模块
│   ├── memory.py      # 记忆管理
│   ├── orchestrator.py # 任务编排
│   ├── roles.py       # 角色管理
│   └── context.py     # 上下文管理
├── config.py          # 配置管理
├── server.py          # MCP 服务器
└── main.py           # 主入口
```

### 添加新功能

1. **在 `tools/` 目录下创建新模块**
2. **实现核心功能类**
3. **添加配置支持**
4. **编写单元测试**
5. **更新文档**
6. **添加使用示例**

### 修复 Bug

1. **重现问题**
2. **编写失败的测试用例**
3. **修复代码**
4. **确保测试通过**
5. **验证修复效果**

## 🤝 社区

### 沟通渠道

- **GitHub Issues**: 报告问题和功能请求
- **GitHub Discussions**: 技术讨论和问答
- **Pull Requests**: 代码审查和讨论

### 行为准则

我们致力于为所有参与者创造一个友好、包容的环境：

- **尊重他人**: 尊重不同的观点和经验
- **建设性反馈**: 提供有帮助的、建设性的反馈
- **协作精神**: 以协作的态度解决问题
- **学习心态**: 保持开放的学习心态

## 📄 许可证

通过贡献代码，您同意您的贡献将在 [Apache 2.0 许可证](LICENSE) 下发布。

## 🙏 致谢

感谢所有为 Solo MCP 项目做出贡献的开发者！您的贡献让这个项目变得更好。

---

如果您有任何问题，请随时通过 GitHub Issues 联系我们。我们很乐意帮助您开始贡献！