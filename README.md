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

* **Upload your own notes:** each chats session belong to a single lecture notes.
* **No hallucination:** if what you're looking isn't in the notes, it will say so and doesn't create false information.
* **Good explanation of any concept:** The chatbot assists in making sure that you will understand everything in the lecture notes.
* **Per chat isolation:** Each chat session will only search through the document uploaded in that chat session.
* **Per user isolation:** each user can see only their own chat session.
* **Persistent chat history:** every messages with the chatbot is saved.
* **Streaming Responses:** AI messages are typed out live.
* **Secure authentication:** Each login gets a JWT token, every endpoint requires a token, password hashing



## Tech Stack

*   **Frontend:** Streamlit
*   **Backend:** FastAPI
*   **Database:** PostgreSQL
*   **Vector Database:** ChromaDB
*   **Embeddings & LLM:** OpenAI
*   **Authentication:** JWT + Oauth
*   **Retrieval:** Hybrid Search(vector search(semantic) + keyword search(BM25) )
*   **Reranker:** Hugging Face CrossEncoder(ms-marco-MiniLM-L-2-v2)


## Demo

## Getting Started

### Prerequisites

### Setup

## Usage

## Design Notes

## Future Improvements
* Deploy to cloud platform and get a live URL
* Background processing for large PDF file
* Persistent login via cookies
* More creative frontend UI
* Add caching, background task processing and rate limiting for scaling the app

## Contact
Shafin Ahmed - shafinahmed076@gmail.com
Project Link: https://github.com/shafin08/Lecture-Assistant-RAG.git













