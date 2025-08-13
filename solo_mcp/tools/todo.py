"""Todo list management tool for Solo MCP."""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class TodoTask:
    """Todo task data structure."""
    id: str
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    created_at: str = ""
    updated_at: str = ""
    due_date: Optional[str] = None
    tags: List[str] = None
    dependencies: List[str] = None
    notes: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.dependencies is None:
            self.dependencies = []
        if self.notes is None:
            self.notes = []
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at


class TodoTool:
    """Todo list management tool."""
    
    def __init__(self, data_dir: str = ".memory"):
        """Initialize todo tool.
        
        Args:
            data_dir: Directory to store todo data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.todo_file = self.data_dir / "todos.json"
        self._tasks: Dict[str, TodoTask] = {}
        self._load_tasks()
    
    def _load_tasks(self) -> None:
        """Load tasks from file."""
        if self.todo_file.exists():
            try:
                with open(self.todo_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for task_id, task_data in data.items():
                        # Convert string enums back to enum objects
                        if 'status' in task_data:
                            task_data['status'] = TaskStatus(task_data['status'])
                        if 'priority' in task_data:
                            task_data['priority'] = TaskPriority(task_data['priority'])
                        self._tasks[task_id] = TodoTask(**task_data)
            except (json.JSONDecodeError, ValueError, TypeError) as e:
                print(f"Error loading tasks: {e}")
                self._tasks = {}
    
    def _save_tasks(self) -> None:
        """Save tasks to file."""
        try:
            data = {}
            for task_id, task in self._tasks.items():
                task_dict = asdict(task)
                # Convert enums to strings for JSON serialization
                task_dict['status'] = task.status.value
                task_dict['priority'] = task.priority.value
                data[task_id] = task_dict
            
            with open(self.todo_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving tasks: {e}")
    
    def create_task(self, title: str, description: str = "", 
                   priority: str = "medium", due_date: Optional[str] = None,
                   tags: Optional[List[str]] = None) -> str:
        """Create a new task.
        
        Args:
            title: Task title
            description: Task description
            priority: Task priority (low, medium, high, urgent)
            due_date: Due date in ISO format
            tags: List of tags
            
        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())
        try:
            priority_enum = TaskPriority(priority.lower())
        except ValueError:
            priority_enum = TaskPriority.MEDIUM
        
        task = TodoTask(
            id=task_id,
            title=title,
            description=description,
            priority=priority_enum,
            due_date=due_date,
            tags=tags or []
        )
        
        self._tasks[task_id] = task
        self._save_tasks()
        return task_id
    
    def list_tasks(self, status: Optional[str] = None, 
                  priority: Optional[str] = None,
                  tag: Optional[str] = None) -> List[Dict[str, Any]]:
        """List tasks with optional filters.
        
        Args:
            status: Filter by status
            priority: Filter by priority
            tag: Filter by tag
            
        Returns:
            List of task dictionaries
        """
        tasks = list(self._tasks.values())
        
        # Apply filters
        if status:
            try:
                status_enum = TaskStatus(status.lower())
                tasks = [t for t in tasks if t.status == status_enum]
            except ValueError:
                pass
        
        if priority:
            try:
                priority_enum = TaskPriority(priority.lower())
                tasks = [t for t in tasks if t.priority == priority_enum]
            except ValueError:
                pass
        
        if tag:
            tasks = [t for t in tasks if tag in t.tags]
        
        # Convert to dictionaries for JSON serialization
        result = []
        for task in tasks:
            task_dict = asdict(task)
            task_dict['status'] = task.status.value
            task_dict['priority'] = task.priority.value
            result.append(task_dict)
        
        return result
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific task.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task dictionary or None
        """
        task = self._tasks.get(task_id)
        if task:
            task_dict = asdict(task)
            task_dict['status'] = task.status.value
            task_dict['priority'] = task.priority.value
            return task_dict
        return None
    
    def update_task(self, task_id: str, **kwargs) -> bool:
        """Update a task.
        
        Args:
            task_id: Task ID
            **kwargs: Fields to update
            
        Returns:
            True if updated successfully
        """
        if task_id not in self._tasks:
            return False
        
        task = self._tasks[task_id]
        
        # Update allowed fields
        if 'title' in kwargs:
            task.title = kwargs['title']
        if 'description' in kwargs:
            task.description = kwargs['description']
        if 'status' in kwargs:
            try:
                task.status = TaskStatus(kwargs['status'].lower())
            except ValueError:
                pass
        if 'priority' in kwargs:
            try:
                task.priority = TaskPriority(kwargs['priority'].lower())
            except ValueError:
                pass
        if 'due_date' in kwargs:
            task.due_date = kwargs['due_date']
        if 'tags' in kwargs:
            task.tags = kwargs['tags'] or []
        
        task.updated_at = datetime.now().isoformat()
        self._save_tasks()
        return True
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            True if deleted successfully
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            self._save_tasks()
            return True
        return False
    
    def add_dependency(self, task_id: str, dependency_id: str) -> bool:
        """Add a dependency to a task.
        
        Args:
            task_id: Task ID
            dependency_id: Dependency task ID
            
        Returns:
            True if added successfully
        """
        if task_id in self._tasks and dependency_id in self._tasks:
            task = self._tasks[task_id]
            if dependency_id not in task.dependencies:
                task.dependencies.append(dependency_id)
                task.updated_at = datetime.now().isoformat()
                self._save_tasks()
                return True
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get todo statistics.
        
        Returns:
            Statistics dictionary
        """
        total = len(self._tasks)
        status_counts = {status.value: 0 for status in TaskStatus}
        priority_counts = {priority.value: 0 for priority in TaskPriority}
        
        for task in self._tasks.values():
            status_counts[task.status.value] += 1
            priority_counts[task.priority.value] += 1
        
        return {
            'total_tasks': total,
            'status_breakdown': status_counts,
            'priority_breakdown': priority_counts
        }
    
    def search_tasks(self, query: str) -> List[Dict[str, Any]]:
        """Search tasks by title or description.
        
        Args:
            query: Search query
            
        Returns:
            List of matching task dictionaries
        """
        query_lower = query.lower()
        matching_tasks = []
        
        for task in self._tasks.values():
            if (query_lower in task.title.lower() or 
                query_lower in task.description.lower() or
                any(query_lower in tag.lower() for tag in task.tags)):
                task_dict = asdict(task)
                task_dict['status'] = task.status.value
                task_dict['priority'] = task.priority.value
                matching_tasks.append(task_dict)
        
        return matching_tasks
    
    def add_note(self, task_id: str, note: str) -> bool:
        """Add a note to a task.
        
        Args:
            task_id: Task ID
            note: Note content
            
        Returns:
            True if added successfully
        """
        if task_id in self._tasks:
            task = self._tasks[task_id]
            timestamp = datetime.now().isoformat()
            task.notes.append(f"[{timestamp}] {note}")
            task.updated_at = timestamp
            self._save_tasks()
            return True
        return False