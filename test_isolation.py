from app.rag.embedder import get_vectordb
from collections import Counter

vs = get_vectordb()

data = vs.get(where={
    "$and": [{"user_id":1},
             {"conversation_id": 4}

]}
,include=["embeddings", "documents", "metadatas"])

print(f"Total chunks: {len(data['ids'])}")


print("\nSample data:")
for i in range(len(data['ids'])):
    print(f"Length: {len(data['embeddings'][i])}")
    print(f"Text: {data['documents'][i]}")
    print(f"Metadata: {data['metadatas'][i]}")
    print(f"Embeddings: {data['embeddings'][i][:10]}")
    print("-----")



