"""
Critical Evaluation Module for Aquila-R.

Responsible for:
- Testing logical consistency of arguments
- Detecting bias (ideological, geographic, disciplinary)
- Assessing methodological quality
- Highlighting weak or unsupported claims
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field

from aquila_r.modules.base import (
    BaseModule,
    ModuleContext,
    ModuleResult,
    ModuleStatus,
    Finding,
)


class BiasType(str, Enum):
    """Types of bias to detect."""
    IDEOLOGICAL = "ideological"
    GEOGRAPHIC = "geographic"
    DISCIPLINARY = "disciplinary"
    TEMPORAL = "temporal"
    SELECTION = "selection"
    CONFIRMATION = "confirmation"
    PUBLICATION = "publication"
    LANGUAGE = "language"


class ArgumentStrength(str, Enum):
    """Strength assessment of an argument."""
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    UNSUPPORTED = "unsupported"


class LogicalFallacy(str, Enum):
    """Common logical fallacies to detect."""
    AD_HOMINEM = "ad_hominem"
    STRAW_MAN = "straw_man"
    FALSE_DILEMMA = "false_dilemma"
    APPEAL_TO_AUTHORITY = "appeal_to_authority"
    CIRCULAR_REASONING = "circular_reasoning"
    HASTY_GENERALIZATION = "hasty_generalization"
    POST_HOC = "post_hoc"
    SLIPPERY_SLOPE = "slippery_slope"
    FALSE_EQUIVALENCE = "false_equivalence"


class BiasIndicator(BaseModel):
    """An identified bias indicator."""
    
    bias_type: BiasType
    description: str
    severity: str = Field(default="medium")  # low, medium, high
    evidence: str = Field(default="")
    source_id: Optional[str] = None


class ArgumentEvaluation(BaseModel):
    """Evaluation of an argument."""
    
    claim: str
    strength: ArgumentStrength
    evidence_provided: bool = Field(default=False)
    evidence_quality: str = Field(default="unknown")
    logical_issues: List[str] = Field(default_factory=list)
    fallacies: List[LogicalFallacy] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    counter_evidence: List[str] = Field(default_factory=list)


class MethodologicalAssessment(BaseModel):
    """Assessment of methodological quality."""
    
    methodology_stated: bool = Field(default=False)
    methodology_appropriate: Optional[bool] = Field(default=None)
    sample_adequate: Optional[bool] = Field(default=None)
    limitations_acknowledged: bool = Field(default=False)
    replicable: Optional[bool] = Field(default=None)
    quality_score: float = Field(ge=0.0, le=1.0, default=0.5)
    notes: List[str] = Field(default_factory=list)


class CriticalResult(ModuleResult):
    """Extended result for critical evaluation module."""
    
    arguments: List[ArgumentEvaluation] = Field(default_factory=list)
    biases: List[BiasIndicator] = Field(default_factory=list)
    methodology_assessment: Optional[MethodologicalAssessment] = None
    weak_claims: List[str] = Field(default_factory=list)
    unsupported_claims: List[str] = Field(default_factory=list)
    
    def get_argument_summary(self) -> Dict[str, int]:
        """Summarize arguments by strength."""
        summary: Dict[str, int] = {}
        for arg in self.arguments:
            strength = arg.strength.value
            summary[strength] = summary.get(strength, 0) + 1
        return summary
    
    def get_bias_summary(self) -> Dict[str, int]:
        """Summarize biases by type."""
        summary: Dict[str, int] = {}
        for bias in self.biases:
            b_type = bias.bias_type.value
            summary[b_type] = summary.get(b_type, 0) + 1
        return summary


class CriticalModule(BaseModule):
    """
    Critical Evaluation Module.
    
    Performs rigorous evaluation of arguments, evidence,
    and methodology with explicit bias detection.
    """
    
    name = "critical"
    description = "Critical evaluation of arguments, bias detection, and methodological assessment"
    supported_languages = ["en", "ar"]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._fallacy_patterns: Dict[LogicalFallacy, List[str]] = {}
    
    def execute(self, context: ModuleContext) -> CriticalResult:
        """
        Execute critical evaluation.
        
        Args:
            context: Execution context
            
        Returns:
            CriticalResult with evaluations and biases
        """
        issues = self.validate_context(context)
        if issues:
            return CriticalResult(
                module_name=self.name,
                status=ModuleStatus.FAILED,
                warnings=[self.create_warning(issue, "high") for issue in issues],
            )
        
        result = CriticalResult(
            module_name=self.name,
            status=ModuleStatus.COMPLETED,
            language=context.language,
        )
        
        # Add methodology notes
        result.methodology_notes.append(
            "Critical evaluation follows epistemic standards requiring "
            "evidence-backed claims and explicit assumption declaration."
        )
        
        # Add warning about LLM requirement
        result.warnings.append(self.create_warning(
            "Full critical evaluation requires LLM integration for "
            "argument analysis and bias detection.",
            severity="medium",
            category="llm_integration",
        ))
        
        return result
    
    def evaluate_argument(
        self,
        claim: str,
        evidence: Optional[str] = None,
        source_context: Optional[str] = None,
    ) -> ArgumentEvaluation:
        """
        Evaluate a single argument.
        
        Args:
            claim: The claim being made
            evidence: Evidence provided for the claim
            source_context: Context from the source
            
        Returns:
            ArgumentEvaluation with strength and issues
        """
        # Determine if evidence is provided
        evidence_provided = evidence is not None and len(evidence.strip()) > 0
        
        # Initial strength assessment
        if not evidence_provided:
            strength = ArgumentStrength.UNSUPPORTED
            evidence_quality = "none"
        else:
            strength = ArgumentStrength.MODERATE
            evidence_quality = "requires_assessment"
        
        evaluation = ArgumentEvaluation(
            claim=claim,
            strength=strength,
            evidence_provided=evidence_provided,
            evidence_quality=evidence_quality,
        )
        
        # Check for overstatement indicators
        overstatement_terms = [
            "proves", "definitively", "certainly", "undoubtedly",
            "clearly shows", "without question", "obviously"
        ]
        claim_lower = claim.lower()
        for term in overstatement_terms:
            if term in claim_lower:
                evaluation.logical_issues.append(
                    f"Potential overstatement: '{term}' used without sufficient qualification"
                )
                if strength == ArgumentStrength.MODERATE:
                    evaluation.strength = ArgumentStrength.WEAK
        
        # Express assumptions if claim contains implicit conditions
        conditional_terms = ["all", "every", "always", "never", "none"]
        for term in conditional_terms:
            if term in claim_lower:
                evaluation.assumptions.append(
                    f"Universal claim ('{term}') assumes no exceptions exist"
                )
        
        return evaluation
    
    def detect_bias(
        self,
        content: str,
        source_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[BiasIndicator]:
        """
        Detect potential biases in content.
        
        Args:
            content: Text content to analyze
            source_metadata: Metadata about the source
            
        Returns:
            List of identified bias indicators
        """
        biases = []
        content_lower = content.lower()
        
        # Geographic bias indicators
        western_centric_terms = [
            "the west", "western values", "developed countries",
            "modern societies", "advanced nations"
        ]
        for term in western_centric_terms:
            if term in content_lower:
                biases.append(BiasIndicator(
                    bias_type=BiasType.GEOGRAPHIC,
                    description=f"Potential Western-centric framing detected: '{term}'",
                    severity="medium",
                    evidence=f"Term '{term}' found in content",
                ))
        
        # Language bias
        if source_metadata:
            sources_languages = source_metadata.get("source_languages", [])
            if sources_languages and "ar" not in sources_languages:
                biases.append(BiasIndicator(
                    bias_type=BiasType.LANGUAGE,
                    description="Analysis based primarily on English-language sources; "
                               "Arabic perspectives may be underrepresented",
                    severity="medium",
                ))
        
        return biases
    
    def assess_methodology(
        self,
        methodology_text: Optional[str] = None,
        sample_size: Optional[int] = None,
        time_period: Optional[str] = None,
        data_sources: Optional[List[str]] = None,
    ) -> MethodologicalAssessment:
        """
        Assess methodological quality.
        
        Args:
            methodology_text: Description of methodology
            sample_size: Sample size if applicable
            time_period: Time period covered
            data_sources: Data sources used
            
        Returns:
            MethodologicalAssessment with quality score
        """
        assessment = MethodologicalAssessment()
        
        # Check if methodology is stated
        assessment.methodology_stated = (
            methodology_text is not None and len(methodology_text.strip()) > 0
        )
        
        if not assessment.methodology_stated:
            assessment.notes.append(
                "No methodology explicitly stated; "
                "unable to assess appropriateness"
            )
            assessment.quality_score = 0.3
            return assessment
        
        # Assess sample adequacy
        if sample_size is not None:
            if sample_size < 30:
                assessment.sample_adequate = False
                assessment.notes.append(
                    f"Small sample size (n={sample_size}); "
                    "statistical power may be limited"
                )
            else:
                assessment.sample_adequate = True
        
        # Check for limitations acknowledgment
        if methodology_text:
            limitation_terms = ["limitation", "constraint", "caveat", "weakness"]
            assessment.limitations_acknowledged = any(
                term in methodology_text.lower() for term in limitation_terms
            )
            
            if not assessment.limitations_acknowledged:
                assessment.notes.append(
                    "No limitations explicitly acknowledged in methodology"
                )
        
        # Calculate quality score
        score = 0.5  # Base score
        if assessment.methodology_stated:
            score += 0.2
        if assessment.sample_adequate:
            score += 0.15
        if assessment.limitations_acknowledged:
            score += 0.15
        
        assessment.quality_score = min(score, 1.0)
        
        return assessment
    
    def identify_weak_claims(
        self,
        claims: List[str],
    ) -> tuple[List[str], List[str]]:
        """
        Identify weak and unsupported claims.
        
        Args:
            claims: List of claims to evaluate
            
        Returns:
            Tuple of (weak_claims, unsupported_claims)
        """
        weak_claims = []
        unsupported_claims = []
        
        for claim in claims:
            evaluation = self.evaluate_argument(claim)
            
            if evaluation.strength == ArgumentStrength.UNSUPPORTED:
                unsupported_claims.append(claim)
            elif evaluation.strength == ArgumentStrength.WEAK:
                weak_claims.append(claim)
        
        return weak_claims, unsupported_claims
