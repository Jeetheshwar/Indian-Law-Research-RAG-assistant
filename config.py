"""Configuration management for the Legal RAG system."""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Groq Configuration
    groq_api_key: Optional[str] = None  # Groq API token

    # OpenAI Configuration (or OpenAI-compatible API like Kimi)
    openai_api_key: Optional[str] = None
    openai_api_base: Optional[str] = None  # For OpenAI-compatible APIs like Kimi

    # HuggingFace Configuration
    hf_token: Optional[str] = None  # HuggingFace API token

    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-4-turbo-preview"
    temperature: float = 0.1

    # Vector Database
    chroma_persist_dir: str = "./data/chroma_db"
    
    # Retrieval Configuration
    max_retrieval_documents: int = 10
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_retrieval: int = 5
    
    # Reranking
    use_reranking: bool = True
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    
    # Multi-agent Configuration
    max_iterations: int = 5
    agent_temperature: float = 0.0
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()
