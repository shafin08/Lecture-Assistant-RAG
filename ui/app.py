# ============================================================
# ui/app.py
# Streamlit frontend — the chat UI for your Naruto RAG chatbot
# Run with: streamlit run ui/app.py
# Make sure FastAPI is running on port 8000 first
# ============================================================

import streamlit as st
import requests

# ============================================================
# Page Config — must be the very first Streamlit call
# ============================================================



st.set_page_config(
    page_title= "Naruto AI ChatBot",
    page_icon="🍥",
    layout="centered",
)

API_URL = "http://127.0.0.1:8000"



# ============================================================
# Helper Functions
# ============================================================

def check_api_health():
    try:
        response = requests.get(f"{API_URL}/health", timeout=3)
        return response.status_code == 200
        
    except:    
        return False
    
def send_question(query, chathistory):
    try:
        response = requests.post(f"{API_URL}/chat", json = {
            "query": query,
            "chathistory": chathistory
        }, 
        timeout=60 
                                 
        )

        if response.status_code == 200:
            return response.json()
        else:
            return None

        
    except requests.exceptions.ConnectionError:
        return None
    except requests.exceptions.Timeout:
        return None
    except Exception:
        return None

def clear_chat():
    st.session_state.messages = []
    st.session_state.chat_history = []


# ============================================================
# Initialize Session State
# Runs on every rerun — only sets values if they don't exist
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ============================================================
# Sidebar
# ============================================================

with st.sidebar:
    st.title("🍥 Naruto Chatbot")
    st.markdown("Ask me anything about Naruto characters! "
        "I'll answer based on the Naruto wiki.")
    
    st.divider()

    if st.sidebar.button("Clear chat", use_container_width=True):
        clear_chat()
        st.rerun()
    st.divider()

    # Example questions
    st.subheader("Example Questions")
    st.markdown("""
    - What is Naruto's signature jutsu?
    - Who is Sasuke Uchiha?
    - What are Kakashi's abilities?
    - Tell me about the Akatsuki members
    - Who is the strongest character?
    """)





# ============================================================
# Main Chat Interface
# ============================================================


st.title("🍥 Welcome to Naruto Chatbot!")
st.caption("A friendly and helpful AI-powered chatbot that will answer any questions about the Naruto Series")

st.divider()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

query = st.chat_input("Ask about any Naruto character....")

if query:
    with st.chat_message("user", avatar="https://static.wikia.nocookie.net/naruto/images/4/4d/Mecha-Naruto.png/revision/latest?cb=20210813034620"):
        st.write(query)
    st.session_state.messages.append(
        {
            "role": "user",
            "content": query
        }
    )

    with st.chat_message("assistant", avatar="https://static.wikia.nocookie.net/naruto-ultimate-ninja-storm/images/6/62/Mecha_Naruto.png/revision/latest?cb=20200923180940"):
        with st.spinner("Thinking..."):
            result = send_question(
                query=query, 
                chathistory=st.session_state.chat_history

            )
        if result:
            answer = result.get("answer", "Sorry I couldn't generate an answer.")
        

            st.write(answer)

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
            })

            # Add both messages to chat history for FastAPI
            # This enables multi-turn conversation
            st.session_state.chat_history.append({
                "role": "user",
                "content": query
            })
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": answer
            })
        else:
            error_message = "Could not connect to the API"

            st.error(error_message)
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_message,
            })



