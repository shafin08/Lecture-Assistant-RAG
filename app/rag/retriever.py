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

from langchain_community.retrievers import BM25Retriever         
from langchain.schema import Document                            

def compute_k(chunks_length):
    '''
    Dynamically compute the amount of chunks to return in a search based on the total amount of chunks of an uploaded document
    '''

    initial_k = max(5, int(chunks_length * 0.1))

    return min(25, initial_k)


def get_user_chunks(user_id, vectorstore, conversation_id):

    # Fetch this conversation's chunks with their text and metadata
    usr_chunks = vectorstore.get(where={"$and":[
        {"user_id": user_id},
        {"conversation_id": conversation_id}
    ]})

    document = []
    for text, metadata in zip(usr_chunks["documents"], usr_chunks["metadatas"]):
        document.append(
            Document(page_content=text, metadata=metadata)
        )

    return document

def keyword_search(query, chunks):

    bm25 = BM25Retriever.from_documents(chunks)
    bm25.k = 5

    results = bm25.invoke(query)
    return results

    


def hybrid_search(query,vectorstore, user_id, conversation_id):
    """
    Combines semantic search and BM25 keyword search.
    Returns a non duplicated list of relevant chunks.
    """


    convo_chunks = get_user_chunks(user_id, vectorstore, conversation_id)

    if not convo_chunks:
        return []
    
    k = compute_k(len(convo_chunks))
    
    # Semantic search - finds chunks with similar meaning
    semantic_search = vectorstore.similarity_search(
        query, 
        k= k,
        filter={"$and":[
        {"user_id": user_id},
        {"conversation_id": conversation_id}
    ]})

    # Keyword search - use bm_25
    bm25_search = keyword_search(query, convo_chunks)


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












    
