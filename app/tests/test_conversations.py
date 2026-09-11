# ============================================================
# tests/test_conversations.py
# Conversation CRUD, ownership, and history persistence.
# Fast — no API cost.
# ============================================================


def test_create(user, client):
    r = client.post("/conversation", headers=user["headers"])
    assert r.status_code == 200
    assert r.json()["title"] == "New Conversation"


def test_list(user, client):
    client.post("/conversation", headers=user["headers"])
    client.post("/conversation", headers=user["headers"])
    r = client.get("/conversation", headers=user["headers"])
    assert r.status_code == 200
    assert len(r.json()) >= 2


def test_get_detail_empty(user, client):
    cid = client.post("/conversation", headers=user["headers"]).json()["id"]
    r = client.get(f"/conversation/{cid}", headers=user["headers"])
    assert r.status_code == 200
    assert r.json()["messages"] == []


def test_rename(user, client):
    cid = client.post("/conversation", headers=user["headers"]).json()["id"]
    r = client.patch(f"/conversation/{cid}",
                     headers=user["headers"],
                     json={"title": "Biology"})
    assert r.status_code == 200
    assert r.json()["title"] == "Biology"


def test_delete(user, client):
    cid = client.post("/conversation", headers=user["headers"]).json()["id"]
    assert client.delete(f"/conversation/{cid}",
                         headers=user["headers"]).status_code == 200
    assert client.get(f"/conversation/{cid}",
                      headers=user["headers"]).status_code == 404


# ---- Ownership isolation ----

def test_cannot_read_others_conversation(user, second_user, client):
    cid = client.post("/conversation", headers=user["headers"]).json()["id"]
    r = client.get(f"/conversation/{cid}", headers=second_user["headers"])
    assert r.status_code in (403, 404)


def test_cannot_delete_others_conversation(user, second_user, client):
    cid = client.post("/conversation", headers=user["headers"]).json()["id"]
    r = client.delete(f"/conversation/{cid}", headers=second_user["headers"])
    assert r.status_code in (403, 404)
    # still there for the owner
    assert client.get(f"/conversation/{cid}",
                      headers=user["headers"]).status_code == 200
