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



def search_vectordb(query: str, n_results: int = 3):
    """Søg i de interne guides og returnér de mest relevante afsnit.
    Brug den ved spørgsmål om, hvordan man gør noget i CRM, eller når noget ikke virker.

    Args:
        query: Kort søgetekst om emnet, fx "meld fraflytning" eller "CRM virker ikke".
        n_results: Antal afsnit der returneres.
    """
    vector = model.encode("query: " + query)
    result = collection.query(query_embeddings=[vector.tolist()], n_results=n_results)
    return [{"file": m["file"], "text": d} for m, d in zip(result["metadatas"][0], result["documents"][0])]



if __name__ == "__main__":
    build_vectordb(["./tester"])