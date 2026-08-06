# ============================================================
# app/api/main.py
# Main FastAPI app — includes all routers
# ============================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.database import create_tables
from app.api import auth, documents, chat, conversation 
from app.rag.embedder import get_vectordb
from sentence_transformers import CrossEncoder
from config import RERANKER_MODEL







# ============================================================
# Lifespan — runs on startup and shutdown
# Creates database tables when the server starts
# ============================================================

@asynccontextmanager
async def lifespan(app:FastAPI):
    # This runs once when the server starts
    create_tables()
    app.state.vector_db = get_vectordb()
    app.state.reranker_model = CrossEncoder(RERANKER_MODEL)
    yield



app = FastAPI(
    title="Lecture RAG API",
    description="Personal Lecture Assistant",
    version="1.0.0",
    lifespan=lifespan
)
    


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Include Routers
# Each router handles a different group of endpoints
# ============================================================

app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(conversation.router)



# ============================================================
# Health check 
# ============================================================
@app.get("/health")
def get_health():
    return {"status": "ok",
            "message": "Chatbot RAG API is running"
            
    }

@app.get("/")
def root():
    return {"message": "Chatbot API is running!"}
    






if __name__ == "__main__":
    uvicorn.run(
        "app.api.main:app",
        host="0.0.0.0",   # accept connections from any IP
        port=8000,
        reload=True        # auto-restart when code changes
    )
