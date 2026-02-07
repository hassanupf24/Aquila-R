"""
Conceptual Translation for Aquila-R.

Performs conceptual (not literal) translation between
English and Arabic, preserving theoretical and
disciplinary meaning.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class TranslationConfidence(str, Enum):
    """Confidence level in translation."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    CONTESTED = "contested"


class TranslationNote(BaseModel):
    """A note about translation choices."""
    
    note_type: str  # "untranslatable", "contested", "alternative", "context"
    message: str
    alternatives: List[str] = Field(default_factory=list)


class TranslationResult(BaseModel):
    """Result of a conceptual translation."""
    
    source_text: str
    source_language: str
    target_text: str
    target_language: str
    confidence: TranslationConfidence = Field(default=TranslationConfidence.MEDIUM)
    notes: List[TranslationNote] = Field(default_factory=list)
    preserved_terms: List[str] = Field(default_factory=list)
    requires_review: bool = Field(default=False)
    
    def has_contested_terms(self) -> bool:
        """Check if translation includes contested terms."""
        return any(n.note_type == "contested" for n in self.notes)
    
    def get_alternatives(self) -> Dict[str, List[str]]:
        """Get all alternative translations offered."""
        alternatives = {}
        for note in self.notes:
            if note.alternatives:
                alternatives[note.message] = note.alternatives
        return alternatives


