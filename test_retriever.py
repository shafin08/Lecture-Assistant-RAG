# test_retriever.py
# Tests hybrid search filtering by user_id + conversation_id

from app.rag.retriever import hybrid_search, get_user_chunks
from app.rag.pipeline import ask_llm

# ============================================================
# Set these to real IDs from your database
# ============================================================
USER_ID = 1
CONVERSATION_ID = 4


# ============================================================
# Test 1 — Test chat
# ============================================================
query = "what major program is he in?"

test_pipeline = ask_llm(query, USER_ID, USER_ID,USER_ID, USER_ID, CONVERSATION_ID)

