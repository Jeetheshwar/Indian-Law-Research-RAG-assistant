# Streamlit Cloud Deployment Setup

## 🚀 Quick Deployment Steps

### 1. Deploy to Streamlit Cloud

1. Go to https://share.streamlit.io
2. Sign in with your GitHub account
3. Click **"New app"**
4. Select:
   - **Repository**: `Jeetheshwar/Indian-Law-Research-RAG-assistant`
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
5. Click **"Advanced settings"** before deploying

### 2. Configure Secrets

In the **Advanced settings** → **Secrets** section, add the following:

```toml
# Groq API Configuration (REQUIRED)
GROQ_API_KEY = "your_groq_api_key_here"

# Model Configuration (REQUIRED)
LLM_MODEL = "moonshotai/kimi-k2-instruct-0905"

# Optional: Override default settings
# TEMPERATURE = "0.1"
# CHROMA_PERSIST_DIR = "./data/chroma_db"
# MAX_RETRIEVAL_DOCUMENTS = "10"
# CHUNK_SIZE = "1000"
# CHUNK_OVERLAP = "200"
```

**Note:** You do NOT need to set `OPENAI_API_KEY` or `OPENAI_API_BASE`. The app automatically uses free local HuggingFace embeddings when OpenAI credentials are not provided.

### 3. Deploy

Click **"Deploy!"** and wait for the app to build and start.

---

## ⚙️ Configuration Details

### Required Secrets

- **GROQ_API_KEY**: Your Groq API key (get it from https://console.groq.com/keys)
- **LLM_MODEL**: The model to use (`moonshotai/kimi-k2-instruct-0905`)

### Optional Settings

All other settings have defaults in the code, but you can override them in secrets.

### Embeddings

The app automatically uses **free local HuggingFace embeddings** (`all-MiniLM-L6-v2`). You don't need to configure anything for embeddings - they work out of the box!

---

## 🔧 Troubleshooting

### Issue: "Unable to locate package" error

**Solution**: The `packages.txt` file should be empty or contain only valid apt package names (no comments).

### Issue: "Module not found" errors

**Solution**: Make sure all dependencies are listed in `requirements.txt`.

### Issue: "API key not found" errors

**Solution**: Double-check that you've added `GROQ_API_KEY` to the Streamlit Cloud secrets.

### Issue: App takes long to start

**Solution**: First deployment includes data ingestion (5-10 minutes). Subsequent restarts are faster.

---

## 📊 Expected Behavior

1. **First deployment**: 
   - Downloads and processes legal documents
   - Creates vector database
   - Takes 5-10 minutes

2. **Subsequent restarts**:
   - Loads existing vector database
   - Starts in ~30 seconds

---

## 🎯 Post-Deployment

After successful deployment, you'll get a URL like:
```
https://your-app-name.streamlit.app
```

Share this URL to let others use your Legal RAG Assistant!

---

## 🔒 Security Notes

- Never commit `.env` file to GitHub (it's in `.gitignore`)
- Use Streamlit Cloud secrets for sensitive API keys
- The Groq API key in this guide is for demonstration - replace with your own

