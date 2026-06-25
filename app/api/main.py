import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from sentence_transformers import CrossEncoder
from config import RERANKER_MODEL, LLM_MODEL
from langchain_openai import ChatOpenAI

from rag.pipeline import ask_llm
from rag.retriever import load_vectorstore, load_bm25
from rag.reranker import run_reranker
from fastapi.responses import StreamingResponse



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


class HealthResponse(BaseModel):
    """
    Shape of the response from GET /health
    """
    status: str
    message: str


@asynccontextmanager
async def lifespan(app:FastAPI):
    # This runs once when the server starts
    app.state.vectorstore = load_vectorstore()
    app.state.bm25_retriever = load_bm25()
    app.state.reranker_model = CrossEncoder(RERANKER_MODEL)
    yield



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
async def chat(request: ChatRequest, http_request: Request):
    vb = http_request.app.state.vectorstore
    bm_25 = http_request.app.state.bm25_retriever
    reranker = http_request.app.state.reranker_model

    llm_model = ChatOpenAI(
        model=LLM_MODEL,
        temperature=0.1,
        max_retries=10,
        timeout=120
    )

    try: 
        if not request.query.strip():
            raise HTTPException(
                status_code = 400,
                detail= "Question cannot be empty"
            )
    

        results = ask_llm(request.query, vb, bm_25, reranker, request.chathistory)
        
        def generate():
            for chunk in llm_model.stream(results):
                if chunk:
                 yield chunk.content
        return StreamingResponse(generate(), media_type="text/plain")

    except Exception as e:
         print(f"Error processing question: {e}")
         raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
@app.get("/")
def root():
    return {"message": "Naruto Chatbot API is running!"}
    






if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",   # accept connections from any IP
        port=8000,
        reload=True        # auto-restart when code changes
    )