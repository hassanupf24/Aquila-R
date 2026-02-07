"""
Test suite for Aquila-R output components.
"""

import pytest
from aquila_r.output import (
    OutputStandards,
    OutputSection,
    format_research_output,
    MarkdownFormatter,
)


class TestOutputStandards:
    """Tests for output standards."""
    
    def test_section_titles(self):
        """Test section title retrieval."""
        standards = OutputStandards()
        
        en_title = standards.get_section_title(OutputSection.METHODOLOGY, "en")
        ar_title = standards.get_section_title(OutputSection.METHODOLOGY, "ar")
        
        assert "Methodological" in en_title
        assert "المنهج" in ar_title
    
    def test_required_sections(self):
        """Test retrieving required sections."""
        standards = OutputStandards()
        required = standards.get_required_sections()
        
        assert OutputSection.CONTEXT in required
        assert OutputSection.METHODOLOGY in required
        assert OutputSection.ANALYSIS in required
    
    def test_output_validation(self):
        """Test output validation logic."""
        standards = OutputStandards()
        
        # Valid output
        valid_sections = {
            OutputSection.CONTEXT: "Context " * 10,
            OutputSection.METHODOLOGY: "Methods " * 20,
            OutputSection.EVIDENCE: "Evidence " * 10,
            OutputSection.ANALYSIS: "Analysis " * 40,
            OutputSection.GAPS: "Gaps content",
            OutputSection.SOURCES: "Sources list",
            OutputSection.ASSUMPTIONS: "Assumptions list",
        }
        
        issues = standards.validate_output(valid_sections)
        assert len(issues) == 0
        
        # Invalid output (missing section)
        invalid_sections = {
            OutputSection.CONTEXT: "Context content",
        }
        
        issues = standards.validate_output(invalid_sections)
        assert len(issues) > 0


class TestFormatters:
    """Tests for output formatters."""
    
    def test_markdown_formatter(self):
        """Test markdown formatting."""
        sections = {
            OutputSection.CONTEXT: "This is the context.",
            OutputSection.ANALYSIS: "This is the analysis.",
        }
        
        output = format_research_output(
            sections,
            format_type="markdown",
            language="en",
        )
        
        assert "# Research Analysis" in output
        assert "## Context" in output
        assert "This is the context." in output
    
    def test_arabic_markdown(self):
        """Test Arabic markdown formatting."""
        sections = {
            OutputSection.CONTEXT: "هذا هو السياق.",
        }
        
        output = format_research_output(
            sections,
            format_type="markdown",
            language="ar",
        )
        
        assert "# تحليل بحثي" in output
        assert "السياق" in output
        assert "هذا هو السياق." in output
    
    def test_html_formatter(self):
        """Test HTML formatting."""
        sections = {
            OutputSection.CONTEXT: "Context content.",
        }
        
        output = format_research_output(
            sections,
            format_type="html",
            language="en",
        )
        
        assert "<html" in output
        assert "<h1>Research Analysis</h1>" in output
        assert "<p>Context content.</p>" in output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
