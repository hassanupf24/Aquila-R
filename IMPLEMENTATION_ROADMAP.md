# Aquila-R: Implementation Roadmap & Action Plan

**Purpose:** Specific, actionable steps to move from Beta (55% complete) to Production-Ready (85%+ complete)

---

## Phase 1: Foundation & Core (Weeks 1-2)

### Goal
Establish error handling, testing infrastructure, and async foundations

### 1.1 Fix Import Issues

**File:** `aquila_r/core/agent.py`

**Current:**
```python
import asyncio as int_asyncio  # Line 18
```

**Change to:**
```python
import asyncio
```

**Rationale:** The odd naming is confusing and appears to be a typo. If intentional, should have explanatory comment.

---

### 1.2 Create Custom Exception Hierarchy

**Create file:** `aquila_r/core/exceptions.py`

```python
"""
Custom exceptions for Aquila-R.

Provides domain-specific error types for better error handling
and clearer error messages.
"""

class AquilaError(Exception):
    """Base exception for all Aquila-R errors."""
    pass


class ConfigurationError(AquilaError):
    """Configuration is invalid or incomplete."""
    pass


class ModuleExecutionError(AquilaError):
    """Error during module execution."""
    pass


class LLMError(AquilaError):
    """Error communicating with LLM."""
    pass


class IdentityViolationError(AquilaError):
    """Agent attempted to violate identity constraint."""
    pass


class ValidationError(AquilaError):
    """Data validation failed."""
    pass


class MemoryError(AquilaError):
    """Error in memory operations."""
    pass


class ToolError(AquilaError):
    """Error in tool execution."""
    pass
```

**Update imports in:**
- `core/agent.py`
- `core/config.py`
- `modules/base.py`
- `tools/base.py`

---

### 1.3 Create Test Fixtures & Mocks

**Create file:** `tests/conftest.py`

```python
"""
Pytest configuration and fixtures for Aquila-R tests.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from aquila_r import AquilaConfig
from aquila_r.core.llm import LLMClient
from aquila_r.core.identity import AgentIdentity


@pytest.fixture
def mock_llm_client():
    """Mock LLM client for testing."""
    mock = AsyncMock(spec=LLMClient)
    mock.generate = AsyncMock(return_value="Mock LLM response")
    return mock


@pytest.fixture
def test_config():
    """Test configuration with dummy API key."""
    return AquilaConfig(
        llm=AquilaConfig.default_llm_config(provider="local")
    )


@pytest.fixture
def test_identity():
    """Test agent identity."""
    return AgentIdentity()


@pytest.fixture
def sample_research_query():
    """Sample research query for testing."""
    return "What are the main theories of state formation?"


@pytest.fixture
def sample_research_results():
    """Sample research results for testing."""
    return {
        "findings": [
            {
                "content": "Test finding 1",
                "confidence": 0.85,
                "source_id": "test_source_1",
            }
        ],
        "sources": [
            {
                "id": "test_source_1",
                "title": "Test Source",
                "authors": ["Author A"],
                "year": 2023,
            }
        ],
    }
```

---

### 1.4 Implement IdentityGuard Validation

**File:** `aquila_r/core/identity.py`

**Add to IdentityGuard class:**

