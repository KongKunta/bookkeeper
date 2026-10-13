from pathlib import Path
import chromadb
from docx import Document
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("intfloat/multilingual-e5-base")
db = chromadb.PersistentClient(path="./vectordb")
collection = db.get_or_create_collection("documents")


def chunk_text(text, size=768, overlap=100):
    return [text[i:i + size] for i in range(0, len(text), size - overlap)]


def build_vectordb(search_roots):
    for root in search_roots:
        for f in Path(root).rglob("*.docx"):
            if f.name.startswith("~$"):
                continue
            text = "\n".join(p.text for p in Document(f).paragraphs)
            chunks = chunk_text(text)
            vectors = model.encode(["passage: " + c for c in chunks])
            collection.upsert(
                ids=[f"{f}_{i}" for i in range(len(chunks))],
                documents=chunks,
                embeddings=vectors.tolist(),
                metadatas=[{"file": str(f)} for _ in chunks],
            )


if __name__ == "__main__":
    build_vectordb(["./tester"])