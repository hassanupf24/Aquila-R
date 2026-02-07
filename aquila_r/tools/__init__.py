"""
Tool integration layer for Aquila-R.

Provides base classes and utilities for integrating
external tools for retrieval, parsing, and verification.
"""

from aquila_r.tools.base import BaseTool, ToolResult, ToolError
from aquila_r.tools.retrieval import RetrievalTool, SearchResult
from aquila_r.tools.parsing import DocumentParser, ParsedDocument

__all__ = [
    "BaseTool",
    "ToolResult",
    "ToolError",
    "RetrievalTool",
    "SearchResult",
    "DocumentParser",
    "ParsedDocument",
]
