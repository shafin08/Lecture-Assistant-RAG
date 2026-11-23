# ============================================================
# app/config.py — Centralized project settings
# All hardcoded values live here, loaded from .env
# ============================================================

import os
from dotenv import load_dotenv

load_dotenv()

# --- API Keys ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")

# --- Models ---
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-6-luna")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-2-v2"


# --- Chunking ---
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 512))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 64))


# --- DB ---
DATABASE_URL = os.getenv("DATABASE_URL")


#---JWT---
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES"))


# --- Paths ---
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR", "chroma_db")

CORS_ORIGINS = os.getenv("CORS_ORIGIN", "http://localhost:8501").split(",")