```python
class IdentityGuard:
    """
    Enforces identity constraints on agent outputs and behaviors.
    
    Validates that findings, claims, and outputs comply with
    identity requirements.
    """
    
    def __init__(self, identity: AgentIdentity):
        self.identity = identity
        self.standards = identity.epistemic_standards
        self.rules = identity.integrity_rules
    
    def validate_finding(self, finding: "Finding") -> bool:
        """
        Validate a finding against identity constraints.
        
        Raises:
            IdentityViolationError: If constraint violated
        """
        # Check for fabricated content
        if finding.confidence > 0.95 and finding.source_id is None:
            raise IdentityViolationError(
                "High-confidence finding without source attribution"
            )
        
        # Check for overstatement
        if finding.confidence > 0.9 and "evidence_type" not in finding.metadata:
            raise IdentityViolationError(
                "High-confidence claim lacks evidence type specification"
            )
        
        return True
    
    def validate_claim(self, claim: str) -> bool:
        """
        Validate a claim text against prohibited behaviors.
        
        Raises:
            IdentityViolationError: If constraint violated
        """
        prohibited = [
            ("fabricated", "Making up facts"),
            ("invent", "Inventing data"),
            ("assume without evidence", "Unsupported assumption"),
        ]
        
        claim_lower = claim.lower()
        for keyword, violation_type in prohibited:
            if keyword in claim_lower:
                raise IdentityViolationError(
                    f"Claim violates integrity rule: {violation_type}"
                )
        
        return True
    
    def sanitize_output(
        self, output: "ResearchOutput"
    ) -> "ResearchOutput":
        """
        Sanitize output to remove constraint violations.
        
        Returns:
            Cleaned output with violations removed or flagged
        """
        # Remove high-confidence unsourced findings
        cleaned_findings = []
        for finding in output.evidence:
            try:
                if finding.get("confidence", 0) < 0.9 or finding.get("source"):
                    cleaned_findings.append(finding)
                else:
                    # Flag but keep with lower confidence
                    finding["confidence"] *= 0.7
                    finding["flagged"] = True
                    cleaned_findings.append(finding)
            except Exception:
                # If validation fails, exclude the finding
                pass
        
        output.evidence = cleaned_findings
        return output
```

---

### 1.5 Add Configuration Validation

**File:** `aquila_r/core/config.py`

**Add to AquilaConfig class:**

```python
def validate(self) -> List[str]:
    """
    Validate configuration completeness and correctness.
    
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Validate LLM configuration
    if not self.llm.api_key and self.llm.provider != LLMProvider.LOCAL:
        errors.append(
            f"Missing API key for {self.llm.provider}. "
            f"Set {self._get_env_var_name(self.llm.provider)}"
        )
    
    if self.llm.temperature < 0 or self.llm.temperature > 2:
        errors.append("LLM temperature must be between 0 and 2")
    
    if self.llm.max_tokens < 256:
        errors.append("LLM max_tokens must be at least 256")
    
    # Validate memory configuration
    if self.memory.max_context_items < 10:
        errors.append("Memory max_context_items must be at least 10")
    
    # Validate tool configuration
    # ... add tool validations ...
    
    return errors
```

**Update AquilaR.__init__():**

```python
def __init__(self, config: Optional[AquilaConfig] = None, ...):
    self.config = config or AquilaConfig.from_env()
    
    # Validate configuration
    errors = self.config.validate()
    if errors:
        logger.warning(f"Configuration issues detected:\n" + "\n".join(errors))
        if any("Missing API key" in e for e in errors):
            raise ConfigurationError(
                "Required API key missing. Cannot initialize agent."
            )
    
    # ... rest of initialization ...
```

---

### 1.6 Implement Async Execution Framework

**File:** `aquila_r/core/agent.py`

**Add method to AquilaR class:**

```python
async def _execute_modules_async(
    self,
    context: ModuleContext,
    modules: List[str],
) -> Dict[str, ModuleResult]:
    """
    Execute modules in parallel where possible.
    
    Args:
        context: Execution context
        modules: List of module names to execute
        
    Returns:
        Dictionary mapping module names to results
    """
    # Map module names to executables
    module_executors = {
        "literature": self._execute_literature,
        "critical": self._execute_critical,
        "synthesis": self._execute_synthesis,
        "evidence": self._execute_evidence,
        "writing": self._execute_writing,
    }
    
    # Create tasks for all requested modules
    tasks = {}
    for module_name in modules:
        if module_name in module_executors:
            executor = module_executors[module_name]
            tasks[module_name] = executor(context)
    
    # Execute all in parallel
    results = await asyncio.gather(
        *tasks.values(),
        return_exceptions=True,
    )
    
    # Map results back to module names
    output = {}
    for (module_name, result) in zip(tasks.keys(), results):
        if isinstance(result, Exception):
            output[module_name] = ModuleResult(
                module_name=module_name,
                status=ModuleStatus.FAILED,
                warnings=[self._create_warning(str(result), "high")],
            )
        else:
            output[module_name] = result
    
    return output
```

---

## Phase 2: Core Implementation (Weeks 2-4)

