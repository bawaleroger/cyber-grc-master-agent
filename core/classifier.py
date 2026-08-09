from pathlib import Path
def classify_document(name, text):
 n=(name+" "+(text or "")).lower()
 if "tdr" in n or "terme" in n: return "TDR"
 if "dao" in n: return "DAO"
 if "offre" in n: return "OFFRE"
 return "AUTRE"
def ensure_folder_structure(b,c):
 p=b/"data"/c
 p.mkdir(parents=True, exist_ok=True)
 return p
