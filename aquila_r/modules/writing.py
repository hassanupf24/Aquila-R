"""
Writing Support Module for Aquila-R.

Responsible for:
- Assisting with research proposals, abstracts, literature reviews, policy briefs
- Always allowing user control and revision
- Never inventing citations
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
)


class DocumentType(str, Enum):
    """Types of documents the module can assist with."""
    RESEARCH_PROPOSAL = "research_proposal"
    ABSTRACT = "abstract"
    LITERATURE_REVIEW = "literature_review"
    POLICY_BRIEF = "policy_brief"
    METHODOLOGY_SECTION = "methodology_section"
    DISCUSSION = "discussion"
    EXECUTIVE_SUMMARY = "executive_summary"


class DraftSection(BaseModel):
    """A section of a document draft."""
    
    heading: str
    content: str
    citations_used: List[str] = Field(default_factory=list)
    notes_for_user: List[str] = Field(default_factory=list)
    requires_user_input: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.7)


class DocumentTemplate(BaseModel):
    """Template for a document type."""
    
    document_type: DocumentType
    sections: List[str]
    required_elements: List[str]
    optional_elements: List[str]
    max_length_words: Optional[int] = None
    language: str = Field(default="en")


class WritingResult(ModuleResult):
    """Extended result for writing module."""
    
    document_type: Optional[DocumentType] = None
    draft_sections: List[DraftSection] = Field(default_factory=list)
    citations_referenced: List[str] = Field(default_factory=list)
    user_action_required: List[str] = Field(default_factory=list)
    revision_notes: List[str] = Field(default_factory=list)
    
    def get_full_draft(self) -> str:
        """Combine all sections into full draft."""
        parts = []
        for section in self.draft_sections:
            parts.append(f"## {section.heading}\n\n{section.content}\n")
        return "\n".join(parts)


class WritingModule(BaseModule):
    """
    Writing Support Module (Human-in-the-Loop).
    
    Assists with academic writing while maintaining user control
    and never fabricating citations.
    """
    
    name = "writing"
    description = "Human-in-the-loop writing support for academic documents"
    supported_languages = ["en", "ar"]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._templates = self._load_templates()
    
    def _load_templates(self) -> Dict[DocumentType, DocumentTemplate]:
        """Load document templates."""
        return {
            DocumentType.RESEARCH_PROPOSAL: DocumentTemplate(
                document_type=DocumentType.RESEARCH_PROPOSAL,
                sections=[
                    "Title and Abstract",
                    "Introduction and Problem Statement",
                    "Literature Review",
                    "Research Questions/Hypotheses",
                    "Methodology",
                    "Expected Contributions",
                    "Timeline",
                    "References",
                ],
                required_elements=[
                    "Clear research question",
                    "Methodological approach",
                    "Significance statement",
                ],
                optional_elements=[
                    "Preliminary findings",
                    "Budget",
                ],
            ),
            DocumentType.ABSTRACT: DocumentTemplate(
                document_type=DocumentType.ABSTRACT,
                sections=[
                    "Background",
                    "Methods",
                    "Results",
                    "Conclusions",
                ],
                required_elements=[
                    "Research objective",
                    "Key findings",
                ],
                optional_elements=[
                    "Implications",
                ],
                max_length_words=300,
            ),
            DocumentType.LITERATURE_REVIEW: DocumentTemplate(
                document_type=DocumentType.LITERATURE_REVIEW,
                sections=[
                    "Introduction",
                    "Search Strategy",
                    "Thematic Analysis",
                    "Critical Evaluation",
                    "Synthesis",
                    "Gaps and Future Directions",
                ],
                required_elements=[
                    "Scope definition",
                    "Source evaluation criteria",
                    "Synthesis of findings",
                ],
                optional_elements=[
                    "Theoretical framework",
                ],
            ),
            DocumentType.POLICY_BRIEF: DocumentTemplate(
                document_type=DocumentType.POLICY_BRIEF,
                sections=[
                    "Executive Summary",
                    "Problem Statement",
                    "Evidence Review",
                    "Policy Options",
                    "Recommendations",
                ],
                required_elements=[
                    "Clear problem definition",
                    "Evidence-based recommendations",
                ],
                optional_elements=[
                    "Cost-benefit analysis",
                    "Implementation timeline",
                ],
                max_length_words=2000,
            ),
        }
    
    def execute(self, context: ModuleContext) -> WritingResult:
        """
        Execute writing assistance.
        
        Args:
            context: Execution context
            
        Returns:
            WritingResult with draft sections
        """
        issues = self.validate_context(context)
        if issues:
            return WritingResult(
                module_name=self.name,
                status=ModuleStatus.FAILED,
                warnings=[self.create_warning(issue, "high") for issue in issues],
            )
        
        result = WritingResult(
            module_name=self.name,
            status=ModuleStatus.COMPLETED,
            language=context.language,
        )
        
        # Critical methodology note
        result.methodology_notes.append(
            "Writing module operates in human-in-the-loop mode. "
            "All drafts require user review and revision. "
            "No citations are fabricated - only verified sources are referenced."
        )
        
        # User action required
        result.user_action_required.append(
            "Review all generated content for accuracy and appropriateness"
        )
        result.user_action_required.append(
            "Verify all citations against original sources"
        )
        result.user_action_required.append(
            "Add domain-specific content that requires expertise"
        )
        
        return result
    
    def get_template(
        self,
        document_type: DocumentType,
        language: str = "en",
    ) -> DocumentTemplate:
        """
        Get template for a document type.
        
        Args:
            document_type: Type of document
            language: Output language
            
        Returns:
            DocumentTemplate with structure
        """
        template = self._templates.get(document_type)
        if template:
            template.language = language
            return template
        
        # Return generic template if specific not found
        return DocumentTemplate(
            document_type=document_type,
            sections=["Introduction", "Main Content", "Conclusion"],
            required_elements=["Clear objective"],
            optional_elements=[],
            language=language,
        )
    
    def generate_section_draft(
        self,
        section_type: str,
        content_guidance: str,
        available_sources: List[str],
        language: str = "en",
    ) -> DraftSection:
        """
        Generate a draft for a section.
        
        Args:
            section_type: Type of section
            content_guidance: Guidance for content
            available_sources: Sources that can be cited
            language: Output language
            
        Returns:
            DraftSection with draft content
        """
        draft = DraftSection(
            heading=section_type,
            content=self._get_placeholder_content(section_type, language),
            citations_used=[],  # Only use verified sources
            notes_for_user=[
                "This is a structural placeholder requiring your expertise",
                "Add specific content based on your research",
            ],
            requires_user_input=[
                "Specific findings from your research",
                "Domain expertise and interpretation",
            ],
            confidence=0.3,  # Low confidence for placeholder
        )
        
        return draft
    
    def _get_placeholder_content(self, section_type: str, language: str) -> str:
        """Get placeholder content for a section."""
        if language == "ar":
            return (
                f"[محتوى قسم {section_type}]\n\n"
                "يتطلب هذا القسم محتوى محدداً من المستخدم.\n"
                "يرجى إضافة:\n"
                "- نتائج بحثك المحددة\n"
                "- خبرتك في المجال\n"
                "- الاستشهادات الموثقة\n"
            )
        
        return (
            f"[{section_type} Content]\n\n"
            "This section requires specific content from the user.\n"
            "Please add:\n"
            "- Your specific research findings\n"
            "- Domain expertise and interpretation\n"
            "- Verified citations from your sources\n"
        )
    
    def validate_citations(
        self,
        citations: List[str],
        verified_sources: List[str],
    ) -> tuple[List[str], List[str]]:
        """
        Validate citations against verified sources.
        
        Args:
            citations: Citations to validate
            verified_sources: List of verified source identifiers
            
        Returns:
            Tuple of (valid_citations, invalid_citations)
        """
        valid = []
        invalid = []
        
        for citation in citations:
            if citation in verified_sources:
                valid.append(citation)
            else:
                invalid.append(citation)
        
        return valid, invalid
    
    def generate_abstract_structure(
        self,
        research_question: str,
        methodology: str,
        key_findings: List[str],
        language: str = "en",
    ) -> DraftSection:
        """
        Generate structured abstract.
        
        Args:
            research_question: Main research question
            methodology: Methodology used
            key_findings: List of key findings
            language: Output language
            
        Returns:
            DraftSection with abstract structure
        """
        if language == "ar":
            content = self._build_arabic_abstract(
                research_question, methodology, key_findings
            )
        else:
            content = self._build_english_abstract(
                research_question, methodology, key_findings
            )
        
        return DraftSection(
            heading="Abstract" if language == "en" else "الملخص",
            content=content,
            notes_for_user=[
                "Review for accuracy and completeness",
                "Ensure word count meets requirements",
            ],
            requires_user_input=[
                "Specific numerical results if applicable",
                "Precise methodology details",
            ],
            confidence=0.5,
        )
    
    def _build_english_abstract(
        self,
        research_question: str,
        methodology: str,
        key_findings: List[str],
    ) -> str:
        """Build English abstract."""
        parts = [
            f"**Background:** This study addresses: {research_question}\n",
            f"**Methods:** {methodology}\n",
            "**Results:** " + "; ".join(key_findings) + "\n" if key_findings else "",
            "**Conclusions:** [User to add conclusions based on findings]\n",
        ]
        return "\n".join(parts)
    
    def _build_arabic_abstract(
        self,
        research_question: str,
        methodology: str,
        key_findings: List[str],
    ) -> str:
        """Build Arabic abstract."""
        parts = [
            f"**الخلفية:** تتناول هذه الدراسة: {research_question}\n",
            f"**المنهجية:** {methodology}\n",
            "**النتائج:** " + "؛ ".join(key_findings) + "\n" if key_findings else "",
            "**الخلاصة:** [يضيف المستخدم الاستنتاجات بناءً على النتائج]\n",
        ]
        return "\n".join(parts)
