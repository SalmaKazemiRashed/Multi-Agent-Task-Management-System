"""
Coordinator Agent
Manages task distribution and system coordination
"""

import asyncio
from typing import List, Dict, Any
from datetime import datetime

from .base_agent import BaseAgent
from ..tasks.task import Task, TaskStatus
from ..tasks.task_queue import TaskQueue
from ..communication.message import Message


class CoordinatorAgent(BaseAgent):
    """Coordinator agent responsible for task management and distribution"""
    
    def __init__(self, name: str, broker):
        super().__init__(name, broker, "coordinator")
        self.task_queue = TaskQueue()
        self.worker_registry: Dict[str, Dict[str, Any]] = {}
        self.task_assignments: Dict[str, str] = {}  # task_id -> worker_id
        self.completed_tasks: List[Task] = []
    
    async def perceive(self):
        """Monitor system state and worker availability"""
        # Check worker statuses
        for worker_id, info in self.worker_registry.items():
            if datetime.now().timestamp() - info.get("last_heartbeat", 0) > 30:
                info["status"] = "offline"
                self.logger.warning(f"Worker {worker_id} appears offline")
    
    async def decide(self):
        """Decide on task assignments"""
        # Get pending tasks
        pending_tasks = self.task_queue.get_pending_tasks()
        
        # Get available workers
        available_workers = [
            worker_id for worker_id, info in self.worker_registry.items()
            if info.get("status") == "available"
        ]
        
        # Assign tasks to workers
        for task in pending_tasks[:len(available_workers)]:
            worker_id = self._select_best_worker(task, available_workers)
            if worker_id:
                self.task_assignments[task.id] = worker_id
                available_workers.remove(worker_id)
                self.logger.info(f"Assigned task {task.id} to worker {worker_id}")
    
    async def act(self):
        """Distribute tasks to workers"""
        for task_id, worker_id in list(self.task_assignments.items()):
            task = self.task_queue.get_task(task_id)
            if task and task.status == TaskStatus.PENDING:
                # Send task to worker
                self.send_message(
                    worker_id,
                    {"task": task.to_dict(), "action": "execute"},
                    "task_assignment"
                )
                task.status = TaskStatus.ASSIGNED
                # Update worker status
                if worker_id in self.worker_registry:
                    self.worker_registry[worker_id]["status"] = "busy"
    
    async def handle_message(self, message: Message):
        """Handle incoming messages"""
        if message.msg_type == "worker_registration":
            self._register_worker(message)
        elif message.msg_type == "worker_heartbeat":
            self._update_worker_heartbeat(message)
        elif message.msg_type == "task_completed":
            await self._handle_task_completion(message)
        elif message.msg_type == "task_failed":
            await self._handle_task_failure(message)
        elif message.msg_type == "resource_request":
            await self._handle_resource_request(message)
    
    def submit_task(self, task: Task):
        """Submit a new task to the system"""
        self.task_queue.add_task(task)
        self.logger.info(f"Task {task.id} submitted: {task.name}")
        self.broadcast_message(
            {"task_id": task.id, "name": task.name, "priority": task.priority},
            "new_task"
        )
    
    def _select_best_worker(self, task: Task, available_workers: List[str]) -> str:
        """Select the best worker for a task based on capabilities and load"""
        if not available_workers:
            return None
        
        best_worker = None
        best_score = -1
        
        for worker_id in available_workers:
            worker_info = self.worker_registry.get(worker_id, {})
            
            # Calculate suitability score
            score = 0
            
            # Check capabilities match
            capabilities = worker_info.get("capabilities", [])
            if task.required_capability in capabilities:
                score += 10
            
            # Consider worker performance history
            success_rate = worker_info.get("success_rate", 1.0)
            score += success_rate * 5
            
            # Consider current load
            current_load = worker_info.get("current_load", 0)
            score -= current_load
            
            if score > best_score:
                best_score = score
                best_worker = worker_id
        
        return best_worker
    
    def _register_worker(self, message: Message):
        """Register a new worker"""
        worker_id = message.sender_id
        worker_info = message.content
        
        self.worker_registry[worker_id] = {
            "id": worker_id,
            "name": worker_info.get("name"),
            "capabilities": worker_info.get("capabilities", []),
            "status": "available",
            "last_heartbeat": datetime.now().timestamp(),
            "success_rate": 1.0,
            "current_load": 0
        }
        
        self.logger.info(f"Worker {worker_id} registered")
    
    def _update_worker_heartbeat(self, message: Message):
        """Update worker heartbeat"""
        worker_id = message.sender_id
        if worker_id in self.worker_registry:
            self.worker_registry[worker_id]["last_heartbeat"] = datetime.now().timestamp()
            self.worker_registry[worker_id]["status"] = message.content.get("status", "available")
    
    async def _handle_task_completion(self, message: Message):
        """Handle task completion notification"""
        task_id = message.content.get("task_id")
        worker_id = message.sender_id
        
        if task_id in self.task_assignments:
            task = self.task_queue.get_task(task_id)
            if task:
                task.status = TaskStatus.COMPLETED
                task.result = message.content.get("result")
                self.completed_tasks.append(task)
                
                # Update worker status
                if worker_id in self.worker_registry:
                    self.worker_registry[worker_id]["status"] = "available"
                    self.worker_registry[worker_id]["current_load"] -= 1
                    
                    # Update success rate
                    total = self.worker_registry[worker_id].get("total_tasks", 0) + 1
                    successful = self.worker_registry[worker_id].get("successful_tasks", 0) + 1
                    self.worker_registry[worker_id]["total_tasks"] = total
                    self.worker_registry[worker_id]["successful_tasks"] = successful
                    self.worker_registry[worker_id]["success_rate"] = successful / total
                
                del self.task_assignments[task_id]
                self.logger.info(f"Task {task_id} completed by worker {worker_id}")
    
    async def _handle_task_failure(self, message: Message):
        """Handle task failure notification"""
        task_id = message.content.get("task_id")
        worker_id = message.sender_id
        error = message.content.get("error")
        
        if task_id in self.task_assignments:
            task = self.task_queue.get_task(task_id)
            if task:
                task.status = TaskStatus.FAILED
                task.retry_count += 1
                
                # Update worker status
                if worker_id in self.worker_registry:
                    self.worker_registry[worker_id]["status"] = "available"
                    self.worker_registry[worker_id]["current_load"] -= 1
                    
                    # Update success rate
                    total = self.worker_registry[worker_id].get("total_tasks", 0) + 1
                    successful = self.worker_registry[worker_id].get("successful_tasks", 0)
                    self.worker_registry[worker_id]["total_tasks"] = total
                    self.worker_registry[worker_id]["successful_tasks"] = successful
                    self.worker_registry[worker_id]["success_rate"] = successful / total if total > 0 else 0
                
                # Retry task if retry count is below threshold
                if task.retry_count < 3:
                    task.status = TaskStatus.PENDING
                    self.logger.info(f"Retrying task {task_id} (attempt {task.retry_count + 1})")
                else:
                    self.logger.error(f"Task {task_id} permanently failed after 3 retries: {error}")
                
                del self.task_assignments[task_id]
    
    async def _handle_resource_request(self, message: Message):
        """Handle resource requests from workers"""
        worker_id = message.sender_id
        requested_resources = message.content.get("resources", {})
        
        # Check resource availability (simplified)
        available = True  # In a real system, check actual resource availability
        
        if available:
            self.send_message(
                worker_id,
                {"approved": True, "resources": requested_resources},
                "resource_response"
            )
        else:
            self.send_message(
                worker_id,
                {"approved": False, "reason": "Insufficient resources"},
                "resource_response"
            )