"""Data models for legal documents and metadata."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


class DocumentType(str, Enum):
    """Types of legal documents in the system."""
    BARE_ACT = "bare_act"
    CASE_LAW = "case_law"
    REGULATION = "regulation"
    JUDGEMENT = "judgement"


class LegalDocument(BaseModel):
    """Represents a legal document with metadata."""
    
    id: str
    title: str
    document_type: DocumentType
    content: str
    
    # Metadata
    year: Optional[int] = None
    jurisdiction: Optional[str] = None
    court: Optional[str] = None
    citation: Optional[str] = None
    act_number: Optional[int] = None
    
    # Structural metadata
    sections: Optional[List[str]] = Field(default_factory=list)
    articles: Optional[List[str]] = Field(default_factory=list)
    
    # Source information
    source_url: Optional[str] = None
    date_retrieved: datetime = Field(default_factory=datetime.now)
    
    # Additional metadata
    keywords: List[str] = Field(default_factory=list)
    summary: Optional[str] = None


class DocumentChunk(BaseModel):
    """Represents a chunk of a legal document."""
    
    chunk_id: str
    document_id: str
    content: str
    
    # Metadata from parent document
    document_title: str
    document_type: DocumentType
    citation: Optional[str] = None
    
    # Chunk-specific metadata
    section_reference: Optional[str] = None
    page_number: Optional[int] = None
    chunk_index: int
    
    # Embedding metadata
    embedding_model: Optional[str] = None


class RetrievalResult(BaseModel):
    """Represents a retrieved document chunk with score."""
    
    chunk: DocumentChunk
    score: float
    reranked_score: Optional[float] = None
    
    
class Citation(BaseModel):
    """Represents a citation to a legal document."""
    
    document_id: str
    document_title: str
    document_type: DocumentType
    citation_text: Optional[str] = None
    section_reference: Optional[str] = None
    relevance_score: float
    excerpt: str


class ChatMessage(BaseModel):
    """Represents a chat message in the conversation."""
    
    role: str  # 'user', 'assistant', 'system'
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    citations: List[Citation] = Field(default_factory=list)


class ConversationHistory(BaseModel):
    """Manages conversation history."""
    
    messages: List[ChatMessage] = Field(default_factory=list)
    session_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    
    def add_message(self, role: str, content: str, citations: List[Citation] = None):
        """Add a message to the conversation history."""
        message = ChatMessage(
            role=role,
            content=content,
            citations=citations or []
        )
        self.messages.append(message)
        return message
    
    def get_recent_context(self, max_messages: int = 6) -> List[ChatMessage]:
        """Get recent conversation context."""
        return self.messages[-max_messages:]
