"""
Message Broker
Central hub for message routing between agents
"""

import asyncio
from typing import Dict, List, Optional
from collections import defaultdict
import logging

from .message import Message


class MessageBroker:
    """Central message broker for agent communication"""
    
    def __init__(self):
        self.agents: Dict[str, Any] = {}  # agent_id -> agent_instance
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.subscriptions: Dict[str, List[str]] = defaultdict(list)  # topic -> [agent_ids]
        self.message_history: List[Message] = []
        self.logger = logging.getLogger(self.__class__.__name__)
        self.running = False
    
    def register_agent(self, agent):
        """Register an agent with the broker"""
        self.agents[agent.id] = agent
        self.logger.info(f"Registered agent: {agent.name} ({agent.id})")
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent from the broker"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            # Remove from all subscriptions
            for topic in self.subscriptions:
                if agent_id in self.subscriptions[topic]:
                    self.subscriptions[topic].remove(agent_id)
            self.logger.info(f"Unregistered agent: {agent_id}")
    
    def subscribe(self, agent_id: str, topic: str):
        """Subscribe an agent to a topic"""
        if agent_id not in self.subscriptions[topic]:
            self.subscriptions[topic].append(agent_id)
            self.logger.debug(f"Agent {agent_id} subscribed to topic: {topic}")
    
    def unsubscribe(self, agent_id: str, topic: str):
        """Unsubscribe an agent from a topic"""
        if agent_id in self.subscriptions[topic]:
            self.subscriptions[topic].remove(agent_id)
            self.logger.debug(f"Agent {agent_id} unsubscribed from topic: {topic}")
    
    def send_message(self, message: Message):
        """Send a message to a specific agent"""
        recipient_id = message.recipient_id
        
        if recipient_id in self.agents:
            self.agents[recipient_id].receive_message(message)
            self.message_history.append(message)
            self.logger.debug(
                f"Message delivered from {message.sender_id} to {recipient_id}: {message.msg_type}"
            )
        else:
            self.logger.warning(f"Recipient {recipient_id} not found for message")
    
    def broadcast_message(self, message: Message):
        """Broadcast a message to all agents except sender"""
        sender_id = message.sender_id
        
        for agent_id, agent in self.agents.items():
            if agent_id != sender_id:
                agent.receive_message(message)
        
        self.message_history.append(message)
        self.logger.debug(f"Broadcast message from {sender_id}: {message.msg_type}")
    
    def publish_to_topic(self, topic: str, message: Message):
        """Publish a message to all agents subscribed to a topic"""
        subscribers = self.subscriptions.get(topic, [])
        
        for agent_id in subscribers:
            if agent_id in self.agents and agent_id != message.sender_id:
                self.agents[agent_id].receive_message(message)
        
        self.logger.debug(
            f"Published message to topic '{topic}' from {message.sender_id}, {len(subscribers)} subscribers"
        )
    
    async def start(self):
        """Start the message broker"""
        self.running = True
        self.logger.info("Message broker started")
        
        # Process message queue
        while self.running:
            try:
                if not self.message_queue.empty():
                    message = await self.message_queue.get()
                    await self._process_message(message)
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")
            
            await asyncio.sleep(0.01)
    
    async def stop(self):
        """Stop the message broker"""
        self.running = False
        self.logger.info("Message broker stopped")
    
    async def _process_message(self, message: Message):
        """Process a message from the queue"""
        # This method can be extended to add message filtering,
        # transformation, or routing logic
        if message.recipient_id == "broadcast":
            self.broadcast_message(message)
        else:
            self.send_message(message)
    
    def get_message_history(self, limit: int = 100) -> List[Message]:
        """Get recent message history"""
        return self.message_history[-limit:]
    
    def get_agent_messages(self, agent_id: str, limit: int = 50) -> List[Message]:
        """Get messages sent or received by a specific agent"""
        agent_messages = [
            msg for msg in self.message_history
            if msg.sender_id == agent_id or msg.recipient_id == agent_id
        ]
        return agent_messages[-limit:]
    
    def clear_message_history(self):
        """Clear message history"""
        self.message_history = []
        self.logger.info("Message history cleared")