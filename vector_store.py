"""Vector store management using ChromaDB for legal document retrieval."""

from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from models import DocumentChunk, DocumentType, RetrievalResult
from config import get_settings
import json


class LegalVectorStore:
    """Manages vector storage and retrieval for legal documents."""
    
    def __init__(self, persist_directory: str = None):
        self.settings = get_settings()
        self.persist_directory = persist_directory or self.settings.chroma_persist_dir

        # Initialize embeddings
        # Use local HuggingFace embeddings for free alternative to OpenAI
        if self.settings.openai_api_base:
            # Using Kimi K2 or other OpenAI-compatible API - use local embeddings
            print("[INFO] Using local HuggingFace embeddings (all-MiniLM-L6-v2)")
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={
                    'device': 'cpu',
                    'trust_remote_code': True
                },
                encode_kwargs={
                    'normalize_embeddings': True,
                    'batch_size': 32
                },
                show_progress=False
            )
        else:
            # Using OpenAI API - use OpenAI embeddings
            print(f"[INFO] Using OpenAI embeddings ({self.settings.embedding_model})")
            self.embeddings = OpenAIEmbeddings(
                model=self.settings.embedding_model,
                openai_api_key=self.settings.openai_api_key
            )
        
        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Create separate collections for different document types
        self.collections = {}
        self._initialize_collections()
    
    def _initialize_collections(self):
        """Initialize separate collections for each document type."""
        collection_names = {
            DocumentType.BARE_ACT: "bare_acts",
            DocumentType.CASE_LAW: "case_laws",
            DocumentType.REGULATION: "regulations",
            DocumentType.JUDGEMENT: "judgements"
        }
        
        for doc_type, collection_name in collection_names.items():
            try:
                self.collections[doc_type] = Chroma(
                    client=self.chroma_client,
                    collection_name=collection_name,
                    embedding_function=self.embeddings
                )
            except Exception as e:
                print(f"Error initializing collection {collection_name}: {e}")
    
    def add_documents(self, chunks: List[DocumentChunk]) -> bool:
        """Add document chunks to the appropriate collection."""
        try:
            # Group chunks by document type
            chunks_by_type = {}
            for chunk in chunks:
                doc_type = chunk.document_type
                if doc_type not in chunks_by_type:
                    chunks_by_type[doc_type] = []
                chunks_by_type[doc_type].append(chunk)
            
            # Add to appropriate collections
            for doc_type, type_chunks in chunks_by_type.items():
                collection = self.collections.get(doc_type)
                if not collection:
                    print(f"Warning: No collection for document type {doc_type}")
                    continue
                
                # Prepare documents for ChromaDB
                texts = [chunk.content for chunk in type_chunks]
                metadatas = [self._chunk_to_metadata(chunk) for chunk in type_chunks]
                ids = [chunk.chunk_id for chunk in type_chunks]
                
                # Add to collection
                collection.add_texts(
                    texts=texts,
                    metadatas=metadatas,
                    ids=ids
                )
            
            return True
        except Exception as e:
            print(f"Error adding documents: {e}")
            return False
    
    def _chunk_to_metadata(self, chunk: DocumentChunk) -> Dict[str, Any]:
        """Convert chunk to metadata dictionary."""
        return {
            "chunk_id": chunk.chunk_id,
            "document_id": chunk.document_id,
            "document_title": chunk.document_title,
            "document_type": chunk.document_type.value,
            "citation": chunk.citation or "",
            "section_reference": chunk.section_reference or "",
            "chunk_index": chunk.chunk_index,
        }
    
    def similarity_search(
        self, 
        query: str, 
        k: int = 5,
        document_types: Optional[List[DocumentType]] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResult]:
        """Perform similarity search across collections."""
        
        if document_types is None:
            document_types = list(self.collections.keys())
        
        all_results = []
        
        for doc_type in document_types:
            collection = self.collections.get(doc_type)
            if not collection:
                continue
            
            try:
                # Perform search
                results = collection.similarity_search_with_relevance_scores(
                    query=query,
                    k=k,
                    filter=filters
                )
                
                # Convert to RetrievalResult
                for doc, score in results:
                    chunk = self._doc_to_chunk(doc)
                    result = RetrievalResult(chunk=chunk, score=score)
                    all_results.append(result)
                    
            except Exception as e:
                print(f"Error searching collection {doc_type}: {e}")
        
        # Sort by score and return top k
        all_results.sort(key=lambda x: x.score, reverse=True)
        return all_results[:k]
    
    def _doc_to_chunk(self, doc) -> DocumentChunk:
        """Convert LangChain document to DocumentChunk."""
        metadata = doc.metadata
        
        return DocumentChunk(
            chunk_id=metadata.get("chunk_id", ""),
            document_id=metadata.get("document_id", ""),
            content=doc.page_content,
            document_title=metadata.get("document_title", ""),
            document_type=DocumentType(metadata.get("document_type", "bare_act")),
            citation=metadata.get("citation"),
            section_reference=metadata.get("section_reference"),
            chunk_index=metadata.get("chunk_index", 0)
        )
    
    def hybrid_search(
        self,
        query: str,
        k: int = 5,
        document_types: Optional[List[DocumentType]] = None,
        alpha: float = 0.5
    ) -> List[RetrievalResult]:
        """
        Perform hybrid search combining semantic and keyword search.
        Alpha controls the balance: 0 = pure keyword, 1 = pure semantic
        """
        # For now, use semantic search
        # In production, you'd combine with BM25 or similar
        return self.similarity_search(query, k, document_types)
    
    def get_collection_stats(self) -> Dict[str, int]:
        """Get statistics about collections."""
        stats = {}
        for doc_type, collection in self.collections.items():
            try:
                # Get collection count
                count = collection._collection.count()
                stats[doc_type.value] = count
            except Exception as e:
                stats[doc_type.value] = 0
        return stats
    
    def clear_collection(self, document_type: DocumentType):
        """Clear a specific collection."""
        try:
            collection = self.collections.get(document_type)
            if collection:
                collection._collection.delete()
            return True
        except Exception as e:
            print(f"Error clearing collection: {e}")
            return False
