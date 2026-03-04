"""
Worker Agent
Executes tasks assigned by the coordinator
"""

import asyncio
import random
from typing import List, Dict, Any, Optional
from datetime import datetime

from .base_agent import BaseAgent
from ..tasks.task import Task, TaskStatus
from ..communication.message import Message


class WorkerAgent(BaseAgent):
    """Worker agent that executes assigned tasks"""
    
    def __init__(self, name: str, broker, capabilities: List[str] = None):
        super().__init__(name, broker, "worker")
        self.capabilities = capabilities or ["general", "computation", "data_processing"]
        self.current_task: Optional[Task] = None
        self.task_history: List[Dict[str, Any]] = []
        self.resource_limits = {
            "cpu": 100,
            "memory": 1024,
            "storage": 10240
        }
        self.current_resources = self.resource_limits.copy()
        self._register_with_coordinator()
    
    def _register_with_coordinator(self):
        """Register with the coordinator agent"""
        self.broadcast_message(
            {
                "name": self.name,
                "capabilities": self.capabilities,
                "resource_limits": self.resource_limits
            },
            "worker_registration"
        )
    
    async def perceive(self):
        """Monitor own state and resources"""
        # Update resource usage
        if self.current_task:
            # Simulate resource consumption
            self.current_resources["cpu"] = max(0, self.current_resources["cpu"] - 10)
            self.current_resources["memory"] = max(0, self.current_resources["memory"] - 50)
        else:
            # Restore resources when idle
            self.current_resources["cpu"] = min(
                self.resource_limits["cpu"],
                self.current_resources["cpu"] + 5
            )
            self.current_resources["memory"] = min(
                self.resource_limits["memory"],
                self.current_resources["memory"] + 25
            )
    
    async def decide(self):
        """Decide on task execution strategy"""
        if self.current_task:
            # Check if we need more resources
            if self.current_resources["cpu"] < 20 or self.current_resources["memory"] < 100:
                await self._request_resources()
            
            # Check task timeout
            if hasattr(self.current_task, 'start_time'):
                elapsed = (datetime.now() - self.current_task.start_time).total_seconds()
                if elapsed > 60:  # 60 second timeout
                    self.logger.warning(f"Task {self.current_task.id} timed out")
                    await self._report_task_failure("Task timed out")
    
    async def act(self):
        """Execute current task"""
        if self.current_task and self.current_task.status == TaskStatus.IN_PROGRESS:
            try:
                result = await self._execute_task(self.current_task)
                await self._report_task_completion(result)
            except Exception as e:
                self.logger.error(f"Task execution failed: {e}")
                await self._report_task_failure(str(e))
    
    async def handle_message(self, message: Message):
        """Handle incoming messages"""
        if message.msg_type == "task_assignment":
            await self._handle_task_assignment(message)
        elif message.msg_type == "resource_response":
            self._handle_resource_response(message)
        elif message.msg_type == "status_request":
            self._send_status_update()
    
    async def _handle_task_assignment(self, message: Message):
        """Handle task assignment from coordinator"""
        task_data = message.content.get("task")
        if task_data and not self.current_task:
            self.current_task = Task.from_dict(task_data)
            self.current_task.status = TaskStatus.IN_PROGRESS
            self.current_task.start_time = datetime.now()
            self.state = "busy"
            
            self.logger.info(f"Accepted task {self.current_task.id}: {self.current_task.name}")
            
            # Send acknowledgment
            self.send_message(
                message.sender_id,
                {"task_id": self.current_task.id, "status": "accepted"},
                "task_acknowledgment"
            )
    
    async def _execute_task(self, task: Task) -> Dict[str, Any]:
        """Execute the assigned task"""
        self.logger.info(f"Executing task {task.id}: {task.name}")
        
        # Simulate task execution based on task type
        execution_time = random.uniform(1, 5)  # Random execution time
        await asyncio.sleep(execution_time)
        
        # Simulate different task outcomes
        success_probability = 0.9 if task.required_capability in self.capabilities else 0.6
        
        if random.random() < success_probability:
            # Task succeeded
            result = {
                "task_id": task.id,
                "status": "completed",
                "execution_time": execution_time,
                "output": f"Task {task.name} completed successfully",
                "metrics": {
                    "cpu_used": random.randint(10, 50),
                    "memory_used": random.randint(50, 200),
                    "operations_performed": random.randint(100, 1000)
                }
            }
            return result
        else:
            # Task failed
            raise Exception(f"Task execution failed: Random failure in simulation")
    
    async def _report_task_completion(self, result: Dict[str, Any]):
        """Report successful task completion to coordinator"""
        if self.current_task:
            self.broadcast_message(
                {
                    "task_id": self.current_task.id,
                    "result": result,
                    "worker_id": self.id,
                    "completion_time": datetime.now().isoformat()
                },
                "task_completed"
            )
            
            # Update task history
            self.task_history.append({
                "task_id": self.current_task.id,
                "name": self.current_task.name,
                "status": "completed",
                "completion_time": datetime.now()
            })
            
            self.current_task = None
            self.state = "idle"
            self.logger.info(f"Task completed and reported")
    
    async def _report_task_failure(self, error: str):
        """Report task failure to coordinator"""
        if self.current_task:
            self.broadcast_message(
                {
                    "task_id": self.current_task.id,
                    "error": error,
                    "worker_id": self.id,
                    "failure_time": datetime.now().isoformat()
                },
                "task_failed"
            )
            
            # Update task history
            self.task_history.append({
                "task_id": self.current_task.id,
                "name": self.current_task.name,
                "status": "failed",
                "error": error,
                "failure_time": datetime.now()
            })
            
            self.current_task = None
            self.state = "idle"
            self.logger.error(f"Task failed: {error}")
    
    async def _request_resources(self):
        """Request additional resources from coordinator"""
        self.broadcast_message(
            {
                "worker_id": self.id,
                "resources": {
                    "cpu": 50,
                    "memory": 256
                },
                "reason": "Low resources for task execution"
            },
            "resource_request"
        )
        self.logger.info("Requested additional resources")
    
    def _handle_resource_response(self, message: Message):
        """Handle resource allocation response"""
        if message.content.get("approved"):
            resources = message.content.get("resources", {})
            self.current_resources["cpu"] = min(
                self.resource_limits["cpu"],
                self.current_resources["cpu"] + resources.get("cpu", 0)
            )
            self.current_resources["memory"] = min(
                self.resource_limits["memory"],
                self.current_resources["memory"] + resources.get("memory", 0)
            )
            self.logger.info("Resources allocated successfully")
        else:
            self.logger.warning(f"Resource request denied: {message.content.get('reason')}")
    
    def _send_status_update(self):
        """Send status update to coordinator"""
        status = "busy" if self.current_task else "available"
        self.broadcast_message(
            {
                "worker_id": self.id,
                "status": status,
                "current_task": self.current_task.id if self.current_task else None,
                "resources": self.current_resources,
                "tasks_completed": len([t for t in self.task_history if t["status"] == "completed"]),
                "tasks_failed": len([t for t in self.task_history if t["status"] == "failed"])
            },
            "worker_heartbeat"
        )
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeat messages"""
        while self.running:
            self._send_status_update()
            await asyncio.sleep(10)  # Send heartbeat every 10 seconds
    
    async def start(self):
        """Start the worker agent with heartbeat"""
        self.running = True
        self.state = "active"
        self.logger.info(f"Worker agent {self.name} started")
        
        # Start concurrent tasks including heartbeat
        await asyncio.gather(
            self._message_handler(),
            self._main_loop(),
            self._heartbeat_loop()
        )