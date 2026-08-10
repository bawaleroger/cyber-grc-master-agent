
import streamlit as st, os, io
from pathlib import Path
from modules.persistence import init_db, save_document, get_all_docs, get_kb_only, get_kb_context, save_tdr, get_latest_tdr, get_all_tdr, clear_all, DB_PATH, DATA_DIR
from modules.document_engine import extract_text, classify_document, parse_tdr
from modules.ai_client import ai
from modules.report_generator import generate_offre_technique_content, generate_offre_financiere_content, generate_dao_content, generate_audit_section, generate_certification_roadmap
import pandas as pd

st.set_page_config(page_title="CYBER-GRC MASTER V4", page_icon="🛡️", layout="wide")
db_path = init_db()

def export_docx(text, title):
    from docx import Document
    doc = Document()
    doc.add_heading(title, 0)
    for para in text.split("\n"):
        p = para.strip()
        if p.startswith("# "): doc.add_heading(p.replace("# ",""), 1)
        elif p.startswith("## "): doc.add_heading(p.replace("## ",""), 2)
        elif p.startswith("### "): doc.add_heading(p.replace("### ",""), 3)
        else: doc.add_paragraph(para)
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

def export_pdf(text, title):
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    bio = io.BytesIO()
    doc = SimpleDocTemplate(bio, pagesize=A4)
    styles = getSampleStyleSheet()
    story = [Paragraph(f"<b>{title}</b>", styles['Title']), Spacer(1,12)]
    for line in text.split("\n")[:600]:
        if line.strip():
            story.append(Paragraph(line[:600].replace("<","&lt;"), styles['Normal']))
            story.append(Spacer(1,4))
    doc.build(story)
    return bio.getvalue()

def export_excel_kit():
    df_erl = pd.DataFrame([
        ["DOC-001","Organigramme DSI + Fiches poste RSSI/DPO/AI Officer","ORG","Critique","J3","DG","ISO 27001 A.5.2 + ISO 42001 A.5.2"],
        ["DOC-042","Logs proxy 12 mois + regles FW","TECH","Critique","J3","DSI","ISO 27001 A.8.15 + NIS2 Art.21 + ISO 42001 A.9.3"],
        ["DOC-089","Inventaire modeles IA + datasets + prompts","IA","Critique","J5","AI Officer","ISO 42001 B.3 + B.7.4 + AI Act Art.49"],
    ], columns=["ID","Document","Type","Criticite","Delai","Resp","Norme"])
    df_raci = pd.DataFrame([
        ["Kick-off","Chef projet CABINET","DG","RSSI,DPO","COMEX","PV Kick-off","Teams","ISO 19011"],
        ["Collecte 150 preuves","Auditeur","RSSI","DSI","DG","ERL","SharePoint","ISO 27001 A.5.33"],
    ], columns=["Tache","R","A","C","I","Livrable","Outil","Norme"])
    df_quest = pd.DataFrame([
        ["Q-042","MFA generalise VPN + M365?","ISO 27001 A.5.17","Non","GPO","Majeur","A5.17 + BCEAO Art.34"],
        ["Q-089","Shadow AI detecte?","ISO 42001 A.9.3","Non","Proxy","Critique","A.9.3 + AI Act Art.50"],
    ], columns=["ID","Question","Norme","Reponse","Preuve","Criticite","Mapping"])
    bio = io.BytesIO()
    with pd.ExcelWriter(bio, engine='openpyxl') as writer:
        df_erl.to_excel(writer, sheet_name='ERL_150', index=False)
        df_raci.to_excel(writer, sheet_name='RACI_Gantt', index=False)
        df_quest.to_excel(writer, sheet_name='350Q', index=False)
    return bio.getvalue()

