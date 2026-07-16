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
from app.api import auth   # import the auth router




# ============================================================
# Lifespan — runs on startup and shutdown
# Creates database tables when the server starts
# ============================================================

@asynccontextmanager
async def lifespan(app:FastAPI):
    # This runs once when the server starts
    create_tables()
    yield



app = FastAPI(
    title="Financial RAG API",
    description="Personal Financial Assistant",
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



# ============================================================
# Health check 
# ============================================================
@app.get("/health")
def get_health():
    return {"status": "ok",
            "message": "Chhatbot RAG API is running"
            
    }

@app.get("/")
def root():
    return {"message": "Chatbot API is running!"}
    






if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",   # accept connections from any IP
        port=8000,
        reload=True        # auto-restart when code changes
    )
