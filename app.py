
import streamlit as st, os, io
from pathlib import Path
from modules.persistence import init_db, save_document, get_all_docs, get_kb_only, get_kb_context, save_tdr, get_latest_tdr, clear_all, DB_PATH
from modules.document_engine import extract_text, classify_document, parse_tdr
from modules.ai_client import ai
from modules.report_generator import generate_offre_technique_content, generate_offre_financiere_content, generate_dao_content, generate_audit_section, generate_certification_roadmap
import pandas as pd

st.set_page_config(page_title="CYBER-GRC MASTER V5", page_icon="🛡️", layout="wide")
db_path = init_db()

def export_docx(text, title):
    from docx import Document
    doc = Document()
    doc.add_heading(title, 0)
    for para in text.split("\n"):
        p=para.strip()
        if p.startswith("# "): doc.add_heading(p.replace("# ",""),1)
        elif p.startswith("## "): doc.add_heading(p.replace("## ",""),2)
        else: doc.add_paragraph(para)
    bio=io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

def export_pdf(text, title):
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    bio=io.BytesIO()
    doc=SimpleDocTemplate(bio, pagesize=A4)
    styles=getSampleStyleSheet()
    story=[Paragraph(f"<b>{title}</b>",styles['Title']),Spacer(1,12)]
    for line in text.split("\n")[:600]:
        if line.strip():
            story.append(Paragraph(line[:500].replace("<","&lt;"),styles['Normal']))
            story.append(Spacer(1,4))
    doc.build(story)
    return bio.getvalue()

def export_excel_kit():
    df=pd.DataFrame([["DOC-001","Organigramme","ORG","Critique","J3","DG","ISO 27001 A.5.2"]],columns=["ID","Doc","Type","Crit","Delai","Resp","Norme"])
    bio=io.BytesIO()
    with pd.ExcelWriter(bio, engine='openpyxl') as w:
        df.to_excel(w, sheet_name='ERL_150', index=False)
    return bio.getvalue()

if "tdr_dict" not in st.session_state:
    latest=get_latest_tdr()
    if latest:
        st.session_state["tdr_dict"]=latest["tdr_dict"]
        st.session_state["tdr_raw"]=latest["raw_text"]
        st.session_state["client"]=latest["client"]
        st.session_state["cabinet"]=latest["cabinet"]
        st.session_state["tdr_loaded_from_db"]=True

st.sidebar.title("🛡️ CYBER-GRC MASTER V5")
st.sidebar.caption(f"DB: {DB_PATH} Persistant Fix")

client=st.sidebar.text_input("CLIENT", st.session_state.get("client","BCEAO BANK UEMOA"))
cabinet=st.sidebar.text_input("CABINET", st.session_state.get("cabinet","CYBER-GRC CONSULTING"))
st.session_state["client"]=client
st.session_state["cabinet"]=cabinet

st.sidebar.divider()
st.sidebar.subheader("ETAPE 1: TDRs")
tdr_files=st.sidebar.file_uploader("A. TDR / DAO", accept_multiple_files=True, type=["pdf","docx","txt"], key="tdr_upl")
if st.sidebar.button("Ingerer TDRs"):
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
        st.sidebar.success("TDR sauvegarde - survivra au refresh!")
        st.rerun()

st.sidebar.divider()
st.sidebar.subheader("B. Base Connaissance PERMANENTE")
st.sidebar.markdown("Reste apres refresh/reboot")
kb_files=st.sidebar.file_uploader("B. Docs pour nourrir", accept_multiple_files=True, type=["pdf","docx","txt"], key="kb_upl")
if st.sidebar.button("🧠 Nourrir Base KB"):
    cnt=0
    for f in kb_files or []:
        txt=extract_text(f)
        dtype,best,_=classify_document(txt)
        save_document(f.name, txt, dtype, best, client, is_kb=True)
        cnt+=1
    if cnt>0:
        st.sidebar.success(f"✅ {cnt} docs KB ajoutes permanents!")
        st.rerun()

docs_all=get_all_docs()
docs_kb=get_kb_only()
st.sidebar.metric("Total Docs DB", len(docs_all))
st.sidebar.metric("KB permanente", len(docs_kb))
if docs_all:
    with st.sidebar.expander(f"Voir {len(docs_all)} docs persistants"):
        for fn, dtype, norme, date, cli, size, is_kb in docs_all[:20]:
            st.write(f"{'🧠' if is_kb else '📄'} {fn[:30]} | {norme}")

if st.sidebar.button("Vider base"):
    clear_all()
    st.session_state.clear()
    st.rerun()

st.sidebar.divider()
mode=st.sidebar.radio("Mode", ["Avec Chat IA (Groq/OpenAI)", "Sans IA locale"])
api_key=st.sidebar.text_input("Cle API temp", type="password")
if api_key: os.environ["GROQ_API_KEY"]=api_key
st.sidebar.caption(f"Mode:{ai.mode.upper()} | KB:{len(get_kb_context(1000))} chars")

st.title("CYBER-GRC MASTER V5 - Fix ModuleNotFoundError + Persistence")
st.markdown(f"**CLIENT:** {client} | **CABINET:** {cabinet} | **KB:** {len(docs_kb)} docs permanents | **Total:** {len(docs_all)}")