# ========= PERSISTENCE FIX - AUTO-RELOAD APRES REFRESH =========
# Si session_state vide mais DB contient un TDR, on recharge auto
if "tdr_dict" not in st.session_state:
    latest = get_latest_tdr()
    if latest:
        st.session_state["tdr_dict"] = latest["tdr_dict"]
        st.session_state["tdr_raw"] = latest["raw_text"]
        st.session_state["client"] = latest["client"]
        st.session_state["cabinet"] = latest["cabinet"]
        st.session_state["tdr_loaded_from_db"] = True

# SIDEBAR
st.sidebar.title("🛡️ CYBER-GRC MASTER V4")
st.sidebar.caption(f"DB: {DB_PATH} | Persistant")

client = st.sidebar.text_input("CLIENT", st.session_state.get("client","BCEAO BANK UEMOA"))
cabinet = st.sidebar.text_input("CABINET", st.session_state.get("cabinet","CYBER-GRC CONSULTING"))
st.session_state["client"]=client
st.session_state["cabinet"]=cabinet

st.sidebar.divider()
st.sidebar.subheader("ETAPE 1: CHARGER TDRs")
tdr_files = st.sidebar.file_uploader("A. TDR / DAO (mission en cours)", accept_multiple_files=True, type=["pdf","docx","txt"], key="tdr_upl")
if st.sidebar.button("Ingerer TDRs", type="primary"):
    full=""
    for f in tdr_files or []:
        txt=extract_text(f)
        full+=txt+"\n"
        dtype,best,_=classify_document(txt)
        save_document(f.name, txt, dtype, best, client, is_kb=False)
        st.sidebar.success(f"TDR {f.name} -> {best}")
    if full:
        tdr_dict=parse_tdr(full)
        save_tdr(client,cabinet,tdr_dict,full)
        st.session_state["tdr_dict"]=tdr_dict
        st.session_state["tdr_raw"]=full
        st.sidebar.success("TDR sauvegarde en DB - survivra au refresh!")

st.sidebar.divider()
st.sidebar.subheader("B. Base de Connaissance - Auto-nourrissement PERMANENT")
st.sidebar.markdown("⚠️ Cette base reste **même après refresh / reboot**. Elle nourrit l'agent.")
kb_files = st.sidebar.file_uploader("B. Docs pour nourrir l'agent (PSSI, politiques, anciens rapports, referentiels)", accept_multiple_files=True, type=["pdf","docx","txt"], key="kb_upl")
if st.sidebar.button("🧠 Nourrir Base KB (Permanent)"):
    cnt=0
    for f in kb_files or []:
        txt=extract_text(f)
        dtype,best,_=classify_document(txt)
        save_document(f.name, txt, dtype, best, client, is_kb=True)
        cnt+=1
    if cnt>0:
        st.sidebar.success(f"✅ {cnt} docs ajoutes en base permanente! Ils resteront apres refresh.")
        st.rerun()

# Affichage KB permanent - TOUJOURS depuis DB, pas depuis uploader
docs_all = get_all_docs()
docs_kb = get_kb_only()
st.sidebar.metric("📚 Total Docs en DB (persistants)", len(docs_all))
st.sidebar.metric("🧠 KB permanente (auto-nourrissement)", len(docs_kb))

if docs_all:
    with st.sidebar.expander(f"Voir {len(docs_all)} docs persistants"):
        for filename, dtype, norme, date, cli, size, is_kb in docs_all[:20]:
            icon = "🧠" if is_kb else "📄"
            st.write(f"{icon} {filename[:30]} | {norme} | {dtype} | {str(date)[:16]}")
else:
    st.sidebar.info("Aucun doc en DB. Charge en B. et clique Nourrir.")

if st.sidebar.button("🗑️ Vider toute la base (reset)"):
    clear_all()
    st.session_state.clear()
    st.sidebar.warning("Base videe")
    st.rerun()

st.sidebar.divider()
st.sidebar.subheader("ETAPE 2: MODE IA")
mode = st.sidebar.radio("Moteur", ["Avec Chat IA (Groq/OpenAI API)", "Sans IA - Base auto-nourrissante locale"])
api_key = st.sidebar.text_input("Cle API temporaire", type="password")
if api_key: os.environ["GROQ_API_KEY"]=api_key
st.sidebar.caption(f"Mode detecte: {ai.mode.upper()} | KB: {len(get_kb_context(1000))} chars | DB: {Path(DB_PATH).exists()}")

