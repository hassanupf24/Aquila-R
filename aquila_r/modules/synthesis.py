"""
Research Synthesis Module for Aquila-R.

Responsible for:
- Producing structured literature reviews
- Building conceptual and theoretical frameworks
- Mapping debates and schools of thought
- Preserving disagreements rather than flattening them
"""

from typing import Dict, List, Optional, Any, Set
from enum import Enum
from pydantic import BaseModel, Field

from aquila_r.modules.base import (
    BaseModule,
    ModuleContext,
    ModuleResult,
    ModuleStatus,
    Finding,
)


class TheoreticalPosition(BaseModel):
    """A theoretical position or school of thought."""
    
    name: str
    description: str
    key_proponents: List[str] = Field(default_factory=list)
    key_claims: List[str] = Field(default_factory=list)
    evidence_types: List[str] = Field(default_factory=list)
    critiques: List[str] = Field(default_factory=list)
    language_tradition: str = Field(default="both")  # en, ar, both


class ScholarlyDebate(BaseModel):
    """A debate or disagreement in the literature."""
    
    topic: str
    positions: List[TheoreticalPosition] = Field(default_factory=list)
    unresolved_questions: List[str] = Field(default_factory=list)
    methodological_differences: List[str] = Field(default_factory=list)
    consensus_points: List[str] = Field(default_factory=list)
    
    def is_contested(self) -> bool:
        """Check if debate is still contested."""
        return len(self.positions) > 1 and len(self.unresolved_questions) > 0


class ConceptualFramework(BaseModel):
    """A conceptual or theoretical framework."""
    
    name: str
    description: str
    core_concepts: List[str] = Field(default_factory=list)
    relationships: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    applicability: str = Field(default="")
    limitations: List[str] = Field(default_factory=list)


class LiteratureTheme(BaseModel):
    """A theme identified in the literature."""
    
    name: str
    description: str
    source_count: int = Field(default=0)
    languages: List[str] = Field(default_factory=list)
    sub_themes: List[str] = Field(default_factory=list)
    key_findings: List[str] = Field(default_factory=list)


class SynthesisResult(ModuleResult):
    """Extended result for synthesis module."""
    
    themes: List[LiteratureTheme] = Field(default_factory=list)
    debates: List[ScholarlyDebate] = Field(default_factory=list)
    frameworks: List[ConceptualFramework] = Field(default_factory=list)
    theoretical_positions: List[TheoreticalPosition] = Field(default_factory=list)
    consensus_findings: List[str] = Field(default_factory=list)
    contested_findings: List[str] = Field(default_factory=list)
    
    def get_unresolved_questions(self) -> List[str]:
        """Get all unresolved questions across debates."""
        questions = []
        for debate in self.debates:
            questions.extend(debate.unresolved_questions)
        return questions


