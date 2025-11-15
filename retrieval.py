"""Advanced RAG retrieval with reranking and contextual compression."""

from typing import List, Optional, Dict, Any
from models import RetrievalResult, Citation, DocumentType
from vector_store import LegalVectorStore
from config import get_settings
import re


class AdvancedRetriever:
    """Advanced retrieval system with reranking and compression."""
    
    def __init__(self, vector_store: LegalVectorStore):
        self.vector_store = vector_store
        self.settings = get_settings()
        
        # Initialize reranker lazily to avoid heavy deps if unavailable
        self.reranker = None
        if self.settings.use_reranking:
            try:
                from sentence_transformers import CrossEncoder  # local import
                self.reranker = CrossEncoder(self.settings.reranker_model)
            except Exception:
                # Fallback: proceed without reranker
                self.reranker = None
    
    def retrieve(
        self,
        query: str,
        k: int = None,
        document_types: Optional[List[DocumentType]] = None,
        use_reranking: bool = True
    ) -> List[RetrievalResult]:
        """Retrieve relevant documents with optional reranking."""
        
        k = k or self.settings.top_k_retrieval
        
        # Initial retrieval (retrieve more for reranking)
        initial_k = k * 3 if use_reranking and self.reranker else k
        
        results = self.vector_store.similarity_search(
            query=query,
            k=initial_k,
            document_types=document_types
        )
        
        # Rerank if enabled
        if use_reranking and self.reranker and results:
            results = self._rerank_results(query, results)
        
        # Return top k
        return results[:k]
    
    def _rerank_results(
        self,
        query: str,
        results: List[RetrievalResult]
    ) -> List[RetrievalResult]:
        """Rerank results using cross-encoder."""
        
        if not results:
            return results
        
        # Prepare pairs for reranking
        pairs = [(query, result.chunk.content) for result in results]
        
        # Get reranking scores
        rerank_scores = self.reranker.predict(pairs)
        
        # Update results with reranked scores
        for result, score in zip(results, rerank_scores):
            result.reranked_score = float(score)
        
        # Sort by reranked score
        results.sort(key=lambda x: x.reranked_score or x.score, reverse=True)
        
        return results
    
    def retrieve_with_compression(
        self,
        query: str,
        k: int = None,
        max_tokens: int = 2000
    ) -> List[RetrievalResult]:
        """Retrieve and compress context to fit token budget."""
        
        results = self.retrieve(query, k=k or self.settings.top_k_retrieval)
        
        # Simple compression: truncate to token budget
        # In production, use more sophisticated compression
        compressed_results = []
        total_tokens = 0
        
        for result in results:
            # Rough token estimation (1 token ≈ 4 characters)
            chunk_tokens = len(result.chunk.content) // 4
            
            if total_tokens + chunk_tokens <= max_tokens:
                compressed_results.append(result)
                total_tokens += chunk_tokens
            else:
                break
        
        return compressed_results
    
    def create_citations(self, results: List[RetrievalResult]) -> List[Citation]:
        """Create citation objects from retrieval results."""
        
        citations = []
        seen_docs = set()
        
        for result in results:
            chunk = result.chunk
            doc_id = chunk.document_id
            
            # Avoid duplicate citations for the same document
            if doc_id in seen_docs:
                continue
            
            seen_docs.add(doc_id)
            
            # Create excerpt (first 200 characters)
            excerpt = chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content
            
            citation = Citation(
                document_id=doc_id,
                document_title=chunk.document_title,
                document_type=chunk.document_type,
                citation_text=chunk.citation,
                section_reference=chunk.section_reference,
                relevance_score=result.reranked_score or result.score,
                excerpt=excerpt
            )
            
            citations.append(citation)
        
        return citations


class QueryExpander:
    """Expands user queries with legal synonyms and related terms."""
    
    LEGAL_SYNONYMS = {
        "contract": ["agreement", "covenant", "understanding"],
        "breach": ["violation", "infringement", "non-compliance"],
        "damages": ["compensation", "reparation", "remedy"],
        "liability": ["responsibility", "obligation", "accountability"],
        "consumer": ["buyer", "purchaser", "customer"],
        "seller": ["vendor", "merchant", "supplier"],
        "goods": ["products", "merchandise", "items"],
        "services": ["provisions", "offerings"],
    }
    
    @classmethod
    def expand_query(cls, query: str) -> str:
        """Expand query with legal synonyms."""
        
        query_lower = query.lower()
        expanded_terms = []
        
        for term, synonyms in cls.LEGAL_SYNONYMS.items():
            if term in query_lower:
                expanded_terms.extend(synonyms)
        
        if expanded_terms:
            return f"{query} {' '.join(expanded_terms)}"
        
        return query


class ContextualRetriever(AdvancedRetriever):
    """Retriever that uses conversation context for better results."""
    
    def retrieve_with_context(
        self,
        query: str,
        conversation_history: List[str],
        k: int = None
    ) -> List[RetrievalResult]:
        """Retrieve with conversation context."""
        
        # Combine recent conversation for context
        context = " ".join(conversation_history[-3:]) if conversation_history else ""
        
        # Expand query with context
        enhanced_query = f"{context} {query}" if context else query
        
        # Retrieve
        return self.retrieve(enhanced_query, k=k)
    
    def identify_relevant_document_types(self, query: str) -> List[DocumentType]:
        """Identify which document types are most relevant to the query."""
        
        query_lower = query.lower()
        relevant_types = []
        
        # Keywords that suggest different document types
        if any(word in query_lower for word in ["section", "act", "statute", "provision"]):
            relevant_types.append(DocumentType.BARE_ACT)
        
        if any(word in query_lower for word in ["case", "judgement", "ruling", "precedent", "held"]):
            relevant_types.append(DocumentType.CASE_LAW)
            relevant_types.append(DocumentType.JUDGEMENT)
        
        if any(word in query_lower for word in ["rule", "regulation", "guideline"]):
            relevant_types.append(DocumentType.REGULATION)
        
        # Default: search all types
        if not relevant_types:
            relevant_types = list(DocumentType)
        
        return relevant_types
