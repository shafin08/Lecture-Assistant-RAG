# ============================================================
# ingestion/chunker.py
# Loads .txt files from data/raw/ and splits them into chunks
# Saves chunks to data/processed/chunks.pkl
# ============================================================

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pickle
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from config import RAW_DATA_DIR, PROCESSED_DATA_DIR, CHUNK_SIZE, CHUNK_OVERLAP


def create_documents():
    """
    Read each file from the data/raw directory and put them into a langchain document object
    Return a list of langchain document object
    """

    documents = []

    # Return all the txt filename in data/raw
    raw_file_name = os.listdir(RAW_DATA_DIR)
    

    for name in raw_file_name:
      filepath = os.path.join(RAW_DATA_DIR, name)
      with open(filepath, "r",  encoding="utf-8") as f:
         text_file = f.readlines()

         title = text_file[0].replace("Title: ", "").strip()
         url = text_file[1].replace("URL: ", "").strip()
         content = "".join(text_file[3:]).strip()


         if not content:
            break

        # Create a LangChain Document object
        # page_content = the text
        # metadata = extra info to identify the document and for citation purposes
         doc = Document(
            page_content= content,
            metadata={
               "title": title,
               "source": url
            }
         )

         documents.append(doc)
    return documents

def chunk_documents(documents):
    """
    Create chunks for all documents
    """
    
    

    





create_documents()

    