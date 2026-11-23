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
* **Good explanation of any concept:** The chatbot provide explanation that makes sure you get a good understanding of the lecture notes.
* **Per chat isolation:** Each chat session will only search through the document uploaded in that chat session.
* **Per user isolation:** each user can see only their own chat session.
* **Persistent chat history:** every messages with the chatbot is saved.
* **Streaming Responses:** AI responses are typed out live.
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
*   **Docker Desktop:** You can download it here: https://www.docker.com/products/docker-desktop/
*   **An OpenAI API key:** You can get one here: https://platform.openai.com/api-keys

### Setup
1. **Clone the repository**
2. **Create your .env files from the .evn.example**
  ```bash
   cp .env.example .env
   ```
   Open .env and fill:
   - OPENAI_API_KEY: your OpenAI API key
   - JWT_SECRET_KEY: a random secret. Generate one with:
     ```bash
     python3 -c "import secrets; print(secrets.token_hex(32))"
     ```
   - POSTGRES_PASSWORD: any password for the local database
3. **Build and start the app**
   ```bash
   docker compose up -d --build
   ```
    The first build takes about 4 minutes, because it installs all the dependencies.
4. **Open the app** at http://localhost:8501
    The backend needs a few seconds to start the first time. If the page says "Could not connect to the server", wait a moment and refresh.


## Usage
| Task | Command |
|---|---|
| Start the app | `docker compose up -d` |
| Stop the app | `docker compose stop` |
| Rebuild after changing code or requirements | `docker compose up -d --build` |

- **App:** http://localhost:8501

## Contact
* Shafin Ahmed - shafinahmed076@gmail.com
* Project Link: https://github.com/shafin08/Lecture-Assistant-RAG


