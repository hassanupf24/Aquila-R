"""
Memory and context management for Aquila-R.

Handles session memory, project-level context, and cumulative
research understanding across interactions.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum
import json
import hashlib


class MemoryItemType(str, Enum):
    """Types of items stored in memory."""
    SOURCE = "source"
    FINDING = "finding"
    ASSUMPTION = "assumption"
    METHODOLOGY = "methodology"
    QUERY = "query"
    SYNTHESIS = "synthesis"
    CRITIQUE = "critique"
    CONTEXT = "context"


class MemoryItem(BaseModel):
    """A single item in research memory."""
    
    id: str = Field(description="Unique identifier")
    type: MemoryItemType = Field(description="Type of memory item")
    content: str = Field(description="Content of the item")
    language: str = Field(default="en", description="Language of content")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    relevance_score: float = Field(default=1.0, ge=0.0, le=1.0)
    source_id: Optional[str] = Field(default=None)
    
    @classmethod
    def create(
        cls,
        type: MemoryItemType,
        content: str,
        language: str = "en",
        metadata: Optional[Dict] = None,
    ) -> "MemoryItem":
        """Create a new memory item with auto-generated ID."""
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:12]
        item_id = f"{type.value}_{content_hash}_{datetime.utcnow().timestamp():.0f}"
        return cls(
            id=item_id,
            type=type,
            content=content,
            language=language,
            metadata=metadata or {},
        )


class SourceReference(BaseModel):
    """Reference to an academic source."""
    
    id: str = Field(description="Unique source identifier")
    title: str = Field(description="Source title")
    authors: List[str] = Field(default_factory=list)
    year: Optional[int] = Field(default=None)
    source_type: str = Field(default="unknown")  # journal, book, report, etc.
    language: str = Field(default="en")
    verified: bool = Field(default=False)
    url: Optional[str] = Field(default=None)
    doi: Optional[str] = Field(default=None)
    abstract: Optional[str] = Field(default=None)
    retrieved_at: datetime = Field(default_factory=datetime.utcnow)
    
    def to_citation(self, style: str = "apa") -> str:
        """Generate citation string in specified style."""
        authors_str = ", ".join(self.authors) if self.authors else "Unknown"
        year_str = str(self.year) if self.year else "n.d."
        
        if style == "apa":
            return f"{authors_str} ({year_str}). {self.title}."
        elif style == "mla":
            return f'{authors_str}. "{self.title}." {year_str}.'
        else:
            return f"{authors_str} ({year_str}). {self.title}."


class ResearchContext(BaseModel):
    """Context for a research inquiry."""
    
    research_question: Optional[str] = Field(default=None)
    methodology: Optional[str] = Field(default=None)
    domain: Optional[str] = Field(default=None)
    assumptions: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=lambda: ["en"])


class ProjectContext(BaseModel):
    """
    Project-level context that persists across sessions.
    
    Maintains cumulative research understanding and
    consistency in analytical standards.
    """
    
    project_id: str = Field(description="Unique project identifier")
    name: str = Field(description="Project name")
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    research_context: ResearchContext = Field(default_factory=ResearchContext)
    sources: Dict[str, SourceReference] = Field(default_factory=dict)
    findings: List[MemoryItem] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    methodology_notes: List[str] = Field(default_factory=list)
    
    def add_source(self, source: SourceReference) -> None:
        """Add a source to the project."""
        self.sources[source.id] = source
        self.updated_at = datetime.utcnow()
    
    def add_finding(self, finding: MemoryItem) -> None:
        """Add a finding to the project."""
        self.findings.append(finding)
        self.updated_at = datetime.utcnow()
    
    def add_assumption(self, assumption: str) -> None:
        """Record an assumption."""
        if assumption not in self.assumptions:
            self.assumptions.append(assumption)
            self.updated_at = datetime.utcnow()
    
    def get_source_count(self) -> Dict[str, int]:
        """Get count of sources by type."""
        counts: Dict[str, int] = {}
        for source in self.sources.values():
            counts[source.source_type] = counts.get(source.source_type, 0) + 1
        return counts


class ResearchMemory:
    """
    Main memory management for Aquila-R.
    
    Handles both session-level and project-level memory,
    supporting cumulative research understanding.
    """
    
    def __init__(
        self,
        max_items: int = 100,
        enable_project_memory: bool = True,
    ):
        """
        Initialize research memory.
        
        Args:
            max_items: Maximum items to retain in session memory
            enable_project_memory: Whether to maintain project context
        """
        self.max_items = max_items
        self.enable_project_memory = enable_project_memory
        
        self.session_items: List[MemoryItem] = []
        self.projects: Dict[str, ProjectContext] = {}
        self.active_project_id: Optional[str] = None
    
    def add_item(self, item: MemoryItem) -> None:
        """Add an item to session memory."""
        self.session_items.append(item)
        
        # Prune if exceeds limit
        if len(self.session_items) > self.max_items:
            # Remove lowest relevance items
            self.session_items.sort(key=lambda x: x.relevance_score, reverse=True)
            self.session_items = self.session_items[:self.max_items]
    
    def add_source(
        self,
        title: str,
        authors: List[str],
        year: Optional[int] = None,
        source_type: str = "unknown",
        language: str = "en",
        verified: bool = False,
        **kwargs,
    ) -> SourceReference:
        """Add a source reference."""
        source_id = hashlib.sha256(
            f"{title}_{authors}_{year}".encode()
        ).hexdigest()[:16]
        
        source = SourceReference(
            id=source_id,
            title=title,
            authors=authors,
            year=year,
            source_type=source_type,
            language=language,
            verified=verified,
            **kwargs,
        )
        
        # Add to active project if exists
        if self.active_project_id and self.enable_project_memory:
            project = self.projects.get(self.active_project_id)
            if project:
                project.add_source(source)
        
        # Add to session memory
        self.add_item(MemoryItem.create(
            type=MemoryItemType.SOURCE,
            content=source.to_citation(),
            language=language,
            metadata={"source_id": source.id},
        ))
        
        return source
    
    def record_finding(
        self,
        content: str,
        language: str = "en",
        source_id: Optional[str] = None,
        confidence: float = 0.8,
    ) -> MemoryItem:
        """Record a research finding."""
        finding = MemoryItem.create(
            type=MemoryItemType.FINDING,
            content=content,
            language=language,
            metadata={
                "source_id": source_id,
                "confidence": confidence,
            },
        )
        finding.relevance_score = confidence
        
        self.add_item(finding)
        
        if self.active_project_id and self.enable_project_memory:
            project = self.projects.get(self.active_project_id)
            if project:
                project.add_finding(finding)
        
        return finding
    
    def record_assumption(self, assumption: str) -> MemoryItem:
        """Record a methodological assumption."""
        item = MemoryItem.create(
            type=MemoryItemType.ASSUMPTION,
            content=assumption,
        )
        self.add_item(item)
        
        if self.active_project_id and self.enable_project_memory:
            project = self.projects.get(self.active_project_id)
            if project:
                project.add_assumption(assumption)
        
        return item
    
    def create_project(
        self,
        name: str,
        description: Optional[str] = None,
    ) -> ProjectContext:
        """Create a new project context."""
        project_id = hashlib.sha256(
            f"{name}_{datetime.utcnow().isoformat()}".encode()
        ).hexdigest()[:16]
        
        project = ProjectContext(
            project_id=project_id,
            name=name,
            description=description,
        )
        
        self.projects[project_id] = project
        self.active_project_id = project_id
        
        return project
    
    def set_active_project(self, project_id: str) -> bool:
        """Set the active project context."""
        if project_id in self.projects:
            self.active_project_id = project_id
            return True
        return False
    
    def get_active_project(self) -> Optional[ProjectContext]:
        """Get the active project context."""
        if self.active_project_id:
            return self.projects.get(self.active_project_id)
        return None
    
    def get_relevant_context(
        self,
        query: str,
        max_items: int = 10,
        item_types: Optional[List[MemoryItemType]] = None,
    ) -> List[MemoryItem]:
        """
        Retrieve relevant context items for a query.
        
        Args:
            query: The query to find relevant context for
            max_items: Maximum items to return
            item_types: Filter by specific item types
            
        Returns:
            List of relevant memory items
        """
        candidates = self.session_items
        
        if item_types:
            candidates = [i for i in candidates if i.type in item_types]
        
        # Sort by relevance (simple recency-based for now)
        candidates.sort(key=lambda x: x.timestamp, reverse=True)
        
        return candidates[:max_items]
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session memory."""
        type_counts: Dict[str, int] = {}
        for item in self.session_items:
            type_counts[item.type.value] = type_counts.get(item.type.value, 0) + 1
        
        return {
            "total_items": len(self.session_items),
            "items_by_type": type_counts,
            "active_project": self.active_project_id,
            "projects_count": len(self.projects),
        }
    
    def clear_session(self) -> None:
        """Clear session memory (preserves project memory)."""
        self.session_items = []
    
    def export_to_json(self) -> str:
        """Export memory state to JSON."""
        data = {
            "session_items": [i.model_dump(mode="json") for i in self.session_items],
            "projects": {
                pid: p.model_dump(mode="json")
                for pid, p in self.projects.items()
            },
            "active_project_id": self.active_project_id,
        }
        return json.dumps(data, default=str, ensure_ascii=False, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str, max_items: int = 100) -> "ResearchMemory":
        """Load memory state from JSON."""
        data = json.loads(json_str)
        
        memory = cls(max_items=max_items)
        
        for item_data in data.get("session_items", []):
            memory.session_items.append(MemoryItem(**item_data))
        
        for pid, project_data in data.get("projects", {}).items():
            memory.projects[pid] = ProjectContext(**project_data)
        
        memory.active_project_id = data.get("active_project_id")
        
        return memory
