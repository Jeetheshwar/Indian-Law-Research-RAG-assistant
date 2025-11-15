@echo off
echo ========================================
echo Legal RAG Assistant - Quick Start
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo ERROR: .env file not found!
    echo Please create a .env file with your HuggingFace token.
    echo.
    echo Example .env content:
    echo HF_TOKEN=your_huggingface_token_here
    echo OPENAI_API_BASE=dummy
    echo OPENAI_API_KEY=dummy
    echo LLM_MODEL=moonshotai/Kimi-K2-Thinking
    echo.
    pause
    exit /b 1
)

REM Check if chroma_db exists
if not exist chroma_db (
    echo No vector database found. Running document ingestion...
    echo This will take 2-3 minutes...
    echo.
    python ingest.py
    if errorlevel 1 (
        echo ERROR: Document ingestion failed!
        pause
        exit /b 1
    )
    echo.
    echo Document ingestion completed successfully!
    echo.
)

echo Starting Streamlit web interface...
echo.
echo The app will open at: http://localhost:8501
echo Press Ctrl+C to stop the server
echo.
streamlit run streamlit_app.py

