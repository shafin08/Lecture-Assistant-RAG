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
from app.models import User, Document       # the table models
from app.api.dependencies import get_current_user  # auth protection 
from app.services.pdf_service import process_pdf    # PDF logic 
from pydantic import BaseModel               # response models
from datetime import datetime                # for response timestamps
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
async def upload(user: User = Depends(get_current_user), db: Session = Depends(get_db), file: UploadFile = File()):
    '''
    Endpoint for uploading documents
    '''


    # Validate if its a pdf file
    content = await file.read(4)
    if content != b"%PDF":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="File is not a valid PDF"
        )
    await file.seek(0)
    
    try:
     content = await file.read()
     processed_pdf = process_pdf(content, file, user.id)

     if not processed_pdf["text"]: # if the pdf is empty
         
         if os.path.exists(processed_pdf["filepath"]):
             os.remove(processed_pdf["filepath"])
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not extract PDF file, could be empty")
     
     
     
     # Create new document in database record
     new_doc = Document(
        user_id = user.id,
        filename = processed_pdf["filename"],
        file_path =  processed_pdf["filepath"],
        content= processed_pdf["text"]

     )
     db.add(new_doc)
     db.commit()
     db.refresh(new_doc)

    # NOTE: In Phase 4 you'll add chunking + embedding here
    # so the document becomes searchable

     return {
        "message": "Document uploaded successfully",
        "document": new_doc
     }
    except HTTPException:
     raise 
    except Exception as e:
       raise HTTPException(
          status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
          detail=f"Failed to process pdf: str({e})"
       )
    
@router.get("/getdocs", response_model=list[DocumentResponse])
async def list_documents(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
   """
    Returns all documents belonging to the current user.
    Never returns other users' documents.
    """
   
   usr_doc = db.scalars(select(Document).where(Document.user_id == user.id)).all()

   return usr_doc

@router.delete("/{document_id}")
async def delete_documents(document_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
   """
    Deletes a document owned by the current user.
    Removes both the file from disk and the database record.
    """
   
   document = db.scalar(select(Document).where(Document.id == document_id))
   if not document:
      raise HTTPException(
         status_code=status.HTTP_404_NOT_FOUND,
         detail="User document not found"
      )
   

   if document.user_id != user.id:
      raise HTTPException(
         status_code=status.HTTP_403_FORBIDDEN,
         detail="Not allowed to delete this document"
      )
   
   if os.path.exists(document.file_path):
      os.remove(document.file_path)

   db.delete(document)
   db.commit()
   # NOTE: In Phase 4 you'll also delete this document's chunks
   # from ChromaDB here

   return {
      "message": "Document successfully deleted"
   }


      

   
   

















