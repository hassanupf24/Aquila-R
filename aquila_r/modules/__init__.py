"""
Functional research modules for Aquila-R.

Each module provides specialized research capabilities:
- Literature: Source discovery and evaluation
- Critical: Argument and evidence evaluation
- Synthesis: Research synthesis and framework building
- Evidence: Data and statistical reasoning
- Writing: Human-in-the-loop writing support
"""

from aquila_r.modules.base import BaseModule, ModuleResult
from aquila_r.modules.literature import LiteratureModule
from aquila_r.modules.critical import CriticalModule
from aquila_r.modules.synthesis import SynthesisModule
from aquila_r.modules.evidence import EvidenceModule
from aquila_r.modules.writing import WritingModule

__all__ = [
    "BaseModule",
    "ModuleResult",
    "LiteratureModule",
    "CriticalModule",
    "SynthesisModule",
    "EvidenceModule",
    "WritingModule",
]
