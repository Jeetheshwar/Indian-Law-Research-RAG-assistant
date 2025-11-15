"""Document processing and ingestion pipeline for legal documents."""

import re
from typing import List, Dict, Any, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from models import LegalDocument, DocumentChunk, DocumentType
import hashlib


class LegalDocumentProcessor:
    """Processes legal documents for ingestion into the RAG system."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
        )
    
    def process_document(self, document: LegalDocument) -> List[DocumentChunk]:
        """Process a legal document into chunks with metadata preservation."""
        
        # Extract section references if it's a bare act
        if document.document_type == DocumentType.BARE_ACT:
            sections = self._extract_sections(document.content)
            document.sections = sections
        
        # Create chunks
        chunks = self._create_chunks(document)
        
        return chunks
    
    def _extract_sections(self, content: str) -> List[str]:
        """Extract section numbers from legal text."""
        # Pattern to match section references like "Section 10", "Sec. 15", etc.
        section_pattern = r'(?:Section|Sec\.?|§)\s*(\d+[A-Z]?)'
        sections = re.findall(section_pattern, content, re.IGNORECASE)
        return list(set(sections))
    
    def _create_chunks(self, document: LegalDocument) -> List[DocumentChunk]:
        """Create document chunks with metadata."""
        
        # Split the document
        text_chunks = self.text_splitter.split_text(document.content)
        
        chunks = []
        for idx, chunk_text in enumerate(text_chunks):
            # Extract section reference from chunk if present
            section_ref = self._find_section_reference(chunk_text)
            
            # Generate unique chunk ID
            chunk_id = self._generate_chunk_id(document.id, idx)
            
            chunk = DocumentChunk(
                chunk_id=chunk_id,
                document_id=document.id,
                content=chunk_text,
                document_title=document.title,
                document_type=document.document_type,
                citation=document.citation,
                section_reference=section_ref,
                chunk_index=idx
            )
            chunks.append(chunk)
        
        return chunks
    
    def _find_section_reference(self, text: str) -> Optional[str]:
        """Find the most relevant section reference in a chunk."""
        # Look for section headers
        patterns = [
            r'(?:Section|Sec\.?|§)\s*(\d+[A-Z]?)[:\.\s]',
            r'^(\d+[A-Z]?)\.\s+[A-Z]',  # Numbered headings
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                return f"Section {match.group(1)}"
        
        return None
    
    def _generate_chunk_id(self, document_id: str, chunk_index: int) -> str:
        """Generate a unique chunk ID."""
        content = f"{document_id}_{chunk_index}"
        return hashlib.md5(content.encode()).hexdigest()


class LegalDocumentEnhancer:
    """Enhances legal documents with additional metadata and structure."""
    
    @staticmethod
    def extract_key_provisions(document: LegalDocument) -> List[str]:
        """Extract key provisions from legal documents."""
        provisions = []
        
        # Look for important sections
        important_keywords = [
            "definition", "interpretation", "scope", "application",
            "rights", "duties", "obligations", "penalties", "remedies"
        ]
        
        lines = document.content.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in important_keywords):
                provisions.append(line.strip())
        
        return provisions[:10]  # Return top 10
    
    @staticmethod
    def extract_definitions(content: str) -> Dict[str, str]:
        """Extract definitions from legal text."""
        definitions = {}
        
        # Pattern for definitions like "X means Y"
        pattern = r'"([^"]+)"\s+means\s+([^;\.]+)'
        matches = re.findall(pattern, content, re.IGNORECASE)
        
        for term, definition in matches:
            definitions[term.strip()] = definition.strip()
        
        return definitions
    
    @staticmethod
    def identify_cross_references(content: str) -> List[str]:
        """Identify cross-references to other legal provisions."""
        references = []
        
        # Patterns for cross-references
        patterns = [
            r'as per [Ss]ection (\d+[A-Z]?)',
            r'under [Ss]ection (\d+[A-Z]?)',
            r'in accordance with [Ss]ection (\d+[A-Z]?)',
            r'subject to [Ss]ection (\d+[A-Z]?)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            references.extend([f"Section {m}" for m in matches])
        
        return list(set(references))
