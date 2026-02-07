"""
Methodological Frameworks for Aquila-R.

Defines research paradigms and provides methodology-aware
guidance for research analysis.
"""

from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field


class ResearchParadigm(str, Enum):
    """Major research paradigms."""
    POSITIVIST = "positivist"
    INTERPRETIVIST = "interpretivist"
    CRITICAL = "critical"
    PRAGMATIST = "pragmatist"
    CONSTRUCTIVIST = "constructivist"
    POST_STRUCTURALIST = "post_structuralist"


class ResearchApproach(str, Enum):
    """Research approaches within paradigms."""
    QUANTITATIVE = "quantitative"
    QUALITATIVE = "qualitative"
    MIXED_METHODS = "mixed_methods"
    COMPARATIVE = "comparative"
    CASE_STUDY = "case_study"
    ETHNOGRAPHIC = "ethnographic"
    HISTORICAL = "historical"
    EXPERIMENTAL = "experimental"


class ParadigmDescription(BaseModel):
    """Description of a research paradigm."""
    
    paradigm: ResearchParadigm
    name_en: str
    name_ar: str
    description_en: str
    description_ar: str
    ontology: str  # View of reality
    epistemology: str  # View of knowledge
    methodology: str  # Preferred approaches
    key_assumptions: List[str]
    common_methods: List[str]
    strengths: List[str]
    limitations: List[str]


