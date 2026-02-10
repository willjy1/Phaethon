"""Initialize adapters module."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

__all__ = ["BaseAdapter"]


class BaseAdapter(ABC):
    """Abstract base class for all Phaethon adapters.
    
    Adapters connect Phaethon to external systems:
    - Browser extensions
    - HTTP/DNS proxies
    - Application APIs
    - Custom integrations
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize adapter.
        
        Args:
            config: Configuration dict for the adapter.
        """
        self.config = config or {}
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def start(self) -> None:
        """Start the adapter."""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stop the adapter."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if adapter is healthy.
        
        Returns:
            True if healthy, False otherwise.
        """
        pass
