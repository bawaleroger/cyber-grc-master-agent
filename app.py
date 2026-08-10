
import streamlit as st, os, hashlib, io, datetime
from modules.persistence import init_db, save_document, get_all_docs, get_kb_context, save_tdr
from modules.document_engine import extract_text, classify_document, parse_tdr
from modules.ai_client import ai
from modules.report_generator import generate_offre_technique_content, generate_offre_financiere_content, generate_dao_content, generate_audit_section, generate_certification_roadmap

st.set_page_config(page_title="CYBER-GRC MASTER AGENT V2", page_icon="🛡️", layout="wide")
init_db()

# Helpers export
def export_docx(text, filename):
    from docx import Document
    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    for line in text.split("\n"):
        doc.add_paragraph(line)
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

def export_pdf(text, filename):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import cm
    bio = io.BytesIO()
    c = canvas.Canvas(bio, pagesize=A4)
    width, height = A4
    y = height - 2*cm
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2*cm, y, f"CYBER-GRC MASTER - {filename}")
    y -= 1*cm
    c.setFont("Helvetica", 9)
    for line in text.split("\n")[:200]:
        if y < 2*cm:
            c.showPage()
            y = height - 2*cm
            c.setFont("Helvetica", 9)
        c.drawString(2*cm, y, line[:110])
        y -= 0.5*cm
    c.save()
    return bio.getvalue()

