# ============================================================
# ui/api_client.py
# Wraps every backend API call into one clean function.
# ============================================================
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")


class APIError(Exception):
    """The request failed: bad input, server error, or server unreachable."""


class AuthError(Exception):
    """Token missing, invalid or expired: the user must log in again."""


def auth_headers(token: str):
    """Builds the Authorization header for protected endpoints."""
    return {"Authorization": f"Bearer {token}"}


def _error_detail(response, default):
    '''
    Pull the error message out of a failed response, falling back to default
    when the body isn't JSON (e.g. a plain-text 500)
    '''
    try:
        detail = response.json().get("detail", default)
    except ValueError:
        return default
    if isinstance(detail, list):  # FastAPI 422 validation errors
        detail = detail[0].get("msg", default)
    return detail


def _request(method, path, token=None, default_error="Something went wrong", **kwargs):
    '''
    Send a request to the backend and turn every failure into APIError or AuthError
    '''
    kwargs.setdefault("timeout", 10)
    headers = auth_headers(token) if token else {}
    try:
        response = requests.request(method, f"{API_URL}{path}", headers=headers, **kwargs)
    except requests.exceptions.ConnectionError:
        raise APIError("Could not connect to the server.")
    except requests.exceptions.Timeout:
        raise APIError("The server took too long to respond.")

    if response.status_code == 401:
        raise AuthError("Your session has expired. Please log in again.")
    if not response.ok:
        raise APIError(_error_detail(response, default_error))
    return response


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
       response.raise_for_status()
  except requests.exceptions.ConnectionError:
    return False, "Could not connect to the server."
  except requests.exceptions.HTTPError:
     detail = response.json().get("detail", "Login Failed")
     if isinstance(detail, list):
        detail = detail[0]["msg"]
     return False, detail
  except Exception as e:
     return False, str(e)


def create_conversation(token):
    return _request("POST", "/conversation", token, "Couldn't create chat").json()


def list_conversation(token):
    return _request("GET", "/conversation", token, "Couldn't load chats").json()


def get_conversation(token, conversation_id):
    return _request("GET", f"/conversation/{conversation_id}", token,
                    "Couldn't fetch conversation").json()


def change_title(token, conversation_id, title):
    return _request("PATCH", f"/conversation/{conversation_id}", token,
                    "Couldn't rename title", json={"title": title}).json()


def delete_convo(token, conversation_id):
    return _request("DELETE", f"/conversation/{conversation_id}", token,
                    "Couldn't delete chat").json()


def upload(token, conversation_id, file):
    return _request(
        "POST", "/documents", token, "Couldn't upload document",
        # Streamlit's uploaded file has .name and .getvalue()
        files={"file": (file.name, file.getvalue(), "application/pdf")},
        data={"conversation_id": conversation_id},
        timeout=120,
    ).json()


def list_documents(token, conversation_id):
    return _request("GET", "/documents", token, "Couldn't fetch documents",
                    params={"conversation_id": conversation_id}).json()


def delete_document(token, document_id, conversation_id):
    return _request("DELETE", f"/documents/{document_id}", token, "Couldn't delete document",
                    params={"document_id": document_id, "conversation_id": conversation_id}).json()


def send_message(token, conversation_id, query):
    response = _request(
        "POST", "/chat", token, "Couldn't get an answer",
        json={"query": query, "conversation_id": conversation_id},
        stream=True,
        timeout=(5, 180),
    )
    try:
        for chunk in response.iter_content(chunk_size=4, decode_unicode=True):
            if chunk:
                yield chunk
    except requests.exceptions.RequestException:
        raise APIError("The connection dropped while the answer was streaming.")
