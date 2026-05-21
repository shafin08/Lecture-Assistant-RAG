#!/bin/bash
# ============================================================
# Anime RAG Project — Phase 1 Setup Script
# Run this once to scaffold the full project structure
# ============================================================

echo "🚀 Setting up Anime RAG project..."

# Create folder structure
mkdir -p data/raw
mkdir -p data/processed
mkdir -p ingestion
mkdir -p rag
mkdir -p api
mkdir -p ui
mkdir -p evals
mkdir -p .github/workflows
mkdir -p chroma_db

# Create empty __init__.py files
touch ingestion/__init__.py
touch rag/__init__.py
touch api/__init__.py
touch ui/__init__.py
touch evals/__init__.py

# Create placeholder files
touch ingestion/scraper.py
touch ingestion/chunker.py
touch ingestion/embedder.py
touch rag/retriever.py
touch rag/reranker.py
touch rag/pipeline.py
touch api/main.py
touch ui/app.py
touch evals/eval.py

echo "✅ Folder structure created!"

# Create virtual environment
python3 -m venv .venv
echo "✅ Virtual environment created!"

# Activate and install dependencies
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Dependencies installed!"
echo ""
echo "Next steps:"
echo "  1. Copy .env.example to .env and fill in your API keys"
echo "  2. Run: source .venv/bin/activate"
echo "  3. Start with Phase 2 — ingestion/scraper.py"
