"""FastAPI server for the Legal RAG multi-agent chat system."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from config import get_settings
from vector_store import LegalVectorStore
from agents import LegalMultiAgentSystem
from models import ConversationHistory, Citation
from ingest import ingest_all

app = FastAPI(title="Legal RAG Assistant", version="1.0")

# Bootstrap on startup
settings = get_settings()
store = LegalVectorStore(settings.chroma_persist_dir)
system = None


class ChatRequest(BaseModel):
    session_id: str
    message: str
    history: Optional[List[str]] = None


class ChatResponse(BaseModel):
    response: str
    citations: List[dict]
    metadata: dict
    num_documents: int


@app.on_event("startup")
def startup_event():
    global system
    stats = store.get_collection_stats()
    total = sum(stats.values())
    if total == 0:
        try:
            ingest_all(store)
        except Exception as e:
            # Defer ingestion failure to runtime
            print(f"Ingestion error on startup: {e}")
    system = LegalMultiAgentSystem(store)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if system is None:
        raise HTTPException(status_code=503, detail="System not initialized")

    # Construct history
    history = ConversationHistory(session_id=req.session_id)
    if req.history:
        for i, turn in enumerate(req.history):
            role = "user" if i % 2 == 0 else "assistant"
            history.add_message(role, turn)

    result = system.process_query(req.message, history)

    # Serialize citations
    cites = []
    for c in result["citations"]:
        cites.append({
            "document_id": c.document_id,
            "document_title": c.document_title,
            "document_type": c.document_type.value,
            "citation_text": c.citation_text,
            "section_reference": c.section_reference,
            "relevance_score": c.relevance_score,
            "excerpt": c.excerpt,
        })

    return ChatResponse(
        response=result["response"],
        citations=cites,
        metadata=result["metadata"],
        num_documents=result["num_documents"],
    )
