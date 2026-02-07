"""
Main Aquila-R Agent Implementation.

The central orchestrator that coordinates all research modules,
maintains identity constraints, and manages research workflows.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field
import logging

from aquila_r.core.identity import AgentIdentity, AgentRole, IdentityGuard
from aquila_r.core.config import AquilaConfig, MethodologyParadigm, OutputLanguage, LLMProvider
from aquila_r.core.memory import ResearchMemory, MemoryItemType
from aquila_r.core.llm import LLMClient
import asyncio as int_asyncio
import json


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aquila_r")


class ResearchRequest(BaseModel):
    """A research request to Aquila-R."""
    
    query: str = Field(description="The research query or question")
    language: OutputLanguage = Field(default=OutputLanguage.AUTO)
    methodology: Optional[MethodologyParadigm] = Field(default=None)
    modules: List[str] = Field(
        default_factory=lambda: ["literature", "synthesis", "critical"]
    )
    max_sources: int = Field(default=20, ge=1, le=100)
    output_format: str = Field(default="structured")
    context: Optional[Dict[str, Any]] = Field(default=None)


class ResearchOutput(BaseModel):
    """Structured output from Aquila-R research."""
    
    research_question: str = Field(description="Formulated research question")
    methodology: str = Field(description="Methodological approach used")
    evidence: List[Dict[str, Any]] = Field(description="Evidence and findings")
    analysis: str = Field(description="Critical analysis")
    gaps: List[str] = Field(description="Identified gaps and limitations")
    next_steps: List[str] = Field(description="Suggested next steps")
    sources: List[Dict[str, Any]] = Field(description="Sources consulted")
    confidence: float = Field(description="Confidence in findings", ge=0.0, le=1.0)
    language: str = Field(description="Output language")
    warnings: List[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def to_markdown(self) -> str:
        """Convert output to markdown format."""
        sections = []
        
        # Header
        sections.append(f"# Research Analysis\n")
        sections.append(f"*Generated: {self.generated_at.strftime('%Y-%m-%d %H:%M')} UTC*\n")
        
        # Research Question
        sections.append(f"\n## 1. Research Question\n\n{self.research_question}\n")
        
        # Methodology
        sections.append(f"\n## 2. Methodological Approach\n\n{self.methodology}\n")
        
        # Evidence
        sections.append("\n## 3. Evidence & Findings\n")
        for i, ev in enumerate(self.evidence, 1):
            finding = ev.get("finding", "")
            source = ev.get("source", "")
            conf = ev.get("confidence", "medium")
            sections.append(f"\n### Finding {i}\n")
            sections.append(f"{finding}\n")
            if source:
                sections.append(f"*Source: {source}*\n")
            sections.append(f"*Confidence: {conf}*\n")
        
        # Analysis
        sections.append(f"\n## 4. Critical Analysis\n\n{self.analysis}\n")
        
        # Gaps
        sections.append("\n## 5. Gaps & Limitations\n")
        for gap in self.gaps:
            sections.append(f"- {gap}\n")
        
        # Next Steps
        sections.append("\n## 6. Suggested Next Steps\n")
        for step in self.next_steps:
            sections.append(f"- {step}\n")
        
        # Sources
        sections.append("\n## Sources\n")
        for source in self.sources:
            title = source.get("title", "Unknown")
            authors = source.get("authors", [])
            year = source.get("year", "n.d.")
            verified = source.get("verified", False)
            status = "✓" if verified else "⚠️"
            authors_str = ", ".join(authors) if authors else "Unknown"
            sections.append(f"- {status} {authors_str} ({year}). *{title}*\n")
        
        # Warnings
        if self.warnings:
            sections.append("\n---\n\n**⚠️ Warnings:**\n")
            for warning in self.warnings:
                sections.append(f"- {warning}\n")
        
        # Confidence
        sections.append(f"\n---\n*Overall Confidence: {self.confidence:.0%}*\n")
        
        return "".join(sections)
    
    def to_arabic_markdown(self) -> str:
        """Convert output to Arabic markdown format."""
        sections = []
        
        sections.append(f"# تحليل بحثي\n")
        sections.append(f"*تاريخ الإنشاء: {self.generated_at.strftime('%Y-%m-%d %H:%M')} UTC*\n")
        
        sections.append(f"\n## 1. سؤال البحث\n\n{self.research_question}\n")
        sections.append(f"\n## 2. المنهج المتبع\n\n{self.methodology}\n")
        
        sections.append("\n## 3. الأدلة والنتائج\n")
        for i, ev in enumerate(self.evidence, 1):
            finding = ev.get("finding", "")
            source = ev.get("source", "")
            conf = ev.get("confidence", "متوسط")
            sections.append(f"\n### النتيجة {i}\n")
            sections.append(f"{finding}\n")
            if source:
                sections.append(f"*المصدر: {source}*\n")
            sections.append(f"*درجة الثقة: {conf}*\n")
        
        sections.append(f"\n## 4. التحليل النقدي\n\n{self.analysis}\n")
        
        sections.append("\n## 5. الفجوات والقيود\n")
        for gap in self.gaps:
            sections.append(f"- {gap}\n")
        
        sections.append("\n## 6. الخطوات التالية المقترحة\n")
        for step in self.next_steps:
            sections.append(f"- {step}\n")
        
        sections.append("\n## المصادر\n")
        for source in self.sources:
            title = source.get("title", "غير معروف")
            verified = source.get("verified", False)
            status = "✓" if verified else "⚠️"
            sections.append(f"- {status} *{title}*\n")
        
        if self.warnings:
            sections.append("\n---\n\n**⚠️ تحذيرات:**\n")
            for warning in self.warnings:
                sections.append(f"- {warning}\n")
        
        sections.append(f"\n---\n*درجة الثقة الإجمالية: {self.confidence:.0%}*\n")
        
        return "".join(sections)


class AquilaR:
    """
    Aquila-R: Autonomous Bilingual Research Intelligence.
    
    Main agent class that orchestrates research operations,
    maintains identity constraints, and coordinates modules.
    """
    
    def __init__(
        self,
        config: Optional[AquilaConfig] = None,
        identity: Optional[AgentIdentity] = None,
    ):
        """
        Initialize Aquila-R agent.
        
        Args:
            config: Agent configuration (uses defaults if None)
            identity: Agent identity (uses defaults if None)
        """
        self.config = config or AquilaConfig.from_env()
        self.identity = identity or AgentIdentity()
        self.identity_guard = IdentityGuard(self.identity)
        
        self.memory = ResearchMemory(
            max_items=self.config.memory.max_context_items,
            enable_project_memory=self.config.memory.project_memory,
        )
        
        self.llm = LLMClient(self.config.llm)
        self._initialized = True
        
        logger.info(f"Aquila-R v{self.identity.version} initialized")
    
    def _detect_language(self, text: str) -> str:
        """Detect if text is primarily Arabic or English."""
        arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
        total_chars = len(text.replace(" ", ""))
        
        if total_chars == 0:
            return "en"
        
        arabic_ratio = arabic_chars / total_chars
        return "ar" if arabic_ratio > 0.3 else "en"
    
    def _resolve_language(
        self, 
        request_language: OutputLanguage, 
        query: str
    ) -> str:
        """Resolve the output language."""
        if request_language == OutputLanguage.AUTO:
            return self._detect_language(query)
        elif request_language == OutputLanguage.BILINGUAL:
            return "bilingual"
        return request_language.value
    
    def _resolve_methodology(
        self,
        request_methodology: Optional[MethodologyParadigm],
    ) -> str:
        """Resolve the methodology paradigm."""
        if request_methodology and request_methodology != MethodologyParadigm.AUTO:
            return request_methodology.value
        
        default = self.config.research.default_methodology
        if default != MethodologyParadigm.AUTO:
            return default.value
        
        return "mixed"  # Default to mixed if auto
    
    def get_system_prompt(self, language: str = "en") -> str:
        """Get the system prompt for LLM interactions."""
        return self.identity.get_system_prompt(language)
    
    def analyze(
        self,
        query: str,
        modules: Optional[List[str]] = None,
        methodology: Optional[MethodologyParadigm] = None,
        output_language: Optional[OutputLanguage] = None,
        max_sources: int = 20,
        context: Optional[Dict[str, Any]] = None,
    ) -> ResearchOutput:
        """
        Perform research analysis on a query.
        
        Args:
            query: The research question or topic
            modules: Which modules to use (literature, synthesis, critical, etc.)
            methodology: Methodological paradigm to apply
            output_language: Desired output language
            max_sources: Maximum sources to consult
            context: Additional context for the analysis
            
        Returns:
            Structured research output
        """
        request = ResearchRequest(
            query=query,
            modules=modules or ["literature", "synthesis", "critical"],
            methodology=methodology,
            language=output_language or OutputLanguage.AUTO,
            max_sources=max_sources,
            context=context,
        )
        
        # Run async execution synchronously
        return int_asyncio.run(self._execute_research(request))
    
    async def _execute_research(self, request: ResearchRequest) -> ResearchOutput:
        """Execute a research request."""
        logger.info(f"Executing research: {request.query[:100]}...")
        
        # Resolve language and methodology
        output_lang = self._resolve_language(request.language, request.query)
        methodology = self._resolve_methodology(request.methodology)
        
        # Record in memory
        self.memory.add_item(
            self.memory.record_assumption(f"Methodology: {methodology}").model_copy()
        )
        
        try:
            # Generate research using LLM
            output_data = await self._run_research_generation(
                request.query, 
                methodology, 
                output_lang
            )
            
            output = ResearchOutput(
                research_question=request.query,
                methodology=output_data.get("methodology", self._get_methodology_description(methodology, output_lang)),
                evidence=output_data.get("evidence", []),
                analysis=output_data.get("analysis", "Analysis failed to generate."),
                gaps=output_data.get("gaps", []),
                next_steps=output_data.get("next_steps", []),
                sources=output_data.get("sources", []),
                confidence=output_data.get("confidence", 0.5),
                language=output_lang,
                generated_at=datetime.utcnow(),
            )
            
        except Exception as e:
            logger.error(f"Research generation failed: {str(e)}")
            # Fallback to sparse output on error
            output = ResearchOutput(
                research_question=request.query,
                methodology=self._get_methodology_description(methodology, output_lang),
                evidence=[],
                analysis=f"Analysis failed due to error: {str(e)}",
                gaps=[],
                next_steps=[],
                sources=[],
                confidence=0.0,
                language=output_lang,
                warnings=[f"Error during generation: {str(e)}"]
            )
        
        # Validate output against identity constraints
        if output_lang == "en":
            markdown = output.to_markdown()
        else:
            markdown = output.to_arabic_markdown()
        
        warnings = self.identity.validate_response(markdown)
        output.warnings.extend(warnings)
        
        return output

    async def _run_research_generation(
        self, 
        query: str, 
        methodology: str, 
        lang: str
    ) -> Dict[str, Any]:
        """
        Run the LLM generation process.
        
        Constructs the prompt and calls the LLM.
        """
        system_prompt = self.get_system_prompt(lang)
        
        # Construct detailed prompt
        if lang == "ar":
            prompt = f"""
            سؤال البحث: {query}
            المنهجية: {methodology}
            
            قم بإجراء تحليل بحثي شامل ينتج عنه مخرجات بصيغة JSON بالتنسيق التالي:
            {{
                "methodology": "وصف المنهجية المستخدمة",
                "evidence": [
                    {{"finding": "النتيجة الرئيسية 1", "confidence": "high/medium/low", "source": "المصدر إن وجد"}}
                ],
                "analysis": "تحليل نقدي مفصل يربط بين الأدلة (طويل ومفصل)",
                "gaps": ["فجوة 1", "فجوة 2"],
                "next_steps": ["خطوة 1", "خطوة 2"],
                "sources": [
                    {{"title": "عنوان المصدر", "authors": ["مؤلف"], "year": 2023, "verified": false}}
                ],
                "confidence": 0.8
            }}
            
            تأكد من أن التحليل عميق، نقدي، ويلتزم بمنهجية {methodology}.
            لا تختلق المصادر. إذا لم تكن هناك مصادر، اترك القائمة فارغة.
            """
        else:
            prompt = f"""
            Research Query: {query}
            Methodology: {methodology}
            
            Perform a comprehensive research analysis producing JSON output with the following schema:
            {{
                "methodology": "Description of methodology used",
                "evidence": [
                    {{"finding": "Key finding 1", "confidence": "high/medium/low", "source": "Citation if available"}}
                ],
                "analysis": "Detailed critical analysis synthesizing findings (long and rigorous)",
                "gaps": ["Gap 1", "Gap 2"],
                "next_steps": ["Step 1", "Step 2"],
                "sources": [
                    {{"title": "Source Title", "authors": ["Author"], "year": 2023, "verified": false}}
                ],
                "confidence": 0.8
            }}
            
            Ensure the analysis is deep, critical, and adheres to the {methodology} paradigm.
            DO NOT hallucinate sources. If you don't have sources, leave the list empty or note they are general knowledge.
            """
            
        # Call LLM
        response_text = await self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            json_output=True
        )
        
        # Parse JSON
        try:
            import json
            return json.loads(response_text)
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON output, falling back to text wrapping")
            return {
                "analysis": response_text,
                "confidence": 0.0,
                "warnings": ["Output format parsing failed"]
            }
    
    def _get_methodology_description(self, methodology: str, lang: str) -> str:
        """Get methodology description in specified language."""
        descriptions = {
            "positivist": {
                "en": "This analysis follows a positivist/empirical approach, focusing on observable, measurable phenomena and hypothesis testing.",
                "ar": "يتبع هذا التحليل منهجاً وضعياً/تجريبياً، يركز على الظواهر القابلة للملاحظة والقياس واختبار الفرضيات.",
            },
            "interpretivist": {
                "en": "This analysis follows an interpretivist approach, emphasizing understanding meaning, context, and subjective experience.",
                "ar": "يتبع هذا التحليل منهجاً تفسيرياً، مع التركيز على فهم المعنى والسياق والتجربة الذاتية.",
            },
            "critical": {
                "en": "This analysis follows a critical approach, examining power structures, ideology, and systemic factors.",
                "ar": "يتبع هذا التحليل منهجاً نقدياً، يفحص هياكل السلطة والأيديولوجيا والعوامل النظامية.",
            },
            "mixed": {
                "en": "This analysis employs a mixed-methods approach, integrating multiple methodological perspectives as appropriate to the research question.",
                "ar": "يستخدم هذا التحليل منهجاً مختلطاً، يدمج وجهات نظر منهجية متعددة حسب مقتضيات سؤال البحث.",
            },
        }
        
        desc = descriptions.get(methodology, descriptions["mixed"])
        return desc.get(lang, desc["en"])
    
    def create_project(
        self,
        name: str,
        description: Optional[str] = None,
    ) -> str:
        """
        Create a new research project context.
        
        Args:
            name: Project name
            description: Project description
            
        Returns:
            Project ID
        """
        project = self.memory.create_project(name, description)
        logger.info(f"Created project: {name} ({project.project_id})")
        return project.project_id
    
    def get_project_summary(self) -> Optional[Dict[str, Any]]:
        """Get summary of active project."""
        project = self.memory.get_active_project()
        if not project:
            return None
        
        return {
            "id": project.project_id,
            "name": project.name,
            "description": project.description,
            "sources_count": len(project.sources),
            "findings_count": len(project.findings),
            "assumptions": project.assumptions,
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat(),
        }
    
    def validate_configuration(self) -> List[str]:
        """Validate current configuration."""
        return self.config.validate_for_operation()
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status information."""
        
        # Check LLM connection
        llm_connected = False
        try:
            # We need to run the async check synchronously here
            llm_connected = int_asyncio.run(self.llm.check_connection())
        except Exception:
            llm_connected = False
            
        return {
            "agent": self.identity.name,
            "version": self.identity.version,
            "roles": [r.value for r in self.identity.active_roles],
            "config_valid": len(self.validate_configuration()) == 0,
            "memory": self.memory.get_session_summary(),
            "llm_provider": self.config.llm.provider.value,
            "llm_configured": self.config.llm.get_api_key() is not None or self.config.llm.provider == LLMProvider.OLLAMA,
            "llm_connected": llm_connected,
        }