def export_excel_financiere():
    import pandas as pd
    df = pd.DataFrame([
        ["Phase 0 Cadrage",5,3,750000,350000,4800000],
        ["Phase 1 Carto + Registre IA",10,8,750000,350000,10300000],
        ["Phase 2 Audit Tech PTES/WSTG/LLM",15,10,850000,400000,16750000],
        ["Phase 3 Gap Analysis",10,5,750000,350000,9250000],
        ["Phase 4 Redaction PSSI/SoA/IA",12,8,750000,350000,11800000],
        ["Phase 5 Forensic",3,2,800000,400000,3200000],
        ["Phase 6 Restitution",5,2,750000,350000,4450000],
    ], columns=["Phase","JH Senior","JH Junior","PU Senior","PU Junior","Total XOF"])
    bio = io.BytesIO()
    with pd.ExcelWriter(bio, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Offre Financiere')
    return bio.getvalue()

# SIDEBAR
st.sidebar.title("🛡️ CYBER-GRC MASTER V2")
client = st.sidebar.text_input("CLIENT {{CLIENT}}", st.session_state.get("client","BCEAO BANK UEMOA"))
cabinet = st.sidebar.text_input("CABINET {{CABINET}}", st.session_state.get("cabinet","CYBER-GRC CONSULTING"))
st.session_state["client"]=client
st.session_state["cabinet"]=cabinet

st.sidebar.divider()
st.sidebar.subheader("ETAPE 1: CHARGER TDRs")
uploaded = st.sidebar.file_uploader("TDR / DAO / Preuves", accept_multiple_files=True, type=["pdf","docx","txt"])
if st.sidebar.button("Ingerer TDRs"):
    full=""
    for f in uploaded or []:
        txt=extract_text(f)
        full+=txt+"\n"
        dtype,norme,_=classify_document(txt)
        save_document(f.name, txt, dtype, norme, client)
        st.sidebar.success(f"{f.name} -> {norme}")
    if full:
        tdr_dict=parse_tdr(full)
        save_tdr(client,cabinet,tdr_dict,full)
        st.session_state["tdr_dict"]=tdr_dict
        st.session_state["tdr_raw"]=full

if "tdr_dict" in st.session_state:
    st.sidebar.json(st.session_state["tdr_dict"])
    st.sidebar.metric("KB Docs", len(get_all_docs()))

st.sidebar.divider()
st.sidebar.subheader("ETAPE 2: MODE IA")
mode = st.sidebar.radio("Moteur", ["Avec Chat IA (API Groq/OpenAI)", "Sans IA - Base auto-nourrissante"])
api_key = st.sidebar.text_input("Cle API temporaire", type="password")
if api_key:
    os.environ["GROQ_API_KEY"]=api_key

st.sidebar.caption(f"Mode detecte: {ai.mode.upper()} | KB: {len(get_kb_context(1000))} chars")

# MAIN
st.title("CYBER-GRC MASTER - Workflow V2 Autonome")
st.markdown(f"**CLIENT:** {client} | **CABINET:** {cabinet} | **Devise:** XOF")

if "tdr_dict" not in st.session_state:
    st.warning("👈 ETAPE 1: Charge tes TDRs dans la sidebar pour commencer. L'app se nourrit et persiste apres refresh.")
    st.stop()

tdr_dict = st.session_state["tdr_dict"]
kb_ctx = get_kb_context(15000)
tdr_raw = st.session_state.get("tdr_raw","")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📄 OFFRE TECHNIQUE", "💰 OFFRE FINANCIERE", "📘 DAO", "🚀 MISSION AUDIT BOUT EN BOUT", "🏅 CERTIFICATION"])

with tab1:
    st.header("Bouton Offre Technique - Redaction complete Big Four")
    if st.button("Générer Offre Technique Complete", type="primary", key="b1"):
        with st.spinner("CISO Big Four redige..."):
            if "Avec Chat IA" in mode:
                prompt = f"GENERE OFFRE TECHNIQUE COMPLETE pour {client} par {cabinet}. TDR:{tdr_raw[:3000]} KB:{kb_ctx[:4000]}. Respecte PROTOCOLE ANTI-HALLUCINATION, mapping [ISO 27001] [ISO 42001] [BCEAO]. 0 etc."
                result = ai.generate(prompt, kb_ctx, tdr_raw)
            else:
                result = generate_offre_technique_content(client, cabinet, tdr_dict, kb_ctx)
            st.session_state["offre_tech"]=result
    if "offre_tech" in st.session_state:
        st.markdown(st.session_state["offre_tech"])
        colA,colB,colC = st.columns(3)
        colA.download_button("Exporter WORD", export_docx(st.session_state["offre_tech"], "Offre_Technique"), f"Offre_Technique_{client}.docx")
        colB.download_button("Exporter PDF", export_pdf(st.session_state["offre_tech"], "Offre_Technique"), f"Offre_Technique_{client}.pdf")
        colC.download_button("Exporter MD", st.session_state["offre_tech"], f"Offre_Technique_{client}.md")

with tab2:
    st.header("Bouton Offre Financiere - Detaillee XOF")
    if st.button("Générer Offre Financiere XOF", type="primary", key="b2"):
        with st.spinner("Calcul JH + XOF..."):
            if "Avec Chat IA" in mode:
                prompt = f"GENERE OFFRE FINANCIERE DETAILLEE EN XOF JH + couts pour {client}. Phases ISO 19011 + ISO 27001 + ISO 42001. Tableau detaille + TVA UEMOA 18%. TDR:{tdr_raw[:2000]}"
                result = ai.generate(prompt, kb_ctx, tdr_raw)
            else:
                result = generate_offre_financiere_content(client, cabinet, tdr_dict)
            st.session_state["offre_fin"]=result
    if "offre_fin" in st.session_state:
        st.markdown(st.session_state["offre_fin"])
        c1,c2,c3 = st.columns(3)
        c1.download_button("Exporter WORD", export_docx(st.session_state["offre_fin"], "Offre_Financiere"), f"Offre_Financiere_{client}.docx")
        c2.download_button("Exporter EXCEL", export_excel_financiere(), f"Offre_Financiere_{client}.xlsx")
        c3.download_button("Exporter PDF", export_pdf(st.session_state["offre_fin"], "Offre_Financiere"), f"Offre_Financiere_{client}.pdf")

with tab3:
    st.header("Bouton DAO / Cahier des Charges")
    if st.button("Générer DAO Pro", type="primary", key="b3"):
        with st.spinner("Redaction DAO BCEAO/UEMOA..."):
            if "Avec Chat IA" in mode:
                prompt = f"GENERE DAO/CAHIER DES CHARGES PRO conforme BCEAO UEMOA + ISO 27001:2022 + ISO 42001:2023 pour {client}. Clauses admin + tech + criteres eval."
                result = ai.generate(prompt, kb_ctx, tdr_raw)
            else:
                result = generate_dao_content(client, cabinet, tdr_dict)
            st.session_state["dao"]=result
    if "dao" in st.session_state:
        st.markdown(st.session_state["dao"])
        col1,col2 = st.columns(2)
        col1.download_button("Exporter WORD", export_docx(st.session_state["dao"], "DAO"), f"DAO_{client}.docx")
        col2.download_button("Exporter PDF", export_pdf(st.session_state["dao"], "DAO"), f"DAO_{client}.pdf")

with tab4:
    st.header("Bouton Demarrer Mission Audit - De bout en bout - Section par section")
    st.info("Vu le volume, generation section par section pour efficacite. Background: CISO Big Four 50 ans exp, +500 missions Afrique BCEAO/COBAC, Europe NIS2/DORA, USA NIST/SOC2, Certs ISO 27001 LA, 42001 LA, 22301 LA, CISA CISM CISSP-ISSAP CRISC EBIOS RM OSCP OSEP PNPT SABSA")
    
    phases = ["A_CADRAGE - Cadrage & Lancement RACI","B_CARTO - Etat existant & Carto actifs + Registre IA Art.49","C_RISQUES - Analyse risques EBIOS RM + Pentest PTES/WSTG/LLM","D_GAP - Gap Analysis Matrice croisee 2026","E_REMEDIATION - Plan action XOF + 10 Livrables"]
    
    selected = st.selectbox("Choisir phase a generer", phases)
    key = selected.split(" - ")[0]
    
    if st.button(f"Générer {selected}", type="primary"):
        with st.spinner(f"Generation {selected}..."):
            if "Avec Chat IA" in mode:
                prompt = f"MISSION AUDIT - GENERE UNIQUEMENT SECTION {selected} pour {client} par {cabinet}. Respecte normes: ISO 27001:2022 Clause exacte + ISO 42001:2023 Clause exacte + NIS2 Art + DORA Art + PCI DSS 4.0.1 + BCEAO Art34 + MITRE ATT&CK + CVSS v4.0. Donne templates, check-lists [ ], RACI, commandes arsenal. Background CISO 50 ans exp. TDR:{tdr_raw[:3000]} KB:{kb_ctx[:5000]}"
                result = ai.generate(prompt, kb_ctx, tdr_raw)
            else:
                result = generate_audit_section(key, client, cabinet, tdr_dict, kb_ctx)
            st.session_state[f"audit_{key}"]=result
    
    # Affichage historique sections
    for p in phases:
        k = p.split(" - ")[0]
        if f"audit_{k}" in st.session_state:
            with st.expander(f"✅ {p}", expanded=(k==key)):
                st.markdown(st.session_state[f"audit_{k}"])
                c1,c2 = st.columns(2)
                c1.download_button(f"WORD {k}", export_docx(st.session_state[f"audit_{k}"], k), f"{k}_{client}.docx", key=f"docx_{k}")
                c2.download_button(f"PDF {k}", export_pdf(st.session_state[f"audit_{k}"], k), f"{k}_{client}.pdf", key=f"pdf_{k}")
    
    if any(f"audit_{p.split(' - ')[0]}" in st.session_state for p in phases):
        if st.button("Fusionner tout en rapport final"):
            full_report = "\n\n".join([st.session_state.get(f"audit_{p.split(' - ')[0]}","") for p in phases])
            st.session_state["audit_full"]=full_report
            st.download_button("Rapport Complet WORD", export_docx(full_report,"Rapport_Audit_Complet"), f"Rapport_Audit_Complet_{client}.docx")
            st.download_button("Rapport Complet PDF", export_pdf(full_report,"Rapport_Audit_Complet"), f"Rapport_Audit_Complet_{client}.pdf")

with tab5:
    st.header("Bouton Certification - Accompagnement bout en bout")
    norme = st.selectbox("Choisis la norme cible", ["ISO 27001:2022","ISO 42001:2023","ISO 9001:2015","ISO 22301:2019","PCI DSS 4.0.1","SOC 2","NIS2","DORA"])
    if st.button(f"Demarrer accompagnement {norme}", type="primary"):
        with st.spinner(f"Roadmap certification {norme}..."):
            if "Avec Chat IA" in mode:
                prompt = f"GENERE ROADMAP CERTIFICATION BOUT EN BOUT pour {norme} pour {client} par {cabinet}. Workflow: Gap Analysis -> Mise en conformite -> Documentation -> Implementation -> Audit blanc ISO 19011 -> Accompagnement final certificateur. Chiffrage XOF + delais + templates + RACI + clauses exactes {norme}. TDR:{tdr_raw[:2000]} KB:{kb_ctx[:3000]}"
                result = ai.generate(prompt, kb_ctx, tdr_raw)
            else:
                result = generate_certification_roadmap(norme, client, cabinet)
            st.session_state[f"cert_{norme}"]=result
    if f"cert_{norme}" in st.session_state:
        st.markdown(st.session_state[f"cert_{norme}"])
        st.download_button("Exporter WORD", export_docx(st.session_state[f"cert_{norme}"], f"Certif_{norme}"), f"Certification_{norme}_{client}.docx")
