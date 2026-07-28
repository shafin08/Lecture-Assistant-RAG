from app.rag.embedder import get_vectordb
from collections import Counter

vs = get_vectordb()

data = vs.get(where={"user_id":"3"})

print(f"Total chunks: {len(data['ids'])}")


print("\nSample data:")
for i in range(len(data['ids'])):
    print(f"Text: {data['documents'][i]}")
    print(f"Metadata: {data['metadatas'][i]}")
    print("-----")



