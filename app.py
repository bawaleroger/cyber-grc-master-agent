
import streamlit as st
import json, os
from datetime import datetime
from pathlib import Path
from io import BytesIO
import pypdf

st.set_page_config(page_title="MADOU GRC AUTOPILOT V9", page_icon="🛡️", layout="wide")

# ========== DRIVE SYNC (ton code d'hier) ==========
DRIVE_AVAILABLE = False
drive_service = None
GDRIVE_FOLDER_ID = None
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
    if "GDRIVE_CREDENTIALS_JSON" in st.secrets and "GDRIVE_FOLDER_ID" in st.secrets:
        creds_dict = dict(st.secrets["GDRIVE_CREDENTIALS_JSON"])
        SCOPES = ['https://www.googleapis.com/auth/drive']
        creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        drive_service = build('drive', 'v3', credentials=creds)
        GDRIVE_FOLDER_ID = st.secrets["GDRIVE_FOLDER_ID"]
        DRIVE_AVAILABLE = True
except Exception as e:
    DRIVE_AVAILABLE = False
    drive_error = str(e)

def save_to_drive(data_dict, filename="knowledge_base.json"):
    if not DRIVE_AVAILABLE: return False, "Drive non configuré"
    try:
        query = f"name='{filename}' and '{GDRIVE_FOLDER_ID}' in parents and trashed=false"
        results = drive_service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])
        json_bytes = json.dumps(data_dict, ensure_ascii=False, indent=2).encode('utf-8')
        media = MediaIoBaseUpload(BytesIO(json_bytes), mimetype='application/json')
        if files:
            file_id = files[0]['id']
            drive_service.files().update(fileId=file_id, media_body=media).execute()
            return True, "Mis à jour Drive"
        else:
            file_metadata = {'name': filename, 'parents': [GDRIVE_FOLDER_ID]}
            drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            return True, "Créé Drive"
    except Exception as ex:
        return False, str(ex)

def load_from_drive(filename="knowledge_base.json"):
    if not DRIVE_AVAILABLE: return None
    try:
        query = f"name='{filename}' and '{GDRIVE_FOLDER_ID}' in parents and trashed=false"
        results = drive_service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])
        if not files: return None
        file_id = files[0]['id']
        request = drive_service.files().get_media(fileId=file_id)
        fh = BytesIO()
        from googleapiclient.http import MediaIoBaseDownload
        downloader = MediaIoBaseDownload(fh, request)
        done=False
        while not done:
            status, done = downloader.next_chunk()
        fh.seek(0)
        return json.loads(fh.read().decode('utf-8'))
    except:
        return None

# ========== OPENROUTER CONFIG ==========
OPENROUTER_KEY = st.secrets.get("OPENROUTER_API_KEY","") or os.getenv("OPENROUTER_API_KEY","")

def call_llm(system_prompt, user_prompt, model):
    if not OPENROUTER_KEY:
        return "❌ Ajoute OPENROUTER_API_KEY dans Secrets"
    try:
        from openai import OpenAI
        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_KEY)
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role":"system","content": system_prompt}, {"role":"user","content": user_prompt}],
            temperature=0.2,
            max_tokens=6000,
            extra_headers={"HTTP-Referer": "https://madou-grc.streamlit.app", "X-Title": "MADOU V9"}
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Erreur OpenRouter ({model}): {e}. Va sur openrouter.ai -> Credits -> ajoute 1$ si 402"

def extract_text(file):
    text=""
    try:
        if file.name.lower().endswith(".pdf"):
            file.seek(0)
            reader = pypdf.PdfReader(file)
            text = "\n".join([p.extract_text() or "" for p in reader.pages[:30]])
        elif file.name.lower().endswith(".docx"):
            import docx
            file.seek(0)
            doc = docx.Document(file)
            text = "\n".join([p.text for p in doc.paragraphs])
        else:
            file.seek(0)
            text = file.read().decode('utf-8', errors='ignore')[:10000]
    except Exception as ex:
        text = f"Erreur lecture: {ex}"
    return text

