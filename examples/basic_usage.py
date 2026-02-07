"""
Basic Usage Example for Aquila-R.

Demonstrates core functionality of the research agent.
"""

from aquila_r import AquilaR, AquilaConfig
from aquila_r.core.config import MethodologyParadigm, OutputLanguage
from aquila_r.language import LanguageDetector, TechnicalGlossary
from aquila_r.methodology import AssumptionTracker, ClaimValidator


def example_basic_analysis():
    """Basic research analysis example."""
    print("=" * 60)
    print("EXAMPLE 1: Basic Research Analysis")
    print("=" * 60)
    
    # Initialize agent with default configuration
    agent = AquilaR()
    
    # Check status
    status = agent.get_status()
    print(f"\nAgent: {status['agent']} v{status['version']}")
    print(f"LLM Configured: {status['llm_configured']}")
    
    # Perform analysis
    query = "What are the main theoretical debates on state formation in the MENA region?"
    
    print(f"\nQuery: {query}\n")
    
    result = agent.analyze(
        query=query,
        modules=["literature", "synthesis", "critical"],
        methodology=MethodologyParadigm.INTERPRETIVIST,
    )
    
    # Print result
    print(result.to_markdown())


def example_arabic_analysis():
    """Arabic research analysis example."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Arabic Research Analysis")
    print("=" * 60)
    
    agent = AquilaR()
    
    # Arabic query
    query = "ما هي النظريات الرئيسية حول تشكل الدولة في المنطقة العربية؟"
    
    print(f"\nQuery: {query}\n")
    
    result = agent.analyze(
        query=query,
        output_language=OutputLanguage.ARABIC,
    )
    
    print(result.to_arabic_markdown())


def example_language_detection():
    """Language detection example."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Language Detection")
    print("=" * 60)
    
    detector = LanguageDetector()
    
    texts = [
        "The state formation process in the Arab world differs significantly from European models.",
        "تختلف عملية تشكل الدولة في العالم العربي اختلافاً كبيراً عن النماذج الأوروبية.",
        "The concept of دولة (dawla) has evolved over time in Arabic political thought.",
    ]
    
    for text in texts:
        score = detector.detect(text)
        print(f"\nText: {text[:50]}...")
        print(f"  Primary: {score.primary}")
        print(f"  English: {score.english:.2f}")
        print(f"  Arabic: {score.arabic:.2f}")
        print(f"  Mixed: {score.mixed}")


def example_glossary():
    """Technical glossary example."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Technical Glossary")
    print("=" * 60)
    
    glossary = TechnicalGlossary()
    
    # Show summary
    summary = glossary.get_summary()
    print(f"\nGlossary has {summary['total_entries']} entries")
    print(f"Domains: {', '.join(summary['domains'])}")
    
    # Look up terms
    terms = ["state", "governance", "civil society"]
    
    print("\nTerm lookups:")
    for term in terms:
        entry = glossary.get_entry(term)
        if entry:
            print(f"\n  {entry.term_en} → {entry.term_ar}")
            print(f"    Status: {entry.status.value}")
            if entry.usage_notes:
                print(f"    Note: {entry.usage_notes}")
    
    # Show contested terms
    print("\nContested terms:")
    for entry in glossary.get_contested():
        print(f"  - {entry.term_en}: {entry.usage_notes or 'No notes'}")


def example_assumption_tracking():
    """Assumption tracking example."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Assumption Tracking")
    print("=" * 60)
    
    tracker = AssumptionTracker()
    
    # Add assumptions
    tracker.add_methodological(
        "Analysis assumes sources in English and Arabic represent the field",
        justification="Limited access to other language sources",
    )
    
    tracker.add_theoretical(
        "State formation is treated as a contested historical process",
        justification="Following critical political economy approach",
    )
    
    tracker.add_data(
        "Historical data reliability varies by source",
    )
    
    # Generate disclosure
    disclosure = tracker.generate_disclosure()
    print(disclosure)
    
    # Summary
    summary = tracker.get_summary()
    print(f"\nTotal assumptions: {summary['total']}")
    print(f"By type: {summary['by_type']}")


def example_claim_validation():
    """Claim validation example."""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Claim Validation")
    print("=" * 60)
    
    validator = ClaimValidator()
    
    claims = [
        "Colonialism definitely caused state weakness in the region.",
        "The data suggests an association between oil wealth and authoritarianism.",
        "All Arab states follow the same developmental trajectory.",
        "Historical evidence indicates that state formation was influenced by external factors.",
    ]
    
    print("\nValidating claims:\n")
    
    for claim in claims:
        validation = validator.validate_claim(claim)
        print(f"Claim: {claim[:60]}...")
        print(f"  Status: {validation.status.value}")
        print(f"  Strength: {validation.strength.value}")
        if validation.issues:
            print(f"  Issues: {', '.join(validation.issues[:2])}")
        if validation.suggested_qualifications:
            print(f"  Suggestion: {validation.suggested_qualifications[0]}")
        print()


def example_project_memory():
    """Project memory example."""
    print("\n" + "=" * 60)
    print("EXAMPLE 7: Project Memory")
    print("=" * 60)
    
    agent = AquilaR()
    
    # Create a project
    project_id = agent.create_project(
        name="State Formation Study",
        description="Research on state formation in the MENA region",
    )
    
    print(f"Created project: {project_id}")
    
    # Add some sources to memory
    agent.memory.add_source(
        title="The Politics of State Formation",
        authors=["Lisa Anderson"],
        year=1987,
        source_type="journal",
        language="en",
    )
    
    agent.memory.record_finding(
        "European models of state formation have limited applicability to MENA",
        confidence=0.8,
    )
    
    agent.memory.record_assumption(
        "Colonial boundaries shape contemporary state structures",
    )
    
    # Get project summary
    summary = agent.get_project_summary()
    print(f"\nProject Summary:")
    print(f"  Name: {summary['name']}")
    print(f"  Sources: {summary['sources_count']}")
    print(f"  Findings: {summary['findings_count']}")
    print(f"  Assumptions: {len(summary['assumptions'])}")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("AQUILA-R: Research Agent Examples")
    print("=" * 60)
    
    # Run examples
    example_basic_analysis()
    example_arabic_analysis()
    example_language_detection()
    example_glossary()
    example_assumption_tracking()
    example_claim_validation()
    example_project_memory()
    
    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
