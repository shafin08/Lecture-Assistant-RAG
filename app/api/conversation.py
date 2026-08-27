# ============================================================
# app/api/conversation.py
# Endpoints handles user interaction within a chat session
# Handles creating a new chat, listing all of user chat sessions, deleting a chat session, changing a chat title,
# Displaying all messages of a chat session
# ============================================================



from fastapi import APIRouter, Depends, HTTPException, status, Request  
from sqlalchemy.orm import Session                            
from pydantic import BaseModel                                
from datetime import datetime                                 

from app.database import get_db                               
from app.models import User                                   
from app.api.dependencies import get_current_user            
from app.services.chat_service import (                        
    create_conversation,
    get_usr_convo,
    get_convo,
    get_messages,
    update_title,
    delete_conversation
)


router = APIRouter(prefix="/conversation", tags={"Conversation"})


class ConversationResponse(BaseModel):
    '''
    Response model for a single chat session
    '''
    id: int
    title: str
    created_at: datetime

    class Config:
        from_attributes = True   # lets Pydantic read from the ORM object

class MessageResponse(BaseModel):
    """Shape of a single message when loading a conversation."""
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationDetailResponse(BaseModel):
    """Full conversation with all its messages — for GET /conversations/{id}."""
    id: int
    title: str
    created_at: datetime
    messages: list[MessageResponse]

    class Config:
        from_attributes = True


# ============================================================
# Request Models
# ============================================================

class RenameRequest(BaseModel):
    """Body for PATCH /conversations/{id} — renaming a conversation."""
    title: str

@router.post("",response_model=ConversationResponse)
async def new_conversation(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    '''
    Create a new conversation
    '''
    conversation = create_conversation(db, user.id)
    return conversation

@router.get("",response_model=list[ConversationResponse])
async def list_conversation(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    '''
    For the app sidebar that lists all of the user created chat sessions
    '''
    return get_usr_convo(db, user.id)

@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(conversation_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    '''
    User open a single chat session and gets all the chat messages
    '''
    conversation = get_convo(db, user.id, conversation_id)
    if not conversation:
        raise HTTPException(
         status_code=status.HTTP_404_NOT_FOUND,
         detail="Conversation not found"
        )
    messages = get_messages(db, conversation_id)
    return {
        "id": conversation.id,
        "title":  conversation.title,
        "created_at": conversation.created_at,
        "messages": messages
    }

@router.patch("/{conversation_id}")
async def change_title(title: RenameRequest, conversation_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    '''
    Modify a chat session title
    '''
    check_convo = get_convo(db, user.id, conversation_id)
    if not check_convo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Couldn't find conversation"
        )

    if not title.title:
        raise HTTPException(
         status_code=status.HTTP_400_BAD_REQUEST,
         detail="Title can't be empty"
        )

    rename_chat = update_title(db, conversation_id, title.title)

    if not rename_chat:
        raise HTTPException(
                 status_code=status.HTTP_400_BAD_REQUEST,
                 detail="Couldn't rename the chat"
                )
    return rename_chat

@router.delete("/{conversation_id}")
def delete_convo(conversation_id: int, http_request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    '''
    Delete a chat session along with the document attached to it and the messages in that chat session
    '''
    vector_db = http_request.app.state.vector_db
    delete_convo = delete_conversation(db, vector_db,  conversation_id, user.id)
    if not delete_convo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Couldn't delete conversation"
        )
    return {
        "message": delete_convo
    }


    

    
