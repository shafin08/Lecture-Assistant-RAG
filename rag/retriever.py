# ============================================================
# rag/retriever.py
# Hybrid search — combines semantic search (ChromaDB)
# and keyword search (BM25) for better retrieval
# ============================================================



import warnings
warnings.filterwarnings("ignore")
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pickle
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from config import (
    CHROMA_DB_DIR,
    PROCESSED_DATA_DIR,
    EMBEDDING_MODEL,
    OPENAI_API_KEY,
    TOP_K_RETRIEVAL
)


def load_vectorstore():
    """
    Loads the existing ChromaDB vectorstore from disk.
    This is the semantic search component.
    """

    embeddings = OpenAIEmbeddings(
        model=EMBEDDING_MODEL

    )
    # Loading the vector database from the disk
    vector_store = Chroma(
        collection_name="Naruto_vector_embeddings",
        embedding_function=embeddings,
        persist_directory=CHROMA_DB_DIR
    
    )

    return vector_store

def load_bm25():
    """
    Loads chunks from disk and creates a BM25 retriever.
    This is the keyword search component.
    """

    filepath = os.path.join(PROCESSED_DATA_DIR, "chunks.pkl")

    with open(filepath, "rb") as f:
        chunks = pickle.load(f)
        print(f"Loaded: {len(chunks)} chunks")

    bm_25_retriever = BM25Retriever.from_documents(documents=chunks)
    bm_25_retriever.k = TOP_K_RETRIEVAL

    return bm_25_retriever

def hybrid_search(query,vectorstore,bm25retriever):
    """
    Combines semantic search and BM25 keyword search.
    Returns a deduplicated list of relevant chunks.
    """
    # Semantic search — finds chunks with similar meaning
    semantic_search = vectorstore.similarity_search(query, k=TOP_K_RETRIEVAL)

    # Keyword search - use bm_25
    keyword_search = bm25retriever.invoke(query)

    combined_search = semantic_search + keyword_search

    seen = set()

    final_chunks = []

    for chunk in combined_search:
        if chunk.page_content not in seen:
            final_chunks.append(chunk)
            seen.add(chunk.page_content)
        else:
            continue
    return final_chunks












    
