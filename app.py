"""CLI and API entrypoint for the Legal RAG multi-agent chat system."""

import os
from typing import Optional
from config import get_settings
from vector_store import LegalVectorStore
from agents import LegalMultiAgentSystem
from models import ConversationHistory
from ingest import ingest_all
from rich import print


def ensure_env():
    if not os.path.exists('.env'):
        print('[yellow]No .env found. Copying from .env.example...[/yellow]')
        if os.path.exists('.env.example'):
            with open('.env.example', 'r', encoding='utf-8') as fsrc, open('.env', 'w', encoding='utf-8') as fdst:
                fdst.write(fsrc.read())
            print('[green].env created from template. Please update your API key.[/green]')
        else:
            print('[red].env.example missing. Please create .env manually.[/red]')


def bootstrap(vector_store: Optional[LegalVectorStore] = None) -> LegalMultiAgentSystem:
    settings = get_settings()
    store = vector_store or LegalVectorStore(settings.chroma_persist_dir)
    
    # If DB is empty, trigger ingestion
    stats = store.get_collection_stats()
    total = sum(stats.values())
    if total == 0:
        print('[yellow]Vector DB empty. Ingesting sources (this may take a few minutes)...[/yellow]')
        try:
            n = ingest_all(store)
            print(f'[green]Ingested {n} chunks.[/green]')
        except Exception as e:
            print(f'[red]Ingestion failed: {e}[/red]')
            raise
    else:
        print(f'[green]Vector DB has {total} chunks across collections: {stats}[/green]')
    
    system = LegalMultiAgentSystem(store)
    return system


def run_cli():
    ensure_env()
    settings = get_settings()
    system = bootstrap()
    
    history = ConversationHistory(session_id="local-cli")
    print('[cyan]Legal RAG Assistant ready. Type your question, or /exit to quit.[/cyan]')
    while True:
        try:
            q = input('\nYou: ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\n[cyan]Goodbye![/cyan]')
            break
        if not q:
            continue
        if q.lower() in {"/exit", "exit", "quit", "/quit"}:
            print('[cyan]Goodbye![/cyan]')
            break
        
        # Process query
        out = system.process_query(q, history)
        answer = out["response"]
        citations = out["citations"]
        
        # Add to history
        history.add_message("user", q)
        history.add_message("assistant", answer)
        
        # Print answer
        print(f"\n[bold]Assistant:[/bold] {answer}\n")
        
        # Print citations
        if citations:
            print("[bold]Citations:[/bold]")
            for idx, c in enumerate(citations, 1):
                sec = f" - {c.section_reference}" if c.section_reference else ""
                cite = f" ({c.citation_text})" if c.citation_text else ""
                print(f"  {idx}. {c.document_title}{cite}{sec}")


if __name__ == "__main__":
    run_cli()
