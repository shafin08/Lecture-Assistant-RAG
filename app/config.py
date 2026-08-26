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
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-2-v2"


# --- Chunking ---
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 512))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 64))

# --- Retrieval ---
TOP_K_RERANK = int(os.getenv("TOP_K_RERANK", 5))

# --- DB ---
DATABASE_URL = os.getenv("DATABASE_URL")


#---JWT---
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES"))


# --- Paths ---
CHROMA_DB_DIR = "chroma_db"
UPLOADS_DIR = "upload"

CORS_ORIGIN = os.getenv("CORS_ORIGIN", "http://localhost:8501").split(",")

# --- Validation ---
def validate_config():
    """
    Checks that all required environment variables are set.
    Called at startup so the app fails fast with a clear error
    instead of crashing mid-request.
    """
    required = {
        "OPENAI_API_KEY": OPENAI_API_KEY,
        "DATABASE_URL": DATABASE_URL,
        "JWT_SECRET_KEY": JWT_SECRET_KEY,
    }

    missing = [name for name, value in required.items() if not value]

    if missing: 
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}. "
            f"Check your .env file."
        )

if __name__ == "__main__":
    validate_config()
    print(" Config loaded successfully")
    print(f"  LLM: {LLM_MODEL}")
    print(f"  Embedding: {EMBEDDING_MODEL}")
