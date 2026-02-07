"""
Output Formatters for Aquila-R.

Formats research outputs in various formats with
language-specific handling.
"""

from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from datetime import datetime

from aquila_r.output.standards import OutputStandards, OutputSection


class OutputFormatter(ABC):
    """Base class for output formatters."""
    
    @abstractmethod
    def format(
        self,
        sections: Dict[OutputSection, str],
        metadata: Optional[Dict[str, Any]] = None,
        language: str = "en",
    ) -> str:
        """Format the output."""
        pass


class MarkdownFormatter(OutputFormatter):
    """Formats output as Markdown."""
    
    def __init__(self):
        """Initialize the formatter."""
        self.standards = OutputStandards()
    
    def format(
        self,
        sections: Dict[OutputSection, str],
        metadata: Optional[Dict[str, Any]] = None,
        language: str = "en",
    ) -> str:
        """
        Format sections as Markdown.
        
        Args:
            sections: Section content
            metadata: Optional metadata
            language: Output language
            
        Returns:
            Formatted Markdown string
        """
        lines = []
        
        # Title
        if language == "ar":
            lines.append("# تحليل بحثي\n")
        else:
            lines.append("# Research Analysis\n")
        
        # Metadata
        if metadata:
            generated = metadata.get("generated_at", datetime.utcnow())
            if isinstance(generated, datetime):
                generated = generated.strftime("%Y-%m-%d %H:%M UTC")
            lines.append(f"*Generated: {generated}*\n\n")
        
        # Sections
        for section in self.standards.SECTION_ORDER:
            content = sections.get(section)
            if content:
                title = self.standards.get_section_title(section, language)
                lines.append(f"\n## {title}\n\n")
                lines.append(f"{content}\n")
        
        return "".join(lines)
    
    def format_with_confidence(
        self,
        sections: Dict[OutputSection, str],
        confidence: float,
        language: str = "en",
    ) -> str:
        """Format with confidence indicator."""
        output = self.format(sections, language=language)
        
        if language == "ar":
            output += f"\n---\n*درجة الثقة الإجمالية: {confidence:.0%}*\n"
        else:
            output += f"\n---\n*Overall Confidence: {confidence:.0%}*\n"
        
        return output


class HTMLFormatter(OutputFormatter):
    """Formats output as HTML."""
    
    def __init__(self):
        """Initialize the formatter."""
        self.standards = OutputStandards()
    
    def format(
        self,
        sections: Dict[OutputSection, str],
        metadata: Optional[Dict[str, Any]] = None,
        language: str = "en",
    ) -> str:
        """Format as HTML."""
        direction = "rtl" if language == "ar" else "ltr"
        
        lines = [
            f'<!DOCTYPE html>',
            f'<html lang="{language}" dir="{direction}">',
            '<head>',
            '<meta charset="UTF-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
            '<title>Research Analysis</title>',
            '<style>',
            'body { font-family: system-ui, sans-serif; max-width: 800px; margin: 0 auto; padding: 2rem; line-height: 1.6; }',
            'h1 { color: #1a365d; }',
            'h2 { color: #2c5282; border-bottom: 1px solid #e2e8f0; padding-bottom: 0.5rem; }',
            '.confidence { background: #f7fafc; padding: 1rem; border-radius: 0.5rem; }',
            '.warning { background: #fffbeb; border-left: 4px solid #f59e0b; padding: 1rem; }',
            '</style>',
            '</head>',
            '<body>',
        ]
        
        # Title
        title = "تحليل بحثي" if language == "ar" else "Research Analysis"
        lines.append(f'<h1>{title}</h1>')
        
        # Sections
        for section in self.standards.SECTION_ORDER:
            content = sections.get(section)
            if content:
                title = self.standards.get_section_title(section, language)
                lines.append(f'<h2>{title}</h2>')
                lines.append(f'<p>{content}</p>')
        
        lines.extend(['</body>', '</html>'])
        
        return '\n'.join(lines)


def format_research_output(
    sections: Dict[OutputSection, str],
    format_type: str = "markdown",
    language: str = "en",
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Format research output in specified format.
    
    Args:
        sections: Section content
        format_type: Output format ("markdown", "html")
        language: Output language
        metadata: Optional metadata
        
    Returns:
        Formatted output string
    """
    formatters = {
        "markdown": MarkdownFormatter,
        "html": HTMLFormatter,
    }
    
    formatter_class = formatters.get(format_type, MarkdownFormatter)
    formatter = formatter_class()
    
    return formatter.format(sections, metadata, language)
