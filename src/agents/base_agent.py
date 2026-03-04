"""
Base Agent Class
Provides fundamental agent capabilities and interface
"""

import asyncio
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

from ..communication.message import Message
from ..communication.message_broker import MessageBroker


class BaseAgent(ABC):
    """Abstract base class for all agents in the system"""
    
    def __init__(self, name: str, broker: MessageBroker, agent_type: str = "base"):
        self.id = str(uuid.uuid4())
        self.name = name
        self.agent_type = agent_type
        self.broker = broker
        self.state = "idle"
        self.inbox: List[Message] = []
        self.knowledge_base: Dict[str, Any] = {}
        self.running = False
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{name}")
        
        # Register with broker
        self.broker.register_agent(self)
    
    async def start(self):
        """Start the agent's main loop"""
        self.running = True
        self.state = "active"
        self.logger.info(f"Agent {self.name} started")
        
        # Start concurrent tasks
        await asyncio.gather(
            self._message_handler(),
            self._main_loop()
        )
    
    async def stop(self):
        """Stop the agent"""
        self.running = False
        self.state = "stopped"
        self.logger.info(f"Agent {self.name} stopped")
    
    async def _message_handler(self):
        """Handle incoming messages"""
        while self.running:
            if self.inbox:
                message = self.inbox.pop(0)
                await self.handle_message(message)
            await asyncio.sleep(0.1)
    
    async def _main_loop(self):
        """Main agent loop"""
        while self.running:
            await self.perceive()
            await self.decide()
            await self.act()
            await asyncio.sleep(0.5)
    
    @abstractmethod
    async def perceive(self):
        """Perceive the environment"""
        pass
    
    @abstractmethod
    async def decide(self):
        """Make decisions based on perceptions"""
        pass
    
    @abstractmethod
    async def act(self):
        """Execute actions based on decisions"""
        pass
    
    @abstractmethod
    async def handle_message(self, message: Message):
        """Handle incoming messages"""
        pass
    
    def send_message(self, recipient_id: str, content: Any, msg_type: str = "info"):
        """Send a message to another agent"""
        message = Message(
            sender_id=self.id,
            recipient_id=recipient_id,
            content=content,
            msg_type=msg_type,
            timestamp=datetime.now()
        )
        self.broker.send_message(message)
        self.logger.debug(f"Sent {msg_type} message to {recipient_id}")
    
    def broadcast_message(self, content: Any, msg_type: str = "info"):
        """Broadcast a message to all agents"""
        message = Message(
            sender_id=self.id,
            recipient_id="broadcast",
            content=content,
            msg_type=msg_type,
            timestamp=datetime.now()
        )
        self.broker.broadcast_message(message)
        self.logger.debug(f"Broadcast {msg_type} message")
    
    def receive_message(self, message: Message):
        """Receive a message from the broker"""
        self.inbox.append(message)
    
    def update_knowledge(self, key: str, value: Any):
        """Update the agent's knowledge base"""
        self.knowledge_base[key] = value
        self.logger.debug(f"Updated knowledge: {key}")
    
    def get_knowledge(self, key: str) -> Optional[Any]:
        """Retrieve knowledge from the knowledge base"""
        return self.knowledge_base.get(key)