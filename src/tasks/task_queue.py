"""
Task Queue
Priority queue for task management
"""

import heapq
from typing import List, Optional, Dict
from threading import Lock

from .task import Task, TaskStatus, TaskPriority


class TaskQueue:
    """Priority queue for managing tasks"""
    
    def __init__(self):
        self.tasks: List[tuple] = []  # Heap of (priority, creation_time, task)
        self.task_map: Dict[str, Task] = {}  # task_id -> task
        self.lock = Lock()
        self.task_counter = 0
    
    def add_task(self, task: Task):
        """Add a task to the queue"""
        with self.lock:
            # Use negative priority for max heap behavior (higher priority first)
            priority_value = -task.priority
            
            # Use counter to ensure FIFO for same priority tasks
            self.task_counter += 1
            
            heapq.heappush(
                self.tasks,
                (priority_value, self.task_counter, task.id)
            )
            self.task_map[task.id] = task
    
    def get_next_task(self) -> Optional[Task]:
        """Get the highest priority pending task"""
        with self.lock:
            while self.tasks:
                _, _, task_id = heapq.heappop(self.tasks)
                
                if task_id in self.task_map:
                    task = self.task_map[task_id]
                    if task.status == TaskStatus.PENDING and task.is_ready():
                        return task
            
            return None
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a specific task by ID"""
        return self.task_map.get(task_id)
    
    def get_pending_tasks(self) -> List[Task]:
        """Get all pending tasks sorted by priority"""
        with self.lock:
            pending = [
                task for task in self.task_map.values()
                if task.status == TaskStatus.PENDING
            ]
            # Sort by priority (descending) and creation time (ascending)
            pending.sort(key=lambda t: (-t.priority, t.created_at))
            return pending
    
    def get_assigned_tasks(self) -> List[Task]:
        """Get all assigned tasks"""
        return [
            task for task in self.task_map.values()
            if task.status == TaskStatus.ASSIGNED
        ]
    
    def get_in_progress_tasks(self) -> List[Task]:
        """Get all in-progress tasks"""
        return [
            task for task in self.task_map.values()
            if task.status == TaskStatus.IN_PROGRESS
        ]
    
    def remove_task(self, task_id: str) -> bool:
        """Remove a task from the queue"""
        with self.lock:
            if task_id in self.task_map:
                del self.task_map[task_id]
                return True
            return False
    
    def clear_completed_tasks(self):
        """Remove all completed tasks from the queue"""
        with self.lock:
            completed_ids = [
                task_id for task_id, task in self.task_map.items()
                if task.status in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]
            ]
            for task_id in completed_ids:
                del self.task_map[task_id]
    
    def size(self) -> int:
        """Get the number of tasks in the queue"""
        return len(self.task_map)
    
    def is_empty(self) -> bool:
        """Check if the queue is empty"""
        return len(self.task_map) == 0
    
    def get_statistics(self) -> Dict[str, int]:
        """Get task statistics"""
        stats = {
            "total": len(self.task_map),
            "pending": 0,
            "assigned": 0,
            "in_progress": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0
        }
        
        for task in self.task_map.values():
            status_key = task.status.value.replace("_", "_")
            if status_key in stats:
                stats[status_key] += 1
        
        return stats