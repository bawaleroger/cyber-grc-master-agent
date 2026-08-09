
import json, os, uuid, datetime
from pathlib import Path
from typing import List, Dict

KB_PATH = Path(__file__).parent.parent / "data" / "knowledge_base.json"

def load_kb() -> Dict:
    if not KB_PATH.exists():
        return {"documents": [], "classifications": {}, "apis": [], "missions": []}
    with open(KB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_kb(kb: Dict):
    KB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(KB_PATH, "w", encoding="utf-8") as f:
        json.dump(kb, f, indent=2, ensure_ascii=False)

def add_document(entry: Dict):
    kb = load_kb()
    entry["id"] = str(uuid.uuid4())
    entry["added_at"] = datetime.datetime.now().isoformat()
    kb["documents"].append(entry)
    # classification bucket
    cat = entry.get("classification", "AUTRE")
    if cat not in kb["classifications"]:
        kb["classifications"][cat] = []
    kb["classifications"][cat].append(entry["id"])
    save_kb(kb)
    return entry

def list_documents(filter_cat=None):
    kb = load_kb()
    if filter_cat:
        ids = set(kb["classifications"].get(filter_cat, []))
        return [d for d in kb["documents"] if d["id"] in ids]
    return kb["documents"]

def search_kb(query: str) -> List[Dict]:
    kb = load_kb()
    q = query.lower()
    return [d for d in kb["documents"] if q in d.get("filename","").lower() or q in d.get("summary","").lower() or q in d.get("classification","").lower()]
