"""
Configuration management for Aquila-R.

Handles LLM, memory, tools, output, and research settings.
"""

import os
from enum import Enum
from typing import Optional, List
from pathlib import Path
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

load_dotenv()


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    LOCAL = "local"
    OLLAMA = "ollama"


class MethodologyParadigm(str, Enum):
    """Research methodology paradigms."""
    POSITIVIST = "positivist"
    INTERPRETIVIST = "interpretivist"
    CRITICAL = "critical"
    PRAGMATIST = "pragmatist"
    MIXED = "mixed"
    AUTO = "auto"


class OutputLanguage(str, Enum):
    """Supported output languages."""
    ENGLISH = "en"
    ARABIC = "ar"
    AUTO = "auto"
    BILINGUAL = "bilingual"


class LLMConfig(BaseModel):
    """LLM provider configuration."""
    provider: LLMProvider = Field(default=LLMProvider.OPENAI)
    model: str = Field(default="gpt-4-turbo-preview")
    api_key: Optional[str] = Field(default=None)
    api_base: Optional[str] = Field(default=None)
    temperature: float = Field(default=0.3, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, ge=1, le=128000)
    timeout: int = Field(default=120, ge=10, le=600)
    
    def get_api_key(self) -> Optional[str]:
        if self.api_key:
            return self.api_key
        env_keys = {
            LLMProvider.OPENAI: "OPENAI_API_KEY",
            LLMProvider.ANTHROPIC: "ANTHROPIC_API_KEY",
            LLMProvider.GOOGLE: "GOOGLE_API_KEY",
        }
        env_var = env_keys.get(self.provider)
        return os.getenv(env_var) if env_var else None


class MemoryConfig(BaseModel):
    """Memory and persistence configuration."""
    enabled: bool = Field(default=True)
    project_memory: bool = Field(default=True)
    session_memory: bool = Field(default=True)
    max_context_items: int = Field(default=100, ge=10, le=1000)
    persistence_path: Optional[Path] = Field(default=None)
    
    @field_validator("persistence_path", mode="before")
    @classmethod
    def validate_path(cls, v):
        return Path(v) if v is not None else None


class ToolConfig(BaseModel):
    """Tool integration configuration."""
    enable_retrieval: bool = Field(default=True)
    enable_parsing: bool = Field(default=True)
    enable_search: bool = Field(default=True)
    max_sources: int = Field(default=50, ge=1, le=200)
    source_verification: bool = Field(default=True)
    pdf_parsing: bool = Field(default=True)
    arxiv_enabled: bool = Field(default=True)
    scholarly_enabled: bool = Field(default=True)


class OutputConfig(BaseModel):
    """Output formatting configuration."""
    default_language: OutputLanguage = Field(default=OutputLanguage.AUTO)
    structured_output: bool = Field(default=True)
    include_methodology: bool = Field(default=True)
    include_limitations: bool = Field(default=True)
    include_next_steps: bool = Field(default=True)
    citation_style: str = Field(default="apa")
    max_output_length: int = Field(default=8000, ge=500, le=50000)


class ResearchConfig(BaseModel):
    """Research behavior configuration."""
    default_methodology: MethodologyParadigm = Field(default=MethodologyParadigm.AUTO)
    critical_mode: bool = Field(default=True)
    preserve_disagreements: bool = Field(default=True)
    flag_weak_evidence: bool = Field(default=True)
    assumption_checking: bool = Field(default=True)
    uncertainty_marking: bool = Field(default=True)
    min_confidence_threshold: float = Field(default=0.6, ge=0.0, le=1.0)


class AquilaConfig(BaseModel):
    """Master configuration for Aquila-R."""
    llm: LLMConfig = Field(default_factory=LLMConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    tools: ToolConfig = Field(default_factory=ToolConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    research: ResearchConfig = Field(default_factory=ResearchConfig)
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")
    
    @classmethod
    def from_env(cls) -> "AquilaConfig":
        """Create configuration from environment variables."""
        provider_str = os.getenv("AQUILA_LLM_PROVIDER", "openai").lower()
        try:
            provider = LLMProvider(provider_str)
        except ValueError:
            provider = LLMProvider.OPENAI
        
        methodology_str = os.getenv("AQUILA_METHODOLOGY", "auto").lower()
        try:
            methodology = MethodologyParadigm(methodology_str)
        except ValueError:
            methodology = MethodologyParadigm.AUTO
        
        language_str = os.getenv("AQUILA_DEFAULT_LANGUAGE", "auto").lower()
        try:
            language = OutputLanguage(language_str)
        except ValueError:
            language = OutputLanguage.AUTO
        
        return cls(
            llm=LLMConfig(
                provider=provider,
                model=os.getenv("AQUILA_MODEL", "gpt-4-turbo-preview"),
                temperature=float(os.getenv("AQUILA_TEMPERATURE", "0.3")),
            ),
            memory=MemoryConfig(
                enabled=os.getenv("AQUILA_MEMORY_ENABLED", "true").lower() == "true",
            ),
            tools=ToolConfig(
                max_sources=int(os.getenv("AQUILA_MAX_SOURCES", "50")),
            ),
            output=OutputConfig(default_language=language),
            research=ResearchConfig(default_methodology=methodology),
            debug=os.getenv("AQUILA_DEBUG", "false").lower() == "true",
            log_level=os.getenv("AQUILA_LOG_LEVEL", "INFO"),
        )
    
    def validate_for_operation(self) -> List[str]:
        """Validate configuration, returning list of issues."""
        issues = []
        if self.llm.provider != LLMProvider.LOCAL:
            if not self.llm.get_api_key():
                issues.append(
                    f"No API key for {self.llm.provider.value}. "
                    f"Set {self.llm.provider.value.upper()}_API_KEY."
                )
        return issues


default_config = AquilaConfig.from_env()
