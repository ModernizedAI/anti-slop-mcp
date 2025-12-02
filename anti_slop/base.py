"""Base classes for anti-slop tools."""
from abc import ABC, abstractmethod
from typing import Dict, Any
from pydantic import BaseModel


class ToolResult(BaseModel):
    """Standard result format for all tools."""
    success: bool
    data: Dict[str, Any]
    error: str | None = None


class BaseTool(ABC):
    """Base class for all anti-slop tools."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description."""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given arguments."""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
        }
