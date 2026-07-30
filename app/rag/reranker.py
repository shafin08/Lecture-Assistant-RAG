# ============================================================
# rag/reranker.py
# Re-ranks chunks by relevance using a CrossEncoder model
# Keeps only the top K most relevant chunks
# ============================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import TOP_K_RERANK, RERANKER_MODEL
from sentence_transformers import CrossEncoder



def run_reranker(query,chunks):
    # Note: later load reranker from the app

    if not chunks:
        return []


    pairs = []
    model = CrossEncoder(RERANKER_MODEL)

    for chunk in chunks:
        pairs.append([query,chunk.page_content])
    
    results = model.predict(pairs)

    scored_results = sorted(
        zip(chunks, results),
        key=lambda x: x[1],
        reverse=True
    )

    final_chunks = []

    counter = 0

    for item in scored_results:
        if counter < 3:
            final_chunks.append(item[0])
        
        counter += 1
    

    return final_chunks