class MethodologyFramework:
    """
    Framework for methodology awareness.
    
    Provides descriptions, assumptions, and guidance for
    different research paradigms.
    """
    
    def __init__(self):
        """Initialize the framework."""
        self._paradigms = self._load_paradigms()
    
    def _load_paradigms(self) -> Dict[ResearchParadigm, ParadigmDescription]:
        """Load paradigm descriptions."""
        return {
            ResearchParadigm.POSITIVIST: ParadigmDescription(
                paradigm=ResearchParadigm.POSITIVIST,
                name_en="Positivism",
                name_ar="الوضعية",
                description_en=(
                    "Positivism assumes an objective reality that can be observed and "
                    "measured. It emphasizes hypothesis testing, quantification, and "
                    "the search for general laws."
                ),
                description_ar=(
                    "تفترض الوضعية وجود واقع موضوعي يمكن ملاحظته وقياسه. "
                    "تركز على اختبار الفرضيات والتكميم والبحث عن قوانين عامة."
                ),
                ontology="Realist: reality exists independently of perception",
                epistemology="Objectivist: knowledge through empirical observation",
                methodology="Quantitative, experimental, hypothesis-driven",
                key_assumptions=[
                    "Reality is objective and measurable",
                    "Researcher can be value-neutral",
                    "General laws can be discovered",
                    "Causation can be established through controlled methods",
                ],
                common_methods=[
                    "Surveys", "Experiments", "Statistical analysis",
                    "Hypothesis testing", "Regression analysis"
                ],
                strengths=[
                    "Rigorous methodology",
                    "Replicable findings",
                    "Generalizable results",
                ],
                limitations=[
                    "May oversimplify complex phenomena",
                    "Struggles with meaning and interpretation",
                    "Value-neutrality is contested",
                ],
            ),
            ResearchParadigm.INTERPRETIVIST: ParadigmDescription(
                paradigm=ResearchParadigm.INTERPRETIVIST,
                name_en="Interpretivism",
                name_ar="التفسيرية",
                description_en=(
                    "Interpretivism focuses on understanding meaning, context, and "
                    "subjective experience. It emphasizes how people make sense of "
                    "their world."
                ),
                description_ar=(
                    "تركز التفسيرية على فهم المعنى والسياق والتجربة الذاتية. "
                    "تؤكد على كيفية فهم الناس لعالمهم."
                ),
                ontology="Relativist: multiple realities constructed by individuals",
                epistemology="Subjectivist: knowledge through interpretation",
                methodology="Qualitative, hermeneutic, understanding-focused",
                key_assumptions=[
                    "Reality is socially constructed",
                    "Understanding requires interpretation",
                    "Context shapes meaning",
                    "Research is value-laden",
                ],
                common_methods=[
                    "Interviews", "Focus groups", "Discourse analysis",
                    "Ethnography", "Hermeneutics"
                ],
                strengths=[
                    "Rich, contextual understanding",
                    "Captures complexity and nuance",
                    "Centers participant perspectives",
                ],
                limitations=[
                    "Limited generalizability",
                    "Potential researcher bias",
                    "Time-intensive",
                ],
            ),
            ResearchParadigm.CRITICAL: ParadigmDescription(
                paradigm=ResearchParadigm.CRITICAL,
                name_en="Critical Theory",
                name_ar="النظرية النقدية",
                description_en=(
                    "Critical theory examines power structures, ideology, and social "
                    "inequalities. It aims not just to understand but to transform "
                    "oppressive conditions."
                ),
                description_ar=(
                    "تفحص النظرية النقدية هياكل السلطة والأيديولوجيا وعدم المساواة الاجتماعية. "
                    "تهدف ليس فقط للفهم بل لتحويل الظروف القمعية."
                ),
                ontology="Historical realism: reality shaped by power and history",
                epistemology="Value-mediated: knowledge serves interests",
                methodology="Critical, emancipatory, participatory",
                key_assumptions=[
                    "Power shapes knowledge and reality",
                    "Research should serve emancipatory goals",
                    "Status quo benefits dominant groups",
                    "Critique enables transformation",
                ],
                common_methods=[
                    "Critical discourse analysis", "Ideology critique",
                    "Participatory action research", "Historical analysis"
                ],
                strengths=[
                    "Reveals hidden power dynamics",
                    "Oriented toward change",
                    "Questions taken-for-granted assumptions",
                ],
                limitations=[
                    "May be seen as politically motivated",
                    "Normative stance explicit",
                    "Can oversimplify power relations",
                ],
            ),
            ResearchParadigm.PRAGMATIST: ParadigmDescription(
                paradigm=ResearchParadigm.PRAGMATIST,
                name_en="Pragmatism",
                name_ar="البراغماتية",
                description_en=(
                    "Pragmatism focuses on practical consequences and what works. "
                    "It is flexible about methods, choosing based on research questions."
                ),
                description_ar=(
                    "تركز البراغماتية على العواقب العملية وما ينجح. "
                    "مرنة حول الأساليب، تختار بناءً على أسئلة البحث."
                ),
                ontology="Diverse: accepts multiple forms of reality",
                epistemology="Practical: knowledge through action and consequences",
                methodology="Mixed methods, problem-centered",
                key_assumptions=[
                    "Research should be driven by practical problems",
                    "Methods should fit questions",
                    "What works is what matters",
                    "Multiple methods can be combined",
                ],
                common_methods=[
                    "Mixed methods", "Action research",
                    "Program evaluation", "Design-based research"
                ],
                strengths=[
                    "Flexible and adaptive",
                    "Problem-focused",
                    "Bridges qualitative-quantitative divide",
                ],
                limitations=[
                    "May lack theoretical depth",
                    "Can be seen as atheoretical",
                    "Potential for inconsistency",
                ],
            ),
        }
    
    def get_paradigm(self, paradigm: ResearchParadigm) -> Optional[ParadigmDescription]:
        """Get description of a paradigm."""
        return self._paradigms.get(paradigm)
    
    def get_all_paradigms(self) -> List[ParadigmDescription]:
        """Get all paradigm descriptions."""
        return list(self._paradigms.values())
    
    def get_paradigm_assumptions(self, paradigm: ResearchParadigm) -> List[str]:
        """Get key assumptions of a paradigm."""
        desc = self._paradigms.get(paradigm)
        return desc.key_assumptions if desc else []
    
    def compare_paradigms(
        self,
        paradigm_a: ResearchParadigm,
        paradigm_b: ResearchParadigm,
        language: str = "en",
    ) -> Dict[str, Any]:
        """
        Compare two paradigms.
        
        Args:
            paradigm_a: First paradigm
            paradigm_b: Second paradigm
            language: Output language
            
        Returns:
            Comparison dictionary
        """
        desc_a = self._paradigms.get(paradigm_a)
        desc_b = self._paradigms.get(paradigm_b)
        
        if not desc_a or not desc_b:
            return {"error": "Paradigm not found"}
        
        name_key = f"name_{language}"
        desc_key = f"description_{language}"
        
        return {
            "paradigm_a": {
                "name": getattr(desc_a, name_key, desc_a.name_en),
                "ontology": desc_a.ontology,
                "epistemology": desc_a.epistemology,
                "strengths": desc_a.strengths,
            },
            "paradigm_b": {
                "name": getattr(desc_b, name_key, desc_b.name_en),
                "ontology": desc_b.ontology,
                "epistemology": desc_b.epistemology,
                "strengths": desc_b.strengths,
            },
            "complementary_aspects": self._find_complementary(desc_a, desc_b),
            "tensions": self._find_tensions(desc_a, desc_b),
        }
    
    def _find_complementary(
        self,
        a: ParadigmDescription,
        b: ParadigmDescription,
    ) -> List[str]:
        """Find complementary aspects between paradigms."""
        complementary = []
        
        # Example: positivist + interpretivist
        if (a.paradigm == ResearchParadigm.POSITIVIST and 
            b.paradigm == ResearchParadigm.INTERPRETIVIST):
            complementary.append(
                "Quantitative breadth (positivist) + Qualitative depth (interpretivist)"
            )
        
        return complementary
    
    def _find_tensions(
        self,
        a: ParadigmDescription,
        b: ParadigmDescription,
    ) -> List[str]:
        """Find tensions between paradigms."""
        tensions = []
        
        # Example: different ontologies
        if a.ontology != b.ontology:
            tensions.append(
                f"Ontological tension: {a.ontology} vs {b.ontology}"
            )
        
        return tensions


def get_paradigm_description(
    paradigm: ResearchParadigm,
    language: str = "en",
) -> str:
    """
    Get a description of the paradigm in specified language.
    
    Args:
        paradigm: The paradigm
        language: Language code ("en" or "ar")
        
    Returns:
        Description text
    """
    framework = MethodologyFramework()
    desc = framework.get_paradigm(paradigm)
    
    if not desc:
        return "Unknown paradigm"
    
    if language == "ar":
        return desc.description_ar
    return desc.description_en
