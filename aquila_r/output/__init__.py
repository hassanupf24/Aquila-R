"""
Output formatting and standards for Aquila-R.

Ensures all outputs follow academic standards and
structured formats.
"""

from aquila_r.output.standards import OutputStandards, OutputSection
from aquila_r.output.formatters import (
    OutputFormatter,
    MarkdownFormatter,
    format_research_output,
)

__all__ = [
    "OutputStandards",
    "OutputSection",
    "OutputFormatter",
    "MarkdownFormatter",
    "format_research_output",
]