class ConceptualTranslator:
    """
    Conceptual translator for academic/research text.
    
    Key principles:
    - Conceptual translation, not literal
    - Preserve theoretical and disciplinary meaning
    - Flag terms lacking direct equivalents
    - Offer alternatives for contested concepts
    """
    
    def __init__(self):
        """Initialize the translator."""
        self._untranslatable_terms: Dict[str, List[str]] = {
            # Terms that should remain in original or require special handling
            "en_to_ar": [
                "governance",  # حوكمة is sometimes used but contested
                "agency",  # فاعلية but meaning differs
                "discourse",  # خطاب but lacks full Foucauldian meaning
                "narrative",  # سردية emerging but not standard
                "paradigm",  # براديغم transliteration common
            ],
            "ar_to_en": [
                "عصبية",  # asabiyya - no English equivalent
                "مقاصد الشريعة",  # maqasid al-shariah
                "اجتهاد",  # ijtihad
                "تجديد",  # tajdid
                "أصالة",  # asala
            ],
        }
        
        self._contested_terms: Dict[str, Dict[str, str]] = {
            # Terms with multiple contested translations
            "state": {
                "primary": "دولة",
                "alternatives": ["سلطة", "كيان سياسي"],
                "context": "Modern nation-state concept may not map to historical Arabic concepts",
            },
            "democracy": {
                "primary": "ديمقراطية",
                "alternatives": ["شورى"],
                "context": "Shura (consultation) sometimes offered as indigenous equivalent",
            },
            "civil society": {
                "primary": "المجتمع المدني",
                "alternatives": ["مجتمع أهلي"],
                "context": "Ahli (familial/communal) vs madani (civic) distinction important",
            },
            "secularism": {
                "primary": "علمانية",
                "alternatives": ["مدنية", "لا دينية"],
                "context": "Highly contested; 'almāniyya has negative connotations in some contexts",
            },
        }
    
    def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        preserve_technical_terms: bool = True,
        domain: Optional[str] = None,
    ) -> TranslationResult:
        """
        Perform conceptual translation.
        
        Args:
            text: Text to translate
            source_lang: Source language ("en" or "ar")
            target_lang: Target language ("en" or "ar")
            preserve_technical_terms: Whether to keep untranslatable terms
            domain: Academic domain for specialized handling
            
        Returns:
            TranslationResult with translation and notes
        """
        if source_lang == target_lang:
            return TranslationResult(
                source_text=text,
                source_language=source_lang,
                target_text=text,
                target_language=target_lang,
                confidence=TranslationConfidence.HIGH,
            )
        
        result = TranslationResult(
            source_text=text,
            source_language=source_lang,
            target_text="",  # Will be filled by LLM in actual use
            target_language=target_lang,
            requires_review=True,
        )
        
        # Check for untranslatable terms
        direction = f"{source_lang}_to_{target_lang}"
        untranslatable = self._untranslatable_terms.get(direction, [])
        
        for term in untranslatable:
            if term.lower() in text.lower():
                result.notes.append(TranslationNote(
                    note_type="untranslatable",
                    message=f"Term '{term}' lacks direct equivalent",
                    alternatives=[],
                ))
                if preserve_technical_terms:
                    result.preserved_terms.append(term)
        
        # Check for contested terms
        for term, info in self._contested_terms.items():
            if term.lower() in text.lower():
                result.notes.append(TranslationNote(
                    note_type="contested",
                    message=f"'{term}' → '{info['primary']}' (contested translation)",
                    alternatives=info.get("alternatives", []),
                ))
                result.confidence = TranslationConfidence.CONTESTED
        
        # Add LLM integration note
        result.notes.append(TranslationNote(
            note_type="context",
            message="Full conceptual translation requires LLM integration",
        ))
        
        return result
    
    def flag_untranslatable(
        self,
        text: str,
        source_lang: str,
    ) -> List[Dict[str, Any]]:
        """
        Identify terms that lack direct translation.
        
        Args:
            text: Text to analyze
            source_lang: Source language
            
        Returns:
            List of untranslatable term information
        """
        flags = []
        target_lang = "ar" if source_lang == "en" else "en"
        direction = f"{source_lang}_to_{target_lang}"
        
        untranslatable = self._untranslatable_terms.get(direction, [])
        
        for term in untranslatable:
            if term.lower() in text.lower():
                flags.append({
                    "term": term,
                    "source_language": source_lang,
                    "reason": "No direct equivalent in target language",
                    "recommendation": "Consider keeping original with explanation",
                })
        
        return flags
    
    def get_contested_translation(
        self,
        term: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get information about a contested term's translation.
        
        Args:
            term: Term to look up
            
        Returns:
            Dictionary with translation options and context
        """
        term_lower = term.lower()
        
        if term_lower in self._contested_terms:
            info = self._contested_terms[term_lower]
            return {
                "term": term,
                "primary_translation": info["primary"],
                "alternatives": info.get("alternatives", []),
                "context": info.get("context", ""),
                "recommendation": "Use primary but acknowledge alternatives when relevant",
            }
        
        return None
    
    def add_contested_term(
        self,
        term: str,
        primary: str,
        alternatives: List[str],
        context: str,
    ) -> None:
        """
        Add a new contested term to the translator.
        
        Args:
            term: The term (in source language)
            primary: Primary translation
            alternatives: Alternative translations
            context: Context explaining the contestation
        """
        self._contested_terms[term.lower()] = {
            "primary": primary,
            "alternatives": alternatives,
            "context": context,
        }
    
    def get_translation_guidance(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
    ) -> Dict[str, Any]:
        """
        Get guidance for translating text.
        
        Args:
            text: Text to translate
            source_lang: Source language
            target_lang: Target language
            
        Returns:
            Dictionary with translation guidance
        """
        guidance = {
            "source_text": text,
            "direction": f"{source_lang} → {target_lang}",
            "untranslatable_terms": [],
            "contested_terms": [],
            "recommendations": [],
        }
        
        # Find untranslatable terms
        guidance["untranslatable_terms"] = self.flag_untranslatable(text, source_lang)
        
        # Find contested terms
        for term in self._contested_terms:
            if term.lower() in text.lower():
                guidance["contested_terms"].append(
                    self.get_contested_translation(term)
                )
        
        # Add general recommendations
        guidance["recommendations"] = [
            "Prioritize conceptual accuracy over literal translation",
            "Preserve disciplinary terminology meaning",
            "Provide transliteration for untranslatable terms",
            "Note contested terms in footnotes when appropriate",
        ]
        
        return guidance
