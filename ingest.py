"""Ingestion utilities for legal documents: download, normalize, and index."""

from typing import List, Dict
from models import LegalDocument, DocumentType
from document_processor import LegalDocumentProcessor
from vector_store import LegalVectorStore
from config import get_settings
import requests
import re
import uuid
import io
from bs4 import BeautifulSoup
from pypdf import PdfReader


# Simple source registry with working URLs (updated 2025)
SOURCES = {
    "bare_acts": [
        {
            "title": "Sale of Goods Act, 1930",
            "url": "https://www.indiacode.nic.in/bitstream/123456789/2390/1/193003.pdf",
            "year": 1930,
            "act_number": 3,
            "citation": "Act 3 of 1930"
        },
        {
            "title": "Specific Relief Act, 1963",
            "url": "https://www.indiacode.nic.in/bitstream/123456789/1583/7/A1963-47.pdf",
            "year": 1963,
            "act_number": 47,
            "citation": "Act 47 of 1963"
        },
        {
            "title": "Consumer Protection Act, 2019",
            "url": "https://thc.nic.in/Central%20Governmental%20Acts/Consumer%20Protection%20Act,%202019.pdf",
            "year": 2019,
            "act_number": 35,
            "citation": "Act 35 of 2019"
        },
        {
            "title": "Information Technology (Intermediary Guidelines and Digital Media Ethics Code) Rules, 2021",
            "url": "https://www.meity.gov.in/static/uploads/2024/02/Information-Technology-Intermediary-Guidelines-and-Digital-Media-Ethics-Code-Rules-2021-updated-06.04.2023-.pdf",
            "year": 2021,
            "act_number": 21,
            "citation": "IT Rules 2021"
        },
        {
            "title": "Digital Personal Data Protection Act, 2023",
            "url": "https://www.meity.gov.in/static/uploads/2024/06/2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf",
            "year": 2023,
            "act_number": 22,
            "citation": "Act 22 of 2023"
        },
        {
            "title": "Motor Vehicles Act, 1988",
            "url": "https://www.indiacode.nic.in/bitstream/123456789/9460/1/a1988-59.pdf",
            "year": 1988,
            "act_number": 59,
            "citation": "Act 59 of 1988"
        }
    ],
    "regulations": [
        {
            "title": "Consumer Protection (E-Commerce) Rules, 2020",
            "url": "https://wbconsumers.gov.in/writereaddata/ACT%20&%20RULES/Relevant%20Act%20&%20Rules/Sales%20of%20Goods%20Act,%201930.pdf",
            "year": 2020,
            "citation": "GSR 462(E)"
        },
        {
            "title": "Information Technology (Intermediary Guidelines) Rules, 2021",
            "url": "https://www.meity.gov.in/static/uploads/2024/02/Information-Technology-Intermediary-Guidelines-and-Digital-Media-Ethics-Code-Rules-2021-updated-06.04.2023-.pdf",
            "year": 2021,
            "citation": "GSR 139(E)"
        },
        {
            "title": "Digital Personal Data Protection Rules, 2023",
            "url": "https://www.meity.gov.in/static/uploads/2024/06/2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf",
            "year": 2023,
            "citation": "DPDP Rules 2023"
        }
    ],
    "case_laws": [
        # Using Indian Kanoon for case laws (more reliable than government sites)
        {
            "title": "Satyabrata Ghose vs Mugneeram Bangur & Co.",
            "url": "https://indiankanoon.org/doc/1214064/",
            "year": 1954,
            "court": "Supreme Court of India",
            "citation": "AIR 1954 SC 44"
        },
        {
            "title": "Section 56 - Indian Contract Act, 1872",
            "url": "https://indiankanoon.org/doc/648614/",
            "year": 1872,
            "court": "Legal Provision",
            "citation": "Section 56, Contract Act"
        },
        {
            "title": "Indian Contract Act, 1872 - Full Text",
            "url": "https://indiankanoon.org/doc/171398/",
            "year": 1872,
            "court": "Legal Provision",
            "citation": "Act 9 of 1872"
        },
        {
            "title": "Consumer Protection Case Law Compilation",
            "url": "https://indiankanoon.org/search/?formInput=consumer%20protection%20act%202019",
            "year": 2019,
            "court": "Various Courts",
            "citation": "Consumer Protection Jurisprudence"
        },
        {
            "title": "E-Commerce and Digital Rights Cases",
            "url": "https://indiankanoon.org/search/?formInput=information%20technology%20act%20intermediary",
            "year": 2021,
            "court": "Various Courts",
            "citation": "IT Act Cases"
        }
    ]
}


