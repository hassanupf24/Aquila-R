"""
Language Detection for Aquila-R.

Detects whether text is primarily English or Arabic,
with support for mixed-language content.
"""

from typing import Dict, Optional, Tuple
from pydantic import BaseModel, Field
import re


class LanguageScore(BaseModel):
    """Language detection scores."""
    
    english: float = Field(ge=0.0, le=1.0, default=0.0)
    arabic: float = Field(ge=0.0, le=1.0, default=0.0)
    mixed: bool = Field(default=False)
    primary: str = Field(default="en")
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)


class LanguageDetector:
    """
    Detects language of text content.
    
    Specialized for English and Arabic detection
    with support for mixed-language academic text.
    """
    
    # Arabic Unicode range
    ARABIC_PATTERN = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+')
    
    # English pattern (ASCII letters)
    ENGLISH_PATTERN = re.compile(r'[a-zA-Z]+')
    
    def __init__(self):
        """Initialize the language detector."""
        self._cache: Dict[str, LanguageScore] = {}
    
    def detect(self, text: str) -> LanguageScore:
        """
        Detect the language of the given text.
        
        Args:
            text: Text to analyze
            
        Returns:
            LanguageScore with detection results
        """
        if not text or not text.strip():
            return LanguageScore(
                english=0.0,
                arabic=0.0,
                primary="unknown",
                confidence=0.0,
            )
        
        # Check cache
        cache_key = text[:500]  # Use first 500 chars as key
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Count characters
        arabic_chars = len(self.ARABIC_PATTERN.findall(text))
        english_chars = len(self.ENGLISH_PATTERN.findall(text))
        total_alpha = arabic_chars + english_chars
        
        if total_alpha == 0:
            return LanguageScore(
                english=0.0,
                arabic=0.0,
                primary="unknown",
                confidence=0.0,
            )
        
        # Calculate proportions
        arabic_ratio = arabic_chars / total_alpha
        english_ratio = english_chars / total_alpha
        
        # Determine primary language
        if arabic_ratio > 0.6:
            primary = "ar"
            confidence = arabic_ratio
        elif english_ratio > 0.6:
            primary = "en"
            confidence = english_ratio
        else:
            primary = "ar" if arabic_ratio > english_ratio else "en"
            confidence = max(arabic_ratio, english_ratio)
        
        # Check for mixed content
        mixed = (arabic_ratio > 0.2 and english_ratio > 0.2)
        
        score = LanguageScore(
            english=english_ratio,
            arabic=arabic_ratio,
            mixed=mixed,
            primary=primary,
            confidence=confidence,
        )
        
        # Cache result
        self._cache[cache_key] = score
        
        return score
    
    def is_arabic(self, text: str, threshold: float = 0.5) -> bool:
        """
        Check if text is primarily Arabic.
        
        Args:
            text: Text to check
            threshold: Minimum ratio for Arabic classification
            
        Returns:
            True if text is primarily Arabic
        """
        score = self.detect(text)
        return score.arabic >= threshold
    
    def is_english(self, text: str, threshold: float = 0.5) -> bool:
        """
        Check if text is primarily English.
        
        Args:
            text: Text to check
            threshold: Minimum ratio for English classification
            
        Returns:
            True if text is primarily English
        """
        score = self.detect(text)
        return score.english >= threshold
    
    def is_mixed(self, text: str) -> bool:
        """
        Check if text contains significant mixed-language content.
        
        Args:
            text: Text to check
            
        Returns:
            True if text has significant content in both languages
        """
        score = self.detect(text)
        return score.mixed
    
    def get_primary_language(self, text: str) -> str:
        """
        Get the primary language of the text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code ("en", "ar", or "unknown")
        """
        score = self.detect(text)
        return score.primary
    
    def segment_by_language(self, text: str) -> Dict[str, list]:
        """
        Segment text into language-specific portions.
        
        Args:
            text: Mixed-language text
            
        Returns:
            Dictionary with "en" and "ar" keys containing segments
        """
        segments: Dict[str, list] = {"en": [], "ar": []}
        
        # Split by sentences (simple approach)
        sentences = re.split(r'[.!?。؟]', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            lang = self.get_primary_language(sentence)
            if lang in segments:
                segments[lang].append(sentence)
        
        return segments
    
    def clear_cache(self) -> None:
        """Clear the detection cache."""
        self._cache.clear()
