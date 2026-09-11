# ============================================================
# ui/app.py
# Streamlit frontend
# ============================================================

import streamlit as st
import re
from st_keyup import st_keyup
from api_client import (
    register,
    login, 
    create_conversation,
    list_conversation,
    get_conversation,
    change_title,
    delete_convo,
    upload,
    list_documents,
    delete_document,
    send_message
)


# Configure the Streamlit page
st.set_page_config(
    page_title= "Personal Lecture Assistant",
    page_icon="📚",
    layout="centered",
)

API_URL = "http://localhost:8000"


# ============================================================
# Initialize Session State
# Runs on every rerun
# Initialize value that will persist through reruns
# ============================================================


if "token" not in st.session_state:
    st.session_state.token = None

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# ============================================================
# Helper Functions
# ============================================================

def password_check(password):
    '''
    Check that the user password matches the necessary condition to create a strong password
    '''
    return [
        ("At least 12 characters", len(password) >= 12),
        ("An uppercase letter", bool(re.search(r"[A-Z]", password))),
        ("A lowercase letter", bool(re.search(r"[a-z]", password))),
        ("A number", bool(re.search(r"[0-9]",password))),
        ("A special character", bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)))
    ]


def sidebar():
    with st.sidebar:

        # Create new chat button
        if st.button("New Chat", use_container_width=True):
            new_convo = create_conversation(st.session_state.token)
            st.session_state.conversation_id = new_convo['id']
            st.rerun()

        st.divider()

        # Display conversation list
        st.subheader("Your Chats")

        usr_conversation = list_conversation(st.session_state.token)
        if not usr_conversation:
            st.caption("No chats yet, start a new chat above")
            
        for convo in usr_conversation:
            col_chat, col_menu = st.columns([5, 1])

            # For chat selection
            with col_chat:
                is_selected = convo['id'] == st.session_state.conversation_id
                label = f"{'▶ ' if is_selected else ''}{convo['title']}"
                if st.button(label, key=f"conv_{convo['id']}", use_container_width=True):
                    st.session_state.conversation_id = convo['id']
                    st.rerun()

            # Menu for the option to delete or rename a chat
            with col_menu:
                with st.popover("⋮", use_container_width=True):
                    # Rename
                    new_title = st.text_input(
                        "Rename",
                        value=convo["title"],
                        key=f"rename_input_{convo['id']}"
                    )
                    if st.button("Save", key=f"rename_btn_{convo['id']}"):
                        try:
                         change_title(st.session_state.token, convo["id"], new_title)
                         st.rerun()
                        except Exception as e:
                            st.error(str(e))
                    st.divider()
                    # Delete conversation
                    if st.button("Delete chat", key=f"delete_btn_{convo['id']}"):
                        try:
                            delete_convo(st.session_state.token, convo["id"])
                            if st.session_state.conversation_id == convo["id"]:
                                st.session_state.conversation_id = None
                            st.rerun()
                        except Exception as e:
                            st.error(str(e))


        st.divider()
        # Logout button
        if st.button("Logout", use_container_width=True):
            st.session_state.token = None
            st.session_state.conversation_id = None
            st.rerun()

def chat_area():

    if not st.session_state.conversation_id:
        st.info("Create or select a chat to get started")    
    else:
        token = st.session_state.token
        conversation_id = st.session_state.conversation_id

        # Display uploaded documents
        with st.expander("Document uploaded", expanded=True):
            try:
                documents = list_documents(token, conversation_id)
                if documents:
                    for doc in documents:
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.caption(f"• {doc['filename']}")
                        with col2:
                            if st.button("Delete Document", key=f"del_doc_{doc['id']}"):
                                try:
                                 delete_document(st.session_state.token, doc['id'], conversation_id)
                                 st.rerun()
                                except Exception as e:
                                    st.error(str(e))
                                
                else:
                    st.caption("No document uploaded yet")
                    
            except Exception as e:
                st.error(str(e))  

        # Upload widget
        have_document = list_documents(token, conversation_id)
        uploaded = st.file_uploader("Upload a document to start asking, only one document allowed", type={"PDF"}, key=st.session_state.uploader_key, max_upload_size=2000, accept_multiple_files=False)  
        if uploaded and st.button("Upload", disabled= bool(have_document)):
            with st.spinner("Uploading..."):
                try:
                    upload(st.session_state.token, st.session_state.conversation_id, uploaded)
                    st.toast("Document uploaded!", duration='long')
                    st.session_state.uploader_key += 1 # Resets the file uploader
                    st.rerun()

                except Exception as e:
                    st.error(str(e))
        st.divider()

        # Main query area
        have_document = list_documents(token, conversation_id) # A check for only allowing user to ask a query if there is a document uploaded
        try:
         
         convo_messages = get_conversation(st.session_state.token, st.session_state.conversation_id)

         for message in convo_messages['messages']:
            with st.chat_message(message['role']):
                st.write(message['content'])
                    
        except Exception as e:
         st.error(str(e))

        query = st.chat_input("Ask anything...", disabled= not have_document)

        if query:
            with st.chat_message("user"):
                st.write(query)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        st.write_stream(send_message(st.session_state.token, st.session_state.conversation_id, query))
                        
                    except Exception as e:
                        st.error(str(e))
            st.rerun()






# ============================================================
# Screen Functions
# ============================================================

def show_signup():
    login_tab, register_tab = st.tabs(["Login", "Register"])

    # New user registration tab
    with register_tab:

        new_name = st.text_input("Name", key="register_name")
        new_email = st.text_input("Email", key="register_email")
        new_password = st_keyup("Password", key="register_password", type="password")
      
        password_condition = password_check(new_password)
        st.caption("Password must contain: ")
        for label, met in password_condition:
            if met:
                st.markdown(f":green[{label}]")
            else:
                st.markdown(f":red[{label}]")


        if st.button("Create account", use_container_width=True):
            conditions = password_check(new_password)
            condition_met = all(met for _, met in conditions)
            
            if not new_email or not new_password or not new_name :
                st.error("Please fill in all the fields")
            elif "@" not in new_email:
             st.error("Please enter a valid email address")
            elif not condition_met:
                st.error("Password requirements are not met")
            else:
             success, msg = register(new_email, new_name, new_password)
             if success:
                st.success("Go to login page to sign in")
             else:
                st.error(msg)
    # User login tab
    with login_tab:
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", key="login_password", type="password")

        if st.button("Login", use_container_width=True):
         if not login_email or not login_password:
             st.error("Please fill in all the fields")
         elif "@" not in login_email:
             st.error("Please enter a valid email address")   
         else:
            token, msg = login(login_email, login_password)
            if token:
                st.session_state.token = token
                st.rerun()
            else:
                st.error(msg)





def main_app():
    '''
    Shows to the user after a successful login
    '''
    sidebar()
    chat_area()




# ============================================================
# The gate that decides which screen to show the user
# ============================================================

if st.session_state.token is None:
    show_signup()
else:
    main_app()

