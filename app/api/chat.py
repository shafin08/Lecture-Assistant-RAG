from fastapi import (
    APIRouter,           # groups the document endpoints
    Depends,             # dependency injection
    HTTPException,       # returning errors
    status,              # readable status codes
    UploadFile,          # the uploaded file type
    File                 # marks a parameter as a file upload
)
from sqlalchemy.orm import Session          # database session type
import os                                    # deleting files from disk

from app.database import get_db             # database dependency
from app.models import User, Document, Conversation       # the table models
from app.api.dependencies import get_current_user  # auth protection 
from app.services.pdf_service import process_pdf    # PDF logic 
from app.rag.chunker import chunk_documents
from app.rag.embedder import add_chunks_vectordb, delete_document_vectordb
from pydantic import BaseModel               # response models
from datetime import datetime                # for response timestamps
from sqlalchemy import select

router = APIRouter(prefix="/chat", tags={"Chats"})


class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: datetime

    class Config:
        from_attributes = True   # lets Pydantic read from the ORM object

@router.post("/create_conversations", response_model=ConversationResponse)
async def create_conversations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_convo = Conversation(user_id = user.id)
    db.add(new_convo)
    db.commit()
    db.refresh(new_convo)
    return new_convo