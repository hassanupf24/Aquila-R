"""
Research Methodology components for Aquila-R.

Provides explicit awareness of research methodologies and
ensures methodological transparency in all outputs.
"""

from aquila_r.methodology.frameworks import (
    MethodologyFramework,
    ResearchParadigm,
    get_paradigm_description,
)
from aquila_r.methodology.assumptions import (
    AssumptionTracker,
    Assumption,
    AssumptionType,
    AssumptionSeverity,
)
from aquila_r.methodology.validation import (
    ClaimValidator,
    ClaimValidation,
    ValidationResult,
    ClaimType,
    ValidationStatus,
)

__all__ = [
    "MethodologyFramework",
    "ResearchParadigm",
    "get_paradigm_description",
    "AssumptionTracker",
    "Assumption",
    "AssumptionType",
    "AssumptionSeverity",
    "ClaimValidator",
    "ClaimValidation",
    "ValidationResult",
    "ClaimType",
    "ValidationStatus",
]
