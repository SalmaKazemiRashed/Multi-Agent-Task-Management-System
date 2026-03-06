import asyncio
from datetime import datetime
from typing import Optional
from .base_agent import BaseAgent
from ..tasks.task import Task, TaskStatus
from ..communication.message import Message


class WorkerAgent(BaseAgent):
    def __init__(self, name, broker, capabilities=None):
        super().__init__(name, broker, "worker")
        self.capabilities = capabilities or ["general"]
        self.current_task: Optional[Task] = None
        self.state = "idle"
        self.running = False
        self.coordinator_id = None

    async def perceive(self):
        pass

    async def decide(self):
        if self.current_task and self.current_task.status == TaskStatus.ASSIGNED:
            self.current_task.status = TaskStatus.IN_PROGRESS

    async def act(self):
        if self.current_task and self.current_task.status == TaskStatus.IN_PROGRESS:
            await asyncio.sleep(self.current_task.estimated_duration or 2)
            self.current_task.status = TaskStatus.COMPLETED
            self.send_message(
                self.coordinator_id,
                {"task_id": self.current_task.id, "output": f"{self.current_task.name} done"},
                "task_completed"
            )
            self.logger.info(f"Worker {self.name} completed task {self.current_task.name}")
            self.current_task = None
            self.state = "idle"

    async def start(self):
        self.running = True
        self.logger.info(f"Worker agent {self.name} started")

    async def stop(self):
        self.running = False
        self.logger.info(f"Worker agent {self.name} stopped")

    async def handle_message(self, message: Message):
        """Broker will call this when a message arrives"""
        if message.msg_type == "task_assignment":
            task_data = message.content.get("task")
            if task_data:
                self.current_task = Task.from_dict(task_data)
                self.state = "busy"
                self.coordinator_id = message.sender_id
                self.logger.info(f"Worker {self.name} accepted task {self.current_task.name}")
                # Immediately execute the task
                await self.act()