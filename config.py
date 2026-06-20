# ============================================================
# config.py — Centralized project settings
# All hardcoded values live here, loaded from .env
# ============================================================

import os
from dotenv import load_dotenv

load_dotenv()

# --- API Keys ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")

# --- Models ---
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
RERANKER_MODEL = "BAAI/bge-reranker-v2-m3"

# --- Scraping ---
ANIME_SERIES = os.getenv("ANIME_SERIES", "naruto")
MAX_PAGES = int(os.getenv("MAX_PAGES", 5))

WIKI_URLS = {
    "naruto": "https://naruto.fandom.com/wiki",
    "onepiece": "https://onepiece.fandom.com/wiki",
    "attackontitan": "https://attackontitan.fandom.com/wiki",
}

# --- Chunking ---
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 512))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 64))

# --- Retrieval ---
TOP_K_RETRIEVAL = int(os.getenv("TOP_K_RETRIEVAL", 7))
TOP_K_RERANK = int(os.getenv("TOP_K_RERANK", 5))

# --- Paths ---
RAW_DATA_DIR = "data/raw"
PROCESSED_DATA_DIR = "data/processed"
CHROMA_DB_DIR = "chroma_db"
BM25_INDEX_PATH = "data/bm25_index.pkl"

# --- Validation ---
def validate_config():
    missing = []
    if not OPENAI_API_KEY:
        missing.append("OPENAI_API_KEY")
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

if __name__ == "__main__":
    validate_config()
    print("✅ Config loaded successfully")
    print(f"  Series: {ANIME_SERIES}")
    print(f"  LLM: {LLM_MODEL}")
    print(f"  Embedding: {EMBEDDING_MODEL}")