# ========== SESSION STATE ==========
if 'knowledge' not in st.session_state:
    loaded = load_from_drive() if DRIVE_AVAILABLE else None
    st.session_state.knowledge = loaded if loaded else {}

if 'tdr_texts' not in st.session_state:
    st.session_state.tdr_texts = {}  # filename -> text

if 'generated_docs' not in st.session_state:
    st.session_state.generated_docs = {}  # type -> content

# ========== SIDEBAR ==========
st.sidebar.title("🧠 MADOU GRC - Config")
st.sidebar.write("Base auto + Drive + OpenRouter")

if DRIVE_AVAILABLE:
    st.sidebar.success(f"✅ Drive connecté")
else:
    st.sidebar.warning("⚠️ Drive non connecté - Mode local")

if OPENROUTER_KEY:
    st.sidebar.success(f"✅ OpenRouter: {OPENROUTER_KEY[:10]}...{OPENROUTER_KEY[-4:]}")
else:
    st.sidebar.error("Ajoute OPENROUTER_API_KEY dans Secrets")

st.sidebar.divider()
model_choice = st.sidebar.selectbox("Modèle", [
    "meta-llama/llama-4-maverick",
    "meta-llama/llama-3.3-70b-instruct",
    "google/gemini-2.0-flash-001",
    "deepseek/deepseek-chat",
    "qwen/qwen-2.5-72b-instruct"
])

st.sidebar.divider()
st.sidebar.subheader("📚 Base")
st.sidebar.metric("Docs base", len(st.session_state.knowledge))
st.sidebar.metric("TDR chargés", len(st.session_state.tdr_texts))
st.sidebar.metric("Docs générés", len(st.session_state.generated_docs))

# ========== MAIN ==========
st.title("🛡️ MADOU GRC AUTOPILOT V9 - WORKFLOW COMPLET")
st.caption("Upload TDR → Choix action → Génération offre / audit | Chat optionnel")

tab1, tab2, tab3, tab4 = st.tabs(["📄 1. Dépôt TDR", "🚀 2. Génération Auto", "📂 3. Docs & Drive", "💬 4. Chat Optionnel"])

with tab1:
    st.subheader("Étape 1: Dépose tes TDR / DAO / Offres")
    st.info("Glisse ici tous les TDR. Ils seront auto-classés, extraits et prêts pour génération.")
    uploaded = st.file_uploader("PDF, DOCX, XLSX, TXT", accept_multiple_files=True, type=['pdf','docx','xlsx','pptx','txt'], key="tdr_up")
    if uploaded:
        for file in uploaded:
            text = extract_text(file)
            st.session_state.tdr_texts[file.name] = text[:20000]  # garde 20k chars
            
            # Sauve aussi dans knowledge base
            lower=file.name.lower()
            typ="TDR" if "tdr" in lower else "DAO" if "dao" in lower else "Offre" if "offre" in lower else "Document"
            entry = {
                "name": file.name,
                "type": typ,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "size": file.size,
                "content_preview": text[:500]
            }
            st.session_state.knowledge[file.name] = entry
            if DRIVE_AVAILABLE:
                save_to_drive(st.session_state.knowledge)
            st.success(f"✅ {file.name} -> {typ} -> Texte extrait ({len(text)} chars)")

    if st.session_state.tdr_texts:
        st.divider()
        st.subheader(f"✅ {len(st.session_state.tdr_texts)} TDR prêts")
        for name, txt in st.session_state.tdr_texts.items():
            with st.expander(f"{name} - {len(txt)} chars"):
                st.text(txt[:2000])

