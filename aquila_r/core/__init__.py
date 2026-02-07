"""
Core module initialization.
"""

from aquila_r.core.identity import AgentIdentity, AgentRole
from aquila_r.core.config import AquilaConfig, LLMProvider, MethodologyParadigm
from aquila_r.core.memory import ResearchMemory
from aquila_r.core.agent import AquilaR
from aquila_r.core.llm import LLMClient

__all__ = [
    "AgentIdentity",
    "AgentRole",
    "AquilaConfig",
    "LLMProvider",
    "MethodologyParadigm",
    "ResearchMemory",
    "AquilaR",
    "LLMClient",
]
