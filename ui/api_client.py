# ============================================================
# frontend/api_client.py
# Wraps every backend API call in a clean function.
# The UI imports these instead of calling requests directly.
# ============================================================
import requests

API_URL = "http://localhost:8000"


def auth_headers(token: str):
    """Builds the Authorization header for protected endpoints."""
    return {"Authorization": f"Bearer {token}"}

def register(email, username, password):
    try:
     response = requests.post(
        f"{API_URL}/auth/register",
        json={
            "email": email,
            "username": username,
            "password": password

        },
        timeout=10
    )

     if response.status_code == 200:
        return True, None
     elif response.status_code == 400:
        detail = response.json().get("detail", "Register failed")
        return False, detail
    except requests.exceptions.ConnectionError:
     return False, "Could not connect to the server."

def login(email, password):
  try:
    response = requests.post(
      f"{API_URL}/auth/login",
      json={
        "email": email,
        "password": password
      },
      timeout=10
    )

    if response.status_code == 200:
      token = response.json()["access_token"]
      return token, None
    else:
      detail = response.json().get("detail", "Login failed")
      return False, detail
  except requests.exceptions.ConnectionError:
    return False, "Could not connect to the server."   

def create_conversation(token): 
     response = requests.post(
      f"{API_URL}/conversation",
      headers=auth_headers(token),
      timeout=10
    )
     response.raise_for_status()
     return response.json()


def list_conversation(token):

   try:
    response = requests.get(
      f"{API_URL}/conversation",
      headers=auth_headers(token),
      timeout=10
   )
    response.raise_for_status()
    return response.json()
   except requests.exceptions.HTTPError:
    detail = response.json().get("detail")
    raise Exception(detail)



def get_conversation(token, conversation_id):
   try:
    response = requests.get(
      f"{API_URL}/conversation/{conversation_id}",
      headers=auth_headers(token),
      timeout=10
   )
    response.raise_for_status()
    return response.json()
   except requests.exceptions.HTTPError:
    detail = response.json().get("detail", "Couldn't fetch conversation")
    raise Exception(detail)

def change_title(token, conversation_id, title):
   try:
    response = requests.patch(
         f"{API_URL}/conversation/{conversation_id}",
         headers=auth_headers(token),
         json={"title":title},
         timeout=10
      )
    response.raise_for_status() 
    return response.json()
   except requests.exceptions.HTTPError:
      detail = response.json().get("detail", "Couldn't rename title")
      raise Exception(detail)

def delete_convo(token, conversation_id):
  try:
     response = requests.delete(
           f"{API_URL}/conversation/{conversation_id}",
           headers=auth_headers(token),
           timeout=10
        )
     response.raise_for_status() 
     return response.json()
  except requests.exceptions.HTTPError:
     detail = response.json().get("detail")
     raise Exception(detail)


def upload(token, conversation_id, file):
  try:
    response = requests.post(
      f"{API_URL}/documents/upload",
      headers=auth_headers(token),
      # Streamlit's uploaded file has .name and .getvalue()
      files={"file": (file.name, file.getvalue(), "application/pdf")},
      data={"conversation_id": conversation_id},
      timeout=120

    )

    response.raise_for_status()
    return response.json()
  except requests.exceptions.HTTPError:
    detail = response.json().get("detail", "Couldn't upload document")
    raise Exception(detail)

def list_documents(token, conversation_id):
  try:
      response = requests.get(
        f"{API_URL}/documents/getdocs",
        headers=auth_headers(token),
        params={"conversation_id":conversation_id},
        timeout=10
  
      )
  
      response.raise_for_status()
      return response.json()
  except requests.exceptions.HTTPError:
    detail = response.json().get("detail", "Couldn't fetch documents")
    raise Exception(detail)
  except requests.exceptions.RequestException:
     raise Exception("Something went wrong with the request.")

def delete_document(token, document_id):
  try:
    response = requests.delete(
          f"{API_URL}/documents/{document_id}",
          headers=auth_headers(token),
          params={"document_id": document_id},
          timeout=10
    
        )
    
    response.raise_for_status()
    return response.json()
  except requests.exceptions.HTTPError:
        detail = response.json().get("detail")
        raise Exception(detail)

def send_message(token, conversation_id, query):
   try:
       response = requests.post(
             f"{API_URL}/chat",
             headers=auth_headers(token),
             json={
                "query": query,
                "conversation_id": conversation_id

             },
             stream=True,

             timeout=120
       
           )
       response.raise_for_status()

       for chunk in response.iter_content(chunk_size=8, decode_unicode=True):
          if chunk:
             yield chunk
       
   except requests.exceptions.HTTPError:
           detail = response.json().get("detail")
           raise Exception(detail)
   
  

      
   
   
  
 