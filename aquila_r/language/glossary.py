"""
Technical Glossary for Aquila-R.

Manages bilingual technical terms across academic domains,
ensuring consistency in translation and usage.
"""

from typing import Dict, List, Optional, Any, Set
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
import json


class TermStatus(str, Enum):
    """Status of a glossary term."""
    APPROVED = "approved"
    PROVISIONAL = "provisional"
    CONTESTED = "contested"
    DEPRECATED = "deprecated"


class GlossaryEntry(BaseModel):
    """An entry in the technical glossary."""
    
    term_en: str = Field(description="English term")
    term_ar: str = Field(description="Arabic term")
    definition_en: Optional[str] = Field(default=None)
    definition_ar: Optional[str] = Field(default=None)
    domain: str = Field(default="general")
    status: TermStatus = Field(default=TermStatus.PROVISIONAL)
    alternatives_en: List[str] = Field(default_factory=list)
    alternatives_ar: List[str] = Field(default_factory=list)
    usage_notes: Optional[str] = Field(default=None)
    source: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def matches(self, query: str, language: str = "both") -> bool:
        """Check if entry matches a query."""
        query_lower = query.lower()
        
        if language in ("en", "both"):
            if query_lower == self.term_en.lower():
                return True
            if query_lower in [alt.lower() for alt in self.alternatives_en]:
                return True
        
        if language in ("ar", "both"):
            if query == self.term_ar:
                return True
            if query in self.alternatives_ar:
                return True
        
        return False


