# 📋 Step-by-Step: GitHub Upload & Deployment

## ✅ Part 1: Upload to GitHub (5 minutes)

### Step 1: Create GitHub Repository
1. Go to [github.com](https://github.com)
2. Click the **"+"** icon (top-right) → **"New repository"**
3. Fill in:
   - **Repository name**: `legal-rag-assistant` (or your choice)
   - **Description**: "AI-powered Legal Research Assistant with Multi-Agent RAG Architecture"
   - **Visibility**: Public ✅ (required for free Streamlit deployment)
   - **DO NOT** initialize with README (we already have one)
4. Click **"Create repository"**

### Step 2: Push Your Code
Copy the commands from GitHub's "push an existing repository" section, or use these:

```bash
# Set your GitHub username and repo name
git remote add origin https://github.com/YOUR_USERNAME/legal-rag-assistant.git
git branch -M main
git push -u origin main
```

**Replace `YOUR_USERNAME`** with your actual GitHub username!

### Step 3: Verify Upload
- Refresh your GitHub repository page
- You should see all 21 files uploaded
- Check that `.env` is **NOT** uploaded (it's in `.gitignore`)

---

## 🚀 Part 2: Deploy to Streamlit Cloud (10 minutes)

### Step 1: Go to Streamlit Cloud
1. Open [share.streamlit.io](https://share.streamlit.io)
2. Click **"Sign in"** → **"Continue with GitHub"**
3. Authorize Streamlit to access your GitHub repositories

### Step 2: Create New App
1. Click **"New app"** (big button)
2. Fill in the form:
   - **Repository**: Select `YOUR_USERNAME/legal-rag-assistant`
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
   - **App URL**: Choose a custom name (e.g., `legal-rag-assistant`)

### Step 3: Configure Secrets
1. Click **"Advanced settings"** (bottom of the form)
2. In the **"Secrets"** section, paste this:

```toml
HF_TOKEN = "YOUR_HUGGINGFACE_TOKEN_HERE"
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

**IMPORTANT**: Replace `YOUR_HUGGINGFACE_TOKEN_HERE` with your actual token from [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

### Step 4: Deploy!
1. Click **"Deploy"**
2. Wait 5-10 minutes for:
   - Installing dependencies
   - Running data ingestion (downloading legal documents)
   - Starting the app

### Step 5: Success! 🎉
- Your app will be live at: `https://YOUR_APP_NAME.streamlit.app`
- Share this URL with anyone!
- The app will auto-restart if you push updates to GitHub

---

## 🔧 Troubleshooting

### Issue: "Module not found" error
**Solution**: Check that `requirements.txt` is in the repository root

### Issue: "HF_TOKEN not found"
**Solution**: 
1. Go to your app settings on Streamlit Cloud
2. Click "Secrets" in the left sidebar
3. Verify your HuggingFace token is correct

### Issue: App takes too long to load
**Solution**: 
- First deployment takes 5-10 minutes (data ingestion)
- Check logs in Streamlit Cloud dashboard
- If it times out, the app will retry automatically

### Issue: "System Not Initialized"
**Solution**: 
- Wait for data ingestion to complete
- Check logs for errors
- Verify all secrets are set correctly

---

## 📊 What Happens During Deployment?

1. **Build Phase** (2-3 minutes):
   - Streamlit installs Python packages from `requirements.txt`
   - Downloads embedding model (all-MiniLM-L6-v2)

2. **Data Ingestion** (5-7 minutes):
   - Downloads 6 bare acts, 5 case laws, 3 regulations
   - Processes and chunks documents
   - Creates vector database (16,000+ chunks)
   - Stores in `data/chroma_db`

3. **App Start** (30 seconds):
   - Loads vector database
   - Initializes multi-agent system
   - Connects to Kimi K2 via HuggingFace
   - App goes live!

---

## 🎯 Next Steps After Deployment

1. **Test Your App**:
   - Ask: "What constitutes a valid contract under Indian law?"
   - Verify citations are displayed correctly
   - Check that all features work

2. **Share Your Work**:
   - Add the live URL to your GitHub README
   - Share on LinkedIn/Twitter
   - Include in your portfolio

3. **Monitor Usage**:
   - Check Streamlit Cloud dashboard for analytics
   - View logs for errors
   - Monitor resource usage

---

## 🎉 Congratulations!

You now have:
- ✅ Code on GitHub (version controlled)
- ✅ Live deployment (publicly accessible)
- ✅ Professional portfolio project
- ✅ Shareable demo URL

**Your Legal RAG Assistant is live and ready to impress!** 🚀

