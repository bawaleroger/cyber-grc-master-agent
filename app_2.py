
import streamlit as st
import os, json, shutil
from pathlib import Path
from datetime import datetime
from core.classifier import classify_document, ensure_folder_structure
from core.knowledge_base import add_document, list_documents, search_kb, load_kb, save_kb
from core.api_manager import add_api, list_apis
from core.agent import build_system_prompt
import pypdf

BASE = Path(__file__).parent
st.set_page_config(page_title="Cyber-GRC Master Agent", page_icon="🛡️", layout="wide")

# CSS
st.markdown("""
<style>
.big-title{font-size:32px;font-weight:800;color:#0B1D3A}
.card{padding:15px;border-radius:12px;border:1px solid #E5E7EB;background:white;margin-bottom:10px}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">🛡️ CYBER-GRC MASTER AGENT - V5</div>', unsafe_allow_html=True)
st.caption("Agent IA autonome - Knowledge Base JSON persistante - Classification auto - Multi-API - Prêt GitHub & Streamlit.io")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    firm = st.text_input("[NOM DU CABINET]", "CYBER-GRC CONSULTING")
    client = st.text_input("[NOM DU CLIENT]", "CLIENT UEMOA")
    mode_ci = st.checkbox("Activer normes Côte d'Ivoire (RGSSI-CI/ARTCI)")
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
        st.markdown(f"**{api['name']}** - {api['base_url']} - {api.get('description','')}")

    st.divider()
    st.subheader("📚 Knowledge Base")
    st.json(load_kb(), expanded=False)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📄 Dépôt & Classification Auto", "🧠 Agent Chat & Missions", "📂 Explorateur Documents", "🚀 Deploy GitHub"])

with tab1:
    st.subheader("Dépose tes documents - Classement automatique")
    uploaded = st.file_uploader("Rapports, Cours, TDRs, DAO, Offres...", accept_multiple_files=True, type=["pdf","docx","xlsx","pptx","txt","md"])
    if uploaded:
        for file in uploaded:
            # extract snippet for classification
            text_snippet = file.name
            try:
                if file.name.lower().endswith(".pdf"):
                    reader = pypdf.PdfReader(file)
                    text_snippet += " " + (reader.pages[0].extract_text()[:1000] if reader.pages else "")
            except:
                pass
            
            classification = classify_document(file.name, text_snippet)
            target_folder = ensure_folder_structure(BASE, classification)
            # save file
            file_path = target_folder / file.name
            with open(file_path, "wb") as f:
                file.seek(0)
                f.write(file.read())
            
            entry = {
                "filename": file.name,
                "classification": classification,
                "path": str(file_path.relative_to(BASE)),
                "size": file.size,
                "summary": f"Auto-classé en {classification}",
                "firm": firm,
                "client": client,
            }
            add_document(entry)
            st.success(f"✅ {file.name} -> {classification} -> {file_path}")
    
    st.divider()
    st.write("### Création automatique de dossier si manquant")
    st.info("Si un champ manque (ex: pas de PSSI), l'agent crée et classe le dossier seul. Voir code core/classifier.py et knowledge_base.json")

with tab2:
    st.subheader("Chat avec l'Agent Cyber-GRC Master")
    kb = load_kb()
    context = f"Firm: {firm} | Client: {client} | Docs: {len(kb['documents'])} | Classifications: {list(kb['classifications'].keys())} | Mode CI: {mode_ci} | APIs: {[a['name'] for a in kb['apis']]}"
    
    system_prompt = build_system_prompt(context)
    st.text_area("System Prompt Actif (V5 sans CI + ISO 42001)", system_prompt[:2000]+"...", height=200)
    
    # Chat
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role":"system","content":system_prompt}]
    
    for m in st.session_state.messages[1:]:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
    
    prompt = st.chat_input("Pose ta question, upload TDR, ou demande une offre...")
    if prompt:
        st.session_state.messages.append({"role":"user","content":prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Simulated agent response - replace with OpenAI call if API key in secrets
        with st.chat_message("assistant"):
            if "TDR" in prompt.upper() or "DAO" in prompt.upper():
                response = f"""
Bien reçu. Lancement de la mission **{client}**.

**Analyse TDR** : {prompt[:200]}...

**MENU D'ACTIONS AUTOMATIQUE** :
[📄 BOUTON 1 : GÉNÉRER L'OFFRE TECHNIQUE COMPLÈTE DE BOUT EN BOUT]
[💰 BOUTON 2 : GÉNÉRER L'OFFRE FINANCIÈRE DÉTAILLÉE EN XOF]
[📘 BOUTON 3 : GÉNÉRER LE CAHIER DES CHARGES / DAO PRO]
[🚀 BOUTON 4 : DÉMARRER LA MISSION - PLAN D'AUDIT NORMAL & COMPLET]
[🏅 BOUTON 5 : MENU CERTIFICATION - ACCOMPAGNEMENT BOUT EN BOUT]

**Plan d'Audit Normal avec ISO 42001 intégré** :
- Cadrage : ISO 27001 Cl5 + ISO 42001 Cl5 + A.2 + A.5.2 Rôles IA
- Existant : Inventaire actifs + Inventaire Systèmes IA (AI Act Art49 + ISO 42001 B.3)
- Personnel : ISO 27001 A7.2 + ISO 42001 7.2/7.3/A.3.2
- Shadow AI : ISO 42001 A.9.3 + A.10 via logs proxy
- Arsenal détaillé : theHarvester, Maltego, Nmap, PingCastle, Nessus Pro, Burp Pro, etc.

Dis-moi quel bouton tu veux lancer.
"""
            else:
                response = f"""
En tant que **CYBER-GRC MASTER V5** pour **{firm}** / **{client}**, contexte KB: {len(kb['documents'])} docs classés, APIs liées: {len(kb['apis'])}.

**Réponse experte 2026 avec mapping ISO 42001 systématique** :

{prompt}

→ Mapping proposé : ISO 27001 + ISO 42001 A.3.2/A.5.2/A.9.3 + NIS2 Art20 + BCEAO Art34 + NIST AI RMF.

Veux-tu que je génère le livrable complet (Offre Technique, Financière, ou Plan d'Audit) ?
"""
            st.markdown(response)
            st.session_state.messages.append({"role":"assistant","content":response})

with tab3:
    st.subheader("Explorateur Knowledge Base JSON - Documents toujours disponibles")
    docs = list_documents()
    st.metric("Documents persistés", len(docs))
    search = st.text_input("Rechercher dans KB")
    if search:
        docs = search_kb(search)
    for d in docs:
        with st.expander(f"{d['classification']} | {d['filename']}"):
            st.json(d)
            path = BASE / d["path"]
            if path.exists():
                st.download_button(f"Télécharger {d['filename']}", data=open(path,"rb").read(), file_name=d['filename'])

with tab4:
    st.subheader("Déploiement GitHub + Streamlit.io")
    st.code("""
# 1. Push GitHub
git init
git add .
git commit -m "feat: Cyber-GRC Master Agent V5 - ISO 42001 integrated - no CI norms"
git branch -M main
git remote add origin https://github.com/TON_USER/cyber-grc-master-agent.git
git push -u origin main

# 2. Streamlit Cloud
# - Va sur share.streamlit.io
# - New app -> Select repo -> Main file: app.py
# - Add secrets in .streamlit/secrets.toml:
OPENAI_API_KEY="sk-..."
# - Deploy

# 3. Structure persistante
# data/knowledge_base.json est ta KB JSON toujours dispo
# data/documents/<CLASSIFICATION>/ contient tous les docs classés auto
# Si champ manquant, l'agent crée le dossier seul via ensure_folder_structure()
""", language="bash")
    st.success("Repo prêt à être pushé : /mnt/data/cyber-grc-agent")

# footer
st.divider()
st.caption(f"CTO Build - {datetime.now().year} | {firm} | Agent autonome | Knowledge Base JSON | Multi-API ready")
