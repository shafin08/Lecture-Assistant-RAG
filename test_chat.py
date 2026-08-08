# test_chat_flow.py
# Tests the complete chat endpoint — history, titles, persistence

import requests

BASE = "http://localhost:8000"

# ============================================================
# Setup — login to get a token
# ============================================================
login = requests.post(f"{BASE}/auth/login", json={
    "email": "test1@example.com",
    "password": "test2"
})
token = login.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("✅ Logged in")


# ============================================================
# Test 1 — Create a conversation
# ============================================================
print("\n" + "=" * 50)
print("TEST 1 — Create conversation")
print("=" * 50)
'''
conv = requests.post(f"{BASE}/conversation", headers=headers)

print(f"Created conversation {conversation_id}")
print(f"Initial title: {conv.json()['title']}")  # should be "New Conversation"
'''

conversation_id = 4
# ============================================================
# NOTE: upload a document to this conversation first!
# Either do it manually via /docs, or add an upload call here.
# The chat needs documents to answer from.
# ============================================================
'''
input(f"\n⏸️  Upload a PDF to conversation {conversation_id} via /docs, "
      f"then press Enter to continue...")
'''


# ============================================================
# Test 2 — Ask the first question
# ============================================================
print("\n" + "=" * 50)
print("TEST 2 — First question")
print("=" * 50)

q1 = requests.post(f"{BASE}/chat", headers=headers, json={
    "query": "What is the main topic here?",
    "conversation_id": conversation_id
})
print(f"Answer: {q1.json()['answer'][:200]}...")



# ============================================================
# Test 3 — Title auto-generated
# ============================================================
print("\n" + "=" * 50)
print("TEST 3 — Title auto-generation")
print("=" * 50)

convs = requests.get(f"{BASE}/conversation", headers=headers)
this_conv = next(c for c in convs.json() if c["id"] == conversation_id)
print(f"Title after first question: {this_conv['title']}")
if this_conv["title"] != "New Conversation":
    print("✅ PASS — title auto-generated from first question")
else:
    print("❌ FAIL — title still default")


# ============================================================
# Test 4 — Follow-up question (tests history/context)
# ============================================================
print("\n" + "=" * 50)
print("TEST 4 — Follow-up with pronoun (context test)")
print("=" * 50)

q2 = requests.post(f"{BASE}/chat", headers=headers, json={
    "query": "Can you explain that in simpler terms?",
    "conversation_id": conversation_id
})
print(f"Answer: {q2.json()['answer'][:200]}...")
print("✅ If this answer relates to the previous topic, history works")


# ============================================================
# Test 5 — Load conversation with all messages
# ============================================================
print("\n" + "=" * 50)
print("TEST 5 — Load full conversation")
print("=" * 50)

detail = requests.get(f"{BASE}/conversation/{conversation_id}", headers=headers)
messages = detail.json()["messages"]
print(f"Total messages: {len(messages)}")  # should be 4 (2 Q, 2 A)
for m in messages:
    print(f"  [{m['role']}] {m['content'][:60]}...")

if len(messages) == 4:
    print("✅ PASS — all 4 messages saved in order")
else:
    print(f"❌ Expected 4 messages, got {len(messages)}")


# ============================================================
# Test 6 — Rename
# ============================================================
print("\n" + "=" * 50)
print("TEST 6 — Rename conversation")
print("=" * 50)

print(f"Rename using conversation_id={conversation_id}, headers={headers}")

rename = requests.patch(
    f"{BASE}/conversation/{conversation_id}",
    headers=headers,
    json={"title": "My Test Chat"}
)
if rename.status_code == 200:
    print(f"New title: {rename.json()['title']}")
else:
    print(f"Rename failed — {rename.status_code}: {rename.json()}")


# ============================================================
# Test 7 — Ownership (a fake conversation id)
# ============================================================
print("\n" + "=" * 50)
print("TEST 7 — Access nonexistent conversation")
print("=" * 50)

fake = requests.get(f"{BASE}/conversation/999999", headers=headers)
print(f"Status: {fake.status_code}")
if fake.status_code == 404:
    print("✅ PASS — returns 404 for conversation that isn't yours")


# ============================================================
# Test 8 — Delete (cleanup)
# ============================================================
print("\n" + "=" * 50)
print("TEST 8 — Delete conversation")
print("=" * 50)

delete = requests.delete(
    f"{BASE}/conversation/{conversation_id}",
    headers=headers
)
print(f"Status: {delete.status_code}")

# Confirm it's gone
check = requests.get(f"{BASE}/conversation/{conversation_id}", headers=headers)
if check.status_code == 404:
    print("✅ PASS — conversation deleted")