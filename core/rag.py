
import os, uuid
from pathlib import Path
try:
    import chromadb
    CHROMA_AVAILABLE = True
except:
    CHROMA_AVAILABLE = False
BASE = Path(__file__).parent.parent
CHROMA_PATH = BASE / ".chroma"
def get_collection():
    if not CHROMA_AVAILABLE:
        return None
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    coll = client.get_or_create_collection("cyber_grc_docs")
    return coll
def ingest_document_to_chroma(filename: str, text: str, classification: str):
    coll = get_collection()
    if not coll: return
    chunks = [text[i:i+1000] for i in range(0, len(text), 800)]
    for idx, chunk in enumerate(chunks):
        coll.add(documents=[chunk], metadatas=[{"filename": filename, "classification": classification, "chunk": idx}], ids=[f"{filename}_{idx}_{uuid.uuid4()}"])
def query_chroma(query: str, n_results=5):
    coll = get_collection()
    if not coll: return []
    res = coll.query(query_texts=[query], n_results=n_results)
    out=[]
    if res and res.get("documents"):
        for doc, meta in zip(res["documents"][0], res["metadatas"][0]):
            out.append({"document": doc, "metadata": meta})
    return out
