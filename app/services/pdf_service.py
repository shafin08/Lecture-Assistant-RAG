# ============================================================
# app/services/pdf_service.py
# PDF processing — saving uploads, extracting text, cleaning
# ============================================================

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re                          
import pdfplumber                 
from fastapi import UploadFile     
from app.config import UPLOADS_DIR 
import uuid
from app.models import Messages
from sqlalchemy import select


def sanitize_filename(filename: str):
    """
    Cleans a filename to make it safe for saving.
    Removes path separators and dangerous characters.
    """
    # Get just the filename, no directory path
    filename = os.path.basename(filename)

    # Remove any character that isn't alphanumeric, dot, dash, or underscore
    filename = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)

    return filename


def save_pdf_file(content: bytes, file: UploadFile, usr_id):
    """
    Saves an uploaded PDF to disk in the user's folder.

    Files are organized by user ID:
        uploads/1/report.pdf
        uploads/2/budget.pdf

    Returns the file path where it was saved.
    """
    usr_dir = os.path.join(UPLOADS_DIR, str(usr_id))
    os.makedirs(usr_dir, exist_ok=True)
    clean_filename = sanitize_filename(file.filename)

    unique_filename = f"{uuid.uuid4().hex}_{clean_filename}" # Add uuid infront incase user upload file with the same name


    filepath = os.path.join(usr_dir, unique_filename)
    with open(filepath, "wb") as f:
        f.write(content)
    
    # Reset the file pointer
    file.file.seek(0)

    return filepath

def extract_pdf_text(filepath):
     """
    Extracts all text from a PDF file.
    Loops through every page and combines the text.


    Returns: the full text as a single string.
    """
     full_text = ""

     with pdfplumber.open(filepath) as pdf:
         for page in pdf.pages:
             page_text = page.extract_text()
             if page_text:
                 full_text += page_text + "\n"

             tables = page.extract_tables()
             for table in tables:
                 for row in table:
                     full_text += " | ".join(str(cell) for cell in row if cell) + "\n"

     return full_text

def clean_text(text):
     """
    Cleans extracted PDF text:
    - Removes excessive whitespace
    - Removes standalone page numbers
    - Fixes broken line breaks
    - Removes excessive blank lines
    """
     # Remove standalone page number
     text = re.sub(r"\n\s*\d+\s*\n", "\n", text)
    
     # Replace 3+ newlines with just 2 (removes excessive blank lines)
     text = re.sub(r"\n{3,}", "\n\n", text)

     # Replace multiple spaces/tabs with a single space
     text = re.sub(r"[ \t]{2,}", " ", text)

     # Remove leading/trailing whitespace from each line
     lines = [line.strip() for line in text.split("\n")]
     text = "\n".join(lines)

     # Remove leading/trailing whitespace from the whole text
     text = text.strip()

     return text

        

def process_pdf(content: bytes, file: UploadFile, usr_id):
    '''
    Combine all the mechanism needed for pdf document processing into one function

    Params:
    content: the pdf document content
    file: the user uploaded document
    usr_id(int)

    Return:
    the filepath, the filename and the cleaned content of the pdf document
    '''
    
    #Step 1
    pdf_file = save_pdf_file(content, file, usr_id)
    
    #Step 2
    raw_text = extract_pdf_text(pdf_file)

    #Step 3
    cleaned_text = clean_text(raw_text)

    return {
        "filepath": pdf_file,
        "filename": sanitize_filename(file.filename),
        "text": cleaned_text
    }


def delete_message(db, conversation_id):
    '''
    Delete a chat session messages when the user delete a document in a chat session
    '''
    find_messages = db.scalars(
        select(Messages)
        .where(Messages.conversation_id == conversation_id)
    ).all()

    for message in find_messages:
        db.delete(message)

    db.commit()




