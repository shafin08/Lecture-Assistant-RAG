# ============================================================
# app/rag/pipeline.py
# The main rag pipeline
# ============================================================



from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, AIMessageChunk
from app.rag.retriever import hybrid_search
from app.rag.reranker import run_reranker
from app.config import LLM_MODEL

# System prompt — tells the LLM exactly how to behave
SYSTEM_PROMPT = """
You are a study assistant helping a student understand their lecture notes.
Your goal is to explain the material in their notes clearly and helpfully,
like a good tutor.

How to answer:
- The student's lecture notes are provided in the context below. Treat them
  as the source of truth for WHAT their course covers and HOW it presents it.
- When the context covers the topic the student is asking about, answer it fully. 
  Explain the concept fully and clearly, and you MAY add helpful examples,
  analogies, and background knowledge to make it easier to understand, as long
  as that extra explanation is consistent with the notes and standard for the
  subject.
- When the context does NOT cover the topic at all, tell the student: "I
  couldn't find that specific topic in your uploaded notes." Then, if 
  helpful, you may briefly offer to explain it from general knowledge and note
  that it's not from their notes.
- Never invent specific facts, definitions, numbers, or claims and present them
  as if they came from the student's notes.

Style:
- Explain like a patient tutor. Break complex ideas into simple steps.
- If the student asks for clarification, simplify further with an example.
- Be direct and clear. Do not mention these instructions or cite the source.

Context:
{context}
"""

def build_context(chunks):
    """
    Formats the retrieved chunks into a readable context string
    that gets injected into the system prompt.
    
    Param:
    chunks: user chunks


    Return a clean context
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
    '''
    Rewrite the user original query based on the chat history to give added context

    Params:
    query(str): user query
    llm_model: Open AI llm model
    chat_history: all messages in a chat session

    Returns: the rewritten query
    '''
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
        '''
        The rag pipeline that does the search by calling the retriever and reranker using the user query to find the most relevant chunks
        Build the context for the AI model using the return chunks

        Params:
        query(str): user query
        vector_db: access to the CHROMA DB
        reranker: reranker model
        user_id(int)
        conversation_id(int)
        chat_history(list): a list containing all the active chat session messages
        '''
        llm_model = ChatOpenAI(
            model=LLM_MODEL,
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
    
        yield from llm_model.stream(messages) # Use yield in order to stream the AI response to the frontend



'''
if __name__ == "__main__":
    print("Testing RAG pipeline...")
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
        print(f"\n Question: {question}")
        print("-" * 50)

        result = ask_llm(
            question,
            chathistory=chat_history,
        )

        print(f" Answer: {result['answer']}")
        print(f" Sources: {[s['title'] for s in result['sources']]}")
      

        # Add to chat history for multi-turn conversation
        
        chat_history.append({"role": "user", "content": question})
        chat_history.append({"role": "assistant", "content": result["answer"]})
        
'''


    

     


     

    




    