# ============================================================
# ingestion/embedder.py
# Loads chunks from data/processed/chunks.pkl
# Creates embeddings using OpenAI
# Stores everything in ChromaDB
# ============================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_openai import OpenAIEmbeddings        # converts text into vectors
from langchain_chroma import Chroma                   # the vector database
from app.config import (
    CHROMA_DB_DIR,      # where ChromaDB is saved on disk
    EMBEDDING_MODEL,    # which OpenAI embedding model to use
)


def get_vectordb():

    # Set up OpenAI embeddings
    # This is what converts text into vectors
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
    vector_db.delete(
        where={
            "$and": [
                {"user_id": user_id},
                {"document_id": document_id}
            ]
        }
    )
    return "Document chunks successfully deleted"