class SynthesisModule(BaseModule):
    """
    Research Synthesis Module.
    
    Synthesizes literature into coherent frameworks while
    preserving scholarly disagreements and nuance.
    """
    
    name = "synthesis"
    description = "Literature synthesis, framework building, and debate mapping"
    supported_languages = ["en", "ar"]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._themes_cache: Dict[str, LiteratureTheme] = {}
    
    def execute(self, context: ModuleContext) -> SynthesisResult:
        """
        Execute research synthesis.
        
        Args:
            context: Execution context
            
        Returns:
            SynthesisResult with themes, debates, and frameworks
        """
        issues = self.validate_context(context)
        if issues:
            return SynthesisResult(
                module_name=self.name,
                status=ModuleStatus.FAILED,
                warnings=[self.create_warning(issue, "high") for issue in issues],
            )
        
        result = SynthesisResult(
            module_name=self.name,
            status=ModuleStatus.COMPLETED,
            language=context.language,
        )
        
        # Add methodology notes
        result.methodology_notes.append(
            "Synthesis preserves scholarly disagreements and avoids "
            "creating artificial consensus. Contested findings are "
            "explicitly marked as such."
        )
        
        # Add limitation
        result.limitations.append(self.create_limitation(
            description="Full synthesis requires LLM integration and literature retrieval",
            impact="high",
            mitigation="Configure LLM provider and retrieval tools",
        ))
        
        return result
    
    def build_framework(
        self,
        name: str,
        concepts: List[str],
        relationships: List[str],
        source_findings: List[Finding],
    ) -> ConceptualFramework:
        """
        Build a conceptual framework from findings.
        
        Args:
            name: Framework name
            concepts: Core concepts
            relationships: Relationships between concepts
            source_findings: Findings that inform the framework
            
        Returns:
            ConceptualFramework object
        """
        # Extract assumptions from findings
        assumptions = []
        for finding in source_findings:
            if "assumption" in finding.metadata:
                assumptions.append(finding.metadata["assumption"])
        
        # Build framework
        framework = ConceptualFramework(
            name=name,
            description=f"Conceptual framework integrating {len(concepts)} key concepts",
            core_concepts=concepts,
            relationships=relationships,
            assumptions=assumptions,
        )
        
        # Add limitation about construction
        framework.limitations.append(
            "Framework constructed from available sources; "
            "may not represent complete theoretical landscape"
        )
        
        return framework
    
    def map_debate(
        self,
        topic: str,
        positions: List[Dict[str, Any]],
    ) -> ScholarlyDebate:
        """
        Map a scholarly debate.
        
        Args:
            topic: Debate topic
            positions: List of position dictionaries
            
        Returns:
            ScholarlyDebate object
        """
        theoretical_positions = []
        
        for pos_data in positions:
            position = TheoreticalPosition(
                name=pos_data.get("name", "Unknown"),
                description=pos_data.get("description", ""),
                key_proponents=pos_data.get("proponents", []),
                key_claims=pos_data.get("claims", []),
                critiques=pos_data.get("critiques", []),
            )
            theoretical_positions.append(position)
        
        debate = ScholarlyDebate(
            topic=topic,
            positions=theoretical_positions,
        )
        
        return debate
    
    def identify_themes(
        self,
        findings: List[Finding],
        min_occurrence: int = 2,
    ) -> List[LiteratureTheme]:
        """
        Identify themes from research findings.
        
        Args:
            findings: List of research findings
            min_occurrence: Minimum occurrences to count as theme
            
        Returns:
            List of identified themes
        """
        # Simple keyword-based theme identification
        # Full implementation would use NLP/LLM
        
        themes: List[LiteratureTheme] = []
        
        # Placeholder - actual implementation needs NLP
        if findings:
            # Count language distribution
            languages: Set[str] = set()
            for f in findings:
                languages.add(f.language)
            
            # Create a placeholder theme
            themes.append(LiteratureTheme(
                name="Primary Research Theme",
                description="Theme identification requires LLM integration",
                source_count=len(findings),
                languages=list(languages),
            ))
        
        return themes
    
    def synthesize_findings(
        self,
        findings: List[Finding],
        preserve_disagreements: bool = True,
    ) -> tuple[List[str], List[str]]:
        """
        Synthesize findings into consensus and contested lists.
        
        Args:
            findings: List of findings to synthesize
            preserve_disagreements: Whether to keep disagreements explicit
            
        Returns:
            Tuple of (consensus_findings, contested_findings)
        """
        consensus: List[str] = []
        contested: List[str] = []
        
        # Group findings by topic/theme (simplified)
        # Full implementation would use semantic similarity
        
        high_confidence = [f for f in findings if f.confidence >= 0.8]
        medium_confidence = [f for f in findings if 0.5 <= f.confidence < 0.8]
        low_confidence = [f for f in findings if f.confidence < 0.5]
        
        # High confidence with multiple sources -> consensus
        for finding in high_confidence:
            consensus.append(finding.content)
        
        # Lower confidence or single source -> contested
        if preserve_disagreements:
            for finding in medium_confidence + low_confidence:
                contested.append(f"[Confidence: {finding.confidence:.0%}] {finding.content}")
        
        return consensus, contested
    
    def generate_literature_review_structure(
        self,
        themes: List[LiteratureTheme],
        debates: List[ScholarlyDebate],
        language: str = "en",
    ) -> str:
        """
        Generate structured literature review outline.
        
        Args:
            themes: Identified themes
            debates: Mapped debates
            language: Output language
            
        Returns:
            Structured outline as markdown
        """
        if language == "ar":
            return self._generate_arabic_outline(themes, debates)
        return self._generate_english_outline(themes, debates)
    
    def _generate_english_outline(
        self,
        themes: List[LiteratureTheme],
        debates: List[ScholarlyDebate],
    ) -> str:
        """Generate English outline."""
        lines = ["# Literature Review Structure\n"]
        
        lines.append("\n## 1. Introduction\n")
        lines.append("- Research context and significance\n")
        lines.append("- Scope and boundaries\n")
        lines.append("- Review methodology\n")
        
        lines.append("\n## 2. Thematic Analysis\n")
        for i, theme in enumerate(themes, 1):
            lines.append(f"\n### 2.{i}. {theme.name}\n")
            lines.append(f"- Sources: {theme.source_count}\n")
            lines.append(f"- Languages: {', '.join(theme.languages)}\n")
            if theme.sub_themes:
                lines.append("- Sub-themes:\n")
                for st in theme.sub_themes:
                    lines.append(f"  - {st}\n")
        
        lines.append("\n## 3. Scholarly Debates\n")
        for i, debate in enumerate(debates, 1):
            lines.append(f"\n### 3.{i}. {debate.topic}\n")
            if debate.is_contested():
                lines.append("*Status: Contested*\n")
            for pos in debate.positions:
                lines.append(f"\n#### Position: {pos.name}\n")
                lines.append(f"{pos.description}\n")
        
        lines.append("\n## 4. Synthesis and Gaps\n")
        lines.append("- Consensus findings\n")
        lines.append("- Contested areas\n")
        lines.append("- Research gaps\n")
        
        lines.append("\n## 5. Conclusion\n")
        lines.append("- Key insights\n")
        lines.append("- Limitations of review\n")
        lines.append("- Future research directions\n")
        
        return "".join(lines)
    
    def _generate_arabic_outline(
        self,
        themes: List[LiteratureTheme],
        debates: List[ScholarlyDebate],
    ) -> str:
        """Generate Arabic outline."""
        lines = ["# هيكل مراجعة الأدبيات\n"]
        
        lines.append("\n## 1. المقدمة\n")
        lines.append("- سياق البحث وأهميته\n")
        lines.append("- النطاق والحدود\n")
        lines.append("- منهجية المراجعة\n")
        
        lines.append("\n## 2. التحليل الموضوعي\n")
        for i, theme in enumerate(themes, 1):
            lines.append(f"\n### 2.{i}. {theme.name}\n")
            lines.append(f"- المصادر: {theme.source_count}\n")
            lines.append(f"- اللغات: {', '.join(theme.languages)}\n")
        
        lines.append("\n## 3. النقاشات العلمية\n")
        for i, debate in enumerate(debates, 1):
            lines.append(f"\n### 3.{i}. {debate.topic}\n")
        
        lines.append("\n## 4. التوليف والفجوات\n")
        lines.append("- النتائج المتفق عليها\n")
        lines.append("- المناطق المتنازع عليها\n")
        lines.append("- فجوات البحث\n")
        
        lines.append("\n## 5. الخاتمة\n")
        lines.append("- الرؤى الرئيسية\n")
        lines.append("- قيود المراجعة\n")
        lines.append("- اتجاهات البحث المستقبلية\n")
        
        return "".join(lines)