# MAIN
st.title("CYBER-GRC MASTER V4 - Persistence Fix")
st.markdown(f"**CLIENT:** {client} | **CABINET:** {cabinet} | **Devise:** XOF | **KB permanente:** {len(docs_kb)} docs | **Total:** {len(docs_all)} docs")

# Message si recharge depuis DB
if st.session_state.get("tdr_loaded_from_db"):
    st.success(f"✅ TDR recharge automatiquement depuis DB apres refresh! Dernier TDR du {get_latest_tdr()['date'][:19]} - Client: {get_latest_tdr()['client']}")

if "tdr_dict" not in st.session_state:
    st.warning("👈 ETAPE 1: Charge ton TDR en A. puis clique Ingerer TDRs. Ta base KB en B. reste permanente meme apres refresh.")
    # Montre quand meme KB
    if docs_kb:
        st.info(f"ℹ️ Tu as deja {len(docs_kb)} docs en base de connaissance permanente qui nourrissent l'agent:")
        st.dataframe(pd.DataFrame(docs_kb, columns=["Fichier","Type","Norme","Date","Client"]))
    st.stop()

tdr_dict = st.session_state["tdr_dict"]
kb_ctx = get_kb_context(25000)
tdr_raw = st.session_state.get("tdr_raw","")

# Onglets
tab1,tab2,tab3,tab4,tab5 = st.tabs(["📄 OFFRE TECHNIQUE", "💰 OFFRE FINANCIERE", "📘 DAO", "🚀 MISSION AUDIT BOUT EN BOUT", "🏅 CERTIFICATION"])

with tab1:
    st.header("Offre Technique - Full Redaction")
    st.caption(f"KB utilisee: {len(kb_ctx)} chars venant de {len(docs_all)} docs persistants - Auto-nourrissement actif")
    if st.button("Generer Offre Technique Complete", type="primary", key="b1"):
        with st.spinner("Redaction..."):
            if "Avec Chat IA" in mode:
                prompt = f"GENERE OFFRE TECHNIQUE COMPLETE BIG FOUR pour {client} par {cabinet}. TDR:{tdr_raw[:5000]} KB AUTO-NOURRIE PERMANENTE:{kb_ctx[:7000]}"
                result = ai.generate(prompt, kb_ctx, tdr_raw)
            else:
                result = generate_offre_technique_content(client,cabinet,tdr_dict,kb_ctx)
            st.session_state["offre_tech"]=result
    if "offre_tech" in st.session_state:
        st.markdown(st.session_state["offre_tech"])
        c1,c2,c3 = st.columns(3)
        c1.download_button("WORD", export_docx(st.session_state["offre_tech"], "Offre_Technique"), f"Offre_Technique_{client}.docx")
        c2.download_button("PDF", export_pdf(st.session_state["offre_tech"], "Offre_Technique"), f"Offre_Technique_{client}.pdf")
        c3.download_button("KIT Excel ERL+RACI+350Q", export_excel_kit(), f"KIT_CADRAGE_{client}.xlsx")

with tab2:
    st.header("Offre Financiere XOF")
    if st.button("Generer Offre Financiere", type="primary", key="b2"):
        with st.spinner("Calcul..."):
            if "Avec Chat IA" in mode:
                result = ai.generate(f"OFFRE FINANCIERE XOF pour {client} TDR:{tdr_raw[:3000]} KB:{kb_ctx[:3000]}", kb_ctx, tdr_raw)
            else:
                result = generate_offre_financiere_content(client,cabinet,tdr_dict)
            st.session_state["offre_fin"]=result
    if "offre_fin" in st.session_state:
        st.markdown(st.session_state["offre_fin"])
        c1,c2 = st.columns(2)
        c1.download_button("WORD", export_docx(st.session_state["offre_fin"], "Offre_Fin"), f"Offre_Fin_{client}.docx")
        c2.download_button("EXCEL", export_excel_kit(), f"Offre_Fin_{client}.xlsx")

