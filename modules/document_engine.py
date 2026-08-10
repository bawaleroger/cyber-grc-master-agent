
import re
from pypdf import PdfReader
NORMES_KEYWORDS = {"ISO 27001:2022": ["27001","isms","annexe a"],"ISO 42001:2023": ["42001","ia","llm","modele"],"NIS2": ["nis2","2022/2555"],"DORA": ["dora","2022/2554"],"RGPD": ["rgpd","gdpr","dpia"],"PCI DSS 4.0.1": ["pci","dss"],"BCEAO": ["bceao","uemoa","cobac","lc/ft"],"NIST CSF 2.0": ["nist","csf"]}
def extract_text(file):
    try:
        if file.name.endswith(".pdf"):
            reader = PdfReader(file)
            return "\n".join([p.extract_text() or "" for p in reader.pages])
        elif file.name.endswith(".docx"):
            import docx
            doc = docx.Document(file)
            return "\n".join([p.text for p in doc.paragraphs])
        else:
            return file.getvalue().decode("utf-8", errors="ignore")
    except Exception as e:
        return f"[ERREUR {e}]"
def classify_document(text):
    tl=text.lower()
    scores={k:sum(1 for kw in v if kw in tl) for k,v in NORMES_KEYWORDS.items()}
    best=max(scores, key=scores.get)
    if scores[best]==0: best="GENERAL GRC"
    is_tdr=any(w in tl for w in ["termes de reference","tdr","objet de la mission","perimetre"])
    dtype="TDR" if is_tdr else "REFERENTIEL"
    return dtype,best,scores
def parse_tdr(text):
    import re
    return {"objectif": text[:500],"perimetre": "A definir selon TDR","secteur": "Finance" if "bceao" in text.lower() or "banque" in text.lower() else "Multi","normes": [k for k,v in NORMES_KEYWORDS.items() if any(kw in text.lower() for kw in v)],"livrables": ["Rapport audit","Gap analysis","Plan action"],"contraintes": "Delais regulateur"}
