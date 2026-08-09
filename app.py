import streamlit as st, os
from pathlib import Path
from core.classifier import classify_document, ensure_folder_structure
from core.knowledge_base import add_document, list_documents, load_kb
from core.agent import build_system_prompt
from core.rag import query_chroma, ingest_document_to_chroma
import pypdf
BASE=Path(__file__).parent
st.set_page_config(page_title="V7 FREE", page_icon="🛡️", layout="wide")
META=st.secrets.get("META_API_KEY","") if "META_API_KEY" in st.secrets else os.getenv("META_API_KEY","")
GROQ=st.secrets.get("GROQ_API_KEY","") if "GROQ_API_KEY" in st.secrets else os.getenv("GROQ_API_KEY","")
st.markdown('<h1>🛡️ CYBER-GRC V7 - FREE LLAMA</h1>')
st.caption("Groq Llama 3.3 70B gratuit + RAG + ISO 42001")
with st.sidebar:
    firm=st.text_input("CABINET","CYBER-GRC")
    client=st.text_input("CLIENT","UEMOA")
    if GROQ: st.success(f"Groq OK: {GROQ[:8]}...")
    else: st.error("Ajoute GROQ_API_KEY dans Secrets -> console.groq.com")
    if META and META.startswith("LLM_"): st.warning("Clé Meta invalide LLM_... est ID, pas secret. Recrée clé")
    kb=load_kb(); st.metric("Docs", len(kb.get("documents",[])))
def call_llm(sys,messages):
    from openai import OpenAI
    if GROQ:
        try:
            c=OpenAI(base_url="https://api.groq.com/openai/v1", api_key=GROQ)
            r=c.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"system","content":sys}]+messages, temperature=0.2, max_tokens=4000)
            return r.choices[0].message.content
        except Exception as e: return f"Erreur Groq: {e}\nVa sur console.groq.com recrée clé gsk_"
    return "Ajoute GROQ_API_KEY gratuit dans Secrets"
t1,t2,t3=st.tabs(["📄 Dépôt TDR","🧠 Chat FREE","📂 Docs"])
with t1:
    st.subheader("Dépose TDR ici")
    up=st.file_uploader("PDF", accept_multiple_files=True, type=["pdf","docx","xlsx"], key="up")
    if up:
        for file in up:
            full=""
            try:
                if file.name.lower().endswith(".pdf"):
                    file.seek(0); reader=pypdf.PdfReader(file); full="\n".join([p.extract_text() or "" for p in reader.pages[:15]])
            except: pass
            clas=classify_document(file.name, full[:1500])
            folder=ensure_folder_structure(BASE, clas)
            p=folder/file.name
            with open(p,"wb") as f: file.seek(0); f.write(file.read())
            add_document({"filename": file.name, "classification": clas, "path": str(p.relative_to(BASE)), "size": file.size})
            st.success(f"✅ {file.name} -> {clas}")
with t2:
    if "messages" not in st.session_state: st.session_state.messages=[]
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    prompt=st.chat_input("Analyse TDR, offre XOF ISO 42001...")
    if prompt:
        try: rag="\n".join([f"{h['metadata']['filename']}" for h in query_chroma(prompt,4)])
        except: rag=""
        kb=load_kb(); sys=build_system_prompt(f"Client {client} Docs {len(kb.get('documents',[]))} RAG {rag}")
        st.session_state.messages.append({"role":"user","content":prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Llama..."):
                ans=call_llm(sys, st.session_state.messages)
                st.markdown(ans)
        st.session_state.messages.append({"role":"assistant","content":ans})
with t3:
    docs=list_documents()
    for d in docs:
        pp=BASE/d["path"]
        if pp.exists(): st.download_button(f"{d['filename']}", data=open(pp,"rb").read(), file_name=d["filename"], key=f"dl_{d.get('id', d['filename'])}")
