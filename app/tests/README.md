# Study Assistant — Full Test Suite

End-to-end tests for the whole app: auth, conversations, documents,
chat history, and the RAG pipeline — all exercised through the API.

## Setup

```bash
pip install pytest reportlab
```

`reportlab` builds tiny PDFs in memory for the upload/RAG tests.

## Point it at your app

`tests/conftest.py` imports your FastAPI app:

```python
from app.api.main import app
```

Change that one line if your app lives elsewhere.

## Run

```bash
# Fast layer — auth, conversations, validation. No API cost, runs in seconds.
pytest -m "not slow"

# Everything, including document upload + full RAG pipeline.
# Needs OPENAI_API_KEY set. Costs a little in API calls.
pytest

# A single file
pytest tests/test_rag.py -v
```

## What's covered

| File | Area | API cost |
|------|------|----------|
| `test_auth.py` | register, login, token protection, password rules | No |
| `test_conversations.py` | CRUD, ownership, history | No |
| `test_documents.py` | upload, per-chat scoping, deletion | Yes (slow) |
| `test_rag.py` | retrieval, no-hallucination, isolation, context, titles | Yes (slow) |

## The headline tests (put these in your README)

- `test_cross_chat_isolation` — a history question in a biology chat
  is not answered from the history chat's notes.
- `test_cross_user_isolation` — one user never receives another user's content.
- `test_no_hallucination` — questions outside the notes get "couldn't find it",
  not a made-up answer.

## Note on storage

This app does **not** save uploaded PDFs to disk — on upload it extracts
the text, chunks it, and stores only the chunks in ChromaDB. So the
document tests check the DB record and the chunks, never a file on disk.
`test_upload_response_has_no_file_path` asserts no disk path leaks in the
API response.

## Important

The `slow` tests use your **real** database and ChromaDB and create
users, conversations, and document chunks as they run. Point them at a
throwaway/dev environment, never production.
