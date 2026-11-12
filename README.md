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
Lecture Assistant RAG is a full-stack study tool that lets students upload their own lecture notes and ask questions answered directly from that material.

As a university student, lecture notes can easily pile up across courses and before exams there is never enough time to go through all of them. Since Generic AI chatbots can hallucinate, I decided to build a retrival-augmented generation system that grounds each answer with the user's uploaded lecture notes to make explanations accurate to the actual course content.


## Features

* **Upload your own notes:** each chats session belong to a single lecture notes.
* **No hallucination:** if what you're looking for isn't in the notes, it will say so and doesn't create false information.
* **Good explanation of any concept:** The chatbot assists in making sure you will get a good understanding of the lecture notes.
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
*   **Authentication:** JWT
*   **Retrieval:** Hybrid Search( vector search(semantic) + keyword search(BM25) )
*   **Reranker:** Hugging Face CrossEncoder(ms-marco-MiniLM-L-2-v2)


## Demo

## Getting Started

### Prerequisites

### Setup

## Usage
* a
## Design Notes

## Contact
* Shafin Ahmed - shafinahmed076@gmail.com
* Project Link: https://github.com/shafin08/Lecture-Assistant-RAG.git


