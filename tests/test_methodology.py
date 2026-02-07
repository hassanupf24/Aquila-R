"""
Test suite for Aquila-R methodology components.
"""

import pytest
from aquila_r.methodology import (
    MethodologyFramework,
    ResearchParadigm,
    AssumptionTracker,
    AssumptionType,
    AssumptionSeverity,
    ClaimValidator,
    ClaimType,
    ValidationStatus,
)


class TestMethodologyFramework:
    """Tests for methodology framework."""
    
    def test_framework_initialization(self):
        """Test framework loads paradigms."""
        framework = MethodologyFramework()
        paradigms = framework.get_all_paradigms()
        
        assert len(paradigms) > 0
    
    def test_get_paradigm(self):
        """Test getting a specific paradigm."""
        framework = MethodologyFramework()
        desc = framework.get_paradigm(ResearchParadigm.POSITIVIST)
        
        assert desc is not None
        assert desc.name_en == "Positivism"
        assert len(desc.key_assumptions) > 0
        assert len(desc.common_methods) > 0
    
    def test_compare_paradigms(self):
        """Test comparing paradigms."""
        framework = MethodologyFramework()
        comparison = framework.compare_paradigms(
            ResearchParadigm.POSITIVIST,
            ResearchParadigm.INTERPRETIVIST,
        )
        
        assert "paradigm_a" in comparison
        assert "paradigm_b" in comparison
        assert "complementary_aspects" in comparison


class TestAssumptionTracker:
    """Tests for assumption tracking."""
    
    def test_add_assumption(self):
        """Test adding assumptions."""
        tracker = AssumptionTracker()
        tracker.add_methodological("Test assumption")
        
        assumptions = tracker.get_all()
        assert len(assumptions) == 1
        assert assumptions[0].type == AssumptionType.METHODOLOGICAL
    
    def test_severity_levels(self):
        """Test assumption severity."""
        tracker = AssumptionTracker()
        tracker.add(
            "Critical assumption",
            severity=AssumptionSeverity.HIGH,
        )
        
        high_severity = tracker.get_high_severity()
        assert len(high_severity) == 1
    
    def test_disclosure_generation(self):
        """Test generating disclosure statement."""
        tracker = AssumptionTracker()
        tracker.add_methodological("Method assumption")
        tracker.add_theoretical("Theory assumption")
        
        disclosure = tracker.generate_disclosure()
        
        assert "Assumptions" in disclosure
        assert "Methodological" in disclosure
        assert "Theoretical" in disclosure


class TestClaimValidator:
    """Tests for claim validation."""
    
    def test_valid_claim(self):
        """Test validating a reasonable claim."""
        validator = ClaimValidator()
        validation = validator.validate_claim(
            "The data suggests a potential correlation.",
            evidence="Study A",
        )
        
        assert validation.status == ValidationStatus.VALID
        # "suggests" is a hedging term, so no overstatement
    
    def test_overstatement_detection(self):
        """Test detecting overstatement."""
        validator = ClaimValidator()
        validation = validator.validate_claim(
            "This assumes creates a definite proof and always works."
        )
        
        # "definite proof" or similar strong language might trigger overstatement depending on the list
        # "always" is in the overstatement list
        assert validation.status == ValidationStatus.OVERSTATED
        assert len(validation.issues) > 0
    
    def test_causal_claim_check(self):
        """Test causal claim validation."""
        validator = ClaimValidator()
        validation = validator.validate_claim(
            "X causes Y to happen.",
            evidence=None,  # No evidence provided
        )
        
        assert validation.claim_type == ClaimType.CAUSAL
        assert validation.status == ValidationStatus.UNSUPPORTED
    
    def test_hedging_suggestions(self):
        """Test hedging suggestions."""
        validator = ClaimValidator()
        hedged = validator.suggest_hedging("This proves that X is true.")
        
        assert "suggests" in hedged or "indicates" in hedged
        assert "proves" not in hedged


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
