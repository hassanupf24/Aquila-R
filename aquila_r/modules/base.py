"""
Base module classes for Aquila-R research modules.

Provides the foundational abstractions that all research
modules must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class ModuleStatus(str, Enum):
    """Status of module execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ConfidenceLevel(str, Enum):
    """Confidence levels for findings."""
    VERY_HIGH = "very_high"  # 0.9+
    HIGH = "high"            # 0.7-0.9
    MEDIUM = "medium"        # 0.5-0.7
    LOW = "low"              # 0.3-0.5
    VERY_LOW = "very_low"    # <0.3
    
    @classmethod
    def from_score(cls, score: float) -> "ConfidenceLevel":
        """Convert numeric score to confidence level."""
        if score >= 0.9:
            return cls.VERY_HIGH
        elif score >= 0.7:
            return cls.HIGH
        elif score >= 0.5:
            return cls.MEDIUM
        elif score >= 0.3:
            return cls.LOW
        return cls.VERY_LOW


class Finding(BaseModel):
    """A research finding from a module."""
    
    content: str = Field(description="The finding content")
    confidence: float = Field(ge=0.0, le=1.0)
    source_id: Optional[str] = Field(default=None)
    evidence_type: str = Field(default="general")
    language: str = Field(default="en")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @property
    def confidence_level(self) -> ConfidenceLevel:
        """Get confidence as categorical level."""
        return ConfidenceLevel.from_score(self.confidence)


class Warning(BaseModel):
    """A warning or caveat from module execution."""
    
    message: str = Field(description="Warning message")
    severity: str = Field(default="medium")  # low, medium, high
    category: str = Field(default="general")


class Limitation(BaseModel):
    """An identified limitation."""
    
    description: str = Field(description="Limitation description")
    impact: str = Field(default="medium")  # low, medium, high
    mitigation: Optional[str] = Field(default=None)


class ModuleResult(BaseModel):
    """Result from a module execution."""
    
    module_name: str = Field(description="Name of the module")
    status: ModuleStatus = Field(default=ModuleStatus.COMPLETED)
    findings: List[Finding] = Field(default_factory=list)
    warnings: List[Warning] = Field(default_factory=list)
    limitations: List[Limitation] = Field(default_factory=list)
    sources_consulted: List[str] = Field(default_factory=list)
    execution_time_ms: Optional[int] = Field(default=None)
    language: str = Field(default="en")
    methodology_notes: List[str] = Field(default_factory=list)
    raw_data: Optional[Dict[str, Any]] = Field(default=None)
    executed_at: datetime = Field(default_factory=datetime.utcnow)
    
    def get_high_confidence_findings(self) -> List[Finding]:
        """Get findings with high or very high confidence."""
        return [f for f in self.findings if f.confidence >= 0.7]
    
    def get_warnings_by_severity(self, severity: str) -> List[Warning]:
        """Get warnings of specific severity."""
        return [w for w in self.warnings if w.severity == severity]
    
    def to_summary(self, lang: str = "en") -> str:
        """Generate a summary of the result."""
        if lang == "ar":
            return self._to_arabic_summary()
        return self._to_english_summary()
    
    def _to_english_summary(self) -> str:
        """Generate English summary."""
        lines = [f"## {self.module_name} Results\n"]
        lines.append(f"Status: {self.status.value}\n")
        lines.append(f"Findings: {len(self.findings)}\n")
        
        if self.findings:
            lines.append("\n### Key Findings:\n")
            for i, f in enumerate(self.findings[:5], 1):
                conf = f.confidence_level.value
                lines.append(f"{i}. [{conf}] {f.content[:200]}...\n")
        
        if self.warnings:
            lines.append(f"\n⚠️ Warnings: {len(self.warnings)}\n")
        
        if self.limitations:
            lines.append(f"\n📋 Limitations: {len(self.limitations)}\n")
        
        return "".join(lines)
    
    def _to_arabic_summary(self) -> str:
        """Generate Arabic summary."""
        lines = [f"## نتائج {self.module_name}\n"]
        lines.append(f"الحالة: {self.status.value}\n")
        lines.append(f"النتائج: {len(self.findings)}\n")
        
        if self.findings:
            lines.append("\n### النتائج الرئيسية:\n")
            for i, f in enumerate(self.findings[:5], 1):
                lines.append(f"{i}. {f.content[:200]}...\n")
        
        return "".join(lines)


class ModuleContext(BaseModel):
    """Context passed to module during execution."""
    
    query: str = Field(description="Research query")
    language: str = Field(default="en")
    methodology: str = Field(default="mixed")
    max_sources: int = Field(default=20)
    previous_findings: List[Finding] = Field(default_factory=list)
    constraints: Dict[str, Any] = Field(default_factory=dict)


class BaseModule(ABC):
    """
    Base class for all Aquila-R research modules.
    
    All modules must implement the execute method and
    follow the epistemic standards defined in agent identity.
    """
    
    name: str = "base_module"
    description: str = "Base module"
    supported_languages: List[str] = ["en", "ar"]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the module.
        
        Args:
            config: Module-specific configuration
        """
        self.config = config or {}
        self._initialized = False
    
    @abstractmethod
    def execute(self, context: ModuleContext) -> ModuleResult:
        """
        Execute the module's research function.
        
        Args:
            context: Execution context with query and parameters
            
        Returns:
            ModuleResult with findings, warnings, and limitations
        """
        pass
    
    def validate_context(self, context: ModuleContext) -> List[str]:
        """
        Validate the execution context.
        
        Args:
            context: Context to validate
            
        Returns:
            List of validation issues (empty if valid)
        """
        issues = []
        
        if not context.query.strip():
            issues.append("Query cannot be empty")
        
        if context.language not in self.supported_languages:
            issues.append(
                f"Language '{context.language}' not supported. "
                f"Supported: {self.supported_languages}"
            )
        
        return issues
    
    def create_finding(
        self,
        content: str,
        confidence: float,
        source_id: Optional[str] = None,
        evidence_type: str = "general",
        language: str = "en",
        **metadata,
    ) -> Finding:
        """
        Create a finding with proper structure.
        
        Args:
            content: Finding content
            confidence: Confidence score (0-1)
            source_id: Optional source reference
            evidence_type: Type of evidence
            language: Content language
            **metadata: Additional metadata
            
        Returns:
            Structured Finding object
        """
        return Finding(
            content=content,
            confidence=confidence,
            source_id=source_id,
            evidence_type=evidence_type,
            language=language,
            metadata=metadata,
        )
    
    def create_warning(
        self,
        message: str,
        severity: str = "medium",
        category: str = "general",
    ) -> Warning:
        """Create a warning."""
        return Warning(
            message=message,
            severity=severity,
            category=category,
        )
    
    def create_limitation(
        self,
        description: str,
        impact: str = "medium",
        mitigation: Optional[str] = None,
    ) -> Limitation:
        """Create a limitation note."""
        return Limitation(
            description=description,
            impact=impact,
            mitigation=mitigation,
        )
    
    def _empty_result(self, status: ModuleStatus = ModuleStatus.COMPLETED) -> ModuleResult:
        """Create an empty result."""
        return ModuleResult(
            module_name=self.name,
            status=status,
        )
