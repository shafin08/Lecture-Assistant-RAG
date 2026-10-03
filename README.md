# Personal Lecture Assistant - RAG Study Chatbot

## Table of Contents
- [About The Project](#about-the-project)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Demo](#demo)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
- [Usage](#usage)
- [Future Improvements](#future-improvements)
- [Contact](#contact)




## About the Project

## Features

* **Upload your own notes:** Each chats session belong to a single lecture notes.
* **No hallucination:** if what you're looking for isn't in the notes, it will say so and doesn't create false information.
* **Good explanation of any concept:** The chatbot assists in making sure that you will get a full understanding of your lecture materials
* **Per chat isolation:** Each chat session will only search through the document uploaded in that specific chat session.
* **Per user isolation:** Each user can see only their own chat session.
* **Persistent chat history:** Every messages with the chatbot is saved.
* **Streaming Responses:** AI messages are typed out live.
* **Secure authentication:** Each logged in user receives a JWT token that will be used for authentication when calling an endpoint



## Tech Stack

*   **Frontend:** Streamlit
*   **Backend:** FastAPI
*   **Database:** PostgreSQL
*   **Vector Database:** ChromaDB
*   **Embeddings & LLM:** OpenAI
*   **Authentication:** JWT + OAuth
*   **Retrieval:** Hybrid Search(vector search(semantic) + keyword search(BM25))
*   **Reranker:** Hugging Face CrossEncoder(ms-marco-MiniLM-L-2-v2)


## Demo

## Getting Started

### Prerequisites

### Setup

## Usage
* a
## Design Notes

## Future Improvements
* Deploy to cloud platform
* Background processing for large PDF file
* Persistent login via cookies
* Add caching, background task processing and rate limiting for scaling the app

## Contact
* Shafin Ahmed - shafinahmed076@gmail.com
* Project Link: https://github.com/shafin08/Lecture-Assistant-RAG.git













