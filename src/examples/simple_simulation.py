"""
Simple Multi-Agent Simulation
Demonstrates basic agent coordination and task execution
"""

import asyncio
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from src.agents import CoordinatorAgent, WorkerAgent
from src.communication import MessageBroker
from src.tasks import Task, TaskPriority


async def simple_simulation():
    """Run a simple multi-agent simulation"""
    
    print("=" * 50)
    print("Multi-Agent Task Management System")
    print("Simple Simulation")
    print("=" * 50)
    
    # Create message broker
    broker = MessageBroker()
    
    # Create coordinator agent
    coordinator = CoordinatorAgent("MainCoordinator", broker)
    
    # Create worker agents with different capabilities
    worker1 = WorkerAgent("Worker-Alpha", broker, ["computation", "analysis"])
    worker2 = WorkerAgent("Worker-Beta", broker, ["data_processing", "storage"])
    worker3 = WorkerAgent("Worker-Gamma", broker, ["general", "computation"])
    
    # Create sample tasks
    tasks = [
        Task(
            name="Data Analysis Task",
            description="Analyze dataset for patterns",
            priority=TaskPriority.HIGH.value,
            required_capability="analysis",
            estimated_duration=3.0
        ),
        Task(
            name="Computation Task",
            description="Perform complex calculations",
            priority=TaskPriority.NORMAL.value,
            required_capability="computation",
            estimated_duration=2.0
        ),
        Task(
            name="Data Processing Task",
            description="Process raw data",
            priority=TaskPriority.HIGH.value,
            required_capability="data_processing",
            estimated_duration=4.0
        ),
        Task(
            name="General Task 1",
            description="General maintenance task",
            priority=TaskPriority.LOW.value,
            required_capability="general",
            estimated_duration=1.0
        ),
        Task(
            name="Storage Task",
            description="Store processed data",
            priority=TaskPriority.NORMAL.value,
            required_capability="storage",
            estimated_duration=2.0
        ),
    ]
    
    # Submit tasks to coordinator
    print("\nSubmitting tasks to the system...")
    for task in tasks:
        coordinator.submit_task(task)
        print(f"  - Submitted: {task.name} (Priority: {task.priority})")
    
    # Start all agents
    print("\nStarting agents...")
    agent_tasks = [
        asyncio.create_task(coordinator.start()),
        asyncio.create_task(worker1.start()),
        asyncio.create_task(worker2.start()),
        asyncio.create_task(worker3.start()),
        asyncio.create_task(broker.start())
    ]
    
    # Run simulation for 30 seconds
    print("\nSimulation running for 30 seconds...")
    print("-" * 30)
    
    await asyncio.sleep(30)
    
    # Stop all agents
    print("\nStopping simulation...")
    await coordinator.stop()
    await worker1.stop()
    await worker2.stop()
    await worker3.stop()
    await broker.stop()
    
    # Cancel agent tasks
    for task in agent_tasks:
        task.cancel()
    
    # Print results
    print("\n" + "=" * 50)
    print("Simulation Results")
    print("=" * 50)
    
    # Task statistics
    queue_stats = coordinator.task_queue.get_statistics()
    print("\nTask Statistics:")
    print(f"  - Total tasks: {queue_stats['total']}")
    print(f"  - Completed: {len(coordinator.completed_tasks)}")
    print(f"  - Failed: {queue_stats['failed']}")
    print(f"  - Pending: {queue_stats['pending']}")
    
    # Worker statistics
    print("\nWorker Statistics:")
    for worker_id, info in coordinator.worker_registry.items():
        print(f"\n  {info['name']}:")
        print(f"    - Tasks completed: {info.get('successful_tasks', 0)}")
        print(f"    - Success rate: {info.get('success_rate', 0):.2%}")
        print(f"    - Status: {info.get('status', 'unknown')}")
    
    # Completed tasks details
    print("\nCompleted Tasks:")
    for task in coordinator.completed_tasks:
        print(f"  - {task.name}: {task.status.value}")
        if task.result:
            print(f"    Result: {task.result.get('output', 'N/A')}")
    
    print("\n" + "=" * 50)
    print("Simulation Complete")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(simple_simulation())