with tab2:
    st.subheader("Étape 2: Que veux-tu générer ?")
    if not st.session_state.tdr_texts:
        st.warning("👈 Va d'abord déposer au moins 1 TDR dans l'onglet 1")
    else:
        st.success(f"{len(st.session_state.tdr_texts)} TDR chargés, prêts à générer")
        
        # Concatène tous les TDR pour contexte
        all_tdr = "\n\n---\n\n".join([f"### {k}\n{v[:8000]}" for k,v in st.session_state.tdr_texts.items()])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 📄 Offres")
            if st.button("📝 Générer Offre Technique", use_container_width=True):
                with st.spinner("Llama génère l'offre technique..."):
                    sys_prompt = "Tu es expert Cyber-GRC UEMOA ISO 27001, ISO 42001, RGSSI-CI. Tu génères une offre technique professionnelle complète avec: contexte, compréhension TDR, méthodologie, planning, livrables, équipe, mapping ISO 42001 obligatoire, normes. Réponds en français structuré."
                    prompt = f"TDR à analyser:\n{all_tdr}\n\nGénère une OFFRE TECHNIQUE complète pour répondre à ce TDR. Devises XOF, mapping ISO 42001 obligatoire."
                    result = call_llm(sys_prompt, prompt, model_choice)
                    st.session_state.generated_docs["Offre Technique"] = result
                    st.success("Offre Technique générée")
            
            if st.button("💰 Offre Financière XOF", use_container_width=True):
                with st.spinner("Génération offre financière..."):
                    sys_prompt = "Expert Cyber-GRC financier UEMOA. Génère offre financière détaillée en XOF avec tableau prix HT/HDD, TVA 18%, jours/homme, totaux, conditions paiement, validité. ISO 42001 inclus."
                    prompt = f"TDR:\n{all_tdr}\n\nGénère OFFRE FINANCIERE XOF détaillée avec prix justifiés."
                    result = call_llm(sys_prompt, prompt, model_choice)
                    st.session_state.generated_docs["Offre Financière XOF"] = result

            if st.button("📘 Cahier de Choix / Critères", use_container_width=True):
                with st.spinner("Génération cahier de choix..."):
                    sys_prompt = "Expert achat public UEMOA. Génère grille d'évaluation, critères techniques, pondération, cahier de choix pour ce TDR."
                    prompt = f"TDR:\n{all_tdr}\n\nGénère CAHIER DE CHOIX et GRILLE D'EVALUATION."
                    result = call_llm(sys_prompt, prompt, model_choice)
                    st.session_state.generated_docs["Cahier de Choix"] = result

        with col2:
            st.markdown("#### 🔍 Audit")
            if st.button("🚀 Plan d'Audit Complet", use_container_width=True):
                with st.spinner("Plan audit..."):
                    sys_prompt = "Auditeur certifié ISO 27001 Lead Auditor, ISO 42001. Génère plan audit complet: objectifs, périmètre, référentiels, planning, checklists, matrice risques."
                    prompt = f"TDR:\n{all_tdr}\n\nGénère PLAN D'AUDIT COMPLET avec ISO 42001."
                    result = call_llm(sys_prompt, prompt, model_choice)
                    st.session_state.generated_docs["Plan Audit"] = result

            if st.button("📋 Dossier d'Audit", use_container_width=True):
                with st.spinner("Dossier audit..."):
                    sys_prompt = "Expert GRC. Génère dossier d'audit: fiche ouverture, programme, guide entretien, trame rapport."
                    prompt = f"TDR:\n{all_tdr}\n\nGénère DOSSIER D'AUDIT complet."
                    result = call_llm(sys_prompt, prompt, model_choice)
                    st.session_state.generated_docs["Dossier Audit"] = result

            if st.button("⚠️ Matrice Risques", use_container_width=True):
                with st.spinner("Matrice..."):
                    sys_prompt = "Expert ISO 27005. Génère matrice risques, cartographie, plan traitement."
                    prompt = f"TDR:\n{all_tdr}\n\nGénère MATRICE RISQUES."
                    result = call_llm(sys_prompt, prompt, model_choice)
                    st.session_state.generated_docs["Matrice Risques"] = result

        with col3:
            st.markdown("#### 📦 Autres")
            if st.button("📄 DAO Complet", use_container_width=True):
                with st.spinner("DAO..."):
                    sys_prompt = "Expert marchés publics UEMOA. Génère DAO complet à partir du TDR."
                    prompt = f"TDR:\n{all_tdr}\n\nGénère DAO COMPLET."
                    result = call_llm(sys_prompt, prompt, model_choice)
                    st.session_state.generated_docs["DAO"] = result

            if st.button("🏅 Certifications ISO", use_container_width=True):
                with st.spinner("Certifications..."):
                    sys_prompt = "Expert ISO 27001/42001. Génère mapping exigences, plan conformité."
                    prompt = f"TDR:\n{all_tdr}\n\nGénère DOSSIER ISO 42001 + 27001."
                    result = call_llm(sys_prompt, prompt, model_choice)
                    st.session_state.generated_docs["ISO 42001 Mapping"] = result

            if st.button("🗑️ Vider générations", use_container_width=True):
                st.session_state.generated_docs = {}
                st.success("Vidé")

        st.divider()
        if st.session_state.generated_docs:
            st.subheader("📄 Documents Générés")
            for dtype, content in st.session_state.generated_docs.items():
                with st.expander(f"✅ {dtype} - {len(content)} chars", expanded=False):
                    st.markdown(content)
                    st.download_button(f"📥 Télécharger {dtype}", data=content.encode('utf-8'), file_name=f"{dtype}_{datetime.now().strftime('%Y%m%d')}.md", key=f"dl_{dtype}")

