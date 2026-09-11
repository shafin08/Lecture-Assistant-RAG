# ============================================================
# tests/test_documents.py
# Upload, per-conversation scoping, deletion, validation.
# Uploads trigger real chunking + embedding → marked slow.
#
# NOTE: PDFs are NOT saved to disk in this app — text is
# extracted on upload and only the chunks land in ChromaDB.
# So these tests check the DB record + the chunks, never a file.
# ============================================================

import pytest
from tests.conftest import BIOLOGY_NOTES


@pytest.mark.slow
def test_upload(user, new_conversation, upload_pdf):
    cid = new_conversation(user)
    result = upload_pdf(user, cid, BIOLOGY_NOTES)
    assert "document" in result


@pytest.mark.slow
def test_upload_response_has_no_file_path(user, new_conversation, upload_pdf):
    """
    Since PDFs aren't stored on disk, the response should not expose
    a file_path. filename stays (needed for citations + the UI list).
    """
    cid = new_conversation(user)
    result = upload_pdf(user, cid, BIOLOGY_NOTES, filename="lecture.pdf")
    doc = result["document"]
    assert "file_path" not in doc          # no disk path leaked
    assert doc["filename"] == "lecture.pdf"  # filename still present


@pytest.mark.slow
def test_reject_non_pdf(user, new_conversation, client):
    cid = new_conversation(user)
    r = client.post(
        "/documents/upload",
        headers=user["headers"],
        files={"file": ("notes.txt", b"plain text", "text/plain")},
        data={"conversation_id": cid},
    )
    assert r.status_code == 400


@pytest.mark.slow
def test_documents_scoped_to_conversation(user, new_conversation, upload_pdf, client):
    """Each conversation lists only its own documents (Design B)."""
    conv_a = new_conversation(user)
    conv_b = new_conversation(user)

    upload_pdf(user, conv_a, BIOLOGY_NOTES, filename="a.pdf")
    upload_pdf(user, conv_b, BIOLOGY_NOTES, filename="b.pdf")

    docs_a = client.get("/documents", headers=user["headers"],
                        params={"conversation_id": conv_a}).json()
    names_a = [d["filename"] for d in docs_a]
    assert "a.pdf" in names_a and "b.pdf" not in names_a

    docs_b = client.get("/documents", headers=user["headers"],
                        params={"conversation_id": conv_b}).json()
    names_b = [d["filename"] for d in docs_b]
    assert "b.pdf" in names_b and "a.pdf" not in names_b


@pytest.mark.slow
def test_delete_document(user, new_conversation, upload_pdf, client):
    cid = new_conversation(user)
    doc_id = upload_pdf(user, cid, BIOLOGY_NOTES)["document"]["id"]

    assert client.delete(f"/documents/{doc_id}",
                         headers=user["headers"]).status_code == 200

    docs = client.get("/documents", headers=user["headers"],
                      params={"conversation_id": cid}).json()
    assert all(d["id"] != doc_id for d in docs)


@pytest.mark.slow
def test_cannot_upload_to_others_conversation(user, second_user,
                                              new_conversation, client):
    cid = new_conversation(user)
    from tests.conftest import make_pdf
    r = client.post(
        "/documents/upload",
        headers=second_user["headers"],
        files={"file": ("x.pdf", make_pdf(BIOLOGY_NOTES), "application/pdf")},
        data={"conversation_id": cid},
    )
    assert r.status_code in (403, 404)
