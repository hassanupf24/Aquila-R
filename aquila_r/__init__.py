"""
Aquila-R: Autonomous Bilingual Research Intelligence

A rigorous AI research agent designed for academic, technical, and policy research
in English and Arabic. Prioritizes accuracy, epistemic rigor, and transparency.

Core Principles:
- Thinking over speed
- Analysis over fluency
- Research integrity over convenience
"""

from aquila_r.core.agent import AquilaR
from aquila_r.core.identity import AgentIdentity, AgentRole
from aquila_r.core.config import AquilaConfig

__version__ = "1.0.0"
__author__ = "Aquila-R Team"

__all__ = [
    "AquilaR",
    "AgentIdentity",
    "AgentRole",
    "AquilaConfig",
]
