"""
Test suite for Aquila-R language components.
"""

import pytest

from aquila_r.language import (
    LanguageDetector,
    ConceptualTranslator,
    TechnicalGlossary,
    GlossaryEntry,
)
from aquila_r.language.translator import TranslationConfidence


class TestLanguageDetector:
    """Tests for language detector."""
    
    def test_english_detection(self):
        """Test English text detection."""
        detector = LanguageDetector()
        
        score = detector.detect("This is a test sentence in English.")
        
        assert score.primary == "en"
        assert score.english > 0.9
        assert not score.mixed
    
    def test_arabic_detection(self):
        """Test Arabic text detection."""
        detector = LanguageDetector()
        
        score = detector.detect("هذه جملة اختبار باللغة العربية.")
        
        assert score.primary == "ar"
        assert score.arabic > 0.9
        assert not score.mixed
    
    def test_mixed_content(self):
        """Test mixed language detection."""
        detector = LanguageDetector()
        
        score = detector.detect(
            "The concept of دولة (state) is complex في التاريخ العربي."
        )
        
        assert score.mixed
    
    def test_empty_text(self):
        """Test empty text handling."""
        detector = LanguageDetector()
        
        score = detector.detect("")
        
        assert score.primary == "unknown"
        assert score.confidence == 0.0
    
    def test_helper_methods(self):
        """Test helper methods."""
        detector = LanguageDetector()
        
        assert detector.is_english("This is English")
        assert detector.is_arabic("هذا عربي")
        assert detector.get_primary_language("Hello world") == "en"


class TestConceptualTranslator:
    """Tests for conceptual translator."""
    
    def test_same_language(self):
        """Test translation when source and target are same."""
        translator = ConceptualTranslator()
        
        result = translator.translate(
            text="Test text",
            source_lang="en",
            target_lang="en",
        )
        
        assert result.source_text == result.target_text
        assert result.confidence == TranslationConfidence.HIGH
    
    def test_untranslatable_detection(self):
        """Test detection of untranslatable terms."""
        translator = ConceptualTranslator()
        
        flags = translator.flag_untranslatable(
            "The concept of governance is complex.",
            source_lang="en",
        )
        
        assert len(flags) > 0
        assert any(f["term"] == "governance" for f in flags)
    
    def test_contested_term_lookup(self):
        """Test looking up contested terms."""
        translator = ConceptualTranslator()
        
        result = translator.get_contested_translation("democracy")
        
        assert result is not None
        assert "primary_translation" in result
        assert "alternatives" in result
    
    def test_translation_guidance(self):
        """Test getting translation guidance."""
        translator = ConceptualTranslator()
        
        guidance = translator.get_translation_guidance(
            text="The state and civil society relationship",
            source_lang="en",
            target_lang="ar",
        )
        
        assert "recommendations" in guidance
        assert len(guidance["recommendations"]) > 0


class TestTechnicalGlossary:
    """Tests for technical glossary."""
    
    def test_glossary_creation(self):
        """Test glossary is created with defaults."""
        glossary = TechnicalGlossary()
        
        summary = glossary.get_summary()
        assert summary["total_entries"] > 0
    
    def test_term_lookup_english(self):
        """Test looking up English terms."""
        glossary = TechnicalGlossary()
        
        entry = glossary.get_entry("state", "en")
        
        assert entry is not None
        assert entry.term_en == "state"
        assert entry.term_ar == "دولة"
    
    def test_term_lookup_arabic(self):
        """Test looking up Arabic terms."""
        glossary = TechnicalGlossary()
        
        entry = glossary.get_entry("دولة", "ar")
        
        assert entry is not None
        assert entry.term_en == "state"
    
    def test_search(self):
        """Test searching the glossary."""
        glossary = TechnicalGlossary()
        
        results = glossary.search("governance")
        
        assert len(results) > 0
    
    def test_translate(self):
        """Test translating a term."""
        glossary = TechnicalGlossary()
        
        arabic = glossary.translate("methodology", "en")
        
        assert arabic == "منهجية"
    
    def test_get_by_domain(self):
        """Test getting terms by domain."""
        glossary = TechnicalGlossary()
        
        entries = glossary.get_by_domain("methodology")
        
        assert len(entries) > 0
        assert all(e.domain == "methodology" for e in entries)
    
    def test_get_contested(self):
        """Test getting contested terms."""
        glossary = TechnicalGlossary()
        
        contested = glossary.get_contested()
        
        assert len(contested) > 0
    
    def test_add_entry(self):
        """Test adding a new entry."""
        glossary = TechnicalGlossary()
        initial_count = glossary.get_summary()["total_entries"]
        
        glossary.add_entry(GlossaryEntry(
            term_en="test_term",
            term_ar="مصطلح_اختبار",
            domain="test",
        ))
        
        new_count = glossary.get_summary()["total_entries"]
        assert new_count == initial_count + 1
    
    def test_export_import(self):
        """Test exporting and importing glossary."""
        glossary = TechnicalGlossary()
        
        # Export
        json_str = glossary.export_to_json()
        
        # Import
        imported = TechnicalGlossary.from_json(json_str)
        
        assert imported.get_summary()["total_entries"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
