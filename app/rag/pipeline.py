# ============================================================
# rag/pipeline.py
# Logic for the main RAG pipeline
# ============================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, AIMessageChunk
from app.rag.retriever import hybrid_search
from app.rag.reranker import run_reranker
from config import LLM_MODEL

# System prompt — tells the LLM exactly how to behave
SYSTEM_PROMPT = """

You are a study assistant helping student understand their study notes. Answer the student's question using the
context provided below as your primary source. You may make reasonable inferences.

Rules:
1. Use information from the provided context as the primary source
2. If the answer isn't in the context, say "I couldn't find that in 
   your uploaded notes" — do not use outside knowledge
3. Explain concepts clearly, like a helpful tutor
4. If the student asks for clarification, break it down simply
5. Don't cite the source

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
         usr_id = chunk.metadata.get("user_id", "Unknown")
         source = chunk.metadata.get("filename", "")
         content = chunk.page_content

         temp = f"Source {counter}: {usr_id} ({source})\nContent: {content}\n\n"
         formatted_context += temp

         counter += 1
    
    return formatted_context



def rewrite_query(query, llm_model, chathistory=[]):
    if len(chathistory) == 0:
        return query
    
    messages = [
        SystemMessage(content="""Rewrite the student's question to be self-contained 
         using the conversation history, so it can be used to search their lecture notes.
         Resolve any references like "it", "that", "this concept", "the one you mentioned"
         into the actual topic name from the earlier conversation.

         Example:
         History: Q: What is a binary search tree? A: A BST is a tree where each node's left child is smaller and right child is larger.
         Question: What's its time complexity?
         Rewritten: What is the time complexity of a binary search tree?

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
    


def ask_llm(query, vector_db, reranker, user_id, conversation_id, chathistory=[]):
        llm_model = ChatOpenAI(
            model=LLM_MODEL,
            temperature=0.1,
            max_retries=10,
            timeout=120,

        )
        
        query = rewrite_query(query, llm_model, chathistory=chathistory)

        print(query)

        search_results = hybrid_search(query, vector_db, user_id, conversation_id)


        if not search_results:
            yield AIMessageChunk(content="I couldn't find anything about that in your uploaded notes.")
            return
    

        rerank_results = run_reranker(query, reranker, search_results) 
        
        llm_context = build_context(rerank_results)

        print(llm_context)
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
            if chat.get("role") == "user":
                messages.append(HumanMessage(content=chat.get("content")))
            elif chat.get("role") == "assistant":
                messages.append(AIMessage(content=chat.get("content")))
        
        messages.append(HumanMessage(content=query))
        
        
        
        '''
        for items in rerank_results:
            print("Rerank Search")
            print("------------")
            title = items.metadata.get("title", "Unknown")
            print(f"Title: {title}")
            print(f"Content: {items.page_content}\n\n")
        '''
    
        yield from llm_model.stream(messages)



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


    

     


     

    




    