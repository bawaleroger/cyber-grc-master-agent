
import re
from pathlib import Path

CLASSIFICATION_RULES = {
    "TDR": [r"\bTDR\b", r"termes de reference", r"term of reference", r"ToR"],
    "DAO": [r"\bDAO\b", r"dossier d'appel d'offre", r"appel d'offres", r"RFP", r"cahier des charges"],
    "OFFRE_TECHNIQUE": [r"offre technique", r"proposition technique", r"technical proposal"],
    "OFFRE_FINANCIERE": [r"offre financiere", r"proposition financiere", r"financial proposal", r"XOF"],
    "RAPPORT_AUDIT": [r"rapport d'audit", r"audit report", r"rapport final"],
    "PSSI": [r"PSSI", r"politique de securite", r"security policy"],
    "REGISTRE_RISQUES": [r"registre des risques", r"risk register", r"analyse de risques"],
    "COURS": [r"\bcours\b", r"\bTD\b", r"\bTP\b", r"support de cours", r"formation"],
    "POLITIQUE": [r"politique", r"procedure", r"charte"],
}

def classify_document(filename: str, text_snippet: str = "") -> str:
    haystack = f"{filename} {text_snippet}".lower()
    scores = {}
    for cat, patterns in CLASSIFICATION_RULES.items():
        score = sum(1 for pat in patterns if re.search(pat, haystack, re.IGNORECASE))
        if score > 0:
            scores[cat] = score
    if not scores:
        return "AUTRE"
    return max(scores, key=scores.get)

def ensure_folder_structure(base_path: Path, classification: str) -> Path:
    target = base_path / "data" / "documents" / classification
    target.mkdir(parents=True, exist_ok=True)
    return target
