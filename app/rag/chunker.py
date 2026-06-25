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
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings
from config import RAW_DATA_DIR, PROCESSED_DATA_DIR, CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL


def create_documents():
    """
    Read each file from the data/raw directory and put them into a langchain document object
    Return a list of langchain document object
    """

    documents = []  #list of langchain documents objects

    # Return all the raw txt filename in data/raw
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
   
    # Specifications for the chunks
    chunk_splitter = RecursiveCharacterTextSplitter(
       chunk_size = CHUNK_SIZE, # Max tokens per chunks
       chunk_overlap = CHUNK_OVERLAP, # overlap between chunks
      separators=[
        "Background",
        "Personality",
        "Appearance",
        "Abilities",
        "Trivia",
        "Part I",
        "Part II",
        "\n\n"
        
   
    ]

       
    )
    # Split all documents into chunks while preserving the metadata
    chunks = chunk_splitter.split_documents(documents)
    print(type(chunks))
    print(len(chunks))
    return chunks # List of chunks as langchain document object


def save_chunks(chunks):
   """
    Saves chunks to data/processed/chunks.pkl
    so embedder.py can load them without re-chunking.
    """
   
   filepath = os.path.join(PROCESSED_DATA_DIR, "chunks.pkl")
   
   with open(filepath, "wb") as f:
      pickle.dump(chunks, f) # Convert all the chunks into binary and saves it to the disk, avoid having to rechunk everything again
   
   print(f"Saved {len(chunks)} chunks")

def test_semantic_chunker():
   model = OpenAIEmbeddings(
        model=EMBEDDING_MODEL

    )

   ai = SemanticChunker(
      embeddings=model
   )

   filepath = os.path.join(RAW_DATA_DIR, "A_(First_Raikage).txt")
   with open(filepath, "r",  encoding="utf-8") as f:
      text_file = f.readlines()


   chunks = ai.split_documents(text_file)
   print(len(chunks))



def run_chunker():

   all_docs = create_documents()

   chunks = chunk_documents(all_docs)

   save_chunks(chunks)

   
   



if __name__ == "__main__":
    test_semantic_chunker()



   

    

    

    
       
       
       


    