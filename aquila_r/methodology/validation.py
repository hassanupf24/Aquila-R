"""
Claim Validation for Aquila-R.

Validates claims against evidence and methodological standards,
flagging overstatements and unsupported assertions.
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime


class ClaimType(str, Enum):
    """Types of claims."""
    FACTUAL = "factual"
    INTERPRETIVE = "interpretive"
    CAUSAL = "causal"
    PREDICTIVE = "predictive"
    NORMATIVE = "normative"
    METHODOLOGICAL = "methodological"


class ClaimStrength(str, Enum):
    """Strength of a claim."""
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    UNSUPPORTED = "unsupported"


class ValidationStatus(str, Enum):
    """Validation status."""
    VALID = "valid"
    REQUIRES_QUALIFICATION = "requires_qualification"
    OVERSTATED = "overstated"
    UNSUPPORTED = "unsupported"
    NEEDS_EVIDENCE = "needs_evidence"


class ClaimValidation(BaseModel):
    """Validation result for a claim."""
    
    claim: str
    claim_type: ClaimType
    status: ValidationStatus
    strength: ClaimStrength
    issues: List[str] = Field(default_factory=list)
    suggested_qualifications: List[str] = Field(default_factory=list)
    evidence_strength: Optional[str] = Field(default=None)
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)


class ValidationResult(BaseModel):
    """Overall validation result."""
    
    total_claims: int = Field(default=0)
    valid_claims: int = Field(default=0)
    problematic_claims: int = Field(default=0)
    claim_validations: List[ClaimValidation] = Field(default_factory=list)
    summary: str = Field(default="")
    
    def get_overstated(self) -> List[ClaimValidation]:
        """Get overstated claims."""
        return [c for c in self.claim_validations if c.status == ValidationStatus.OVERSTATED]
    
    def get_unsupported(self) -> List[ClaimValidation]:
        """Get unsupported claims."""
        return [c for c in self.claim_validations if c.status == ValidationStatus.UNSUPPORTED]


class ClaimValidator:
    """
    Validates claims for epistemic rigor.
    
    Checks claims against evidence standards and flags
    overstatements, unsupported claims, and claims
    needing qualification.
    """
    
    # Overstatement indicators
    OVERSTATEMENT_TERMS = [
        "proves", "definitively", "certainly", "undoubtedly",
        "clearly demonstrates", "without question", "obviously",
        "unquestionably", "indisputably", "always", "never",
        "all", "none", "every", "completely"
    ]
    
    # Arabic overstatement terms
    OVERSTATEMENT_TERMS_AR = [
        "يثبت بشكل قاطع", "بالتأكيد", "بلا شك",
        "يوضح بشكل واضح", "دائماً", "أبداً",
        "كل", "جميع", "بلا استثناء"
    ]
    
    # Hedging terms (good practice)
    HEDGING_TERMS = [
        "suggests", "indicates", "may", "might", "could",
        "appears to", "seems to", "tends to", "generally",
        "often", "typically", "in many cases"
    ]
    
    HEDGING_TERMS_AR = [
        "يشير إلى", "قد", "ربما", "يبدو",
        "عادةً", "غالباً", "في معظم الحالات"
    ]
    
    def __init__(self):
        """Initialize the validator."""
        pass
    
    def validate_claim(
        self,
        claim: str,
        evidence: Optional[str] = None,
        claim_type: Optional[ClaimType] = None,
        language: str = "en",
    ) -> ClaimValidation:
        """
        Validate a single claim.
        
        Args:
            claim: The claim to validate
            evidence: Supporting evidence if available
            claim_type: Type of claim
            language: Language of the claim
            
        Returns:
            ClaimValidation with status and issues
        """
        # Detect claim type if not provided
        if claim_type is None:
            claim_type = self._detect_claim_type(claim)
        
        validation = ClaimValidation(
            claim=claim,
            claim_type=claim_type,
            status=ValidationStatus.VALID,
            strength=ClaimStrength.MODERATE,
        )
        
        # Check for overstatement
        overstatement_terms = (
            self.OVERSTATEMENT_TERMS_AR if language == "ar" 
            else self.OVERSTATEMENT_TERMS
        )
        
        claim_lower = claim.lower()
        for term in overstatement_terms:
            if term in claim_lower:
                validation.status = ValidationStatus.OVERSTATED
                validation.issues.append(f"Overstatement term '{term}' used")
                validation.suggested_qualifications.append(
                    f"Consider replacing '{term}' with hedging language"
                )
                validation.strength = ClaimStrength.WEAK
        
        # Check for evidence
        if evidence:
            validation.evidence_strength = "provided"
            if validation.status == ValidationStatus.VALID:
                validation.strength = ClaimStrength.MODERATE
        else:
            validation.issues.append("No evidence provided for claim")
            if validation.status == ValidationStatus.VALID:
                validation.status = ValidationStatus.NEEDS_EVIDENCE
        
        # Causal claims require stronger evidence
        if claim_type == ClaimType.CAUSAL:
            causal_terms = ["causes", "leads to", "results in", "produces"]
            has_causal = any(t in claim_lower for t in causal_terms)
            
            if has_causal and not evidence:
                validation.status = ValidationStatus.UNSUPPORTED
                validation.issues.append(
                    "Causal claim made without supporting evidence"
                )
                validation.suggested_qualifications.append(
                    "Use associative language unless causation is established"
                )
        
        # Calculate confidence
        if validation.status == ValidationStatus.VALID:
            validation.confidence = 0.8
        elif validation.status == ValidationStatus.REQUIRES_QUALIFICATION:
            validation.confidence = 0.6
        elif validation.status == ValidationStatus.OVERSTATED:
            validation.confidence = 0.4
        else:
            validation.confidence = 0.2
        
        return validation
    
    def validate_claims(
        self,
        claims: List[str],
        language: str = "en",
    ) -> ValidationResult:
        """
        Validate multiple claims.
        
        Args:
            claims: List of claims to validate
            language: Language of claims
            
        Returns:
            ValidationResult with all validations
        """
        result = ValidationResult(total_claims=len(claims))
        
        for claim in claims:
            validation = self.validate_claim(claim, language=language)
            result.claim_validations.append(validation)
            
            if validation.status == ValidationStatus.VALID:
                result.valid_claims += 1
            else:
                result.problematic_claims += 1
        
        # Generate summary
        result.summary = self._generate_summary(result, language)
        
        return result
    
    def _detect_claim_type(self, claim: str) -> ClaimType:
        """Detect the type of claim."""
        claim_lower = claim.lower()
        
        # Causal indicators
        if any(t in claim_lower for t in ["causes", "leads to", "results in"]):
            return ClaimType.CAUSAL
        
        # Predictive indicators
        if any(t in claim_lower for t in ["will", "predicts", "forecast"]):
            return ClaimType.PREDICTIVE
        
        # Normative indicators
        if any(t in claim_lower for t in ["should", "ought", "must", "need to"]):
            return ClaimType.NORMATIVE
        
        # Default to interpretive for complex claims, factual for simple
        if len(claim.split()) > 15:
            return ClaimType.INTERPRETIVE
        
        return ClaimType.FACTUAL
    
    def _generate_summary(self, result: ValidationResult, language: str) -> str:
        """Generate validation summary."""
        if language == "ar":
            return (
                f"المجموع: {result.total_claims} ادعاءات، "
                f"{result.valid_claims} صالحة، "
                f"{result.problematic_claims} تحتاج مراجعة"
            )
        
        return (
            f"Total: {result.total_claims} claims, "
            f"{result.valid_claims} valid, "
            f"{result.problematic_claims} require attention"
        )
    
    def suggest_hedging(self, claim: str, language: str = "en") -> str:
        """
        Suggest hedging for a claim.
        
        Args:
            claim: The claim to hedge
            language: Output language
            
        Returns:
            Suggested hedged version
        """
        # Replace strong terms with hedged alternatives
        replacements = {
            "proves": "suggests",
            "shows": "indicates",
            "demonstrates": "appears to demonstrate",
            "is": "may be",
            "causes": "is associated with",
            "always": "often",
            "never": "rarely",
        }
        
        hedged = claim
        for strong, hedge in replacements.items():
            if strong in hedged.lower():
                hedged = hedged.replace(strong, hedge)
                hedged = hedged.replace(strong.capitalize(), hedge.capitalize())
        
        return hedged
    
    def check_epistemic_standard(
        self,
        text: str,
        language: str = "en",
    ) -> Dict[str, Any]:
        """
        Check text against epistemic standards.
        
        Args:
            text: Text to check
            language: Language of text
            
        Returns:
            Dictionary with standard checks
        """
        hedging_terms = (
            self.HEDGING_TERMS_AR if language == "ar" 
            else self.HEDGING_TERMS
        )
        overstatement = (
            self.OVERSTATEMENT_TERMS_AR if language == "ar" 
            else self.OVERSTATEMENT_TERMS
        )
        
        text_lower = text.lower()
        
        hedging_count = sum(1 for t in hedging_terms if t in text_lower)
        overstatement_count = sum(1 for t in overstatement if t in text_lower)
        
        # Calculate ratio
        if hedging_count + overstatement_count == 0:
            ratio = 1.0
        else:
            ratio = hedging_count / (hedging_count + overstatement_count)
        
        return {
            "hedging_instances": hedging_count,
            "overstatement_instances": overstatement_count,
            "epistemic_ratio": ratio,
            "assessment": (
                "Good epistemic practice" if ratio > 0.6 
                else "Consider more hedging"
            ),
        }
