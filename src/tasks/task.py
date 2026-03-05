"""
Task Class
Represents work units in the system
"""

import uuid
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional, List


class TaskStatus(Enum):
    """Task status enumeration"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class Task:
    """Represents a task/job in the system"""
    
    name: str
    description: str = ""
    priority: int = TaskPriority.NORMAL.value
    data: Dict[str, Any] = field(default_factory=dict)
    required_capability: str = "general"
    estimated_duration: float = 0.0  # in seconds
    deadline: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)  # List of task IDs
    
    # Auto-generated fields
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    assigned_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    assigned_to: Optional[str] = None  # Agent ID
    result: Optional[Any] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "priority": self.priority,
            "data": self.data,
            "required_capability": self.required_capability,
            "estimated_duration": self.estimated_duration,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "dependencies": self.dependencies,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "assigned_at": self.assigned_at.isoformat() if self.assigned_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "assigned_to": self.assigned_to,
            "result": self.result,
            "error": self.error,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Create task from dictionary"""
        # Convert string timestamps back to datetime objects
        for field in ["created_at", "assigned_at", "started_at", "completed_at", "deadline"]:
            if field in data and data[field]:
                data[field] = datetime.fromisoformat(data[field])
        
        # Convert status string to enum
        if "status" in data and isinstance(data["status"], str):
            data["status"] = TaskStatus(data["status"])
        
        return cls(**data)
    
    def is_ready(self) -> bool:
        """Check if task is ready to execute (all dependencies completed)"""
        # In a real implementation, check if all dependency tasks are completed
        return len(self.dependencies) == 0
    
    def is_overdue(self) -> bool:
        """Check if task has passed its deadline"""
        if self.deadline:
            return datetime.now() > self.deadline
        return False
    
    def can_retry(self) -> bool:
        """Check if task can be retried"""
        return self.retry_count < self.max_retries
    
    def update_status(self, new_status: TaskStatus):
        """Update task status with timestamp tracking"""
        self.status = new_status
        
        if new_status == TaskStatus.ASSIGNED:
            self.assigned_at = datetime.now()
        elif new_status == TaskStatus.IN_PROGRESS:
            self.started_at = datetime.now()
        elif new_status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            self.completed_at = datetime.now()