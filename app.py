
import streamlit as st
import os, hashlib
from modules.persistence import init_db, save_document, get_all_docs, get_kb_context, save_tdr
from modules.document_engine import extract_text, classify_document, parse_tdr
from modules.mapping_engine import auto_map
from modules.ai_client import ai

st.set_page_config(page_title="CYBER-GRC MASTER AGENT", page_icon="🛡️", layout="wide")
init_db()

st.sidebar.title("🛡️ CYBER-GRC MASTER")
st.sidebar.caption("Architecte Principal - Big Four Level")

client = st.sidebar.text_input("CLIENT", value=st.session_state.get("client","SONATEL UEMOA"))
cabinet = st.sidebar.text_input("CABINET", value=st.session_state.get("cabinet","CYBER-GRC CONSULTING"))
st.session_state["client"]=client
st.session_state["cabinet"]=cabinet

st.sidebar.divider()
st.sidebar.subheader("📚 Base de Connaissances Autonome")
st.sidebar.metric("Documents ingérés", len(get_all_docs()))

st.sidebar.divider()
st.sidebar.subheader("⚙️ Moteur IA")
st.sidebar.info(f"Mode actuel: **{ai.mode.upper()}**\nConfigure GROQ_API_KEY dans Secrets pour puissance max.")
api_key_input = st.sidebar.text_input("Clé API temporaire", type="password")
if api_key_input:
    os.environ["GROQ_API_KEY"]=api_key_input

st.title("CYBER-GRC MASTER AGENT - Console Principale")
st.markdown(f"**Client:** {client} | **Cabinet:** {cabinet} | **Devise:** XOF")

tab1, tab2, tab3, tab4 = st.tabs(["PHASE 0 - INGESTION TDR", "CENTRE DOCUMENTAIRE", "MISSION & MENU 5 BOUTONS", "MAPPING & LIVRABLES"])

with tab1:
    st.header("PHASE 0 - INGESTION & CADRAGE INTELLIGENT - ISO 19011:2018")
    uploaded = st.file_uploader("Charge TDR / DAO / Référentiels (PDF, DOCX, TXT) - Persistance garantie", accept_multiple_files=True, type=["pdf","docx","txt"])
    tdr_text_manual = st.text_area("Ou colle le TDR ici", height=200)

    if st.button("INGÉRER & ANALYSER", type="primary"):
        full_text = ""
        if uploaded:
            for f in uploaded:
                txt = extract_text(f)
                full_text += "\n" + txt
                doc_type, norme, scores = classify_document(txt)
                save_document(f.name, txt, doc_type, norme, client)
                st.success(f"{f.name} -> {doc_type} / {norme}")
        if tdr_text_manual:
            full_text += "\n" + tdr_text_manual
        if full_text:
            tdr_dict = parse_tdr(full_text)
            tid = save_tdr(client, cabinet, tdr_dict, full_text)
            st.session_state["tdr_id"]=tid
            st.session_state["tdr_dict"]=tdr_dict
            st.session_state["tdr_raw"]=full_text
            st.json(tdr_dict)
        else:
            st.warning("Aucun document")

with tab2:
    st.header("Centre Documentaire Autonome - Persistence garantie")
    docs = get_all_docs()
    if docs:
        import pandas as pd
        df = pd.DataFrame(docs, columns=["Fichier","Type","Norme","Date","Client","Taille"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Aucun document encore.")

with tab3:
    st.header("MENU INTERACTIF OBLIGATOIRE - PHASE 0")
    st.markdown("BOUTON 1: OFFRE TECHNIQUE | BOUTON 2: FINANCIERE XOF | BOUTON 3: DAO | BOUTON 4: PLAN AUDIT | BOUTON 5: CERTIFICATION")
    col1,col2,col3,col4,col5 = st.columns(5)
    
    if col1.button("B1 - Offre Technique"):
        st.session_state["action"]="GÉNÉRER L'OFFRE TECHNIQUE COMPLÈTE ISO 19011 + ISO 27001 Cl.5 + ISO 42001 Cl.5. Inclure RACI, Planning, Méthodo EBIOS RM, Arsenal technique détaillé, 0 etc., tableaux, check-lists"
    if col2.button("B2 - Offre Financiere"):
        st.session_state["action"]="GÉNÉRER L'OFFRE FINANCIÈRE DÉTAILLÉE EN XOF. Tableau JH par phase, coûts unitaires, totaux, délais, avec mapping XOF et TVA UEMOA. Format Big Four."
    if col3.button("B3 - DAO"):
        st.session_state["action"]="GÉNÉRER LE DAO / CAHIER DES CHARGES PRO conforme BCEAO/UEMOA + ISO 27001:2022 + ISO 42001:2023."
    if col4.button("B4 - Plan Audit"):
        st.session_state["action"]="DÉMARRER LA MISSION - PLAN D'AUDIT COMPLET PHASE 0.B détaillé A-E: Cadrage RACI, Etat existant cartographie actifs ISO 27005 + Registre IA AI Act Art.49, Analyse risques EBIOS RM + ISO 27005 + 42001 + MITRE ATLAS + Pentest PTES + OWASP WSTG + LLM Top10, Arsenal commandes, Méthodo preuve CVSS v4 + Chain Custody"
    if col5.button("B5 - Certification"):
        st.session_state["action"]="MENU CERTIFICATION: [ISO 27001:2022] [ISO 42001:2023] [ISO 9001] [ISO 22301] [PCI DSS 4.0.1] [SOC 2] -> Gap -> Mise en conf -> Doc -> Audit blanc -> Accompagnement XOF"

    user_free = st.text_area("Prompt libre (ex: Fais Gap Analysis MFA + Shadow AI)", height=120)
    if st.button("EXECUTER CYBER-GRC MASTER", type="primary"):
        final_prompt = st.session_state.get("action","") + "\n" + user_free
        if not final_prompt.strip():
            st.warning("Choisis un bouton ou écris un prompt")
        else:
            with st.spinner("CYBER-GRC MASTER réfléchit comme CISO Big Four 50 ans exp..."):
                kb = get_kb_context(12000)
                tdr = st.session_state.get("tdr_raw","")
                result = ai.generate(final_prompt.replace("{{CLIENT}}",client).replace("{{CABINET}}",cabinet), kb, tdr)
                result = result.replace("{{CLIENT}}",client).replace("{{CABINET}}",cabinet)
                st.session_state["last_result"]=result
            st.markdown(st.session_state["last_result"])

    if "last_result" in st.session_state:
        st.divider()
        st.download_button("Telecharger Livrable MD", st.session_state["last_result"], file_name=f"Livrable_{client}.md")

with tab4:
    st.header("Mapping Normatif Obligatoire - 2026")
    action = st.text_input("Action a mapper (ex: MFA + Formation IA)")
    if action:
        st.code(auto_map(action))
