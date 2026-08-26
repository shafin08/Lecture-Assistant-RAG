from fastapi import APIRouter, Depends, HTTPException, status, Request  # routing and errors
from sqlalchemy.orm import Session                             # database session type
from pydantic import BaseModel                                 # request/response models
from datetime import datetime                                  # for response timestamps

from app.database import get_db                                # database dependency
from app.models import User                                    # current user type
from app.api.dependencies import get_current_user              # auth protection
from app.services.chat_service import (                        # DB logic from file 1
    create_conversation,
    get_usr_convo,
    get_convo,
    get_messages,
    save_message,
    update_title,
    delete_conversation
)
from sqlalchemy import select

router = APIRouter(prefix="/conversation", tags={"Conversation"})


class ConversationResponse(BaseModel):
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
    For the app sidebar that shows the user chats
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
    Delete a chat session and all documents attached to it
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


    

    
