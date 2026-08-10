
import streamlit as st, os, io, gc
from pathlib import Path

# Config page early
st.set_page_config(page_title="CYBER-GRC MASTER V6 LIGHT", page_icon="🛡️", layout="wide")

from modules.persistence import init_db, save_document, get_all_docs, get_kb_only, get_kb_context, save_tdr, get_latest_tdr, clear_all, DB_PATH
from modules.document_engine import extract_text, classify_document, parse_tdr
from modules.ai_client import ai

# Lazy imports to save memory
@st.cache_resource
def get_db():
    return init_db()

def export_docx_light(text, title):
    from docx import Document
    doc = Document()
    doc.add_heading(title, 0)
    # Limite a 300 lignes pour economiser RAM
    for para in text.split("\n")[:300]:
        doc.add_paragraph(para[:500])
    bio = io.BytesIO()
    doc.save(bio)
    return bio.getvalue()

def export_excel_kit():
    import pandas as pd
    df = pd.DataFrame([["DOC-001","Organigramme","ORG","Critique"]], columns=["ID","Doc","Type","Crit"])
    bio = io.BytesIO()
    with pd.ExcelWriter(bio, engine='openpyxl') as w:
        df.to_excel(w, index=False)
    return bio.getvalue()

# Init DB
get_db()

# Auto-reload TDR apres refresh
if "tdr_dict" not in st.session_state:
    latest = get_latest_tdr()
    if latest:
        st.session_state["tdr_dict"] = latest["tdr_dict"]
        st.session_state["tdr_raw"] = latest["raw_text"]
        st.session_state["client"] = latest["client"]
        st.session_state["cabinet"] = latest["cabinet"]

# Sidebar
st.sidebar.title("🛡️ CYBER-GRC V6 LIGHT")
st.sidebar.caption("Fix: Memory <1GB + Persistence")

client = st.sidebar.text_input("CLIENT", st.session_state.get("client","BCEAO BANK UEMOA"))
cabinet = st.sidebar.text_input("CABINET", st.session_state.get("cabinet","CYBER-GRC CONSULTING"))
st.session_state["client"]=client
st.session_state["cabinet"]=cabinet

st.sidebar.divider()
st.sidebar.subheader("ETAPE 1: TDRs")
tdr_files = st.sidebar.file_uploader("A. TDR / DAO", accept_multiple_files=True, type=["pdf","docx","txt"], key="tdr_upl")
if st.sidebar.button("Ingerer TDRs"):
    full=""
    for f in tdr_files or []:
        txt = extract_text(f)
        full+=txt+"\n"
        dtype,best,_ = classify_document(txt)
        save_document(f.name, txt[:15000], dtype, best, client, is_kb=False)  # limite taille
        st.sidebar.success(f"{f.name} -> {best}")
    if full:
        tdr_dict = parse_tdr(full)
        save_tdr(client,cabinet,tdr_dict,full[:15000])
        st.session_state["tdr_dict"]=tdr_dict
        st.session_state["tdr_raw"]=full[:15000]
        st.sidebar.success("TDR sauvegarde!")
        st.rerun()

st.sidebar.divider()
st.sidebar.subheader("B. Base Connaissance PERMANENTE")
st.sidebar.markdown("Reste apres refresh")
kb_files = st.sidebar.file_uploader("B. Docs KB", accept_multiple_files=True, type=["pdf","docx","txt"], key="kb_upl")
if st.sidebar.button("🧠 Nourrir KB"):
    cnt=0
    for f in kb_files or []:
        txt = extract_text(f)
        # Limite memoire: coupe a 10000 chars max par doc
        txt = txt[:10000]
        dtype,best,_ = classify_document(txt)
        save_document(f.name, txt, dtype, best, client, is_kb=True)
        cnt+=1
        # Libere memoire
        del txt
        gc.collect()
    if cnt>0:
        st.sidebar.success(f"✅ {cnt} docs KB permanents!")
        st.rerun()

docs_all = get_all_docs()
docs_kb = get_kb_only()
st.sidebar.metric("Total Docs", len(docs_all))
st.sidebar.metric("KB permanente", len(docs_kb))

if st.sidebar.button("Vider base"):
    clear_all()
    st.session_state.clear()
    gc.collect()
    st.rerun()

st.sidebar.divider()
mode = st.sidebar.radio("Mode", ["Avec Chat IA (Groq)", "Sans IA locale"])
api_key = st.sidebar.text_input("Cle API", type="password")
if api_key: os.environ["GROQ_API_KEY"]=api_key
st.sidebar.caption(f"Mode:{ai.mode.upper()} | RAM optimise")

# Main
st.title("CYBER-GRC MASTER V6 LIGHT - Fix Resource Limits")
st.markdown(f"**CLIENT:** {client} | **CABINET:** {cabinet} | **KB:** {len(docs_kb)} docs | **Fix:** <1GB RAM")

