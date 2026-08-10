
import sqlite3, os, json, hashlib, datetime
DB_PATH = "data/cyber_grc.db"
def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS documents (id TEXT PRIMARY KEY, filename TEXT, type TEXT, norme TEXT, content TEXT, hash TEXT, date_ingest TEXT, client TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS tdr (id TEXT PRIMARY KEY, client TEXT, cabinet TEXT, objectif TEXT, perimetre TEXT, secteur TEXT, normes TEXT, livrables TEXT, contraintes TEXT, raw_text TEXT, date TEXT)""")
    conn.commit()
    conn.close()
def save_document(filename, content, doc_type, norme, client="GEN"):
    init_db()
    doc_id = hashlib.sha256((filename+content[:500]).encode()).hexdigest()[:16]
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO documents VALUES (?,?,?,?,?,?,?,?)",(doc_id, filename, doc_type, norme, content, hashlib.sha256(content.encode()).hexdigest(), datetime.datetime.now().isoformat(), client))
    conn.commit()
    conn.close()
    try:
        os.makedirs("data/kb", exist_ok=True)
        open(f"data/kb/{doc_id}_{filename}.txt","w",encoding="utf-8").write(content[:10000])
    except: pass
    return doc_id
def get_all_docs():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT filename, type, norme, date_ingest, client, length(content) FROM documents ORDER BY date_ingest DESC")
    rows = c.fetchall()
    conn.close()
    return rows
def get_kb_context(limit_chars=15000):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT content FROM documents ORDER BY date_ingest DESC")
    texts = c.fetchall()
    conn.close()
    ctx = ""
    for t in texts:
        ctx += t[0][:2000] + "\n---\n"
        if len(ctx) > limit_chars: break
    return ctx
def save_tdr(client, cabinet, tdr_dict, raw_text):
    init_db()
    tid = hashlib.sha256((client+raw_text[:200]).encode()).hexdigest()[:12]
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO tdr VALUES (?,?,?,?,?,?,?,?,?,?,?)",(tid, client, cabinet, tdr_dict.get('objectif',''), tdr_dict.get('perimetre',''), tdr_dict.get('secteur',''), json.dumps(tdr_dict.get('normes',[])), json.dumps(tdr_dict.get('livrables',[])), tdr_dict.get('contraintes',''), raw_text, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return tid
