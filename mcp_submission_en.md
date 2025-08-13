# Solo MCP - Trae Solo Mode Platform

## Project Description

Solo MCP is an intelligent multi-role collaboration platform designed specifically for Trae Solo mode. The platform now supports comprehensive To-Do List task management capabilities, providing developers with powerful task orchestration and collaboration features.

## Key Features

### 🎭 Intelligent Role System
- Multi-role collaboration framework
- Dynamic role assignment
- Role capability assessment

### 🧠 Advanced Memory Management
- Persistent memory storage
- Intelligent memory retrieval
- Context-aware memory

### 📋 Complete To-Do List Functionality
- ✅ Task creation, update, and deletion
- 🏷️ Task status management (pending, in_progress, completed, cancelled)
- ⭐ Priority levels (low, medium, high, urgent)
- 🔗 Task dependencies
- 🏷️ Tag system
- 📝 Task notes
- 🔍 Task search
- 📊 Statistics

### 🎯 Smart Task Orchestration
- Automatic task allocation
- Dependency handling
- Priority sorting
- Conflict detection and resolution

### 🔍 Comprehensive Context Analysis
- Code context collection
- Project structure analysis
- Intelligent index building

## Installation

### Install via pip
```bash
pip install solo-mcp
```

### Install from source
```bash
git clone https://github.com/CHANGGELY/solo-mcp.git
cd solo-mcp
pip install -e .
```

## Usage Examples

### Start MCP Server
```bash
solo-mcp-server
```

### To-Do List Examples

#### Create Task
```python
# Call via MCP client
result = await client.call_tool("todo_create", {
    "title": "Implement new feature",
    "description": "Add user authentication to the project",
    "priority": "high",
    "tags": ["development", "auth"]
})
```

#### List Tasks
```python
# Get all pending tasks
tasks = await client.call_tool("todo_list", {
    "status": "pending"
})
```

#### Update Task Status
```python
# Mark task as in progress
result = await client.call_tool("todo_update", {
    "task_id": "task-uuid",
    "status": "in_progress"
})
```

#### Search Tasks
```python
# Search tasks containing specific keywords
results = await client.call_tool("todo_search", {
    "query": "authentication"
})
```

## Configuration

### Environment Variables
- `SOLO_MCP_DATA_DIR`: Data storage directory (default: `.memory`)
- `SOLO_MCP_LOG_LEVEL`: Log level (default: `INFO`)

### Configuration File
The project supports detailed configuration via `config.json`:

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

## Technical Features

- 🚀 **High Performance**: Asynchronous processing with concurrent operations
- 🔒 **Data Security**: Local storage for privacy protection
- 🔧 **Easy Integration**: Standard MCP protocol, compatible with various clients
- 📱 **Cross-Platform**: Supports Windows, macOS, Linux
- 🎨 **Extensible**: Modular design for easy feature additions

## Project Architecture

```
solo-mcp/
├── solo_mcp/
│   ├── core/           # Core functionality modules
│   ├── tools/          # Tool modules
│   │   ├── todo.py     # To-Do List functionality
│   │   └── orchestrator.py  # Task orchestration
│   ├── memory/         # Memory management
│   └── mcp_server.py   # MCP server
├── tests/              # Test files
└── docs/               # Documentation
```

## Available MCP Tools

### File System Operations
- `fs_read` - Read file contents
- `fs_write` - Write file contents
- `fs_list` - List directory contents

### Memory Management
- `memory_store` - Store information in memory
- `memory_load` - Load information from memory
- `memory_summarize` - Summarize memory contents

### To-Do List Management
- `todo_create` - Create new task
- `todo_list` - List tasks with filters
- `todo_get` - Get task details
- `todo_update` - Update task
- `todo_delete` - Delete task
- `todo_search` - Search tasks
- `todo_statistics` - Get task statistics
- `todo_add_note` - Add note to task
- `todo_add_dependency` - Add task dependency

### Context and Analysis
- `index_build` - Build project index
- `index_search` - Search project index
- `context_collect` - Collect context information
- `roles_evaluate` - Evaluate role capabilities
- `orchestrator_run_round` - Run orchestration round

### Process Management
- `proc_exec` - Execute processes
- `credits_get` - Get credit information
- `credits_add` - Add credits

## Contributing

We welcome community contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

## Contact

- GitHub: [CHANGGELY/solo-mcp](https://github.com/CHANGGELY/solo-mcp)
- Issues: [GitHub Issues](https://github.com/CHANGGELY/solo-mcp/issues)

---

**Solo MCP** - Making Trae Solo mode smarter and more efficient!