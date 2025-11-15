# ⚖️ Legal RAG Multi-Agent Assistant

An intelligent **Retrieval-Augmented Generation (RAG)** chat system with **multi-agent architecture** for Indian legal research. Built with **Kimi K2 LLM** (via HuggingFace) and **free local embeddings**.

## 🎯 Project Overview

This system demonstrates advanced AI engineering for legal document analysis, featuring:

### 📚 Document Coverage
- **6 Bare Acts (Statutes)**: Sale of Goods Act, Specific Relief Act, Consumer Protection Act, IT Rules, DPDP Act, Motor Vehicles Act
- **5 Case Laws**: Supreme Court judgements and legal provisions from Indian Contract Act
- **3 Regulations**: E-Commerce Rules, IT Intermediary Guidelines, DPDP Rules

### 🤖 Multi-Agent Architecture
1. **Retrieval Agent** - Searches vector database for relevant legal documents
2. **Analysis Agent** - Analyzes legal context using Kimi K2 LLM
3. **Citation Agent** - Validates and formats legal citations
4. **Response Agent** - Generates final answer with proper attribution

### ✨ Key Features
- ✅ **100% Free**: Uses HuggingFace Kimi K2 + local embeddings (no paid APIs)
- ✅ **Accurate Citations**: Proper source attribution with section references
- ✅ **Contextual Retrieval**: Hybrid search with BM25 + vector similarity
- ✅ **Web Interface**: Beautiful Streamlit UI for easy interaction
- ✅ **16,000+ Chunks**: Comprehensive legal document coverage
- ✅ **Production Ready**: Deployable to Streamlit Cloud, HuggingFace Spaces, or Render

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- HuggingFace account (free) - Get API token from https://huggingface.co/settings/tokens

### Installation

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd RAGassistant

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
# Create a .env file with:
HF_TOKEN=your_huggingface_token_here
OPENAI_API_BASE=dummy
OPENAI_API_KEY=dummy
LLM_MODEL=moonshotai/Kimi-K2-Thinking
EMBEDDING_MODEL=text-embedding-3-small
TEMPERATURE=0.1

# 4. Ingest legal documents (first time only)
python ingest.py
# This will download and index 16,000+ chunks (~2-3 minutes)

# 5. Run the Streamlit web interface
streamlit run streamlit_app.py
# Opens at http://localhost:8501

# Alternative: Run CLI version
python app.py
```

## 💻 Usage

### Web Interface (Recommended)
1. Run `streamlit run streamlit_app.py`
2. Open http://localhost:8501 in your browser
3. Ask legal questions like:
   - "What is a contract under Indian law?"
   - "What are the remedies for breach of contract?"
   - "Explain consumer rights under the Consumer Protection Act"
   - "What is the liability of e-commerce platforms?"

### CLI Interface
```bash
python app.py
# Type your question at the prompt
```

## 🏗️ Architecture

### System Components
```
User Query
    ↓
Streamlit Web Interface
    ↓
LegalMultiAgentSystem (LangGraph)
    ↓
┌─────────────────────────────────────┐
│  1. Retrieval Agent                 │
│     - Vector search (ChromaDB)      │
│     - BM25 keyword search           │
│     - Hybrid ranking                │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  2. Analysis Agent (Kimi K2)        │
│     - Legal context analysis        │
│     - Key information extraction    │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  3. Citation Agent                  │
│     - Source validation             │
│     - Citation formatting           │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  4. Response Agent (Kimi K2)        │
│     - Final answer generation       │
│     - Quality assurance             │
└─────────────────────────────────────┘
    ↓
Response with Citations
```

### File Structure
- **`streamlit_app.py`** - Web interface (main entry point)
- **`app.py`** - CLI interface
- **`ingest.py`** - Document ingestion pipeline
- **`agents.py`** - Multi-agent system (LangGraph workflow)
- **`retrieval.py`** - Advanced retrieval with reranking
- **`vector_store.py`** - ChromaDB vector store management
- **`huggingface_llm.py`** - Custom LangChain wrapper for Kimi K2
- **`document_processor.py`** - Document chunking and processing
- **`models.py`** - Pydantic data models
- **`config.py`** - Configuration management

## 🌐 Deployment

### Deploy to Streamlit Cloud (Recommended - FREE)

1. **Push to GitHub**
```bash
git init
git add .
git commit -m "Legal RAG Assistant with Kimi K2"
git remote add origin <your-github-repo-url>
git push -u origin main
```

2. **Deploy on Streamlit Cloud**
   - Go to https://streamlit.io/cloud
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file: `streamlit_app.py`
   - Add secrets (HF_TOKEN, etc.)
   - Click "Deploy"

3. **Your app will be live at**: `https://<your-app-name>.streamlit.app`

See `README_DEPLOYMENT.md` for detailed deployment instructions including HuggingFace Spaces and Render.com.

## 🔧 Technical Details

### Models Used
- **LLM**: Kimi K2 Thinking (moonshotai/Kimi-K2-Thinking) via HuggingFace
- **Embeddings**: all-MiniLM-L6-v2 (local, free)
- **Vector DB**: ChromaDB (persistent storage)
- **Reranking**: BM25 + vector similarity hybrid

### Performance
- **Document Chunks**: 16,265 indexed chunks
- **Query Time**: ~5-10 seconds per query
- **First Load**: ~30 seconds (loading embedding model)
- **Cost**: $0 (completely free!)

## 📝 Notes
- First run requires document ingestion (~2-3 minutes)
- Vector database is stored in `chroma_db/` folder
- Some PDFs may have extraction issues - handled gracefully
- HuggingFace free tier has rate limits (~1000 requests/day)

## 🚀 Extending the System
- **Add more documents**: Edit `SOURCES` in `ingest.py`
- **Customize prompts**: Modify agent prompts in `agents.py`
- **Change LLM**: Update `LLM_MODEL` in `.env`
- **Add new agents**: Extend the LangGraph workflow

## 📄 License
Educational project for legal research assistance. Not a substitute for professional legal advice.

## 🙏 Acknowledgments
- Built with LangChain, LangGraph, ChromaDB, Streamlit
- Powered by Kimi K2 (Moonshot AI) via HuggingFace
- Legal documents from India Code, Indian Kanoon, and government sources
