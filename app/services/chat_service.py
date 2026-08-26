import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session                 # database session type
from app.models import Conversation, Messages, Document  # the table models
from app.rag.embedder import delete_document_vectordb     # remove chunks on delete
from sqlalchemy import select



def create_conversation(db, user_id):
    '''
    Create a new row in the db for a new conversation
    Returns a Conversation object
    '''
    new_convo = Conversation(user_id = user_id)
    db.add(new_convo)
    db.commit()
    db.refresh(new_convo)
    return new_convo

def get_usr_convo(db, user_id):
    '''
    Returns every conversation of a user
    '''
    find_convo = db.scalars(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.created_at.desc())
    ).all()

    return find_convo


def get_convo(db, user_id, conversation_id):
    '''
    Returns a single conversation of a user
    '''
    find_convo = db.scalar(
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .where(Conversation.user_id == user_id)
    )

    return find_convo

def get_messages(db, conversation_id):
    '''
    Return all messages of a conversation
    '''
    find_messages = db.scalars(
            select(Messages)
            .where(Messages.conversation_id == conversation_id)
            .order_by(Messages.created_at.asc())
        ).all()
    return find_messages

def save_message(db, conversation_id, role, content):
    '''
    Saves a message to the database
    Return the newly saved Messages object
    '''
    new_message = Messages(
        conversation_id = conversation_id, 
        role = role,
        content = content
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

def update_title(db, conversation_id, title):
    '''
    Update the title of a conversation
    '''
    find_convo = db.scalar(select(Conversation).where(Conversation.id == conversation_id))
    if find_convo:
        find_convo.title = title
        db.commit()
        db.refresh(find_convo)
        return find_convo
    else:
        return None

    

def delete_conversation(db, vector_db, conversation_id, user_id):
    '''
    Delete conversation, documents and messages attached to the conversation in the database
    Delete chunks associated with the documents in CHROMA DB
    Delete all documents in upload associated with the documents
    '''
    find_convo = db.scalar(
            select(Conversation)
            .where(Conversation.id == conversation_id)
            .where(Conversation.user_id == user_id)
        )

    if not find_convo:
        return None
    else:
        find_document = db.scalars(
                    select(Document)
                    .where(Document.conversation_id == conversation_id)
                    .where(Document.user_id == user_id)
                ).all()
        if not find_document: # Conversation is created but no document is uploaded to that conversation yet
            db.delete(find_convo)
            db.commit()
            return "Successfully delete conversation(empty documents)"
        else: 
         # Delete all document in the upload folder
         for document in find_document:
              if os.path.exists(document.file_path):
                   os.remove(document.file_path)
         delete_document_vectordb(user_id, vector_db, conversation_id) # Delete all the document chunks in CHROMA DB
         db.delete(find_convo)
         db.commit()
         return "Successfully delete conversation"
        
        

def generate_title_from_question(question):
    """
    Simple auto-title — uses the first part of the first question.
    Trims to ~40 characters and cleans it up.
    """
    title = question.strip()

    # Trim to 40 characters, add ellipsis if longer
    if len(title) > 40:
        title = title[:40].rsplit(" ", 1)[0] + "..."

    return title

