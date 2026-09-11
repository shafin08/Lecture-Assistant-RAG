# ============================================================
# tests/test_rag.py
# End-to-end RAG behavior THROUGH THE API:
# retrieval quality, isolation, no-hallucination, history.
# Runs the full pipeline → marked slow (needs OPENAI_API_KEY).
# ============================================================

import pytest
from tests.conftest import BIOLOGY_NOTES, HISTORY_NOTES


# ---- Retrieval quality ----

@pytest.mark.slow
def test_answer_from_notes(user, new_conversation, upload_pdf, ask):
    cid = new_conversation(user)
    upload_pdf(user, cid, BIOLOGY_NOTES)

    r = ask(user, cid, "What do mitochondria do?")
    assert r.status_code == 200
    answer = r.json()["answer"].lower()
    assert "atp" in answer or "energy" in answer or "respiration" in answer


@pytest.mark.slow
def test_answer_cites_source(user, new_conversation, upload_pdf, ask):
    cid = new_conversation(user)
    upload_pdf(user, cid, BIOLOGY_NOTES, filename="biology.pdf")

    r = ask(user, cid, "What are mitochondria?")
    sources = r.json().get("sources", [])
    names = [s.get("filename", s.get("title", "")).lower() for s in sources]
    assert any("biology" in n for n in names)


# ---- No hallucination ----

@pytest.mark.slow
def test_no_hallucination(user, new_conversation, upload_pdf, ask):
    """Question outside the notes must not get an outside-knowledge answer."""
    cid = new_conversation(user)
    upload_pdf(user, cid, "This lecture is only about plant photosynthesis. " * 10)

    r = ask(user, cid, "What is the capital of France?")
    answer = r.json()["answer"].lower()
    assert "paris" not in answer


@pytest.mark.slow
def test_empty_conversation_graceful(user, new_conversation, ask):
    """Asking in a chat with no documents should not crash."""
    cid = new_conversation(user)
    r = ask(user, cid, "What's in my notes?")
    assert r.status_code == 200
    assert len(r.json()["answer"]) > 0


# ---- Isolation (the security-critical tests) ----

@pytest.mark.slow
def test_cross_chat_isolation(user, new_conversation, upload_pdf, ask):
    """
    Same user, two chats. A history question asked in the biology
    chat must NOT be answered from the history chat's notes.
    """
    bio = new_conversation(user)
    hist = new_conversation(user)
    upload_pdf(user, bio, BIOLOGY_NOTES, filename="bio.pdf")
    upload_pdf(user, hist, HISTORY_NOTES, filename="history.pdf")

    r = ask(user, bio, "When was the Roman Empire founded?")
    answer = r.json()["answer"].lower()
    # Should not surface the history notes' specifics
    assert "augustus" not in answer
    assert "27 bc" not in answer


@pytest.mark.slow
def test_cross_user_isolation(user, second_user, new_conversation, upload_pdf, ask):
    """
    User A uploads notes. User B, asking the same question in their
    own empty chat, must not get A's content.
    """
    a_conv = new_conversation(user)
    upload_pdf(user, a_conv, BIOLOGY_NOTES, filename="a_biology.pdf")

    b_conv = new_conversation(second_user)
    r = ask(second_user, b_conv, "What are mitochondria?")
    # B has no notes → should be a graceful "not found", not A's answer
    answer = r.json()["answer"].lower()
    assert "powerhouse" not in answer or "couldn't find" in answer or "don't" in answer


# ---- Conversation history / context ----

@pytest.mark.slow
def test_followup_uses_history(user, new_conversation, upload_pdf, ask):
    """A pronoun follow-up should resolve using prior turns."""
    cid = new_conversation(user)
    upload_pdf(user, cid, BIOLOGY_NOTES)

    ask(user, cid, "What are mitochondria?")
    r = ask(user, cid, "What do they produce?")  # "they" needs history
    assert r.status_code == 200
    answer = r.json()["answer"].lower()
    assert "atp" in answer or "energy" in answer


@pytest.mark.slow
def test_messages_persist_and_order(user, new_conversation, upload_pdf, ask, client):
    cid = new_conversation(user)
    upload_pdf(user, cid, BIOLOGY_NOTES)

    ask(user, cid, "What are mitochondria?")

    detail = client.get(f"/conversations/{cid}", headers=user["headers"]).json()
    roles = [m["role"] for m in detail["messages"]]
    assert roles[0] == "user"           # first message is the question
    assert "assistant" in roles         # answer saved too


@pytest.mark.slow
def test_title_auto_generated(user, new_conversation, upload_pdf, ask, client):
    cid = new_conversation(user)
    upload_pdf(user, cid, BIOLOGY_NOTES)

    ask(user, cid, "Explain what mitochondria do in the cell")

    convs = client.get("/conversations", headers=user["headers"]).json()
    this = next(c for c in convs if c["id"] == cid)
    assert this["title"] != "New Conversation"


# ---- Validation ----

def test_empty_question_rejected(user, new_conversation, client):
    cid = new_conversation(user)
    r = client.post("/chat", headers=user["headers"],
                    json={"query": "   ", "conversation_id": cid})
    assert r.status_code == 400
