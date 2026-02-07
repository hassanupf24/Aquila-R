"""
Test suite for Aquila-R core components.

Run with: pytest tests/ -v
"""

import pytest
from datetime import datetime

from aquila_r import AquilaR, AquilaConfig
from aquila_r.core.identity import (
    AgentIdentity,
    AgentRole,
    ProhibitedBehavior,
    IdentityGuard,
)
from aquila_r.core.memory import (
    ResearchMemory,
    MemoryItem,
    MemoryItemType,
    ProjectContext,
)
from aquila_r.core.config import (
    LLMProvider,
    MethodologyParadigm,
    OutputLanguage,
)


class TestAgentIdentity:
    """Tests for agent identity."""
    
    def test_identity_creation(self):
        """Test identity is created with defaults."""
        identity = AgentIdentity()
        
        assert identity.name == "Aquila-R"
        assert identity.version == "1.0.0"
        assert len(identity.active_roles) > 0
        assert len(identity.prohibited_behaviors) > 0
    
    def test_all_roles_present(self):
        """Test all required roles are present."""
        identity = AgentIdentity()
        
        required_roles = {
            AgentRole.RESEARCH_PARTNER,
            AgentRole.CRITICAL_ANALYST,
            AgentRole.METHOD_ADVISOR,
        }
        
        assert required_roles.issubset(identity.active_roles)
    
    def test_all_prohibitions_present(self):
        """Test all prohibited behaviors are defined."""
        identity = AgentIdentity()
        
        assert ProhibitedBehavior.CASUAL_CHATBOT in identity.prohibited_behaviors
        assert ProhibitedBehavior.CITATION_FABRICATION in identity.prohibited_behaviors
        assert ProhibitedBehavior.FACT_FABRICATION in identity.prohibited_behaviors
    
    def test_system_prompt_english(self):
        """Test English system prompt generation."""
        identity = AgentIdentity()
        prompt = identity.get_system_prompt("en")
        
        assert "Aquila-R" in prompt
        assert "research" in prompt.lower()
        assert "NEVER" in prompt
    
    def test_system_prompt_arabic(self):
        """Test Arabic system prompt generation."""
        identity = AgentIdentity()
        prompt = identity.get_system_prompt("ar")
        
        assert "Aquila-R" in prompt
        assert "بحثي" in prompt or "بحث" in prompt
    
    def test_response_validation(self):
        """Test response validation."""
        identity = AgentIdentity()
        
        # Good response
        good_response = "The evidence suggests a potential relationship."
        assert len(identity.validate_response(good_response)) == 0
        
        # Problematic response
        bad_response = "This clearly proves the hypothesis."
        warnings = identity.validate_response(bad_response)
        assert len(warnings) > 0


class TestIdentityGuard:
    """Tests for identity guard."""
    
    def test_guard_creation(self):
        """Test guard is created correctly."""
        identity = AgentIdentity()
        guard = IdentityGuard(identity)
        
        assert guard.identity == identity
        assert len(guard.violation_history) == 0
    
    def test_casual_behavior_detection(self):
        """Test detection of casual chatbot behavior."""
        identity = AgentIdentity()
        guard = IdentityGuard(identity)
        
        is_permitted, message = guard.check_behavior("response", "lol that's funny")
        assert not is_permitted
        assert "casual_chatbot" in message.lower()


