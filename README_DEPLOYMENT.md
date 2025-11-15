# Legal RAG Assistant - Deployment Guide

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd RAGassistant
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
Create a `.env` file with:
```env
HF_TOKEN=your_huggingface_token_here
OPENAI_API_BASE=dummy
OPENAI_API_KEY=dummy
LLM_MODEL=moonshotai/Kimi-K2-Thinking
EMBEDDING_MODEL=text-embedding-3-small
TEMPERATURE=0.1
```

4. **Ingest documents** (first time only)
```bash
python ingest.py
```

5. **Run the Streamlit app**
```bash
streamlit run streamlit_app.py
```

The app will open at `http://localhost:8501`

---

## 🌐 Deployment to Streamlit Cloud (FREE)

### Prerequisites
- GitHub account
- HuggingFace account with API token

### Steps

1. **Push code to GitHub**
```bash
git init
git add .
git commit -m "Initial commit - Legal RAG Assistant"
git remote add origin <your-github-repo-url>
git push -u origin main
```

2. **Go to Streamlit Cloud**
- Visit: https://streamlit.io/cloud
- Sign in with GitHub
- Click "New app"

3. **Configure deployment**
- **Repository**: Select your GitHub repo
- **Branch**: `main`
- **Main file path**: `streamlit_app.py`

4. **Add secrets** (Click "Advanced settings" → "Secrets")
```toml
HF_TOKEN = "your_huggingface_token_here"
OPENAI_API_BASE = "dummy"
OPENAI_API_KEY = "dummy"
LLM_MODEL = "moonshotai/Kimi-K2-Thinking"
EMBEDDING_MODEL = "text-embedding-3-small"
TEMPERATURE = "0.1"
```

5. **Deploy**
- Click "Deploy!"
- Wait 2-3 minutes for deployment
- Your app will be live at: `https://<your-app-name>.streamlit.app`

---

## 📦 Alternative Deployment Options

### Option 1: Hugging Face Spaces

1. Create a new Space at https://huggingface.co/spaces
2. Choose "Streamlit" as the SDK
3. Upload your files or connect GitHub repo
4. Add secrets in Space settings
5. Your app will be live at: `https://huggingface.co/spaces/<username>/<space-name>`

### Option 2: Render.com

1. Create account at https://render.com
2. Create new "Web Service"
3. Connect GitHub repo
4. Build command: `pip install -r requirements.txt`
5. Start command: `streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0`
6. Add environment variables in dashboard

---

## ⚠️ Important Notes

### Document Ingestion
- The vector database (`chroma_db/`) needs to be populated before deployment
- **Option 1**: Run `python ingest.py` locally, then commit the `chroma_db/` folder
- **Option 2**: Add ingestion as a startup script (slower first load)

### Memory Requirements
- Minimum: 2GB RAM
- Recommended: 4GB RAM
- The embedding model runs locally and needs ~500MB

### API Rate Limits
- HuggingFace free tier: ~1000 requests/day
- Consider caching responses for production use

---

## 🔧 Troubleshooting

### "No documents found" error
- Make sure you ran `python ingest.py` successfully
- Check that `chroma_db/` folder exists and has data
- Verify the folder is committed to Git

### "HuggingFace API error"
- Check your HF_TOKEN is valid
- Verify the token has read permissions
- Try regenerating the token

### Slow performance
- First load takes ~30 seconds (loading embedding model)
- Subsequent queries are faster (~5-10 seconds)
- Consider upgrading to paid HuggingFace tier for faster inference

---

## 📊 System Architecture

```
User Query
    ↓
Streamlit Interface
    ↓
Multi-Agent Orchestrator
    ↓
┌─────────────────────────────────────┐
│  1. Retrieval Agent                 │
│     - Searches vector database      │
│     - Finds relevant legal docs     │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  2. Analysis Agent (Kimi K2)        │
│     - Analyzes legal context        │
│     - Extracts key information      │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  3. Citation Agent                  │
│     - Validates sources             │
│     - Formats citations             │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  4. Response Agent (Kimi K2)        │
│     - Generates final answer        │
│     - Ensures accuracy              │
└─────────────────────────────────────┘
    ↓
Formatted Response with Citations
```

---

## 📝 License

This project is for educational purposes. Not a substitute for professional legal advice.

