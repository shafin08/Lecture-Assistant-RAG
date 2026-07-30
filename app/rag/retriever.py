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

from langchain_community.retrievers import BM25Retriever         # keyword search
from langchain.schema import Document                            # rebuilding chunks for BM25
from app.rag.embedder import get_vectordb
from app.config import (
    CHROMA_DB_DIR,
    EMBEDDING_MODEL,
    OPENAI_API_KEY,
    TOP_K_RETRIEVAL
)


def get_user_chunks(user_id, conversation_id):
    vector_db = get_vectordb()
        
    # Fetch this conversation's chunks with their text and metadata
    usr_chunks = vector_db.get(where={"$and":[
        {"user_id": user_id},
        {"conversation_id": conversation_id}
    ]})

    document = []
    for text, metadata in zip(usr_chunks["documents"], usr_chunks["metadatas"]):
        document.append(
            Document(page_content=text, metadata=metadata)
        )

    return document

def keyword_search(query, bm25retriever, chunks):

    bm25 = BM25Retriever.from_documents(chunks)
    bm25.k = 3

    results = bm25.invoke(query)
    return results

    


def hybrid_search(query,vectorstore,bm25retriever, user_id, conversation_id):
    """
    Combines semantic search and BM25 keyword search.
    Returns a non duplicated list of relevant chunks.
    """
    # Semantic search — finds chunks with similar meaning
    # Note: later change to given vector db

    convo_chunks = get_user_chunks(user_id, conversation_id)

    if not convo_chunks:
        return []
    
    vector_db = get_vectordb()

    semantic_search = vector_db.similarity_search(
        query, 
        k= 5,
        filter={"$and":[
        {"user_id": user_id},
        {"conversation_id": conversation_id}
    ]})

    # Keyword search - use bm_25
    bm25_search = keyword_search(query, bm25retriever, convo_chunks)


    combined_search = semantic_search + bm25_search

    seen = set()

    final_chunks = []

    for chunk in combined_search:
        if chunk.page_content not in seen:
            final_chunks.append(chunk)
            seen.add(chunk.page_content)
        else:
            continue
    return final_chunks












    
