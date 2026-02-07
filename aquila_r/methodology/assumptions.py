"""
Assumption Tracking for Aquila-R.

Tracks and declares assumptions made during research analysis,
ensuring methodological transparency.
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class AssumptionType(str, Enum):
    """Types of assumptions in research."""
    METHODOLOGICAL = "methodological"
    THEORETICAL = "theoretical"
    EPISTEMOLOGICAL = "epistemological"
    ONTOLOGICAL = "ontological"
    CONTEXTUAL = "contextual"
    DATA = "data"
    SCOPE = "scope"


class AssumptionSeverity(str, Enum):
    """Impact severity of an assumption."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Assumption(BaseModel):
    """A tracked assumption."""
    
    id: str = Field(description="Unique identifier")
    content: str = Field(description="The assumption statement")
    type: AssumptionType = Field(default=AssumptionType.METHODOLOGICAL)
    severity: AssumptionSeverity = Field(default=AssumptionSeverity.MEDIUM)
    justification: Optional[str] = Field(default=None)
    alternatives: List[str] = Field(default_factory=list)
    affected_conclusions: List[str] = Field(default_factory=list)
    declared_explicitly: bool = Field(default=True)
    source: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    def to_disclosure(self, language: str = "en") -> str:
        """Generate disclosure statement."""
        if language == "ar":
            return f"افتراض ({self.type.value}): {self.content}"
        return f"Assumption ({self.type.value}): {self.content}"


class AssumptionTracker:
    """
    Tracks assumptions throughout research analysis.
    
    Ensures all assumptions are declared explicitly and
    their implications understood.
    """
    
    def __init__(self):
        """Initialize the tracker."""
        self._assumptions: List[Assumption] = []
        self._counter = 0
    
    def add(
        self,
        content: str,
        assumption_type: AssumptionType = AssumptionType.METHODOLOGICAL,
        severity: AssumptionSeverity = AssumptionSeverity.MEDIUM,
        justification: Optional[str] = None,
        alternatives: Optional[List[str]] = None,
    ) -> Assumption:
        """
        Add an assumption.
        
        Args:
            content: The assumption statement
            assumption_type: Type of assumption
            severity: Impact severity
            justification: Why this assumption was made
            alternatives: Alternative assumptions that could be made
            
        Returns:
            The created Assumption
        """
        self._counter += 1
        assumption = Assumption(
            id=f"A{self._counter:03d}",
            content=content,
            type=assumption_type,
            severity=severity,
            justification=justification,
            alternatives=alternatives or [],
        )
        self._assumptions.append(assumption)
        return assumption
    
    def add_methodological(self, content: str, **kwargs) -> Assumption:
        """Add a methodological assumption."""
        return self.add(content, AssumptionType.METHODOLOGICAL, **kwargs)
    
    def add_theoretical(self, content: str, **kwargs) -> Assumption:
        """Add a theoretical assumption."""
        return self.add(content, AssumptionType.THEORETICAL, **kwargs)
    
    def add_data(self, content: str, **kwargs) -> Assumption:
        """Add a data assumption."""
        return self.add(content, AssumptionType.DATA, **kwargs)
    
    def add_scope(self, content: str, **kwargs) -> Assumption:
        """Add a scope assumption."""
        return self.add(content, AssumptionType.SCOPE, **kwargs)
    
    def get_all(self) -> List[Assumption]:
        """Get all tracked assumptions."""
        return self._assumptions.copy()
    
    def get_by_type(self, assumption_type: AssumptionType) -> List[Assumption]:
        """Get assumptions of a specific type."""
        return [a for a in self._assumptions if a.type == assumption_type]
    
    def get_high_severity(self) -> List[Assumption]:
        """Get high-severity assumptions."""
        return [a for a in self._assumptions if a.severity == AssumptionSeverity.HIGH]
    
    def link_to_conclusion(
        self,
        assumption_id: str,
        conclusion: str,
    ) -> None:
        """
        Link an assumption to an affected conclusion.
        
        Args:
            assumption_id: ID of the assumption
            conclusion: The affected conclusion
        """
        for assumption in self._assumptions:
            if assumption.id == assumption_id:
                assumption.affected_conclusions.append(conclusion)
                break
    
    def generate_disclosure(self, language: str = "en") -> str:
        """
        Generate assumption disclosure section.
        
        Args:
            language: Output language
            
        Returns:
            Formatted disclosure text
        """
        if not self._assumptions:
            if language == "ar":
                return "لا توجد افتراضات مسجلة."
            return "No assumptions recorded."
        
        if language == "ar":
            lines = ["## الافتراضات والقيود\n"]
            lines.append("تستند هذه التحليل إلى الافتراضات التالية:\n")
        else:
            lines = ["## Assumptions and Limitations\n"]
            lines.append("This analysis rests on the following assumptions:\n")
        
        # Group by type
        by_type: Dict[AssumptionType, List[Assumption]] = {}
        for a in self._assumptions:
            if a.type not in by_type:
                by_type[a.type] = []
            by_type[a.type].append(a)
        
        for a_type, assumptions in by_type.items():
            type_name = a_type.value.replace("_", " ").title()
            lines.append(f"\n### {type_name}\n")
            
            for a in assumptions:
                severity_marker = "⚠️ " if a.severity == AssumptionSeverity.HIGH else ""
                lines.append(f"- {severity_marker}{a.content}\n")
                
                if a.justification:
                    if language == "ar":
                        lines.append(f"  *التبرير: {a.justification}*\n")
                    else:
                        lines.append(f"  *Justification: {a.justification}*\n")
        
        return "".join(lines)
    
    def clear(self) -> None:
        """Clear all tracked assumptions."""
        self._assumptions = []
        self._counter = 0
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of tracked assumptions."""
        by_type = {}
        by_severity = {}
        
        for a in self._assumptions:
            by_type[a.type.value] = by_type.get(a.type.value, 0) + 1
            by_severity[a.severity.value] = by_severity.get(a.severity.value, 0) + 1
        
        return {
            "total": len(self._assumptions),
            "by_type": by_type,
            "by_severity": by_severity,
            "high_severity_count": len(self.get_high_severity()),
        }
