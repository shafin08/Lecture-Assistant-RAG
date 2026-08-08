# ============================================================
# app/api/chat.py
# Chat endpoint — ties the RAG pipeline to conversation history
# Saves messages, loads history for context, auto-titles chats
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models import User
from app.api.dependencies import get_current_user
from app.services.chat_service import (
    get_convo,
    get_messages,
    save_message,
    update_title,
    generate_title_from_question
)
from app.rag.pipeline import ask_llm

router = APIRouter(prefix="/chat", tags=["Chats"])

# ============================================================
# Pydantic Models
# ============================================================

class ChatRequest(BaseModel):
    query: str
    conversation_id: int


class ChatResponse(BaseModel):
    answer: str

@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, http_request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    '''
    The main query mechanism
    ''' 
    vector_db = http_request.app.state.vector_db
    reranker_model = http_request.app.state.reranker_model

    # Validate the question isn't empty
    if not request.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty"
        )

    chathistory = []
    check_convo = get_convo(db, user.id, request.conversation_id) 
    
    # Check if the conversation belongs to the user
    if not check_convo:
        raise HTTPException(
         status_code=status.HTTP_404_NOT_FOUND,
         detail="Conversation not found"
        )
    convo_messages = get_messages(db, request.conversation_id) # Get all the conversation messages

    for message in convo_messages:
        chathistory.append({
            "role": message.role,
            "content": message.content
        })

   
    save_message(db, request.conversation_id, "user", request.query)
    def generate():
      full_txt = ""
      for chunk in ask_llm(request.query, vector_db, reranker_model, user.id, request.conversation_id, chathistory):
         full_txt += chunk.content
         yield chunk.content
      save_message(db, request.conversation_id, "assistant", full_txt)
      if len(convo_messages) == 0:
        title = generate_title_from_question(full_txt)
        update_title(db, request.conversation_id, title)
      
    

    return StreamingResponse(generate(), media_type="text/plain")
    

    


