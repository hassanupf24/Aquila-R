"""
Output Standards for Aquila-R.

Defines the standard structure and requirements for
all research outputs.
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field


class OutputSection(str, Enum):
    """Standard output sections."""
    CONTEXT = "context"
    METHODOLOGY = "methodology"
    EVIDENCE = "evidence"
    ANALYSIS = "analysis"
    GAPS = "gaps"
    NEXT_STEPS = "next_steps"
    SOURCES = "sources"
    ASSUMPTIONS = "assumptions"


class SectionRequirement(BaseModel):
    """Requirements for an output section."""
    
    section: OutputSection
    required: bool = Field(default=True)
    min_content_length: int = Field(default=0)
    must_cite_sources: bool = Field(default=False)
    must_flag_uncertainty: bool = Field(default=False)
    bilingual_required: bool = Field(default=False)


class OutputStandards:
    """
    Standards for research outputs.
    
    Ensures all outputs meet academic quality requirements
    and follow the defined structure.
    """
    
    # Standard section order
    SECTION_ORDER = [
        OutputSection.CONTEXT,
        OutputSection.METHODOLOGY,
        OutputSection.EVIDENCE,
        OutputSection.ANALYSIS,
        OutputSection.GAPS,
        OutputSection.NEXT_STEPS,
        OutputSection.SOURCES,
        OutputSection.ASSUMPTIONS,
    ]
    
    # Section titles by language
    SECTION_TITLES = {
        OutputSection.CONTEXT: {"en": "Context / Research Question", "ar": "السياق / سؤال البحث"},
        OutputSection.METHODOLOGY: {"en": "Methodological Approach", "ar": "المنهج المتبع"},
        OutputSection.EVIDENCE: {"en": "Evidence & Findings", "ar": "الأدلة والنتائج"},
        OutputSection.ANALYSIS: {"en": "Critical Analysis", "ar": "التحليل النقدي"},
        OutputSection.GAPS: {"en": "Gaps & Limitations", "ar": "الفجوات والقيود"},
        OutputSection.NEXT_STEPS: {"en": "Suggested Next Steps", "ar": "الخطوات التالية المقترحة"},
        OutputSection.SOURCES: {"en": "Sources", "ar": "المصادر"},
        OutputSection.ASSUMPTIONS: {"en": "Assumptions", "ar": "الافتراضات"},
    }
    
    def __init__(self):
        """Initialize output standards."""
        self._requirements = self._define_requirements()
    
    def _define_requirements(self) -> Dict[OutputSection, SectionRequirement]:
        """Define section requirements."""
        return {
            OutputSection.CONTEXT: SectionRequirement(
                section=OutputSection.CONTEXT,
                required=True,
                min_content_length=50,
            ),
            OutputSection.METHODOLOGY: SectionRequirement(
                section=OutputSection.METHODOLOGY,
                required=True,
                min_content_length=100,
                must_flag_uncertainty=True,
            ),
            OutputSection.EVIDENCE: SectionRequirement(
                section=OutputSection.EVIDENCE,
                required=True,
                must_cite_sources=True,
                must_flag_uncertainty=True,
            ),
            OutputSection.ANALYSIS: SectionRequirement(
                section=OutputSection.ANALYSIS,
                required=True,
                min_content_length=200,
            ),
            OutputSection.GAPS: SectionRequirement(
                section=OutputSection.GAPS,
                required=True,
            ),
            OutputSection.NEXT_STEPS: SectionRequirement(
                section=OutputSection.NEXT_STEPS,
                required=False,
            ),
            OutputSection.SOURCES: SectionRequirement(
                section=OutputSection.SOURCES,
                required=True,
            ),
            OutputSection.ASSUMPTIONS: SectionRequirement(
                section=OutputSection.ASSUMPTIONS,
                required=True,
            ),
        }
    
    def get_section_title(self, section: OutputSection, language: str = "en") -> str:
        """Get section title in specified language."""
        titles = self.SECTION_TITLES.get(section, {})
        return titles.get(language, titles.get("en", section.value))
    
    def get_required_sections(self) -> List[OutputSection]:
        """Get list of required sections."""
        return [
            s for s, req in self._requirements.items() 
            if req.required
        ]
    
    def validate_output(
        self,
        sections: Dict[OutputSection, str],
    ) -> List[str]:
        """
        Validate an output against standards.
        
        Args:
            sections: Dictionary of section content
            
        Returns:
            List of validation issues
        """
        issues = []
        
        for section, requirement in self._requirements.items():
            content = sections.get(section, "")
            
            # Check required sections
            if requirement.required and not content:
                issues.append(f"Missing required section: {section.value}")
                continue
            
            # Check minimum length
            if content and len(content) < requirement.min_content_length:
                issues.append(
                    f"Section {section.value} below minimum length "
                    f"({len(content)} < {requirement.min_content_length})"
                )
        
        return issues
    
    def get_template(self, language: str = "en") -> str:
        """
        Get output template.
        
        Args:
            language: Template language
            
        Returns:
            Template string
        """
        lines = []
        
        for section in self.SECTION_ORDER:
            title = self.get_section_title(section, language)
            requirement = self._requirements.get(section)
            
            required_marker = "*" if requirement and requirement.required else ""
            lines.append(f"## {title}{required_marker}\n")
            
            # Add guidance
            if requirement:
                if requirement.must_cite_sources:
                    if language == "ar":
                        lines.append("*يجب ذكر المصادر*\n")
                    else:
                        lines.append("*Must cite sources*\n")
                if requirement.must_flag_uncertainty:
                    if language == "ar":
                        lines.append("*الإشارة إلى عدم اليقين*\n")
                    else:
                        lines.append("*Flag uncertainty where appropriate*\n")
            
            lines.append("\n")
        
        return "\n".join(lines)