### Goal
Complete core module implementations and agent orchestration

### 2.1 Complete Agent.analyze() Method

**File:** `aquila_r/core/agent.py`

**Implement full analyze() with all logic:**

```python
async def analyze(
    self,
    query: str,
    modules: Optional[List[str]] = None,
    methodology: Optional[MethodologyParadigm] = None,
    output_language: OutputLanguage = OutputLanguage.AUTO,
    max_sources: int = 20,
) -> ResearchOutput:
    """
    Execute full research analysis on a query.
    
    This is the main entry point for research workflows.
    
    Args:
        query: Research question/query
        modules: Which modules to use (default: all)
        methodology: Research paradigm to use
        output_language: Output language (EN/AR/AUTO/BILINGUAL)
        max_sources: Max sources to retrieve
        
    Returns:
        Comprehensive research output
        
    Raises:
        ConfigurationError: If config invalid
        IdentityViolationError: If constraints violated
        ModuleExecutionError: If analysis fails
    """
    
    # 1. VALIDATE INPUT
    try:
        if not query or len(query.strip()) < 5:
            raise ValidationError("Query must be at least 5 characters")
        
        if len(query) > 2000:
            raise ValidationError("Query must be less than 2000 characters")
    except ValidationError as e:
        logger.error(f"Input validation failed: {e}")
        raise
    
    # 2. DETECT LANGUAGE
    query_language = self._detect_language(query)
    if output_language == OutputLanguage.AUTO:
        output_language = OutputLanguage.ENGLISH if query_language == "en" else OutputLanguage.ARABIC
    
    # 3. RESOLVE MODULES
    if modules is None:
        modules = ["literature", "critical", "synthesis"]
    
    available_modules = {"literature", "critical", "synthesis", "evidence", "writing"}
    resolved_modules = [m for m in modules if m in available_modules]
    
    if not resolved_modules:
        raise ValidationError(f"No valid modules requested. Available: {available_modules}")
    
    # 4. CREATE EXECUTION CONTEXT
    methodology = methodology or MethodologyParadigm.AUTO
    context = ModuleContext(
        query=query,
        language=query_language,
        methodology=methodology.value if methodology != MethodologyParadigm.AUTO else None,
        modules_requested=resolved_modules,
        max_sources=max_sources,
        timestamp=datetime.utcnow(),
    )
    
    # 5. RECORD QUERY IN MEMORY
    self.memory.record_query(query)
    
    # 6. EXECUTE MODULES
    logger.info(f"Starting analysis: {query[:50]}... with modules: {resolved_modules}")
    
    try:
        # Execute modules (async if possible)
        module_results = await self._execute_modules_async(context, resolved_modules)
    except Exception as e:
        logger.error(f"Module execution failed: {e}")
        raise ModuleExecutionError(f"Module execution failed: {str(e)}") from e
    
    # 7. AGGREGATE RESULTS
    aggregated = self._aggregate_module_results(module_results)
    
    # 8. VALIDATE INTEGRITY
    try:
        self.identity_guard.validate_finding(aggregated)
    except IdentityViolationError as e:
        logger.warning(f"Constraint violation detected: {e}")
        aggregated = self.identity_guard.sanitize_output(aggregated)
    
    # 9. FORMAT OUTPUT
    output = ResearchOutput(
        research_question=query,
        methodology=methodology.value,
        evidence=aggregated.get("findings", []),
        analysis=aggregated.get("analysis", ""),
        gaps=aggregated.get("gaps", []),
        next_steps=aggregated.get("next_steps", []),
        sources=aggregated.get("sources", []),
        confidence=aggregated.get("confidence", 0.5),
        language=output_language.value,
        warnings=aggregated.get("warnings", []),
    )
    
    # 10. RECORD IN MEMORY
    self.memory.record_analysis(query, output)
    
    logger.info(f"Analysis complete: {query[:50]}... (Confidence: {output.confidence:.0%})")
    
    return output
```

---

### 2.2 Implement Synthesis Module

**File:** `aquila_r/modules/synthesis.py`

