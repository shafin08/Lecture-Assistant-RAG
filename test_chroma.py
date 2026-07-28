from app.rag.embedder import get_vectordb


vs = get_vectordb()

data = vs.get()


print(f"Total chunks: {len(data["ids"])}")
"""
print("\nSample data:")
for i in range(3):
    print(f"Text: {data['documents'][i]}")
    print(f"Metadata: {data['metadatas'][i]}")
"""