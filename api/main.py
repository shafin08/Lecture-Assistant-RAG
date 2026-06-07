import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from rag.pipeline import ask_llm
from rag.retriever import load_vectorstore, load_bm25
from rag.reranker import run_reranker


# ============================================================
# Pydantic Models — define the shape of requests and responses
# ============================================================


class ChatRequest(BaseModel):
    query: str 
    chathistory: List[dict] = []

class Source(BaseModel):
    title: str
    url: str


class ChatResponse(BaseModel):
    answer: str 
    sources: List[dict] = []


class HealthResponse(BaseModel):
    """
    Shape of the response from GET /health
    """
    status: str
    message: str


@asynccontextmanager
async def lifespan(app:FastAPI):
    # This runs ONCE when the server starts
    vectorstore = load_vectorstore()
    bm25_retriever = load_bm25()
    yield
    # This runs when the server stops


app = FastAPI(
    title="Naruto RAG API",
    description="Ask questions about Naruto characters",
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




@app.get("/health")
def get_health():
    return {"status": "ok",
            "message": "Naruto RAG API is running"
            
    }



@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try: 
        if not request.query.strip():
            raise HTTPException(
                status_code = 400,
                detail= "Question cannot be empty"
            )
        
        print(f"\n Question received: {request.query}")

        results = ask_llm(request.query, request.chathistory)
        return {
            "answer": results["answer"],
            "sources": results["sources"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
         print(f"Error processing question: {e}")
         raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
    






if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",   # accept connections from any IP
        port=8000,
        reload=True        # auto-restart when code changes
    )