# ============================================================
# app/api/documents.py
# Document endpoint
# Handles uploading, deleting and listing users documents
# ============================================================


from fastapi import (
    APIRouter,           
    Depends,             
    HTTPException,       
    status,             
    UploadFile,          
    File,
    Request,
    Form

                                    
)
from sqlalchemy.orm import Session          
                                  

from app.database import get_db            
from app.models import User, Document, Conversation     
from app.api.dependencies import get_current_user  
from app.services.pdf_service import process_pdf, delete_message   
from app.rag.chunker import chunk_documents
from app.rag.embedder import add_chunks_vectordb, delete_document
from pydantic import BaseModel               
from datetime import datetime                
from sqlalchemy import select

router = APIRouter(prefix="/documents", tags=["Documents"])

class DocumentResponse(BaseModel):
    id: int
    filename: str
    uploaded_at: datetime

    class Config:
        from_attributes = True

class UploadResponse(BaseModel):
    message:str
    document: DocumentResponse

@router.post("/upload", response_model=UploadResponse)
async def upload(http_request: Request, conversation_id: int = Form(), user: User = Depends(get_current_user), db: Session = Depends(get_db), file: UploadFile = File()):
    '''
    Endpoint for handling when a user uploads a pdf document in a chat session
    Turn the document content to chunk, embed the chunks and store in CHROMA DB
    Create a new document record in the database
    '''
    vector_db = http_request.app.state.vector_db

    # Validate if its a pdf file
    content = await file.read(4)
    if content != b"%PDF":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File is not a valid PDF"
        )
    await file.seek(0)

    # Check if the conversation session exists 
    check_conversation = db.scalar(select(Conversation).where(Conversation.id == conversation_id))
    if not check_conversation:
        raise HTTPException(
         status_code=status.HTTP_404_NOT_FOUND,
         detail="Conversations session doesn't exists"
      )
    elif check_conversation.user_id != user.id:
         raise HTTPException(
          status_code=status.HTTP_404_NOT_FOUND,
          detail="Conversations session doesn't exists"
      )
    
    try:
     content = await file.read()
     processed_pdf = process_pdf(content, file, user.id)

     if not processed_pdf["text"]: # Check for invalid PDF file
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="PDF file could be empty or PDF is a scanned image")
     
     
     
     # Create new document record in the database
     new_doc = Document(
        user_id = user.id,
        conversation_id = conversation_id,
        filename = processed_pdf["filename"],
        content= processed_pdf["text"]

     )
     db.add(new_doc)
     db.commit()
     db.refresh(new_doc)

     # Use try and except in case OpenAI API fails
     try:
      chunks = chunk_documents(processed_pdf["text"], user.id, conversation_id, new_doc.id, new_doc.filename)  # Create chunks of the uploaded document content
      add_chunks_vectordb(vector_db, chunks) # Embed the document chunks and store in CHROMA DB
     except Exception:
        db.delete(new_doc)
        db.commit()
        raise HTTPException(status_code=500, detail="Failed to embed documents")


     return {
        "message": "Document uploaded successfully",
        "document": new_doc
     }
    except HTTPException:
     raise 
    except Exception as e:
       raise HTTPException(
          status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
          detail=f"Failed to process pdf: {e}"
       )
    
@router.get("/getdocs", response_model=list[DocumentResponse])
async def list_documents(conversation_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
   """
    Returns all documents belonging to the current user.
    Never returns other users' documents.
    """
   
   usr_doc = db.scalars(
           select(Document)
           .where(Document.user_id == user.id)
           .where(Document.conversation_id == conversation_id)
       ).all()

   

   return usr_doc # Returns a list of document objects or empty list if user has no uploaded document

@router.delete("/{document_id}")
async def delete_documents(document_id: int, conversation_id: int, http_request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
   """
    Deletes a user document
    Removes the pdf document from the disk, remove record in the database and delete all of the document chunks in CHROMA DB
    """


   vector_db = http_request.app.state.vector_db
   
   document = db.scalar(select(Document).where(Document.id == document_id))
   if not document:
      raise HTTPException(
         status_code=status.HTTP_404_NOT_FOUND,
         detail="User document not found"
      )
   
   # Check if the document belong to the user making the request
   if document.user_id != user.id:
      raise HTTPException(
         status_code=status.HTTP_403_FORBIDDEN,
         detail="Not allowed to delete this document"
      )

   # Use try and except in case OpenAI API fails
   try:
    delete_document(user.id, vector_db, document_id) # Delete document chunks in CHROMA DB
    delete_message(db, conversation_id) # Clear conversation history
   except Exception:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not delete document")
   

   db.delete(document)
   db.commit()

   

   return {
      "message": "Document successfully deleted"
   }

