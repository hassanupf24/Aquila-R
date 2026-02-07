"""
Document parsing tools for Aquila-R.

Provides tools for extracting content from various
document formats (PDF, etc.).
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from pathlib import Path
from abc import abstractmethod

from aquila_r.tools.base import BaseTool, ToolResult, ToolStatus


class ParsedSection(BaseModel):
    """A section from a parsed document."""
    
    heading: Optional[str] = None
    content: str
    page_number: Optional[int] = None
    section_type: str = Field(default="body")  # abstract, body, references, etc.


class ParsedDocument(BaseModel):
    """A parsed document."""
    
    title: Optional[str] = None
    authors: List[str] = Field(default_factory=list)
    abstract: Optional[str] = None
    sections: List[ParsedSection] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)
    page_count: Optional[int] = None
    language: str = Field(default="en")
    source_path: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def get_full_text(self) -> str:
        """Get full document text."""
        parts = []
        if self.abstract:
            parts.append(self.abstract)
        for section in self.sections:
            if section.heading:
                parts.append(f"\n{section.heading}\n")
            parts.append(section.content)
        return "\n\n".join(parts)
    
    def get_section_by_type(self, section_type: str) -> List[ParsedSection]:
        """Get sections of a specific type."""
        return [s for s in self.sections if s.section_type == section_type]


class DocumentParser(BaseTool):
    """
    Base class for document parsers.
    
    Parses documents to extract structured content
    for analysis.
    """
    
    name = "document_parser"
    description = "Base document parser"
    supported_formats: List[str] = []
    
    @abstractmethod
    async def parse(self, source: str) -> ParsedDocument:
        """
        Parse a document.
        
        Args:
            source: Path to document or URL
            
        Returns:
            ParsedDocument with extracted content
        """
        pass
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute parsing."""
        source = kwargs.get("source", "")
        
        if not source:
            return self._failure("No source provided")
        
        try:
            document = await self.parse(source)
            return self._success(
                data=document,
                source=source,
                page_count=document.page_count,
            )
        except Exception as e:
            return self._failure(str(e))
    
    def supports_format(self, path: str) -> bool:
        """Check if format is supported."""
        ext = Path(path).suffix.lower().lstrip(".")
        return ext in self.supported_formats


class PDFParser(DocumentParser):
    """Parser for PDF documents."""
    
    name = "pdf_parser"
    description = "Parse PDF documents"
    supported_formats = ["pdf"]
    
    async def parse(self, source: str) -> ParsedDocument:
        """Parse a PDF document."""
        # Placeholder - requires PyPDF2 or pdfplumber
        return ParsedDocument(
            source_path=source,
            metadata={"parser": "pdf_parser", "status": "placeholder"},
        )


class TextParser(DocumentParser):
    """Parser for plain text documents."""
    
    name = "text_parser"
    description = "Parse text documents"
    supported_formats = ["txt", "md", "markdown"]
    
    async def parse(self, source: str) -> ParsedDocument:
        """Parse a text document."""
        try:
            with open(source, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return ParsedDocument(
                source_path=source,
                sections=[ParsedSection(content=content)],
            )
        except Exception as e:
            return ParsedDocument(
                source_path=source,
                metadata={"error": str(e)},
            )