def download_text_from_url(url: str) -> str:
    """Download text from a URL and extract readable text (PDF and HTML supported)."""
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    content_type = resp.headers.get("Content-Type", "") or ""

    # PDF handling with PyPDF
    if "pdf" in content_type.lower() or url.lower().endswith(".pdf"):
        try:
            bio = io.BytesIO(resp.content)
            reader = PdfReader(bio)
            pages_text = []
            for page in reader.pages:
                try:
                    pages_text.append(page.extract_text() or "")
                except Exception:
                    continue
            text = "\n".join(pages_text)
            if text.strip():
                return text
        except Exception:
            pass
        # Fallback to best-effort bytes decode
        try:
            return resp.content.decode("utf-8", errors="ignore")
        except Exception:
            return resp.text

    # HTML handling
    if "html" in content_type.lower():
        soup = BeautifulSoup(resp.text, "lxml")
        # Remove script/style
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = soup.get_text(separator="\n")
        return text

    # Default: return text
    return resp.text


def sanitize_text(text: str) -> str:
    """Basic cleanup of legal text: remove extra whitespace, headers/footers patterns."""
    text = re.sub(r"\r", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def build_legal_document(entry: Dict, doc_type: DocumentType) -> LegalDocument:
    doc_id = str(uuid.uuid4())
    content = sanitize_text(download_text_from_url(entry["url"]))
    return LegalDocument(
        id=doc_id,
        title=entry["title"],
        document_type=doc_type,
        content=content,
        year=entry.get("year"),
        court=entry.get("court"),
        act_number=entry.get("act_number"),
        citation=entry.get("citation"),
        source_url=entry.get("url")
    )


def ingest_all(vector_store: LegalVectorStore, chunk_size: int = None, chunk_overlap: int = None) -> int:
    """Ingest all sources into the vector store. Returns number of chunks added."""
    settings = get_settings()
    processor = LegalDocumentProcessor(
        chunk_size=chunk_size or settings.chunk_size,
        chunk_overlap=chunk_overlap or settings.chunk_overlap
    )
    
    total_chunks = 0
    
    # Bare Acts
    for entry in SOURCES["bare_acts"]:
        try:
            doc = build_legal_document(entry, DocumentType.BARE_ACT)
            chunks = processor.process_document(doc)
            vector_store.add_documents(chunks)
            total_chunks += len(chunks)
        except Exception as e:
            print(f"[ingest] Skipping bare act '{entry.get('title')}' due to error: {e}")
    
    # Regulations
    for entry in SOURCES["regulations"]:
        try:
            doc = build_legal_document(entry, DocumentType.REGULATION)
            chunks = processor.process_document(doc)
            vector_store.add_documents(chunks)
            total_chunks += len(chunks)
        except Exception as e:
            print(f"[ingest] Skipping regulation '{entry.get('title')}' due to error: {e}")
    
    # Case laws
    for entry in SOURCES["case_laws"]:
        try:
            doc = build_legal_document(entry, DocumentType.CASE_LAW)
            chunks = processor.process_document(doc)
            vector_store.add_documents(chunks)
            total_chunks += len(chunks)
        except Exception as e:
            print(f"[ingest] Skipping case law '{entry.get('title')}' due to error: {e}")
    
    return total_chunks


if __name__ == "__main__":
    settings = get_settings()
    store = LegalVectorStore(settings.chroma_persist_dir)
    n = ingest_all(store)
    print(f"Ingested {n} chunks into the vector store.")
