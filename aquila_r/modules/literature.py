"""
Literature Intelligence Module for Aquila-R.

Responsible for:
- Source discovery and evaluation
- Distinguishing peer-reviewed, gray literature, and opinion
- Comparing English and Arabic research traditions
- Identifying gaps, contradictions, and under-researched areas
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime

from aquila_r.modules.base import (
    BaseModule,
    ModuleContext,
    ModuleResult,
    ModuleStatus,
    Finding,
)


class SourceType(str, Enum):
    """Types of academic sources."""
    PEER_REVIEWED = "peer_reviewed"
    GRAY_LITERATURE = "gray_literature"
    OPINION = "opinion"
    BOOK = "book"
    REPORT = "report"
    THESIS = "thesis"
    CONFERENCE = "conference"
    PREPRINT = "preprint"
    NEWS = "news"
    UNKNOWN = "unknown"


class SourceQuality(str, Enum):
    """Quality assessment of sources."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNCERTAIN = "uncertain"


class SourceEvaluation(BaseModel):
    """Evaluation of a single source."""
    
    source_id: str
    title: str
    authors: List[str] = Field(default_factory=list)
    year: Optional[int] = None
    source_type: SourceType = Field(default=SourceType.UNKNOWN)
    quality: SourceQuality = Field(default=SourceQuality.UNCERTAIN)
    language: str = Field(default="en")
    relevance_score: float = Field(ge=0.0, le=1.0, default=0.5)
    verified: bool = Field(default=False)
    
    methodology_notes: List[str] = Field(default_factory=list)
    bias_indicators: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    
    url: Optional[str] = None
    doi: Optional[str] = None
    abstract: Optional[str] = None


class LiteratureGap(BaseModel):
    """An identified gap in the literature."""
    
    description: str
    significance: str = Field(default="medium")  # low, medium, high
    language_context: str = Field(default="both")  # en, ar, both
    research_questions: List[str] = Field(default_factory=list)


class LiteratureContradiction(BaseModel):
    """A contradiction between sources."""
    
    description: str
    source_a: str
    source_b: str
    nature: str = Field(default="methodological")  # methodological, empirical, theoretical
    resolution_notes: Optional[str] = None


class LiteratureResult(ModuleResult):
    """Extended result for literature module."""
    
    sources: List[SourceEvaluation] = Field(default_factory=list)
    gaps: List[LiteratureGap] = Field(default_factory=list)
    contradictions: List[LiteratureContradiction] = Field(default_factory=list)
    research_traditions: Dict[str, List[str]] = Field(default_factory=dict)
    
    def get_high_quality_sources(self) -> List[SourceEvaluation]:
        """Get sources rated as high quality."""
        return [s for s in self.sources if s.quality == SourceQuality.HIGH]
    
    def get_sources_by_language(self, lang: str) -> List[SourceEvaluation]:
        """Get sources in a specific language."""
        return [s for s in self.sources if s.language == lang]
    
    def get_sources_by_type(self, source_type: SourceType) -> List[SourceEvaluation]:
        """Get sources of a specific type."""
        return [s for s in self.sources if s.source_type == source_type]