if st.session_state.get("tdr_loaded_from_db"):
    st.success(f"✅ TDR recharge auto depuis DB apres refresh!")

if "tdr_dict" not in st.session_state:
    st.warning("👈 Charge TDR en A. puis Ingerer. B. reste permanente meme apres refresh.")
    if docs_kb:
        st.dataframe(pd.DataFrame(docs_kb, columns=["Fichier","Type","Norme","Date","Client"]))
    st.stop()

tdr_dict=st.session_state["tdr_dict"]
kb_ctx=get_kb_context(25000)
tdr_raw=st.session_state.get("tdr_raw","")

tab1,tab2,tab3,tab4,tab5=st.tabs(["📄 OFFRE TECHNIQUE","💰 FINANCIERE","📘 DAO","🚀 AUDIT BOUT EN BOUT","🏅 CERTIFICATION"])

with tab1:
    st.header("Offre Technique Full")
    st.caption(f"KB:{len(kb_ctx)} chars de {len(docs_all)} docs persistants")
    if st.button("Generer Offre Technique", type="primary", key="b1"):
        with st.spinner("Redaction..."):
            if "Avec Chat IA" in mode:
                result=ai.generate(f"OFFRE TECHNIQUE COMPLETE pour {client} TDR:{tdr_raw[:5000]} KB:{kb_ctx[:7000]}", kb_ctx, tdr_raw)
            else:
                result=generate_offre_technique_content(client,cabinet,tdr_dict,kb_ctx)
            st.session_state["offre_tech"]=result
    if "offre_tech" in st.session_state:
        st.markdown(st.session_state["offre_tech"])
        c1,c2,c3=st.columns(3)
        c1.download_button("WORD", export_docx(st.session_state["offre_tech"],"Offre_Technique"), f"Offre_Technique_{client}.docx")
        c2.download_button("PDF", export_pdf(st.session_state["offre_tech"],"Offre_Technique"), f"Offre_Technique_{client}.pdf")
        c3.download_button("KIT Excel", export_excel_kit(), f"KIT_{client}.xlsx")

with tab2:
    st.header("Offre Financiere")
    if st.button("Generer Financiere", type="primary", key="b2"):
        if "Avec Chat IA" in mode:
            result=ai.generate(f"OFFRE FINANCIERE XOF pour {client} TDR:{tdr_raw[:3000]}", kb_ctx, tdr_raw)
        else:
            result=generate_offre_financiere_content(client,cabinet,tdr_dict)
        st.session_state["offre_fin"]=result
    if "offre_fin" in st.session_state:
        st.markdown(st.session_state["offre_fin"])
        st.download_button("WORD", export_docx(st.session_state["offre_fin"],"Financiere"), f"Fin_{client}.docx")

with tab3:
    st.header("DAO")
    if st.button("Generer DAO", type="primary", key="b3"):
        if "Avec Chat IA" in mode:
            result=ai.generate(f"DAO BCEAO pour {client} TDR:{tdr_raw[:4000]}", kb_ctx, tdr_raw)
        else:
            result=generate_dao_content(client,cabinet,tdr_dict)
        st.session_state["dao"]=result
    if "dao" in st.session_state:
        st.markdown(st.session_state["dao"])
        st.download_button("WORD DAO", export_docx(st.session_state["dao"],"DAO"), f"DAO_{client}.docx")

with tab4:
    st.header("Mission Audit Bout en Bout")
    st.info(f"Nourri par {len(docs_kb)} docs KB permanente")
    phases=["A_CADRAGE - Kit Cadrage","B_CARTO - Carto+IA","C_RISQUES - EBIOS+Pentest","D_GAP - Gap 2026","E_REMEDIATION - 10 Livrables"]
    sel=st.selectbox("Phase", phases)
    key=sel.split(" - ")[0]
    if st.button(f"Generer {sel}", type="primary"):
        if "Avec Chat IA" in mode:
            result=ai.generate(f"AUDIT {sel} pour {client} TDR:{tdr_raw[:5000]} KB:{kb_ctx[:7000]}", kb_ctx, tdr_raw)
        else:
            result=generate_audit_section(key, client, cabinet, tdr_dict, kb_ctx)
        st.session_state[f"audit_{key}"]=result
    for p in phases:
        k=p.split(" - ")[0]
        if f"audit_{k}" in st.session_state:
            with st.expander(f"✅ {p}", expanded=(k==key)):
                st.markdown(st.session_state[f"audit_{k}"])
                st.download_button(f"WORD {k}", export_docx(st.session_state[f"audit_{k}"], k), f"{k}_{client}.docx", key=f"w_{k}")

with tab5:
    st.header("Certification")
    norme=st.selectbox("Norme", ["ISO 27001:2022","ISO 42001:2023","ISO 9001:2015","ISO 22301:2019","PCI DSS 4.0.1","SOC 2","NIS2","DORA"])
    if st.button(f"Demarrer {norme}", type="primary"):
        if "Avec Chat IA" in mode:
            result=ai.generate(f"CERTIFICATION {norme} pour {client}", kb_ctx, tdr_raw)
        else:
            result=generate_certification_roadmap(norme, client, cabinet)
        st.session_state[f"cert_{norme}"]=result
    if f"cert_{norme}" in st.session_state:
        st.markdown(st.session_state[f"cert_{norme}"])
