
import re
from pypdf import PdfReader
NORMES_KEYWORDS = {
    "ISO 27001:2022": ["27001","isms","annexe a","soa"],
    "ISO 42001:2023": ["42001","ia responsable","llm","modele ia","ai act"],
    "NIS2": ["nis2","2022/2555"],
    "DORA": ["dora","2022/2554"],
    "RGPD": ["rgpd","gdpr","art.30","art.35"],
    "PCI DSS 4.0.1": ["pci","dss"],
    "BCEAO/UEMOA": ["bceao","uemoa","cobac","beac","art.34"],
    "KIT DE CADRAGE": ["kit de cadrage","pv de cadrage","raci","gantt"]
}
def extract_text(file):
    text=""
    try:
        if file.name.endswith(".pdf"):
            reader = PdfReader(file)
            for p in reader.pages: text+= (p.extract_text() or "") + "\n"
        elif file.name.endswith(".docx"):
            import docx
            doc = docx.Document(file)
            for para in doc.paragraphs: text+= para.text + "\n"
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells: text+= cell.text + " | "
                    text+= "\n"
        else:
            text = file.getvalue().decode("utf-8", errors="ignore")
    except Exception as e:
        text = f"[ERREUR {file.name}: {e}]"
    import re
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text

def classify_document(text):
    tl=text.lower()
    scores={k:sum(1 for kw in v if kw.lower() in tl) for k,v in NORMES_KEYWORDS.items()}
    best=max(scores, key=scores.get) if scores else "GENERAL GRC"
    if scores.get(best,0)==0: best="GENERAL GRC"
    if any(x in tl for x in ["termes de reference","t.d.r","dao","cahier des charges"]): dtype="TDR/DAO"
    elif "kit de cadrage" in tl or "taches a faire" in tl: dtype="KIT CADRAGE"
    else: dtype="LIVRABLE / PREUVE"
    return dtype,best,scores

def parse_tdr(text):
    clean=text.strip()
    import re
    m=re.search(r'(KIT DE CADRAGE.*)', clean, re.I|re.S)
    obj = m.group(1)[:1500] if m else clean[:1000]
    obj = re.sub(r'\s+', ' ', obj)
    perim="SI complet + Cloud + AD + IA + Prestataires + SWIFT + Monétique GIM-UEMOA [BCEAO/UEMOA]"
    secteur="Finance / Banque UEMOA" if "bceao" in clean.lower() or "bank" in clean.lower() else "Multi-secteur critique"
    normes=[]
    for norme,kws in NORMES_KEYWORDS.items():
        if norme=="KIT DE CADRAGE": continue
        if any(kw.lower() in clean.lower() for kw in kws): normes.append(norme)
    if not normes: normes=["ISO 27001:2022","ISO 42001:2023","NIS2","DORA","BCEAO/UEMOA","PCI DSS 4.0.1"]
    livrables=[]
    for line in clean.split("\n"):
        line=line.strip()
        if 5<len(line)<120 and any(k in line.lower() for k in ["rapport","pv","lettre","raci","gantt","liste","matrice","questionnaire"]):
            livrables.append(line)
    if not livrables: livrables=["Rapport de Cadrage","PV de Reunion","Lettre + LDD 150","RACI + Gantt Excel","Questionnaire 350Q","Matrice Gap","Registre Risques"]
    return {"objectif":obj,"perimetre":perim,"secteur":secteur,"normes":normes,"livrables":livrables,"contraintes":"Delais regulateur + Confidentialite"}
