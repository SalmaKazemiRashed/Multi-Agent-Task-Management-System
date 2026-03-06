import asyncio
from datetime import datetime
from typing import List, Dict

from .base_agent import BaseAgent
from ..tasks.task import Task, TaskStatus
from ..tasks.task_queue import TaskQueue
from ..communication.message import Message


class CoordinatorAgent(BaseAgent):
    """Coordinator agent responsible for task management and distribution"""

    def __init__(self, name: str, broker):
        super().__init__(name, broker, "coordinator")
        self.task_queue = TaskQueue()
        self.worker_registry: Dict[str, dict] = {}
        self.task_assignments: Dict[str, str] = {}  # task_id -> worker_id
        self.completed_tasks: List[Task] = []
        self.running = False

    async def perceive(self):
        """Monitor worker heartbeats"""
        now = datetime.now().timestamp()
        for wid, info in self.worker_registry.items():
            if now - info.get("last_heartbeat", now) > 30:
                info["status"] = "offline"

    async def decide(self):
        """Assign pending tasks to available workers"""
        pending = self.task_queue.get_pending_tasks()
        available = [wid for wid, w in self.worker_registry.items() if w.get("status") == "available"]

        for task in pending[:len(available)]:
            worker_id = available.pop(0)
            self.task_assignments[task.id] = worker_id
            task.status = TaskStatus.ASSIGNED
            self.worker_registry[worker_id]["status"] = "busy"
            self.send_message(worker_id, {"task": task.to_dict()}, "task_assignment")

    async def act(self):
        pass

    async def _dispatch_loop(self):
        while self.running:
            await self.perceive()
            await self.decide()
            await asyncio.sleep(1)

    async def start(self):
        self.running = True
        asyncio.create_task(self._dispatch_loop())
        self.logger.info(f"Agent {self.name} started")

    async def stop(self):
        self.running = False
        self.logger.info(f"Agent {self.name} stopped")

    async def submit_task(self, task: Task):
        self.task_queue.add_task(task)
        self.logger.info(f"Task {task.id} submitted")

    async def handle_message(self, message: Message):
        """Handle incoming messages from workers"""
        if message.msg_type == "task_completed":
            task_id = message.content.get("task_id")
            output = message.content.get("output")
            task = self.task_queue.get_task(task_id)
            if task:
                task.status = TaskStatus.COMPLETED
                task.result = {"output": output}
                self.completed_tasks.append(task)
                worker_id = self.task_assignments.get(task_id)
                if worker_id:
                    self.worker_registry[worker_id]["status"] = "available"
                self.logger.info(f"Task {task.name} completed by worker {worker_id}")
        elif message.msg_type == "worker_heartbeat":
            wid = message.content.get("worker_id")
            if wid in self.worker_registry:
                self.worker_registry[wid]["last_heartbeat"] = datetime.now().timestamp()
                self.worker_registry[wid]["status"] = message.content.get("status", "available")