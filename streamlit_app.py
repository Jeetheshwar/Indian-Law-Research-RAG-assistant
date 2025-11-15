"""
Indian Law Research Assistant
Professional AI-powered legal research tool with multi-agent architecture
"""

import streamlit as st
import sys
from pathlib import Path
import traceback

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from agents import LegalMultiAgentSystem
from vector_store import LegalVectorStore

# Page configuration
st.set_page_config(
    page_title="Indian Law Research Assistant",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional styling
st.markdown("""<style>
    .main .block-container {
        max-width: 900px;
        padding-top: 2rem;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        border: none;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
    }
</style>""", unsafe_allow_html=True)

# Initialize session state
if 'orchestrator' not in st.session_state:
    with st.spinner("Initializing system..."):
        try:
            st.session_state.vector_store = LegalVectorStore()
            st.session_state.orchestrator = LegalMultiAgentSystem(st.session_state.vector_store)
            st.session_state.initialized = True
            st.session_state.error_message = None
        except Exception as e:
            st.session_state.initialized = False
            st.session_state.orchestrator = None
            st.session_state.error_message = str(e)

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Header
st.title("Indian Law Research Assistant")
st.caption("AI-powered research across statutes, case law, and regulations")

# Status indicator
if st.session_state.get('initialized', False):
    st.success("✓ System Ready")
else:
    st.error("✗ System Error")
    if st.session_state.get('error_message'):
        st.error(f"Initialization failed: {st.session_state.error_message}")
        st.stop()

st.divider()

# Example questions in expander (before input to avoid state issues)
with st.expander("Example Questions"):
    examples = [
        "What constitutes a valid contract under Indian law?",
        "What are the remedies available for breach of contract?",
        "Explain consumer rights under the Consumer Protection Act",
        "What is the liability of e-commerce platforms for defective products?",
        "What are the essential elements of a sale of goods?"
    ]
    for idx, example in enumerate(examples):
        if st.button(example, key=f"example_{idx}", use_container_width=True):
            st.session_state.selected_example = example
            st.rerun()

# Main input area
st.markdown("### Ask a Question")
default_value = st.session_state.get('selected_example', '')
if default_value:
    # Clear the selected example after using it
    st.session_state.selected_example = ''

user_question = st.text_input(
    "Question",
    value=default_value,
    placeholder="e.g., What constitutes a valid contract under Indian law?",
    label_visibility="collapsed",
    key="question_input"
)

# Submit button
submit_clicked = st.button("Search", type="primary", use_container_width=True)

# Process question
if (submit_clicked or user_question) and st.session_state.get('initialized', False):
    if user_question:
        with st.spinner("Analyzing your question..."):
            try:
                result = st.session_state.orchestrator.process_query(user_question)
                st.session_state.chat_history.append({
                    "question": user_question,
                    "result": result
                })
            except Exception as e:
                st.error(f"Error processing question: {str(e)}")
                st.error(f"Details: {traceback.format_exc()}")

# Display results
if st.session_state.chat_history:
    st.markdown("---")

    # Show only the most recent result
    latest = st.session_state.chat_history[-1]
    result = latest['result']

    # Answer
    st.markdown("### Answer")
    st.markdown(result.get('response', 'No response generated'))

    # Citations
    if result.get('citations'):
        st.markdown("### Sources")
        st.caption(f"{len(result['citations'])} document(s) referenced")

        for idx, citation in enumerate(result['citations'], 1):
            # Handle both dict and Citation object
            if isinstance(citation, dict):
                title = citation.get('document_title', 'Unknown')
                cite_text = citation.get('citation_text', 'No citation')
                doc_type = citation.get('document_type', 'Unknown')
                section = citation.get('section_reference', None)
                excerpt = citation.get('excerpt', '')
                score = citation.get('relevance_score', 0)
            else:
                title = citation.document_title
                cite_text = citation.citation_text or 'No citation'
                doc_type = citation.document_type.value if hasattr(citation.document_type, 'value') else str(citation.document_type)
                section = citation.section_reference
                excerpt = citation.excerpt
                score = citation.relevance_score

            # Display citation using native Streamlit components
            with st.container():
                st.markdown(f"**[{idx}] {title}**")
                st.caption(f"{cite_text}")
                if section:
                    st.caption(f"📍 {section}")
                st.caption(f"Relevance: {score:.0%}")
                if excerpt:
                    with st.expander("View excerpt"):
                        st.text(excerpt)

# Sidebar with stats
with st.sidebar:
    st.markdown("### System Information")

    if st.session_state.get('initialized', False):
        try:
            collections = st.session_state.vector_store.chroma_client.list_collections()
            total_chunks = sum([col.count() for col in collections])

            st.metric("Documents Indexed", f"{total_chunks:,}")

            with st.expander("Collection Details"):
                for col in collections:
                    st.caption(f"{col.name}: {col.count():,}")
        except Exception as e:
            st.caption(f"Could not load stats: {str(e)}")

    st.markdown("---")
    st.caption("**Disclaimer:** This tool is for research purposes only and does not constitute legal advice.")