if "tdr_dict" not in st.session_state:
    st.warning("👈 Charge TDR en A. puis Ingerer. B. reste permanente.")
    if docs_kb:
        import pandas as pd
        st.dataframe(pd.DataFrame(docs_kb, columns=["Fichier","Type","Norme","Date","Client"]))
    st.stop()

tdr_dict = st.session_state["tdr_dict"]
# Limite contexte KB a 8000 chars max pour economiser RAM
kb_ctx = get_kb_context(8000)
tdr_raw = st.session_state.get("tdr_raw","")[:8000]

from modules.report_generator import generate_offre_technique_content, generate_offre_financiere_content, generate_dao_content, generate_audit_section, generate_certification_roadmap

tab1,tab2,tab3,tab4,tab5 = st.tabs(["📄 TECHNIQUE","💰 FINANCIERE","📘 DAO","🚀 AUDIT","🏅 CERTIF"])

with tab1:
    st.header("Offre Technique Full")
    st.caption(f"KB: {len(kb_ctx)} chars (limite 8k pour RAM)")
    if st.button("Generer Offre Technique", type="primary", key="b1"):
        with st.spinner("Redaction..."):
            if "Avec Chat IA" in mode:
                result = ai.generate(f"OFFRE TECHNIQUE COMPLETE BIG FOUR pour {client} TDR:{tdr_raw[:3000]} KB:{kb_ctx[:3000]}", kb_ctx, tdr_raw)
            else:
                result = generate_offre_technique_content(client,cabinet,tdr_dict,kb_ctx)
            st.session_state["offre_tech"]=result
    if "offre_tech" in st.session_state:
        st.markdown(st.session_state["offre_tech"])
        st.download_button("WORD", export_docx_light(st.session_state["offre_tech"],"Offre_Technique"), f"Offre_Technique_{client}.docx")
        st.download_button("KIT Excel", export_excel_kit(), f"KIT_{client}.xlsx")

with tab2:
    st.header("Financiere XOF")
    if st.button("Generer Financiere", type="primary", key="b2"):
        if "Avec Chat IA" in mode:
            result = ai.generate(f"OFFRE FINANCIERE XOF pour {client}", kb_ctx, tdr_raw)
        else:
            result = generate_offre_financiere_content(client,cabinet,tdr_dict)
        st.session_state["offre_fin"]=result
    if "offre_fin" in st.session_state:
        st.markdown(st.session_state["offre_fin"])
        st.download_button("WORD", export_docx_light(st.session_state["offre_fin"],"Financiere"), f"Fin_{client}.docx")

with tab3:
    st.header("DAO")
    if st.button("Generer DAO", type="primary", key="b3"):
        if "Avec Chat IA" in mode:
            result = ai.generate(f"DAO BCEAO pour {client} TDR:{tdr_raw[:3000]}", kb_ctx, tdr_raw)
        else:
            result = generate_dao_content(client,cabinet,tdr_dict)
        st.session_state["dao"]=result
    if "dao" in st.session_state:
        st.markdown(st.session_state["dao"])
        st.download_button("WORD DAO", export_docx_light(st.session_state["dao"],"DAO"), f"DAO_{client}.docx")

with tab4:
    st.header("Audit Bout en Bout - Section par Section")
    phases=["A_CADRAGE - Kit Cadrage","B_CARTO - Carto+IA","C_RISQUES - EBIOS+Pentest","D_GAP - Gap 2026","E_REMEDIATION - 10 Livrables"]
    sel=st.selectbox("Phase", phases)
    key=sel.split(" - ")[0]
    if st.button(f"Generer {sel}", type="primary"):
        if "Avec Chat IA" in mode:
            result = ai.generate(f"AUDIT {sel} pour {client} TDR:{tdr_raw[:3000]} KB:{kb_ctx[:3000]}", kb_ctx, tdr_raw)
        else:
            result = generate_audit_section(key, client, cabinet, tdr_dict, kb_ctx)
        st.session_state[f"audit_{key}"]=result
    for p in phases:
        k=p.split(" - ")[0]
        if f"audit_{k}" in st.session_state:
            with st.expander(f"✅ {p}", expanded=(k==key)):
                st.markdown(st.session_state[f"audit_{k}"])
                st.download_button(f"WORD {k}", export_docx_light(st.session_state[f"audit_{k}"], k), f"{k}_{client}.docx", key=f"w_{k}")

with tab5:
    st.header("Certification")
    norme=st.selectbox("Norme", ["ISO 27001:2022","ISO 42001:2023","PCI DSS 4.0.1","SOC 2","NIS2","DORA"])
    if st.button(f"Demarrer {norme}", type="primary"):
        if "Avec Chat IA" in mode:
            result = ai.generate(f"CERTIFICATION {norme} pour {client}", kb_ctx, tdr_raw)
        else:
            result = generate_certification_roadmap(norme, client, cabinet)
        st.session_state[f"cert_{norme}"]=result
    if f"cert_{norme}" in st.session_state:
        st.markdown(st.session_state[f"cert_{norme}"])