class TechnicalGlossary:
    """
    Bilingual technical glossary for academic research.
    
    Manages terminology across domains with support for:
    - Approved/contested status tracking
    - Alternative translations
    - Domain-specific terminology
    """
    
    def __init__(self):
        """Initialize the glossary."""
        self._entries: Dict[str, GlossaryEntry] = {}
        self._domains: Set[str] = {"general"}
        self._load_default_entries()
    
    def _load_default_entries(self) -> None:
        """Load default glossary entries."""
        default_entries = [
            # Political Science
            GlossaryEntry(
                term_en="state",
                term_ar="دولة",
                domain="political_science",
                status=TermStatus.APPROVED,
                alternatives_ar=["سلطة"],
                usage_notes="Use 'dawla' for modern nation-state concept",
            ),
            GlossaryEntry(
                term_en="governance",
                term_ar="حوكمة",
                domain="political_science",
                status=TermStatus.PROVISIONAL,
                alternatives_ar=["إدارة الحكم"],
                usage_notes="'Hawkama' is recent; some prefer descriptive phrases",
            ),
            GlossaryEntry(
                term_en="civil society",
                term_ar="المجتمع المدني",
                domain="political_science",
                status=TermStatus.CONTESTED,
                alternatives_ar=["مجتمع أهلي"],
                usage_notes="Ahli vs Madani distinction reflects different traditions",
            ),
            
            # Methodology
            GlossaryEntry(
                term_en="methodology",
                term_ar="منهجية",
                domain="methodology",
                status=TermStatus.APPROVED,
            ),
            GlossaryEntry(
                term_en="qualitative research",
                term_ar="البحث النوعي",
                domain="methodology",
                status=TermStatus.APPROVED,
                alternatives_ar=["البحث الكيفي"],
            ),
            GlossaryEntry(
                term_en="quantitative research",
                term_ar="البحث الكمي",
                domain="methodology",
                status=TermStatus.APPROVED,
            ),
            GlossaryEntry(
                term_en="hypothesis",
                term_ar="فرضية",
                domain="methodology",
                status=TermStatus.APPROVED,
            ),
            GlossaryEntry(
                term_en="literature review",
                term_ar="مراجعة الأدبيات",
                domain="methodology",
                status=TermStatus.APPROVED,
                alternatives_ar=["استعراض المراجع"],
            ),
            
            # Philosophy
            GlossaryEntry(
                term_en="epistemology",
                term_ar="نظرية المعرفة",
                domain="philosophy",
                status=TermStatus.APPROVED,
                alternatives_ar=["إبستمولوجيا"],
            ),
            GlossaryEntry(
                term_en="ontology",
                term_ar="الأنطولوجيا",
                domain="philosophy",
                status=TermStatus.APPROVED,
                alternatives_ar=["علم الوجود"],
            ),
            
            # Economics
            GlossaryEntry(
                term_en="economic development",
                term_ar="التنمية الاقتصادية",
                domain="economics",
                status=TermStatus.APPROVED,
            ),
            GlossaryEntry(
                term_en="fiscal policy",
                term_ar="السياسة المالية",
                domain="economics",
                status=TermStatus.APPROVED,
            ),
        ]
        
        for entry in default_entries:
            key = entry.term_en.lower()
            self._entries[key] = entry
            self._domains.add(entry.domain)
    
    def add_entry(self, entry: GlossaryEntry) -> None:
        """
        Add an entry to the glossary.
        
        Args:
            entry: GlossaryEntry to add
        """
        key = entry.term_en.lower()
        self._entries[key] = entry
        self._domains.add(entry.domain)
    
    def get_entry(
        self,
        term: str,
        language: str = "en",
    ) -> Optional[GlossaryEntry]:
        """
        Get a glossary entry by term.
        
        Args:
            term: Term to look up
            language: Language of the term ("en" or "ar")
            
        Returns:
            GlossaryEntry if found, None otherwise
        """
        if language == "en":
            key = term.lower()
            return self._entries.get(key)
        
        # Search Arabic terms
        for entry in self._entries.values():
            if entry.term_ar == term or term in entry.alternatives_ar:
                return entry
        
        return None
    
    def search(
        self,
        query: str,
        domain: Optional[str] = None,
        status: Optional[TermStatus] = None,
    ) -> List[GlossaryEntry]:
        """
        Search the glossary.
        
        Args:
            query: Search query
            domain: Filter by domain
            status: Filter by status
            
        Returns:
            List of matching entries
        """
        results = []
        query_lower = query.lower()
        
        for entry in self._entries.values():
            # Check domain filter
            if domain and entry.domain != domain:
                continue
            
            # Check status filter
            if status and entry.status != status:
                continue
            
            # Check for match
            if entry.matches(query):
                results.append(entry)
            elif query_lower in entry.term_en.lower():
                results.append(entry)
            elif query in entry.term_ar:
                results.append(entry)
        
        return results
    
    def translate(
        self,
        term: str,
        source_lang: str,
    ) -> Optional[str]:
        """
        Translate a term using the glossary.
        
        Args:
            term: Term to translate
            source_lang: Source language ("en" or "ar")
            
        Returns:
            Translation if found, None otherwise
        """
        entry = self.get_entry(term, source_lang)
        if entry:
            if source_lang == "en":
                return entry.term_ar
            return entry.term_en
        return None
    
    def get_by_domain(self, domain: str) -> List[GlossaryEntry]:
        """
        Get all entries in a domain.
        
        Args:
            domain: Domain to filter by
            
        Returns:
            List of entries in the domain
        """
        return [e for e in self._entries.values() if e.domain == domain]
    
    def get_contested(self) -> List[GlossaryEntry]:
        """Get all contested terms."""
        return [e for e in self._entries.values() if e.status == TermStatus.CONTESTED]
    
    def get_domains(self) -> List[str]:
        """Get all domains in the glossary."""
        return sorted(list(self._domains))
    
    def export_to_json(self) -> str:
        """Export glossary to JSON."""
        data = {
            "entries": [e.model_dump(mode="json") for e in self._entries.values()],
            "domains": list(self._domains),
        }
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> "TechnicalGlossary":
        """Load glossary from JSON."""
        data = json.loads(json_str)
        glossary = cls()
        glossary._entries.clear()
        
        for entry_data in data.get("entries", []):
            entry = GlossaryEntry(**entry_data)
            glossary.add_entry(entry)
        
        return glossary
    
    def get_summary(self) -> Dict[str, Any]:
        """Get glossary summary statistics."""
        status_counts = {}
        domain_counts = {}
        
        for entry in self._entries.values():
            status = entry.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
            
            domain = entry.domain
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        return {
            "total_entries": len(self._entries),
            "by_status": status_counts,
            "by_domain": domain_counts,
            "domains": self.get_domains(),
        }