with tab3:
    st.header("DAO Complet")
    if st.button("Generer DAO", type="primary", key="b3"):
        with st.spinner("Redaction DAO..."):
            if "Avec Chat IA" in mode:
                result = ai.generate(f"DAO BCEAO pour {client} TDR:{tdr_raw[:4000]} KB:{kb_ctx[:4000]}", kb_ctx, tdr_raw)
            else:
                result = generate_dao_content(client,cabinet,tdr_dict)
            st.session_state["dao"]=result
    if "dao" in st.session_state:
        st.markdown(st.session_state["dao"])
        st.download_button("WORD DAO", export_docx(st.session_state["dao"], "DAO"), f"DAO_{client}.docx")

with tab4:
    st.header("Mission Audit Bout en Bout - Section par Section - Full Redaction")
    st.info(f"Agent nourri par {len(docs_kb)} docs KB permanente + {len(docs_all)-len(docs_kb)} TDRs - Total {len(kb_ctx)} chars de contexte")
    phases = ["A_CADRAGE - Kit Cadrage","B_CARTO - Carto + Registre IA","C_RISQUES - EBIOS + Pentest","D_GAP - Gap 2026","E_REMEDIATION - 10 Livrables"]
    sel = st.selectbox("Choisir phase", phases)
    key = sel.split(" - ")[0]
    if st.button(f"Generer {sel}", type="primary"):
        with st.spinner(f"Generation {sel}..."):
            if "Avec Chat IA" in mode:
                prompt = f"MISSION AUDIT SECTION {sel} pour {client} par {cabinet}. TDR:{tdr_raw[:5000]} KB PERMANENTE:{kb_ctx[:7000]}. Full redaction operationnelle avec templates, matrices, commandes, mapping [ISO 27001 A.x + ISO 42001 A.x + BCEAO Art34]"
                result = ai.generate(prompt, kb_ctx, tdr_raw)
            else:
                result = generate_audit_section(key, client, cabinet, tdr_dict, kb_ctx)
            st.session_state[f"audit_{key}"]=result
    for p in phases:
        k = p.split(" - ")[0]
        if f"audit_{k}" in st.session_state:
            with st.expander(f"✅ {p}", expanded=(k==key)):
                st.markdown(st.session_state[f"audit_{k}"])
                c1,c2 = st.columns(2)
                c1.download_button(f"WORD {k}", export_docx(st.session_state[f"audit_{k}"], k), f"{k}_{client}.docx", key=f"w_{k}")
                c2.download_button(f"PDF {k}", export_pdf(st.session_state[f"audit_{k}"], k), f"{k}_{client}.pdf", key=f"p_{k}")

with tab5:
    st.header("Certification - Dropdown")
    norme = st.selectbox("Norme cible", ["ISO 27001:2022","ISO 42001:2023","ISO 9001:2015","ISO 22301:2019","PCI DSS 4.0.1","SOC 2","NIS2","DORA"])
    if st.button(f"Demarrer {norme}", type="primary"):
        with st.spinner(f"Roadmap {norme}..."):
            if "Avec Chat IA" in mode:
                result = ai.generate(f"CERTIFICATION {norme} pour {client} TDR:{tdr_raw[:3000]} KB:{kb_ctx[:4000]}", kb_ctx, tdr_raw)
            else:
                result = generate_certification_roadmap(norme, client, cabinet)
            st.session_state[f"cert_{norme}"]=result
    if f"cert_{norme}" in st.session_state:
        st.markdown(st.session_state[f"cert_{norme}"])
        st.download_button("WORD", export_docx(st.session_state[f"cert_{norme}"], f"Certif_{norme}"), f"Certif_{norme}_{client}.docx")
