"""
Language processing components for Aquila-R.

Handles bilingual (English/Arabic) operations:
- Language detection
- Conceptual translation
- Technical glossary management
"""

from aquila_r.language.detector import LanguageDetector
from aquila_r.language.translator import ConceptualTranslator, TranslationResult
from aquila_r.language.glossary import TechnicalGlossary, GlossaryEntry

__all__ = [
    "LanguageDetector",
    "ConceptualTranslator",
    "TranslationResult",
    "TechnicalGlossary",
    "GlossaryEntry",
]