with tab3:
    st.subheader("📂 Base de connaissances + Drive")
    col1, col2 = st.columns(2)
    col1.metric("Documents base", len(st.session_state.knowledge))
    col2.metric("Drive", "Connecté ✅" if DRIVE_AVAILABLE else "Local")
    
    if st.session_state.knowledge:
        st.json(st.session_state.knowledge)
        if st.button("🔄 Sync Drive maintenant"):
            if DRIVE_AVAILABLE:
                ok, msg = save_to_drive(st.session_state.knowledge)
                st.success(msg) if ok else st.error(msg)
        if st.button("🗑️ Vider base (local + Drive)"):
            st.session_state.knowledge = {}
            st.session_state.tdr_texts = {}
            if DRIVE_AVAILABLE:
                save_to_drive({})
            st.rerun()
    else:
        st.info("Base vide")

with tab4:
    st.subheader("💬 Chat Optionnel - Après génération ou direct")
    st.info("Ici tu peux affiner avec le chat, poser des questions sur les TDR, ou générer sans passer par les boutons.")
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages=[]
    for m in st.session_state.chat_messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
    chat_prompt = st.chat_input("Question sur TDR, améliore offre, etc...")
    if chat_prompt:
        all_tdr = "\n\n".join([f"{k}: {v[:5000]}" for k,v in st.session_state.tdr_texts.items()])
        gen = "\n\n".join([f"{k}: {v[:2000]}" for k,v in st.session_state.generated_docs.items()])
        system = f"Tu es MADOU GRC AUTOPILOT. TDR: {all_tdr[:10000]} Docs générés: {gen[:5000]}. Réponds expert ISO 27001/42001 XOF."
        st.session_state.chat_messages.append({"role":"user","content": chat_prompt})
        with st.chat_message("user"):
            st.markdown(chat_prompt)
        with st.chat_message("assistant"):
            with st.spinner("Réflexion..."):
                ans = call_llm(system, chat_prompt, model_choice)
                st.markdown(ans)
        st.session_state.chat_messages.append({"role":"assistant","content": ans})

st.caption("MADOU GRC V9 - TDR -> Choix -> Génération + Chat optionnel + Drive")