class TestResearchMemory:
    """Tests for research memory."""
    
    def test_memory_creation(self):
        """Test memory is created correctly."""
        memory = ResearchMemory()
        
        assert len(memory.session_items) == 0
        assert len(memory.projects) == 0
    
    def test_add_item(self):
        """Test adding items to memory."""
        memory = ResearchMemory()
        
        item = MemoryItem.create(
            type=MemoryItemType.FINDING,
            content="Test finding",
        )
        memory.add_item(item)
        
        assert len(memory.session_items) == 1
    
    def test_add_source(self):
        """Test adding sources."""
        memory = ResearchMemory()
        
        source = memory.add_source(
            title="Test Paper",
            authors=["Author One", "Author Two"],
            year=2023,
        )
        
        assert source.title == "Test Paper"
        assert len(source.authors) == 2
        assert source.year == 2023
    
    def test_record_finding(self):
        """Test recording findings."""
        memory = ResearchMemory()
        
        finding = memory.record_finding(
            content="Important finding",
            confidence=0.8,
        )
        
        assert finding.content == "Important finding"
        assert finding.type == MemoryItemType.FINDING
    
    def test_project_creation(self):
        """Test project creation."""
        memory = ResearchMemory()
        
        project = memory.create_project(
            name="Test Project",
            description="A test project",
        )
        
        assert project.name == "Test Project"
        assert memory.active_project_id == project.project_id
    
    def test_session_summary(self):
        """Test session summary."""
        memory = ResearchMemory()
        memory.record_finding("Finding 1", confidence=0.8)
        memory.record_finding("Finding 2", confidence=0.7)
        memory.record_assumption("Assumption 1")
        
        summary = memory.get_session_summary()
        
        assert summary["total_items"] == 3
        assert summary["items_by_type"]["finding"] == 2
        assert summary["items_by_type"]["assumption"] == 1
    
    def test_memory_export_import(self):
        """Test memory export and import."""
        memory = ResearchMemory()
        memory.record_finding("Test finding", confidence=0.9)
        memory.create_project("Test Project")
        
        # Export
        json_str = memory.export_to_json()
        
        # Import
        imported = ResearchMemory.from_json(json_str)
        
        assert len(imported.session_items) == 1
        assert len(imported.projects) == 1


class TestAquilaRAgent:
    """Tests for main agent."""
    
    def test_agent_creation(self):
        """Test agent is created correctly."""
        agent = AquilaR()
        
        assert agent.identity.name == "Aquila-R"
        assert agent.memory is not None
    
    def test_agent_with_config(self):
        """Test agent with custom config."""
        config = AquilaConfig(
            debug=True,
            log_level="DEBUG",
        )
        agent = AquilaR(config=config)
        
        assert agent.config.debug
        assert agent.config.log_level == "DEBUG"
    
    def test_language_detection(self):
        """Test language detection."""
        agent = AquilaR()
        
        assert agent._detect_language("This is English text") == "en"
        assert agent._detect_language("هذا نص عربي") == "ar"
    
    def test_analyze(self):
        """Test analysis execution."""
        agent = AquilaR()
        
        result = agent.analyze(
            query="What are the key debates?",
            modules=["literature", "synthesis"],
        )
        
        assert result.research_question is not None
        assert result.methodology is not None
        assert result.language in ["en", "ar"]
    
    def test_status(self):
        """Test agent status."""
        agent = AquilaR()
        status = agent.get_status()
        
        assert "agent" in status
        assert "version" in status
        assert "roles" in status
    
    def test_project_creation(self):
        """Test project creation through agent."""
        agent = AquilaR()
        
        project_id = agent.create_project(
            name="Research Project",
            description="Testing project creation",
        )
        
        assert project_id is not None
        
        summary = agent.get_project_summary()
        assert summary["name"] == "Research Project"


class TestConfig:
    """Tests for configuration."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = AquilaConfig()
        
        assert config.llm.provider == LLMProvider.OPENAI
        assert config.memory.enabled
        assert config.research.critical_mode
    
    def test_config_from_env(self):
        """Test configuration from environment."""
        config = AquilaConfig.from_env()
        
        # Should not raise
        assert config is not None
    
    def test_config_validation(self):
        """Test configuration validation."""
        config = AquilaConfig(
            llm={"provider": "local"},
        )
        
        issues = config.validate_for_operation()
        # Local provider shouldn't require API key
        assert len([i for i in issues if "API key" in i]) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