```python
"""
Synthesis Module for Aquila-R.

Combines findings from literature and critical analysis
into coherent themes and conceptual frameworks.
"""

from typing import Dict, List, Optional, Any
from aquila_r.modules.base import (
    BaseModule,
    ModuleContext,
    ModuleResult,
    ModuleStatus,
    Finding,
)


class SynthesisResult(ModuleResult):
    """Result from synthesis module."""
    themes: List[Dict[str, Any]] = []
    conceptual_map: Dict[str, List[str]] = {}
    key_insights: List[str] = []
    research_trajectory: List[str] = []


class SynthesisModule(BaseModule):
    """
    Synthesis Module: Integrates findings into coherent frameworks.
    """
    
    name = "synthesis"
    description = "Theme identification and conceptual synthesis"
    
    def execute(self, context: ModuleContext) -> SynthesisResult:
        """
        Execute synthesis analysis.
        
        Takes findings from other modules and synthesizes them
        into coherent themes and conceptual frameworks.
        """
        result = SynthesisResult(
            module_name=self.name,
            status=ModuleStatus.COMPLETED,
            language=context.language,
        )
        
        try:
            # 1. Extract findings from context
            findings = context.get("findings", [])
            sources = context.get("sources", [])
            
            if not findings:
                result.status = ModuleStatus.SKIPPED
                result.warnings.append(
                    self.create_warning("No findings to synthesize", "low")
                )
                return result
            
            # 2. Identify themes
            themes = self._identify_themes(findings)
            result.themes = themes
            
            # 3. Build conceptual map
            concept_map = self._build_conceptual_map(themes)
            result.conceptual_map = concept_map
            
            # 4. Extract key insights
            insights = self._extract_key_insights(themes)
            result.key_insights = insights
            
            # 5. Create findings
            finding = Finding(
                content=f"Identified {len(themes)} main themes in literature",
                confidence=min(0.8, len(themes) / 10),
                source_id="synthesis_module",
                evidence_type="synthesis",
            )
            result.findings.append(finding)
            
        except Exception as e:
            result.status = ModuleStatus.FAILED
            result.warnings.append(self.create_warning(str(e), "high"))
        
        return result
    
    def _identify_themes(self, findings: List[Dict]) -> List[Dict[str, Any]]:
        """Group findings into themes."""
        themes = {}
        
        for finding in findings:
            # Extract key terms from finding content
            content = finding.get("content", "")
            # Simple keyword extraction (should be more sophisticated)
            theme_key = content.split()[0] if content else "unknown"
            
            if theme_key not in themes:
                themes[theme_key] = []
            
            themes[theme_key].append(finding)
        
        return [
            {
                "name": theme,
                "findings_count": len(findings),
                "average_confidence": sum(
                    f.get("confidence", 0.5) for f in findings
                ) / len(findings),
                "findings": findings,
            }
            for theme, findings in themes.items()
        ]
    
    def _build_conceptual_map(self, themes: List[Dict]) -> Dict[str, List[str]]:
        """Build relationships between themes."""
        concept_map = {}
        theme_names = [t["name"] for t in themes]
        
        for theme in themes:
            # Find related themes based on finding content overlap
            related = [
                other for other in theme_names 
                if other != theme["name"]
            ]
            concept_map[theme["name"]] = related[:3]  # Top 3 related
        
        return concept_map
    
    def _extract_key_insights(self, themes: List[Dict]) -> List[str]:
        """Extract high-level insights from themes."""
        insights = []
        
        for theme in sorted(themes, key=lambda t: t["average_confidence"], reverse=True)[:3]:
            insight = f"{theme['name']} emerged as a central theme ({theme['average_confidence']:.0%} confidence)"
            insights.append(insight)
        
        return insights
```

---

### 2.3 Implement Evidence Module

**File:** `aquila_r/modules/evidence.py`

