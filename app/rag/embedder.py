# ============================================================
# app/rag/embedder.py
# Create embeddings of user pdf document chunks and store in CHROMA DB  
# ============================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_openai import OpenAIEmbeddings        
from langchain_chroma import Chroma                   
from app.config import (
    CHROMA_DB_DIR,      
    EMBEDDING_MODEL,    
)


def get_vectordb():
    # Set up OpenAI embeddings
    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL
    
    )
    vector_db = Chroma(
        collection_name="User_Lecture_VectorDB",
        embedding_function=embeddings,
        persist_directory=CHROMA_DB_DIR
               
    )

    return vector_db

def add_chunks_vectordb(vector_db, chunks):
    vector_db.add_documents(chunks)
    return f"Chunks added: {len(chunks)}"

def delete_document_vectordb(user_id, vector_db, conversation_id):
    vector_db.delete(
        where={
            "$and": [
                {"user_id": user_id},
                {"conversation_id": conversation_id}
            ]
        }
    )
    return "User chunks successfully deleted"


def delete_document(user_id, vector_db, document_id):
    '''
    Delete all chunks of a document in CHROMA DB
    '''
    vector_db.delete(
        where={
            "$and": [
                {"user_id": user_id},
                {"document_id": document_id}
            ]
        }
    )
    return "Document chunks successfully deleted"