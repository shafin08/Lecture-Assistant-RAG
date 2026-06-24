# ============================================================
# rag/pipeline.py
# The main RAG pipeline — connects retrieval, reranking,
# and LLM generation into one ask() function
# ============================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from rag.retriever import load_vectorstore, load_bm25, hybrid_search
from rag.reranker import run_reranker
from config import LLM_MODEL, OPENAI_API_KEY

# System prompt — tells the LLM exactly how to behave
SYSTEM_PROMPT = """You are an expert Naruto chatbot. You answer questions 
about Naruto characters using ONLY the context provided below.

Rules you must follow:
1. Use the provided context as your ONLY source of information
2. If there is no relevant information in the context, say "I don't have enough information about that character or topic"
3. Always mention which url the character page your answer came from
4. Be conversational and helpful
5. You can make reasonable inferences from the context



Context:
{context}"""




def build_context(chunks):
    """
    Formats the retrieved chunks into a readable context string
    that gets injected into the system prompt.
    """

    formatted_context = ""

    counter = 1

    for chunk in chunks:
         title = chunk.metadata.get("title", "Unknown")
         url = chunk.metadata.get("source", "")
         content = chunk.page_content

         temp = f"Source {counter}: {title} ({url})\nContent: {content}\n\n"
         formatted_context += temp

         counter += 1
    
    return formatted_context


    

def get_sources(chunks):


    seen = set()
    sources = []

    for chunk in chunks:
        title = chunk.metadata.get("title", "Unknown")
        url = chunk.metadata.get("url", " ")

        if title not in seen:
            seen.add(title)
            sources.append({"title": title, "url": url})

    
    return sources

def rewrite_query(query, llm_model, chathistory=[]):
    if len(chathistory) == 0:
        return query
    
    messages = [
        SystemMessage(content="""Rewrite the user's question to be self contained 
        using the conversation history. 
        Example:
        History: Q: What village is Sasuke from? A: Sasuke is from Konoha
        Question: Who is his love interest?
        Rewritten: Who is Sasuke's love interest?
        
        Only return the rewritten question, nothing else.""")

    ]

    for items in chathistory:
        if items["role"] == "user":
            messages.append(HumanMessage(content=items["content"]))
        elif items["role"] == "assistant":
            messages.append(AIMessage(content=items["content"]))
    
    messages.append(HumanMessage(content=f"Rewrite this question: {query}"))

    new_query = llm_model.invoke(messages)
    return new_query.content
    


def ask_llm(query, vector_db, bm_25, reranker, chathistory=[]):
    t0 = time.time()
    
    llm_model = ChatOpenAI(
        model=LLM_MODEL,
        temperature=0.1,
        max_retries=10,
        timeout=120
    )

    query = rewrite_query(query, llm_model, chathistory=chathistory)

    t1 = time.time()
    print(f"Query rewrite: {t1-t0}")

    print(f"Rewritten query: {query}")


    search_results = hybrid_search(query, vector_db, bm_25)
    t2 = time.time()
    print(f"Search Result: {t2-t1}")

    rerank_results = run_reranker(query, reranker, search_results)
    
    t3 = time.time()
    print(f"Rerank: {t3-t2}")


    

    sources = get_sources(rerank_results)
    llm_context = build_context(rerank_results)
    '''
    for chunk in rerank_results:
        title = chunk.metadata.get("title", "Unknown")
        print(f"Title: {title}")
        print(f"Content: {chunk.page_content}\n\n")
    '''
        
    
    messages = [
           SystemMessage(content=SYSTEM_PROMPT.format(context=llm_context))
    ]

    for chat in chathistory:
        if chat["role"] == "user":
            messages.append(HumanMessage(content=chat["content"]))
        elif chat["role"] == "assistant":
            messages.append(AIMessage(content=chat["content"]))
    
    messages.append(HumanMessage(content=query))
    chathistory.append(HumanMessage(content=query))


    t4 = time.time()
    print(f"LLM Gen: {t4-t3}")

    print(llm_context)
    
    '''
    for items in rerank_results:
        print("Rerank Search")
        print("------------")
        title = items.metadata.get("title", "Unknown")
        print(f"Title: {title}")
        print(f"Content: {items.page_content}\n\n")
    '''
 
    return messages




'''
if __name__ == "__main__":
    print("🚀 Testing RAG pipeline...")
    print("Loading components — first run may take a few minutes...\n")

    # Load components once
    vectorstore = load_vectorstore()
    bm25_retriever = load_bm25()

    # Test questions
    test_questions = [
        "Why did sasuke kill itachi?",

    ]

    chat_history = []

    for question in test_questions:
        print(f"\n❓ Question: {question}")
        print("-" * 50)

        result = ask_llm(
            question,
            chathistory=chat_history,
        )

        print(f"💬 Answer: {result['answer']}")
        print(f"📚 Sources: {[s['title'] for s in result['sources']]}")
      

        # Add to chat history for multi-turn conversation
        
        chat_history.append({"role": "user", "content": question})
        chat_history.append({"role": "assistant", "content": result["answer"]})
        
'''


    

     


     

    




    