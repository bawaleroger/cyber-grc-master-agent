
import sqlite3, os, json, hashlib, datetime
from pathlib import Path
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
KB_DIR = DATA_DIR / "kb"
DB_PATH = DATA_DIR / "cyber_grc.db"

def init_db():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    KB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS documents (id TEXT PRIMARY KEY, filename TEXT, type TEXT, norme TEXT, content TEXT, hash TEXT, date_ingest TEXT, client TEXT, is_kb INTEGER DEFAULT 0)""")
    c.execute("""CREATE TABLE IF NOT EXISTS tdr (id TEXT PRIMARY KEY, client TEXT, cabinet TEXT, objectif TEXT, perimetre TEXT, secteur TEXT, normes TEXT, livrables TEXT, contraintes TEXT, raw_text TEXT, date TEXT)""")
    try:
        c.execute("SELECT is_kb FROM documents LIMIT 1")
    except:
        try: c.execute("ALTER TABLE documents ADD COLUMN is_kb INTEGER DEFAULT 0")
        except: pass
    conn.commit()
    conn.close()
    return str(DB_PATH)

def save_document(filename, content, doc_type, norme, client="GEN", is_kb=False):
    db = init_db()
    doc_id = hashlib.sha256((filename+content[:500]).encode()).hexdigest()[:16]
    conn = sqlite3.connect(db)
    c = conn.cursor()
    content_hash = hashlib.sha256(content.encode()).hexdigest()
    c.execute("SELECT id FROM documents WHERE hash=?", (content_hash,))
    if c.fetchone():
        conn.close()
        return doc_id
    c.execute("INSERT OR REPLACE INTO documents VALUES (?,?,?,?,?,?,?,?,?)",
              (doc_id, filename, doc_type, norme, content, content_hash, datetime.datetime.now().isoformat(), client, 1 if is_kb else 0))
    conn.commit()
    conn.close()
    try:
        safe = "".join([c for c in filename if c.isalnum() or c in "._-"])[:50]
        (KB_DIR / f"{doc_id}_{safe}.txt").write_text(content[:20000], encoding="utf-8", errors="ignore")
    except: pass
    return doc_id

def get_all_docs():
    db = init_db()
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("SELECT filename, type, norme, date_ingest, client, length(content), is_kb FROM documents ORDER BY date_ingest DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def get_kb_only():
    db = init_db()
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("SELECT filename, type, norme, date_ingest, client FROM documents WHERE is_kb=1 ORDER BY date_ingest DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def get_kb_context(limit_chars=25000):
    db = init_db()
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("SELECT content, filename FROM documents ORDER BY is_kb DESC, date_ingest DESC")
    texts = c.fetchall()
    conn.close()
    if not texts:
        try:
            ctx=""
            for f in KB_DIR.glob("*.txt"):
                ctx+= f.read_text(encoding="utf-8", errors="ignore")[:2000] + "\n---\n"
                if len(ctx)>limit_chars: break
            return ctx
        except: return ""
    ctx=""
    for content, fname in texts:
        ctx+= f"\n[DOC:{fname}]\n" + content[:2500] + "\n---\n"
        if len(ctx)>limit_chars: break
    return ctx

def save_tdr(client, cabinet, tdr_dict, raw_text):
    db = init_db()
    tid = hashlib.sha256((client+raw_text[:200]).encode()).hexdigest()[:12]
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO tdr VALUES (?,?,?,?,?,?,?,?,?,?,?)",
              (tid, client, cabinet, tdr_dict.get('objectif',''), tdr_dict.get('perimetre',''), tdr_dict.get('secteur',''), json.dumps(tdr_dict.get('normes',[])), json.dumps(tdr_dict.get('livrables',[])), tdr_dict.get('contraintes',''), raw_text, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return tid

def get_latest_tdr():
    db = init_db()
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("SELECT client, cabinet, objectif, perimetre, secteur, normes, livrables, contraintes, raw_text, date FROM tdr ORDER BY date DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    if not row: return None
    client,cabinet,objectif,perimetre,secteur,normes,livrables,contraintes,raw_text,date = row
    try: normes=json.loads(normes)
    except: normes=[]
    try: livrables=json.loads(livrables)
    except: livrables=[]
    return {"client":client,"cabinet":cabinet,"tdr_dict":{"objectif":objectif,"perimetre":perimetre,"secteur":secteur,"normes":normes,"livrables":livrables,"contraintes":contraintes},"raw_text":raw_text,"date":date}

def clear_all():
    db = init_db()
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("DELETE FROM documents")
    c.execute("DELETE FROM tdr")
    conn.commit()
    conn.close()
    try:
        for f in KB_DIR.glob("*.txt"): f.unlink()
    except: pass
