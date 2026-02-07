"""
Data & Evidence Reasoning Module for Aquila-R.

Responsible for:
- Analyzing tabular and statistical data
- Flagging data limitations and uncertainty
- Avoiding causal claims without justification
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
from pydantic import BaseModel, Field
import json

from aquila_r.modules.base import (
    BaseModule,
    ModuleContext,
    ModuleResult,
    ModuleStatus,
    Finding,
)


class EvidenceType(str, Enum):
    """Types of evidence."""
    STATISTICAL = "statistical"
    QUALITATIVE = "qualitative"
    OBSERVATIONAL = "observational"
    EXPERIMENTAL = "experimental"
    ANECDOTAL = "anecdotal"
    SURVEY = "survey"
    CASE_STUDY = "case_study"


class CausalClaim(str, Enum):
    """Types of causal claims."""
    CORRELATION = "correlation"
    ASSOCIATION = "association"
    CAUSATION = "causation"
    PREDICTION = "prediction"


class DataLimitation(BaseModel):
    """A limitation in the data."""
    
    description: str
    severity: str = Field(default="medium")
    affected_conclusions: List[str] = Field(default_factory=list)
    mitigation: Optional[str] = None


class StatisticalFinding(BaseModel):
    """A statistical finding from data analysis."""
    
    metric: str
    value: Union[float, int, str]
    interpretation: str
    confidence_interval: Optional[str] = None
    sample_size: Optional[int] = None
    p_value: Optional[float] = None
    effect_size: Optional[float] = None
    limitations: List[str] = Field(default_factory=list)


class CausalAnalysis(BaseModel):
    """Analysis of a causal claim."""
    
    claim: str
    claim_type: CausalClaim
    justified: bool = Field(default=False)
    justification: Optional[str] = None
    alternative_explanations: List[str] = Field(default_factory=list)
    confounders: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class EvidenceResult(ModuleResult):
    """Extended result for evidence module."""
    
    statistical_findings: List[StatisticalFinding] = Field(default_factory=list)
    data_limitations: List[DataLimitation] = Field(default_factory=list)
    causal_analyses: List[CausalAnalysis] = Field(default_factory=list)
    unjustified_claims: List[str] = Field(default_factory=list)
    uncertainty_notes: List[str] = Field(default_factory=list)
    
    def get_justified_causal_claims(self) -> List[CausalAnalysis]:
        """Get causal claims that are justified."""
        return [c for c in self.causal_analyses if c.justified]


class EvidenceModule(BaseModule):
    """
    Data & Evidence Reasoning Module.
    
    Analyzes data with explicit attention to limitations,
    uncertainty, and causal claim validity.
    """
    
    name = "evidence"
    description = "Data analysis, statistical reasoning, and causal claim validation"
    supported_languages = ["en", "ar"]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
    
    def execute(self, context: ModuleContext) -> EvidenceResult:
        """
        Execute evidence analysis.
        
        Args:
            context: Execution context
            
        Returns:
            EvidenceResult with findings and limitations
        """
        issues = self.validate_context(context)
        if issues:
            return EvidenceResult(
                module_name=self.name,
                status=ModuleStatus.FAILED,
                warnings=[self.create_warning(issue, "high") for issue in issues],
            )
        
        result = EvidenceResult(
            module_name=self.name,
            status=ModuleStatus.COMPLETED,
            language=context.language,
        )
        
        result.methodology_notes.append(
            "Evidence analysis explicitly flags data limitations and "
            "avoids causal claims without sufficient justification."
        )
        
        return result
    
    def validate_causal_claim(
        self,
        claim: str,
        evidence_type: EvidenceType,
        sample_size: Optional[int] = None,
        has_control_group: bool = False,
        has_randomization: bool = False,
        potential_confounders: Optional[List[str]] = None,
    ) -> CausalAnalysis:
        """
        Validate a causal claim against evidence standards.
        
        Args:
            claim: The causal claim being made
            evidence_type: Type of evidence supporting the claim
            sample_size: Sample size if applicable
            has_control_group: Whether a control group was used
            has_randomization: Whether randomization was used
            potential_confounders: Known potential confounders
            
        Returns:
            CausalAnalysis with validation results
        """
        analysis = CausalAnalysis(claim=claim, claim_type=CausalClaim.CORRELATION)
        confounders = potential_confounders or []
        
        # Determine claim type based on evidence
        if has_randomization and has_control_group:
            if evidence_type == EvidenceType.EXPERIMENTAL:
                analysis.claim_type = CausalClaim.CAUSATION
                analysis.justified = True
                analysis.justification = (
                    "Experimental design with randomization and control group "
                    "supports causal inference."
                )
            else:
                analysis.claim_type = CausalClaim.ASSOCIATION
        elif has_control_group:
            analysis.claim_type = CausalClaim.ASSOCIATION
            analysis.warnings.append(
                "Control group present but no randomization; "
                "claim is associative, not causal."
            )
        else:
            analysis.claim_type = CausalClaim.CORRELATION
            analysis.warnings.append(
                "Observational data without control group; "
                "correlation does not imply causation."
            )
        
        # Check sample size
        if sample_size is not None and sample_size < 30:
            analysis.justified = False
            analysis.warnings.append(
                f"Small sample size (n={sample_size}); "
                "insufficient for robust causal inference."
            )
        
        # Record confounders
        analysis.confounders = confounders
        if confounders:
            analysis.warnings.append(
                f"Potential confounders identified: {', '.join(confounders)}"
            )
        
        # Add alternative explanations
        if evidence_type == EvidenceType.OBSERVATIONAL:
            analysis.alternative_explanations.append(
                "Reverse causation: outcome may cause the predictor"
            )
            analysis.alternative_explanations.append(
                "Omitted variable bias: unobserved factors may explain relationship"
            )
        
        return analysis
    
    def assess_data_quality(
        self,
        data_description: str,
        sample_size: Optional[int] = None,
        missing_rate: Optional[float] = None,
        collection_method: Optional[str] = None,
        time_period: Optional[str] = None,
    ) -> List[DataLimitation]:
        """
        Assess data quality and identify limitations.
        
        Args:
            data_description: Description of the data
            sample_size: Number of observations
            missing_rate: Rate of missing data (0-1)
            collection_method: How data was collected
            time_period: Time period covered
            
        Returns:
            List of identified limitations
        """
        limitations = []
        
        # Sample size assessment
        if sample_size is not None:
            if sample_size < 30:
                limitations.append(DataLimitation(
                    description=f"Very small sample size (n={sample_size}); "
                               "statistical power is severely limited",
                    severity="high",
                    affected_conclusions=["All statistical inferences"],
                    mitigation="Interpret findings as exploratory only",
                ))
            elif sample_size < 100:
                limitations.append(DataLimitation(
                    description=f"Small sample size (n={sample_size}); "
                               "subgroup analyses may be unreliable",
                    severity="medium",
                    mitigation="Avoid subgroup analyses; focus on main effects",
                ))
        
        # Missing data
        if missing_rate is not None and missing_rate > 0:
            if missing_rate > 0.2:
                limitations.append(DataLimitation(
                    description=f"High missing data rate ({missing_rate:.0%}); "
                               "results may be biased",
                    severity="high",
                    affected_conclusions=["Estimates may not represent full population"],
                    mitigation="Consider multiple imputation or sensitivity analysis",
                ))
            elif missing_rate > 0.05:
                limitations.append(DataLimitation(
                    description=f"Moderate missing data ({missing_rate:.0%})",
                    severity="medium",
                    mitigation="Report missingness patterns",
                ))
        
        return limitations
    
    def flag_unjustified_claims(
        self,
        claims: List[str],
        evidence_available: Dict[str, Any],
    ) -> List[str]:
        """
        Identify claims that lack sufficient justification.
        
        Args:
            claims: List of claims to evaluate
            evidence_available: Available evidence
            
        Returns:
            List of unjustified claims
        """
        unjustified = []
        
        causal_indicators = [
            "causes", "leads to", "results in", "produces",
            "determines", "creates", "generates", "makes"
        ]
        
        for claim in claims:
            claim_lower = claim.lower()
            
            # Check for causal language
            has_causal_language = any(
                indicator in claim_lower for indicator in causal_indicators
            )
            
            if has_causal_language:
                # Check if experimental evidence exists
                has_experimental = evidence_available.get("experimental", False)
                
                if not has_experimental:
                    unjustified.append(
                        f"CAUSAL CLAIM WITHOUT EXPERIMENTAL EVIDENCE: {claim}"
                    )
        
        return unjustified
    
    def format_uncertainty(
        self,
        value: float,
        uncertainty: float,
        units: str = "",
        language: str = "en",
    ) -> str:
        """
        Format a value with uncertainty.
        
        Args:
            value: Central value
            uncertainty: Uncertainty (±)
            units: Units of measurement
            language: Output language
            
        Returns:
            Formatted string with uncertainty
        """
        if language == "ar":
            return f"{value:.2f} ± {uncertainty:.2f} {units}"
        return f"{value:.2f} ± {uncertainty:.2f} {units}"
