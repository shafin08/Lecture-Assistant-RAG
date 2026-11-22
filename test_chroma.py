from app.rag.embedder import get_vectordb
import requests

BASE = "http://localhost:8000"


vs = get_vectordb()

data = vs.get()


print(f"Total chunks: {len(data["ids"])}")

print("\nSample data:")


