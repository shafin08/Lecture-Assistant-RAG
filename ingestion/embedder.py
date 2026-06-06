# ============================================================
# ingestion/embedder.py
# Loads chunks from data/processed/chunks.pkl
# Creates embeddings using OpenAI
# Stores everything in ChromaDB
# ============================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pickle
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from config import (
    PROCESSED_DATA_DIR,
    CHROMA_DB_DIR,
    EMBEDDING_MODEL,
)

def load_chunks():
    """
    Loads chunks from data/processed/chunks.pkl
    that were saved by chunker.py
    """

    filepath = os.path.join(PROCESSED_DATA_DIR, "chunks.pkl")

    with open(filepath, "rb") as f:
        chunk = pickle.load(f)
        print(f"Loaded: {len(chunk)} chunks")
        return chunk
    
def embed_and_store(chunks):
    """
    Creates embeddings for each chunk using OpenAI
    and stores everything in ChromaDB.
    """
    
    # Set up OpenAI embeddings
    # This is what converts text into vectors
    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL

    )

    
    # Chroma.from_documents() does everything in one call:
    # - embeds every chunk
    # - stores text + vector + metadata
    # - saves to chroma_db/ folder
    vector_store = Chroma.from_documents(
        collection_name="Naruto_vector_embeddings",
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DB_DIR
       

    )

    print(f"Stored {len(chunks)} chunks in ChromaDB directory")

    return vector_store

    

def run_embedder():

    chunks = load_chunks()

    if not chunks:
        return None

    embed_and_store(chunks)

  

  
if __name__ == "__main__":
    run_embedder()



       


    
    




    