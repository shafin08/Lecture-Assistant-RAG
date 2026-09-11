# ============================================================
# tests/conftest.py
# Shared fixtures for the whole test suite.
#
# Tests run the FastAPI app in-process via TestClient — no need
# to start the server separately. They use your REAL database and
# ChromaDB, so run against a dev/throwaway environment with a valid
# OPENAI_API_KEY, never production.
#
#   pytest -m "not slow"   # fast: auth, conversations, validation
#   pytest                 # everything, incl. RAG (needs API key)
# ============================================================

import io
import uuid
import pytest
from fastapi.testclient import TestClient

# ---- Adjust to your layout if different ----
from app.api.main import app
# --------------------------------------------


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


def _unique_email():
    return f"test_{uuid.uuid4().hex[:10]}@example.com"


# A strong, non-breached password so registration passes any
# strength / breach checks you added.
TEST_PASSWORD = "Study!Test9xQm2Vb"


@pytest.fixture
def user_factory(client):
    """Registers + logs in a fresh user, returns auth headers."""
    def _make_user():
        email = _unique_email()
        username = email.split("@")[0]  # a unique username derived from the email

        r = client.post("/auth/register",
                        json={"email": email, "username": username,
                              "password": TEST_PASSWORD})
        assert r.status_code == 200, f"register failed: {r.text}"

        r = client.post("/auth/login",
                        json={"email": email, "password": TEST_PASSWORD})
        assert r.status_code == 200, f"login failed: {r.text}"
        token = r.json()["access_token"]

        return {"email": email, "username": username,
                "headers": {"Authorization": f"Bearer {token}"}}

    return _make_user


@pytest.fixture
def user(user_factory):
    return user_factory()


@pytest.fixture
def second_user(user_factory):
    return user_factory()


# ============================================================
# PDF helper — builds a tiny real PDF in memory from given text.
# Requires: pip install reportlab
# ============================================================

def make_pdf(text: str) -> bytes:
    reportlab = pytest.importorskip("reportlab")
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    y = 750
    for line in text.split(". "):
        c.drawString(50, y, line[:90])
        y -= 15
        if y < 50:
            c.showPage()
            y = 750
    c.save()
    buffer.seek(0)
    return buffer.read()


@pytest.fixture
def make_pdf_fixture():
    return make_pdf


# ============================================================
# Higher-level helpers used across RAG tests
# ============================================================

@pytest.fixture
def new_conversation(client):
    def _new(user):
        return client.post("/conversation", headers=user["headers"]).json()["id"]
    return _new


@pytest.fixture
def upload_pdf(client):
    def _upload(user, conversation_id, text, filename="notes.pdf"):
        pdf = make_pdf(text)
        r = client.post(
            "/documents/upload",
            headers=user["headers"],
            files={"file": (filename, pdf, "application/pdf")},
            data={"conversation_id": conversation_id},
        )
        assert r.status_code == 200, f"upload failed: {r.text}"
        return r.json()
    return _upload


@pytest.fixture
def ask(client):
    def _ask(user, conversation_id, question):
        return client.post(
            "/chat",
            headers=user["headers"],
            json={"question": question, "conversation_id": conversation_id},
        )
    return _ask


# ============================================================
# Sample note content used by RAG tests
# ============================================================

BIOLOGY_NOTES = (
    "Mitochondria are the powerhouse of the cell. "
    "They generate ATP through cellular respiration. "
    "Chloroplasts carry out photosynthesis in plant cells. "
    "The nucleus stores the cell's DNA. "
) * 6

HISTORY_NOTES = (
    "The Roman Empire was founded in 27 BC by Augustus. "
    "Julius Caesar was assassinated in 44 BC. "
    "The Colosseum was completed in 80 AD. "
    "Rome later split into eastern and western empires. "
) * 6
