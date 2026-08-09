import json, uuid
from pathlib import Path
BASE=Path(__file__).parent.parent/"data"/"knowledge_base.json"
def load_kb():
 if BASE.exists():
  try: return json.loads(BASE.read_text())
  except: pass
 return {"documents":[],"classifications":{}}
def save_kb(kb):
 BASE.parent.mkdir(parents=True, exist_ok=True)
 BASE.write_text(json.dumps(kb, indent=2, ensure_ascii=False))
def add_document(entry):
 kb=load_kb(); entry["id"]=str(uuid.uuid4()); kb["documents"].append(entry); kb["classifications"][entry["classification"]]=kb["classifications"].get(entry["classification"],0)+1; save_kb(kb); return entry
def list_documents():
 return load_kb().get("documents",[])
