"""
Base classes for tool integration.

Tools follow the principle: prefer retrieval and verification
over generation.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Generic, TypeVar
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


T = TypeVar('T')


class ToolStatus(str, Enum):
    """Status of tool execution."""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    UNAVAILABLE = "unavailable"


class ToolError(Exception):
    """Exception raised by tools."""
    
    def __init__(self, message: str, tool_name: str, recoverable: bool = True):
        self.message = message
        self.tool_name = tool_name
        self.recoverable = recoverable
        super().__init__(message)


class ToolResult(BaseModel, Generic[T]):
    """Result from a tool execution."""
    
    tool_name: str = Field(description="Name of the tool")
    status: ToolStatus = Field(default=ToolStatus.SUCCESS)
    data: Optional[Any] = Field(default=None)
    error: Optional[str] = Field(default=None)
    execution_time_ms: Optional[int] = Field(default=None)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    def is_success(self) -> bool:
        """Check if execution was successful."""
        return self.status == ToolStatus.SUCCESS
    
    def is_partial(self) -> bool:
        """Check if execution was partially successful."""
        return self.status == ToolStatus.PARTIAL


class BaseTool(ABC):
    """
    Base class for all Aquila-R tools.
    
    Tools should:
    - Prefer retrieval and verification over generation
    - Track and reference sources explicitly
    - Declare uncertainty when evidence is insufficient
    - Never hallucinate data or sources
    """
    
    name: str = "base_tool"
    description: str = "Base tool"
    requires_api_key: bool = False
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the tool."""
        self.config = config or {}
        self._initialized = False
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool."""
        pass
    
    def validate_config(self) -> List[str]:
        """Validate tool configuration."""
        issues = []
        
        if self.requires_api_key and not self.config.get("api_key"):
            issues.append(f"{self.name} requires API key")
        
        return issues
    
    def _create_result(
        self,
        status: ToolStatus,
        data: Optional[Any] = None,
        error: Optional[str] = None,
        **metadata,
    ) -> ToolResult:
        """Create a tool result."""
        return ToolResult(
            tool_name=self.name,
            status=status,
            data=data,
            error=error,
            metadata=metadata,
        )
    
    def _success(self, data: Any, **metadata) -> ToolResult:
        """Create a success result."""
        return self._create_result(ToolStatus.SUCCESS, data=data, **metadata)
    
    def _failure(self, error: str, **metadata) -> ToolResult:
        """Create a failure result."""
        return self._create_result(ToolStatus.FAILED, error=error, **metadata)
    
    def _partial(self, data: Any, error: str, **metadata) -> ToolResult:
        """Create a partial success result."""
        return self._create_result(
            ToolStatus.PARTIAL, 
            data=data, 
            error=error, 
            **metadata
        )
