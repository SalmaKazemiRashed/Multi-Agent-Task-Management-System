import asyncio
import logging
from src.agents import CoordinatorAgent, WorkerAgent
from src.communication import MessageBroker
from src.tasks.task import Task

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

async def simple_simulation():
    broker = MessageBroker()
    coordinator = CoordinatorAgent("MainCoordinator", broker)
    worker1 = WorkerAgent("Worker-Alpha", broker, ["computation"])
    worker2 = WorkerAgent("Worker-Beta", broker, ["data_processing"])
    worker3 = WorkerAgent("Worker-Gamma", broker, ["general"])

    tasks = [
        Task(name="Data Collection", description="Collect data", estimated_duration=2),
        Task(name="Data Cleaning", description="Clean data", estimated_duration=3),
        Task(name="Analysis", description="Analyze data", estimated_duration=3),
        Task(name="Reporting", description="Generate report", estimated_duration=2),
        Task(name="Visualization", description="Visualize data", estimated_duration=2),
    ]

    for t in tasks:
        await coordinator.submit_task(t)

    agent_tasks = [
        asyncio.create_task(coordinator.start()),
        asyncio.create_task(worker1.start()),
        asyncio.create_task(worker2.start()),
        asyncio.create_task(worker3.start()),
        asyncio.create_task(broker.start())
    ]

    await asyncio.sleep(20)  # simulation runs
    await coordinator.stop()
    await worker1.stop()
    await worker2.stop()
    await worker3.stop()
    await broker.stop()

    print("Completed tasks:")
    for t in coordinator.task_queue.get_all_tasks():
        print(f"{t.name}: {t.status.value}")

asyncio.run(simple_simulation())