```python
"""
Evidence Module for Aquila-R.

Verifies evidence claims and assesses evidentiary quality.
"""

from typing import Dict, List, Optional, Any
from aquila_r.modules.base import (
    BaseModule,
    ModuleContext,
    ModuleResult,
    ModuleStatus,
    Finding,
)


class EvidenceResult(ModuleResult):
    """Result from evidence module."""
    verified_claims: List[Dict[str, Any]] = []
    unverified_claims: List[Dict[str, Any]] = []
    contradiction_alerts: List[str] = []
    evidence_quality_score: float = 0.5


class EvidenceModule(BaseModule):
    """
    Evidence Module: Verifies evidence and assesses quality.
    """
    
    name = "evidence"
    description = "Evidence verification and quality assessment"
    
    def execute(self, context: ModuleContext) -> EvidenceResult:
        """Execute evidence verification."""
        result = EvidenceResult(
            module_name=self.name,
            status=ModuleStatus.COMPLETED,
            language=context.language,
        )
        
        try:
            # 1. Extract evidence from context
            evidence_items = context.get("evidence", [])
            sources = context.get("sources", [])
            
            if not evidence_items:
                result.status = ModuleStatus.SKIPPED
                return result
            
            # 2. Verify each evidence item
            for item in evidence_items:
                if self._verify_claim(item, sources):
                    result.verified_claims.append(item)
                else:
                    result.unverified_claims.append(item)
            
            # 3. Check for contradictions
            contradictions = self._find_contradictions(result.verified_claims)
            result.contradiction_alerts.extend(contradictions)
            
            # 4. Calculate overall evidence quality
            result.evidence_quality_score = self._calculate_quality_score(
                result.verified_claims,
                result.unverified_claims,
            )
            
            # 5. Create finding
            finding = Finding(
                content=f"Verified {len(result.verified_claims)} of {len(evidence_items)} evidence items",
                confidence=result.evidence_quality_score,
                source_id="evidence_module",
                evidence_type="verification",
            )
            result.findings.append(finding)
            
        except Exception as e:
            result.status = ModuleStatus.FAILED
            result.warnings.append(self.create_warning(str(e), "high"))
        
        return result
    
    def _verify_claim(self, claim: Dict, sources: List[Dict]) -> bool:
        """Check if claim is verified by sources."""
        source_id = claim.get("source_id")
        if not source_id:
            return False
        
        # Check if source exists and is verified
        for source in sources:
            if source.get("id") == source_id:
                return source.get("verified", False)
        
        return False
    
    def _find_contradictions(self, claims: List[Dict]) -> List[str]:
        """Find contradictory claims."""
        # Simplified: just report count
        if len(claims) < 2:
            return []
        
        return [f"Note: {len(claims)} distinct verified claims may have subtle contradictions"]
    
    def _calculate_quality_score(
        self,
        verified: List[Dict],
        unverified: List[Dict],
    ) -> float:
        """Calculate overall evidence quality score."""
        total = len(verified) + len(unverified)
        if total == 0:
            return 0.0
        
        return len(verified) / total
```

---

### 2.4 Complete LLM Integrations

**File:** `aquila_r/core/llm.py`

**Implement missing providers:**

```python
async def _generate_anthropic(
    self,
    prompt: str,
    system_prompt: Optional[str],
    json_output: bool,
    temperature: float,
) -> str:
    """Generate using Anthropic (Claude) API."""
    import httpx
    
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": self.api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    
    messages = [{"role": "user", "content": prompt}]
    if system_prompt:
        messages.insert(0, {"role": "assistant", "content": system_prompt})
    
    payload = {
        "model": self.config.model or "claude-3-sonnet-20240229",
        "max_tokens": self.config.max_tokens,
        "temperature": temperature,
        "messages": messages,
    }
    
    async with httpx.AsyncClient(timeout=self.timeout) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        return data["content"][0]["text"]


async def _generate_ollama(
    self,
    prompt: str,
    system_prompt: Optional[str],
    json_output: bool,
    temperature: float,
) -> str:
    """Generate using Ollama API."""
    import httpx
    
    url = f"{self.base_url}/generate"
    
    payload = {
        "model": self.config.model or "llama2",
        "prompt": prompt,
        "system": system_prompt or "",
        "temperature": temperature,
        "stream": False,
    }
    
    async with httpx.AsyncClient(timeout=self.timeout) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        return data.get("response", "")
```

---

## Phase 3: Testing & Integration (Weeks 4-5)

### Goal
Achieve 70%+ test coverage and complete integration testing

### 3.1 Add Integration Tests

