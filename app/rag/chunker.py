# ============================================================
# ingestion/chunker.py
# Loads .txt files from data/raw/ and splits them into chunks
# Saves chunks to data/processed/chunks.pkl
# ============================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain.text_splitter import RecursiveCharacterTextSplitter  # splits text into chunks
from langchain.schema import Document                                # the chunk object with metadata
from app.config import CHUNK_SIZE, CHUNK_OVERLAP                     # chunk settings from .env



def chunk_documents(text, user_id, document_id, filepath):
   '''
   Chunks the user uploaded pdf document
   '''
   # Specifications for the chunks
   chunk_splitter = RecursiveCharacterTextSplitter(
         chunk_size = CHUNK_SIZE, # Max tokens per chunks
         chunk_overlap = CHUNK_OVERLAP, # overlap between chunks  
       )
   
   doc = Document(page_content=text, metadata={"user_id": str(user_id), "document_id": str(document_id), "filepath":filepath })
   chunks = chunk_splitter.split_documents([doc]) # List of chunks as langchain document objects
   return chunks






