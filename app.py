
import streamlit as st
import os, json
from pathlib import Path
from datetime import datetime
from core.classifier import classify_document, ensure_folder_structure
from core.knowledge_base import add_document, list_documents, search_kb, load_kb, save_kb
from core.api_manager import add_api, list_apis
from core.agent import build_system_prompt
from core.rag import ingest_document_to_chroma, query_chroma
import pypdf

BASE = Path(__file__).parent
st.set_page_config(page_title="Cyber-GRC Master Agent V5.3", page_icon="🛡️", layout="wide")

try:
    OPENAI_KEY = st.secrets["OPENAI_API_KEY"]
except:
    OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")

st.markdown('<h1 style="color:#0B1D3A">🛡️ CYBER-GRC MASTER AGENT V5.3 FIXED</h1>', unsafe_allow_html=True)
st.caption("V5 sans CI + ISO 42001 partout + RAG ChromaDB + KB JSON")

with st.sidebar:
    st.header("⚙️ Configuration")
    firm = st.text_input("NOM DU CABINET", "CYBER-GRC CONSULTING")
    client = st.text_input("NOM DU CLIENT", "CLIENT UEMOA")
    mode_ci = st.checkbox("Activer RGSSI-CI (mission Côte d'Ivoire)")
    st.divider()
    st.subheader("🔌 APIs Liées")
    with st.form("api_form"):
        api_name = st.text_input("Nom API")
        api_url = st.text_input("Base URL")
        api_key = st.text_input("API Key", type="password")
        api_desc = st.text_input("Description")
        if st.form_submit_button("Lier API"):
            if api_name and api_url:
                add_api(api_name, api_url, api_key, api_desc)
                st.success(f"API {api_name} liée")
    for api in list_apis():
        st.caption(f"🔗 {api['name']} - {api['base_url']}")
    st.divider()
    kb = load_kb()
    st.metric("Docs classés", len(kb.get("documents", [])))
    if not OPENAI_KEY:
        st.warning("⚠️ Ajoute OPENAI_API_KEY dans Secrets pour mode PROD")

tab1, tab2, tab3, tab4 = st.tabs(["📄 Dépôt & Classification Auto", "🧠 Agent Chat & Missions", "📂 Explorateur Documents", "🚀 Deploy GitHub"])

with tab1:
    st.subheader("Dépose tes documents - Classement auto + RAG")
    uploaded = st.file_uploader("TDR, DAO, Offres, Rapports, Cours...", accept_multiple_files=True, type=["pdf","docx","xlsx","pptx","txt","md"], key="uploader_main")
    if uploaded:
        for file in uploaded:
            text_snippet = file.name
            full_text = ""
            try:
                if file.name.lower().endswith(".pdf"):
                    file.seek(0)
                    reader = pypdf.PdfReader(file)
                    full_text = "\n".join([p.extract_text() or "" for p in reader.pages[:10]])
                    text_snippet += " " + full_text[:1000]
            except Exception as e:
                st.warning(f"PDF read: {e}")
            classification = classify_document(file.name, text_snippet)
            target_folder = ensure_folder_structure(BASE, classification)
            file_path = target_folder / file.name
            with open(file_path, "wb") as f:
                file.seek(0)
                f.write(file.read())
            entry = {"filename": file.name, "classification": classification, "path": str(file_path.relative_to(BASE)), "size": file.size, "summary": text_snippet[:500], "firm": firm, "client": client}
            doc_entry = add_document(entry)
            try:
                if full_text:
                    ingest_document_to_chroma(file.name, full_text, classification)
            except Exception as e:
                st.warning(f"Chroma: {e}")
            st.success(f"✅ {file.name} -> {classification}")

with tab2:
    st.subheader("Chat Agent - PROD avec RAG + KB")
    kb = load_kb()
    context = f"Firm: {firm} | Client: {client} | Docs: {len(kb['documents'])} | Classif: {list(kb['classifications'].keys())} | Mode CI: {mode_ci}"
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": build_system_prompt(context)}]
    for m in st.session_state.messages[1:]:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
    user_prompt = st.chat_input("Ex: Analyse TDR, génère offre technique XOF avec ISO 42001...")
    if user_prompt:
        try:
            rag_hits = query_chroma(user_prompt, n_results=5)
            rag_context = "\n".join([f"[{h['metadata']['classification']}] {h['metadata']['filename']}: {h['document'][:400]}" for h in rag_hits])
        except:
            rag_context = ""
        full_system = build_system_prompt(context + "\nRAG:\n" + rag_context)
        st.session_state.messages.append({"role":"user","content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)
        with st.chat_message("assistant"):
            if OPENAI_KEY:
                try:
                    from openai import OpenAI
                    client_oai = OpenAI(api_key=OPENAI_KEY)
                    resp = client_oai.chat.completions.create(model="gpt-4o", messages=[{"role":"system","content": full_system}] + st.session_state.messages[1:], temperature=0.2)
                    answer = resp.choices[0].message.content
                except Exception as e:
                    answer = f"Erreur OpenAI: {e}"
            else:
                answer = f"**[MODE SIMULÉ]** Mission {client} | RAG: {rag_context[:300]}...\n\n[📄 OFFRE TECHNIQUE] [💰 FINANCIÈRE XOF] [📘 DAO] [🚀 PLAN AUDIT ISO 42001] [🏅 CERTIF]"
            st.markdown(answer)
            st.session_state.messages.append({"role":"assistant","content": answer})

with tab3:
    st.subheader("Knowledge Base JSON - Toujours disponible")
    docs = list_documents()
    if docs:
        st.dataframe([{"filename": d["filename"], "class": d["classification"], "size": d.get("size",0)} for d in docs])
        for d in docs:
            path = BASE / d["path"]
            if path.exists():
                doc_id = d.get("id", d["filename"])
                # FIX: no nested quotes in f-string
                label = f"Telecharger {d['filename']}"
                key = f"dl_{doc_id}"
                st.download_button(label, data=open(path,"rb").read(), file_name=d["filename"], key=key)
    else:
        st.info("Aucun doc. Va dans Dépôt & Classification Auto")
    search_q = st.text_input("Rechercher KB", key="search_kb_main")
    if search_q:
        for d in search_kb(search_q):
            st.json(d)

with tab4:
    st.markdown(Path(BASE / "DEPLOY_GUIDE.md").read_text(encoding="utf-8"))
