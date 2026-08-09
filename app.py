
import streamlit as st
import os
from pathlib import Path
from core.classifier import classify_document, ensure_folder_structure
from core.knowledge_base import add_document, list_documents, search_kb, load_kb
from core.api_manager import add_api, list_apis
from core.agent import build_system_prompt
from core.rag import ingest_document_to_chroma, query_chroma
import pypdf

BASE = Path(__file__).parent
st.set_page_config(page_title="Cyber-GRC Master Agent V6 META LLAMA", page_icon="🛡️", layout="wide")

# --- CLES API ---
try:
    META_KEY = st.secrets["META_API_KEY"]
except:
    META_KEY = os.getenv("META_API_KEY", "")

try:
    GROQ_KEY = st.secrets.get("GROQ_API_KEY", "")
except:
    GROQ_KEY = os.getenv("GROQ_API_KEY", "")

st.markdown('<h1 style="color:#0B1D3A">🛡️ CYBER-GRC MASTER AGENT V6 - META LLAMA 4</h1>', unsafe_allow_html=True)
st.caption("100% Gratuit - Propulsé par Meta Llama API (api.llama.com) + RAG + KB JSON + ISO 42001")

with st.sidebar:
    st.header("⚙️ Configuration")
    firm = st.text_input("NOM DU CABINET", "CYBER-GRC CONSULTING")
    client = st.text_input("NOM DU CLIENT", "CLIENT UEMOA")
    mode_ci = st.checkbox("Activer RGSSI-CI (Côte d'Ivoire)")
    st.divider()
    st.success("✅ Meta Llama API = Gratuit")
    if META_KEY:
        st.caption(f"Clé Meta: {META_KEY[:10]}... OK")
    else:
        st.warning("Ajoute META_API_KEY dans Secrets")
    kb = load_kb()
    st.metric("Docs classés", len(kb.get("documents", [])))

tab1, tab2, tab3 = st.tabs(["📄 Dépôt & Classification Auto", "🧠 Agent Chat META LLAMA", "📂 Explorateur"])

with tab1:
    st.subheader("Dépose ton TDR / DAO / Offre - Classement auto + RAG")
    uploaded = st.file_uploader("PDF, DOCX, XLSX, PPTX, TXT, MD", accept_multiple_files=True, type=["pdf","docx","xlsx","pptx","txt","md"], key="up_v6")
    if uploaded:
        for file in uploaded:
            text_snippet = file.name
            full_text = ""
            try:
                if file.name.lower().endswith(".pdf"):
                    file.seek(0)
                    reader = pypdf.PdfReader(file)
                    full_text = "\n".join([p.extract_text() or "" for p in reader.pages[:15]])
                    text_snippet += " " + full_text[:1500]
            except Exception as e:
                st.warning(f"PDF: {e}")
            classification = classify_document(file.name, text_snippet)
            target_folder = ensure_folder_structure(BASE, classification)
            file_path = target_folder / file.name
            with open(file_path, "wb") as f:
                file.seek(0)
                f.write(file.read())
            entry = {"filename": file.name, "classification": classification, "path": str(file_path.relative_to(BASE)), "size": file.size, "summary": text_snippet[:500], "firm": firm, "client": client}
            add_document(entry)
            try:
                if full_text:
                    ingest_document_to_chroma(file.name, full_text, classification)
            except:
                pass
            st.success(f"✅ {file.name} -> {classification} -> RAG indexé")

with tab2:
    st.subheader("Chat Agent - META LLAMA 4 Maverick (Gratuit)")
    kb = load_kb()
    context = f"Firm: {firm} | Client: {client} | Docs: {len(kb['documents'])} | Classif: {list(kb['classifications'].keys())} | Mode CI: {mode_ci}"
    if "messages" not in st.session_state:
        st.session_state.messages = []
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
    user_prompt = st.chat_input("Ex: Analyse ce TDR, génère offre technique XOF avec ISO 42001, mapping ISO 42001 obligatoire...")
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
            if not META_KEY:
                st.error("Ajoute META_API_KEY dans Streamlit Secrets: Manage app -> Settings -> Secrets -> META_API_KEY = 'ta clé'")
                answer = "**[MODE SANS CLÉ]** Ajoute ta clé Meta dans Secrets pour activer Llama 4"
                st.markdown(answer)
            else:
                try:
                    from openai import OpenAI
                    # META LLAMA API est compatible OpenAI
                    client = OpenAI(base_url="https://api.llama.com/compat/v1", api_key=META_KEY)
                    # Modèle Llama 4 Maverick - le plus puissant de Meta
                    resp = client.chat.completions.create(
                        model="Llama-4-Maverick-17B-128E-Instruct-FP8",
                        messages=[{"role":"system","content": full_system}, *st.session_state.messages],
                        temperature=0.2
                    )
                    answer = resp.choices[0].message.content
                except Exception as e:
                    # fallback essayer ancien nom modèle
                    try:
                        client = OpenAI(base_url="https://api.llama.com/compat/v1", api_key=META_KEY)
                        resp = client.chat.completions.create(
                            model="Llama-3.3-70B-Instruct",
                            messages=[{"role":"system","content": full_system}, *st.session_state.messages],
                            temperature=0.2
                        )
                        answer = resp.choices[0].message.content
                    except Exception as e2:
                        answer = f"Erreur Meta Llama API: {e} / {e2}\n\nVérifie ta clé sur dev.meta.ai -> API keys"
                st.markdown(answer)
            st.session_state.messages.append({"role":"assistant","content": answer})

with tab3:
    docs = list_documents()
    if docs:
        st.dataframe([{"filename": d["filename"], "class": d["classification"]} for d in docs])
        for d in docs:
            p = BASE / d["path"]
            if p.exists():
                st.download_button(f"Télécharger {d['filename']}", data=open(p,"rb").read(), file_name=d["filename"], key=f"dl_{d.get('id', d['filename'])}")
