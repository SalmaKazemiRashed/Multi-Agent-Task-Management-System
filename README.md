# Multi Agent Task Management System

A Python-based multi-agent system demonstrating autonomous agent collaboration, task distribution, and intelligent resource management.

## Project structure

```plaintext
multi-agent-system/
├── README.md
├── requirements.txt
├── setup.py
├── .gitignore
├── LICENSE
├── src/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   ├── coordinator_agent.py
│   │   ├── worker_agent.py
│   │   ├── monitor_agent.py
│   │   └── resource_agent.py
│   ├── communication/
│   │   ├── __init__.py
│   │   ├── message.py
│   │   └── message_broker.py
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── task.py
│   │   └── task_queue.py
│   └── utils/
│       ├── __init__.py
│       └── logger.py
├── examples/
│   ├── __init__.py
│   ├── simple_simulation.py
│   └── advanced_simulation.py
├── tests/
│   ├── __init__.py
│   ├── test_agents.py
│   ├── test_communication.py
│   └── test_tasks.py
└── docs/
    ├── architecture.md
    └── api_reference.md
```



* src/agents/ - Agent implementations
* src/communication/ - Message passing system
* src/tasks/ - Task management components
* examples/ - Usage examples
* tests/ - Unit tests
* docs/ - Documentation


## Features

- **Autonomous Agents**: Multiple agent types with specialized roles
- **Communication Protocol**: Message-based inter-agent communication
- **Task Management**: Dynamic task allocation and execution
- **Resource Optimization**: Intelligent resource distribution
- **Monitoring & Logging**: Real-time system monitoring
- **Extensible Architecture**: Easy to add new agent types

##  Set up

### Installation

```bash
# Clone the repository
git clone https://github.com/SalmaKazemiRashed/Multi-Agent-Task-Management-System.git
cd Multi-Agent-Task-Management-System

# Install dependencies
pip install -r requirements.txt

# Update instantly
pip install -e .

```


