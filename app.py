import streamlit as st, os
from pathlib import Path
from core.classifier import classify_document, ensure_folder_structure
from core.knowledge_base import add_document, list_documents, load_kb
from core.agent import build_system_prompt
import pypdf

BASE = Path(__file__).parent
st.set_page_config(page_title="Cyber-GRC V8 OpenRouter", page_icon="🛡️", layout="wide")

OPENROUTER_KEY = st.secrets.get("OPENROUTER_API_KEY","") or os.getenv("OPENROUTER_API_KEY","")

st.markdown('<h1 style="color:#0B1D3A">🛡️ CYBER-GRC MASTER AGENT V8 - OPENROUTER</h1>', unsafe_allow_html=True)
st.caption("OpenRouter uniquement - Llama 4 Maverick FREE + RAG + ISO 42001 + XOF")

with st.sidebar:
    st.header("Configuration")
    firm = st.text_input("CABINET", "CYBER-GRC")
    client = st.text_input("CLIENT", "UEMOA")
    mode_ci = st.checkbox("RGSSI-CI (Côte d'Ivoire)")
    st.divider()
    if OPENROUTER_KEY:
        st.success(f"OpenRouter OK: {OPENROUTER_KEY[:10]}...{OPENROUTER_KEY[-4:]}")
    else:
        st.error("Ajoute OPENROUTER_API_KEY dans Secrets")
        st.info("openrouter.ai -> API Keys -> Create -> copie sk-or-v1-...")
    kb = load_kb()
    st.metric("Docs", len(kb.get("documents",[])))
    st.divider()
    model = st.selectbox("Modèle", [
        "meta-llama/llama-4-maverick:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "meta-llama/llama-4-scout:free",
        "google/gemini-2.0-flash-exp:free",
        "deepseek/deepseek-r1:free",
        "qwen/qwen-2.5-72b-instruct:free"
    ])

def call_llm(system_prompt, messages, model_name):
    if not OPENROUTER_KEY:
        return "❌ Ajoute OPENROUTER_API_KEY dans Streamlit Secrets (Manage app -> Settings -> Secrets)"
    try:
        from openai import OpenAI
        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_KEY)
        resp = client.chat.completions.create(
            model=model_name,
            messages=[{"role":"system","content": system_prompt}] + messages,
            temperature=0.2,
            max_tokens=5000,
            extra_headers={"HTTP-Referer": "https://cyber-grc.streamlit.app", "X-Title": "Cyber-GRC V8"}
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Erreur OpenRouter: {e}\nVerifie ta cle sk-or-v1-... dans Secrets et que tu as du credit gratuit sur openrouter.ai"

tab1, tab2, tab3 = st.tabs(["📄 Dépôt TDR", "🧠 Chat OpenRouter", "📂 Docs"])

with tab1:
    st.subheader("Dépose ton TDR ici")
    uploaded = st.file_uploader("PDF, DOCX, XLSX", accept_multiple_files=True, type=["pdf","docx","xlsx","pptx","txt","md"], key="up_v8")
    if uploaded:
        for file in uploaded:
            full=""
            try:
                if file.name.lower().endswith(".pdf"):
                    file.seek(0)
                    reader = pypdf.PdfReader(file)
                    full = "\n".join([p.extract_text() or "" for p in reader.pages[:20]])
            except Exception as ex:
                st.warning(str(ex))
            clas = classify_document(file.name, full[:2000])
            folder = ensure_folder_structure(BASE, clas)
            p = folder / file.name
            with open(p, "wb") as f:
                file.seek(0)
                f.write(file.read())
            add_document({"filename": file.name, "classification": clas, "path": str(p.relative_to(BASE)), "size": file.size, "summary": full[:600]})
            st.success(f"✅ {file.name} -> {clas}")

with tab2:
    st.subheader(f"Chat - {model}")
    if "messages" not in st.session_state:
        st.session_state.messages=[]
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
    prompt = st.chat_input("Analyse TDR, génère offre technique XOF avec ISO 42001...")
    if prompt:
        from core.rag import query_chroma
        try:
            rag = ""
        except:
            rag=""
        kb = load_kb()
        ctx = f"Firm: {firm} | Client: {client} | Docs: {len(kb.get('documents',[]))} | RGSSI-CI: {mode_ci}"
        system = build_system_prompt(ctx)
        st.session_state.messages.append({"role":"user","content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner(f"{model} réfléchit..."):
                ans = call_llm(system, st.session_state.messages, model)
                st.markdown(ans)
        st.session_state.messages.append({"role":"assistant","content": ans})

with tab3:
    docs = list_documents()
    if docs:
        st.dataframe([{"file": d["filename"], "class": d["classification"]} for d in docs])
        for d in docs:
            pp = BASE / d["path"]
            if pp.exists():
                st.download_button(f"Télécharger {d['filename']}", data=open(pp,"rb").read(), file_name=d["filename"], key=f"dl_{d.get('id', d['filename'])}")
    else:
        st.info("Aucun doc. Va dans Dépôt TDR")
