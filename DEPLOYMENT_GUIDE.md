# 🚀 Deployment Guide

## Quick Deployment Options

This Legal RAG Assistant can be deployed on **Streamlit Cloud** (recommended), **HuggingFace Spaces**, or **Render** - all free platforms.

---

## ✅ Option 1: Streamlit Cloud (Recommended - Easiest)

### Step 1: Push to GitHub
```bash
# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit: Legal RAG Assistant"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **"New app"**
4. Select your repository: `YOUR_USERNAME/YOUR_REPO_NAME`
5. Set **Main file path**: `streamlit_app.py`
6. Click **"Advanced settings"**
7. Add **Secrets** (paste this):
   ```toml
   HF_TOKEN = "your_huggingface_token_here"
   OPENAI_API_BASE = "dummy"
   OPENAI_API_KEY = "dummy"
   LLM_MODEL = "moonshotai/Kimi-K2-Thinking"
   EMBEDDING_MODEL = "text-embedding-3-small"
   TEMPERATURE = "0.1"
   CHROMA_PERSIST_DIR = "./data/chroma_db"
   MAX_RETRIEVAL_DOCUMENTS = "10"
   CHUNK_SIZE = "1000"
   CHUNK_OVERLAP = "200"
   ```
8. Click **"Deploy"**

### Step 3: Wait for Build
- First deployment takes 5-10 minutes
- Streamlit will install dependencies and run data ingestion
- Your app will be live at: `https://YOUR_APP_NAME.streamlit.app`

**✅ Done! Your app is live and publicly accessible!**

---

## Option 2: HuggingFace Spaces

### Step 1: Create Space
1. Go to [huggingface.co/spaces](https://huggingface.co/spaces)
2. Click **"Create new Space"**
3. Choose **Streamlit** as SDK
4. Name your space (e.g., `legal-rag-assistant`)

### Step 2: Upload Files
```bash
# Clone your space
git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
cd YOUR_SPACE_NAME

# Copy all files from your project
cp -r /path/to/RAGassistant/* .

# Commit and push
git add .
git commit -m "Deploy Legal RAG Assistant"
git push
```

### Step 3: Configure Secrets
1. Go to your Space settings
2. Add **Repository secrets**:
   - `HF_TOKEN`: Your HuggingFace token
   - `OPENAI_API_BASE`: `dummy`
   - `OPENAI_API_KEY`: `dummy`
   - `LLM_MODEL`: `moonshotai/Kimi-K2-Thinking`

**✅ Your app will be live at: `https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME`**

---

## Option 3: Render

### Step 1: Create `render.yaml`
Create this file in your project root:
```yaml
services:
  - type: web
    name: legal-rag-assistant
    env: python
    buildCommand: "pip install -r requirements.txt && python ingest.py"
    startCommand: "streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0"
    envVars:
      - key: HF_TOKEN
        sync: false
      - key: OPENAI_API_BASE
        value: dummy
      - key: OPENAI_API_KEY
        value: dummy
      - key: LLM_MODEL
        value: moonshotai/Kimi-K2-Thinking
```

### Step 2: Deploy
1. Push to GitHub (see Option 1, Step 1)
2. Go to [render.com](https://render.com)
3. Click **"New +"** → **"Web Service"**
4. Connect your GitHub repository
5. Render will auto-detect `render.yaml`
6. Add your `HF_TOKEN` in environment variables
7. Click **"Create Web Service"**

**✅ Your app will be live at: `https://YOUR_APP_NAME.onrender.com`**

---

## 📝 Important Notes

### Data Ingestion
- On first deployment, the system will run `ingest.py` to download and process legal documents
- This takes 5-10 minutes and creates the `data/chroma_db` directory
- Subsequent deployments will be faster (data is cached)

### Environment Variables
All platforms need these secrets:
- `HF_TOKEN`: Get from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
- Other variables: Use values from `.env.example`

### Free Tier Limits
- **Streamlit Cloud**: 1GB RAM, 1 CPU (sufficient for this app)
- **HuggingFace Spaces**: 16GB RAM, 2 CPU (generous free tier)
- **Render**: 512MB RAM (may need optimization)

---

## 🎉 Success!

Once deployed, your Legal RAG Assistant will be publicly accessible and ready to answer legal questions with accurate citations!

**Share your live URL** and let others explore Indian legal research powered by AI! 🚀

