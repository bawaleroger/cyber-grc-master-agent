from pathlib import Path
def classify_document(n,t):
 l=n.lower()
 return 'TDR' if 'tdr' in l else 'DAO' if 'dao' in l else 'AUTRE'
def ensure_folder_structure(b,c):
 p=b/'data'/c
 p.mkdir(parents=True,exist_ok=True)
 return p
