# ============================================================
# qpp/rag/chunker.py
# Load user uploaded document and chunk the content
# ============================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain.text_splitter import RecursiveCharacterTextSplitter  
from langchain.schema import Document                                
from app.config import CHUNK_SIZE, CHUNK_OVERLAP                    



def chunk_documents(text, user_id, conversation_id, document_id, filename):
   '''
   Chunks the user uploaded pdf document
   Return list of chunks as langchain document object
   '''
   # Specifications for the chunks
   chunk_splitter = RecursiveCharacterTextSplitter(
         chunk_size = CHUNK_SIZE, # Max tokens per chunks
         chunk_overlap = CHUNK_OVERLAP, # overlap between chunks  
       )
   
   doc = Document(page_content=text, metadata={"user_id": user_id, "document_id": document_id, "conversation_id": conversation_id, "filename": filename})
   chunks = chunk_splitter.split_documents([doc]) # List of chunks as langchain document objects
   return chunks