**File:** `tests/test_integration.py`

```python
"""
Integration tests for Aquila-R workflow.

Tests the full analyze() workflow end-to-end.
"""

import pytest
import asyncio
from aquila_r import AquilaR
from aquila_r.core.config import MethodologyParadigm


@pytest.mark.asyncio
async def test_full_analysis_workflow(test_config, mock_llm_client):
    """Test complete analysis workflow."""
    agent = AquilaR(test_config)
    agent.llm = mock_llm_client
    
    query = "What are the main theories of state formation?"
    
    result = await agent.analyze(
        query=query,
        modules=["literature", "critical"],
        methodology=MethodologyParadigm.POSITIVIST,
    )
    
    assert result.research_question == query
    assert result.methodology == "positivist"
    assert len(result.evidence) > 0
    assert 0 <= result.confidence <= 1


@pytest.mark.asyncio
async def test_error_recovery_on_module_failure(test_config):
    """Test that analysis continues if one module fails."""
    agent = AquilaR(test_config)
    
    # Mock one module to fail
    # Should still return results from others
    # ...


@pytest.mark.asyncio
async def test_bilingual_analysis(test_config):
    """Test bilingual query and output."""
    agent = AquilaR(test_config)
    
    ar_query = "ما هي نظريات تشكل الدولة؟"
    
    result = await agent.analyze(ar_query)
    
    assert result.language == "ar"
```

---

### 3.2 Add Module Tests

**File:** `tests/test_modules.py`

```python
"""
Tests for research modules.
"""

import pytest
from aquila_r.modules.synthesis import SynthesisModule
from aquila_r.modules.evidence import EvidenceModule


def test_synthesis_module_identify_themes():
    """Test theme identification in synthesis module."""
    module = SynthesisModule()
    
    findings = [
        {"content": "Theme1 important discovery", "confidence": 0.8},
        {"content": "Theme1 related finding", "confidence": 0.7},
        {"content": "Theme2 separate concept", "confidence": 0.85},
    ]
    
    themes = module._identify_themes(findings)
    
    assert len(themes) >= 1
    assert any(t["findings_count"] >= 2 for t in themes)


def test_evidence_module_verification():
    """Test evidence verification logic."""
    module = EvidenceModule()
    
    claim = {"content": "State forms through consent", "source_id": "source1"}
    sources = [{"id": "source1", "verified": True}]
    
    verified = module._verify_claim(claim, sources)
    
    assert verified
```

---

## Phase 4: Polish & Deploy (Week 5-6)

### Goal
Documentation, security, and deployment readiness

### 4.1 Add Deployment Documentation

**Create file:** `DEPLOYMENT.md`

Document:
- Prerequisites (Python 3.10+, API keys)
- Installation steps
- Configuration guide
- Running tests
- Docker setup (optional)
- Monitoring
- Troubleshooting

---

### 4.2 Security Hardening

Implement:
- Input validation layer
- API key redaction in logs
- Prompt injection detection
- Rate limiting
- Error message sanitization

---

## Success Criteria

### Before Release

- [ ] All modules >80% implemented
- [ ] >70% test coverage on critical paths
- [ ] Zero critical exceptions in test runs
- [ ] All async methods properly awaited
- [ ] Configuration validation working
- [ ] Error handling comprehensive
- [ ] Security review passed
- [ ] Documentation complete

### Metrics

**Current State:**
- Implementation: 55%
- Test Coverage: 28%
- Error Handling: 40%
- Overall Score: 59/100

**Target State:**
- Implementation: 95%
- Test Coverage: 75%
- Error Handling: 90%
- Overall Score: 85/100

---

## Timeline Summary

```
Week 1   | Foundation & Exception Handling
Week 2   | Testing Infrastructure & Async Foundations
Week 3   | Core Module Implementations (Synthesis, Evidence)
Week 4   | Module Dependencies & Orchestration Complete
Week 5   | Integration Tests & Security Hardening
Week 6   | Documentation & Release Preparation
         |
Total: 6 weeks to Production-Ready (85+/100 score)
```

---

This roadmap breaks down the critical work into specific, implementable steps. Each phase builds on the previous one, with clear success criteria and timeline.

