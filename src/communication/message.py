"""
Message Class
Defines the structure of messages exchanged between agents
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
import json


@dataclass
class Message:
    """Message structure for inter-agent communication"""
    
    sender_id: str
    recipient_id: str  # Can be specific agent ID or "broadcast"
    content: Any
    msg_type: str = "info"  # info, request, response, command, etc.
    timestamp: datetime = field(default_factory=datetime.now)
    priority: int = 0
    requires_response: bool = False
    correlation_id: Optional[str] = None  # For tracking request-response pairs
    
    def to_dict(self) -> dict:
        """Convert message to dictionary"""
        return {
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "content": self.content,
            "msg_type": self.msg_type,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority,
            "requires_response": self.requires_response,
            "correlation_id": self.correlation_id
        }
    
    def to_json(self) -> str:
        """Convert message to JSON string"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        """Create message from dictionary"""
        if "timestamp" in data:
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> "Message":
        """Create message from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)