class LiteratureModule(BaseModule):
    """
    Literature Intelligence Module.
    
    Discovers, evaluates, and synthesizes academic sources
    with explicit quality assessment and gap identification.
    """
    
    name = "literature"
    description = "Literature discovery, evaluation, and gap identification"
    supported_languages = ["en", "ar"]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.retrieval_tools = []
        self._source_cache: Dict[str, SourceEvaluation] = {}
    
    def execute(self, context: ModuleContext) -> LiteratureResult:
        """
        Execute literature intelligence analysis.
        
        Args:
            context: Execution context with query
            
        Returns:
            LiteratureResult with sources, gaps, and findings
        """
        # Validate context
        issues = self.validate_context(context)
        if issues:
            return LiteratureResult(
                module_name=self.name,
                status=ModuleStatus.FAILED,
                warnings=[self.create_warning(issue, "high") for issue in issues],
            )
        
        # Initialize result
        result = LiteratureResult(
            module_name=self.name,
            status=ModuleStatus.COMPLETED,
            language=context.language,
        )
        
        # Add methodology note
        result.methodology_notes.append(
            "Literature analysis follows systematic review principles, "
            "distinguishing source types and assessing quality explicitly."
        )
        
        # Placeholder for actual retrieval (requires tool integration)
        result.warnings.append(self.create_warning(
            "Literature retrieval requires tool integration. "
            "Configure arxiv, scholarly, or custom retrieval tools.",
            severity="medium",
            category="tool_integration",
        ))
        
        # Add limitation about current state
        result.limitations.append(self.create_limitation(
            description="Full literature retrieval pending tool integration",
            impact="high",
            mitigation="Configure retrieval tools in config or provide sources manually",
        ))
        
        return result
    
    def evaluate_source(
        self,
        title: str,
        authors: List[str],
        year: Optional[int] = None,
        abstract: Optional[str] = None,
        source_type: Optional[SourceType] = None,
        language: str = "en",
        url: Optional[str] = None,
        doi: Optional[str] = None,
    ) -> SourceEvaluation:
        """
        Evaluate a single source.
        
        Args:
            title: Source title
            authors: List of author names
            year: Publication year
            abstract: Source abstract
            source_type: Type of source
            language: Source language
            url: Source URL
            doi: DOI if available
            
        Returns:
            SourceEvaluation with quality assessment
        """
        import hashlib
        
        source_id = hashlib.sha256(
            f"{title}_{authors}_{year}".encode()
        ).hexdigest()[:16]
        
        # Infer source type if not provided
        if source_type is None:
            source_type = self._infer_source_type(title, abstract, url)
        
        # Assess quality
        quality = self._assess_quality(
            source_type=source_type,
            year=year,
            has_doi=doi is not None,
            has_abstract=abstract is not None,
        )
        
        evaluation = SourceEvaluation(
            source_id=source_id,
            title=title,
            authors=authors,
            year=year,
            source_type=source_type,
            quality=quality,
            language=language,
            url=url,
            doi=doi,
            abstract=abstract,
            verified=doi is not None,
        )
        
        # Cache evaluation
        self._source_cache[source_id] = evaluation
        
        return evaluation
    
    def _infer_source_type(
        self,
        title: str,
        abstract: Optional[str],
        url: Optional[str],
    ) -> SourceType:
        """Infer source type from available metadata."""
        title_lower = title.lower()
        
        # Check for common indicators
        if "thesis" in title_lower or "dissertation" in title_lower:
            return SourceType.THESIS
        
        if "report" in title_lower or "working paper" in title_lower:
            return SourceType.REPORT
        
        if "conference" in title_lower or "proceedings" in title_lower:
            return SourceType.CONFERENCE
        
        if url:
            url_lower = url.lower()
            if "arxiv" in url_lower:
                return SourceType.PREPRINT
            if "news" in url_lower or "bbc" in url_lower or "cnn" in url_lower:
                return SourceType.NEWS
        
        return SourceType.UNKNOWN
    
    def _assess_quality(
        self,
        source_type: SourceType,
        year: Optional[int],
        has_doi: bool,
        has_abstract: bool,
    ) -> SourceQuality:
        """Assess source quality based on indicators."""
        score = 0
        
        # Source type scoring
        type_scores = {
            SourceType.PEER_REVIEWED: 3,
            SourceType.BOOK: 2,
            SourceType.THESIS: 2,
            SourceType.CONFERENCE: 2,
            SourceType.REPORT: 1,
            SourceType.GRAY_LITERATURE: 1,
            SourceType.PREPRINT: 1,
            SourceType.OPINION: 0,
            SourceType.NEWS: 0,
            SourceType.UNKNOWN: 0,
        }
        score += type_scores.get(source_type, 0)
        
        # DOI indicates formal publication
        if has_doi:
            score += 2
        
        # Abstract indicates completeness
        if has_abstract:
            score += 1
        
        # Recency (for time-sensitive topics)
        if year and year >= 2020:
            score += 1
        
        # Convert to quality level
        if score >= 5:
            return SourceQuality.HIGH
        elif score >= 3:
            return SourceQuality.MEDIUM
        elif score >= 1:
            return SourceQuality.LOW
        return SourceQuality.UNCERTAIN
    
    def identify_gaps(
        self,
        sources: List[SourceEvaluation],
        query: str,
    ) -> List[LiteratureGap]:
        """
        Identify gaps in the literature based on sources.
        
        Args:
            sources: Evaluated sources
            query: Original research query
            
        Returns:
            List of identified gaps
        """
        gaps = []
        
        # Check language coverage
        en_sources = [s for s in sources if s.language == "en"]
        ar_sources = [s for s in sources if s.language == "ar"]
        
        if not ar_sources and en_sources:
            gaps.append(LiteratureGap(
                description="No Arabic-language sources identified. "
                           "Arabic scholarly perspectives may be underrepresented.",
                significance="high",
                language_context="ar",
                research_questions=[
                    "What Arabic-language scholarship exists on this topic?",
                    "Are there regional perspectives missing from English sources?",
                ],
            ))
        
        if not en_sources and ar_sources:
            gaps.append(LiteratureGap(
                description="No English-language sources identified. "
                           "International perspectives may be underrepresented.",
                significance="medium",
                language_context="en",
            ))
        
        # Check source type diversity
        types_present = {s.source_type for s in sources}
        if SourceType.PEER_REVIEWED not in types_present:
            gaps.append(LiteratureGap(
                description="No peer-reviewed sources identified. "
                           "Findings require validation from peer-reviewed literature.",
                significance="high",
                language_context="both",
            ))
        
        return gaps
    
    def compare_traditions(
        self,
        sources: List[SourceEvaluation],
    ) -> Dict[str, List[str]]:
        """
        Compare English and Arabic research traditions.
        
        Args:
            sources: Evaluated sources
            
        Returns:
            Dictionary mapping tradition to key themes/approaches
        """
        traditions: Dict[str, List[str]] = {
            "english": [],
            "arabic": [],
            "comparative_notes": [],
        }
        
        # Placeholder for actual tradition comparison
        # This would require content analysis through LLM
        
        en_count = len([s for s in sources if s.language == "en"])
        ar_count = len([s for s in sources if s.language == "ar"])
        
        traditions["comparative_notes"].append(
            f"Source distribution: {en_count} English, {ar_count} Arabic"
        )
        
        return traditions
