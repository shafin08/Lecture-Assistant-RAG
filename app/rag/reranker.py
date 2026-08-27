# ============================================================
# app/rag/reranker.py
# Re-ranks chunks by relevance using a CrossEncoder model
# Keeps only the top K most relevant chunks
# ============================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_reranker(query, reranker, chunks):
    '''
    Rerank chunks from the initial hybrid search using a crossencoder model

    Params:
    query(str): the user query
    reranker: reranker model
    chunks(list of langchain document object): a list of chunks from the initial hybrid search

    Return:
    A list of rerank chunks
    '''
  

    if not chunks:
        return []


    pairs = []

    for chunk in chunks:
        pairs.append([query,chunk.page_content])
    
    results = reranker.predict(pairs)

    scored_results = sorted(
        zip(chunks, results),
        key=lambda x: x[1],
        reverse=True
    )



    final_chunks = []

    counter = 0

    for item in scored_results:
        if counter < int(len(chunks)*0.6): # Dynamically compute the top k to take 60% of the rerank results
            final_chunks.append(item[0])
        
        counter += 1
    

    return final_chunks




