
from io import BytesIO
import pandas as pd

def local_fallback(user_prompt, kb_context, tdr_context):
    # Fallback kept simple, main generation via ai_client
    return f"""# CYBER-GRC MASTER LOCAL\n\nDemande: {user_prompt}\n\nKB: {len(kb_context)} chars\nTDR: {tdr_context[:500]}\n\nMode local - configure GROQ_API_KEY pour livrable complet Big Four."""

def generate_offre_technique_content(client, cabinet, tdr_dict, kb_ctx):
    return f"""
# OFFRE TECHNIQUE - AUDIT CYBERSECURITE & GRC & IA RESPONSABLE
**CLIENT: {client} | CABINET: {cabinet} | REF: {tdr_dict.get('secteur','Finance')} - ISO 27001:2022 + ISO 42001:2023**

## 1. COMPREHENSION TDR & OBJECTIFS
{tdr_dict.get('objectif','Audit complet SMSI + SIA + Conformite BCEAO/UEMOA + NIS2/DORA')[:800]}

Perimetre: {tdr_dict.get('perimetre','SI complet + IA + Cloud + OT')}
Normes cibles detectees: {', '.join(tdr_dict.get('normes',[])) if tdr_dict.get('normes') else 'ISO 27001:2022, ISO 42001:2023, NIS2, DORA, PCI DSS 4.0.1, BCEAO Art.34'}

## 2. METHODOLOGIE BIG FOUR - ISO 19011:2018 + EBIOS RM v1.5
Phase 0: Cadrage & Lancement [ISO 27001 Cl.5 + ISO 42001 Cl.5 + A.5.2]
Phase 0.B: Plan Mission RACI, Matrice Escalade, Outils Collecte, Gouvernance SMSI/SIA
Phase 1: Gap Analysis - Matrice croisee format 2026: [ACTION] -> ISO 27001 [Clause] + ISO 42001 [Clause] + NIS2 Art. + PCI + BCEAO
Phase 2: Audit Technique PTES + OWASP WSTG 4.2 + ASVS 4.0.3 + LLM Top10 2025 + MITRE ATT&CK v15
Phase 3: Redaction PSSI, SoA, Registre Risques ISO 27005 + ISO 23894, Registre IA AI Act Art.49, DPIA RGPD Art.35
Phase 5: Forensic ISO 27037/27042/27043
Phase 6: 10 Livrables certifiables

## 3. ARSENAL TECHNIQUE - COMMANDES DETAILLEES
```bash
# OSINT
theHarvester -d {client.lower().replace(' ','')} -b all -l 500
maltego -d {client}
# Reseau/AD
nmap -sV -sC -p- --script vuln 10.0.0.0/24
pingcastle --healthcheck --server
bloodhound-python -d lab.local -u audit -p P@ss --zip
# Vuln
nessus-cli scan --targets {client}
nuclei -t cves/ -u https://{client.lower()}.com
burp --project-file audit.burp
# SAST/Secrets/Shadow AI
semgrep --config=auto --error
trufflehog filesystem . --only-verified
python shadow_ai_detector.py --proxy-logs squid.log --detect openai,anthropic,huggingface
```

## 4. EQUIPE & CERTIFICATIONS
CISO Principal: ISO 27001 LA, ISO 42001 LA, ISO 22301 LA, CISA, CISM, CISSP-ISSAP, CRISC, EBIOS RM LRM, OSCP/OSEP/OSWE, PNPT, SABSA
RSSI Adjoint: ISO 27001 LI, CISM, CEH Master
DPO: CDPSE, CIPP/E, ISO 27701:2025 LA
Forensic: GCFA, CHFI
Pentest: OSCP, OSEP, CRTO

## 5. PLANNING & RACI
| Phase | Duree | R | A | C | I |
|-------|-------|---|---|---|---|
| Cadrage | 5j | RSSI {client} | DG | DPO | Metiers |
| Carto actifs + Registre IA | 10j | Auditeur | RSSI | AI Officer | DSI |
| Audit technique | 15j | Pentester | CISO | DSI | - |
| Gap + Recommandations | 10j | CISO | DG | RSSI/DPO | COMEX |

## 6. LIVRABLES GARANTIS (0 reprise)
1. Executive Summary DG 1 page Risque Business + Risque IA [ISO 27001 Cl.9.3 + ISO 42001 Cl.9.3]
2. Rapport RSSI/DPO 100+ pages source article par article
3. PSSI, SoA, Registre Risques, Registre IA B.7.4
4. Plan traitement vuln Quick Wins/90j/12mois CVSS v4.0
5. Schema Directeur 3 ans chiffre XOF

Contexte KB interne utilise: {len(kb_ctx)} chars de preuves
"""

def generate_offre_financiere_content(client, cabinet, tdr_dict):
    return f"""
# OFFRE FINANCIERE DETAILLEE - DEVISE XOF
**CLIENT: {client} | CABINET: {cabinet}**

| Phase | Description | JH Senior | JH Junior | PU Senior XOF | PU Junior XOF | Total XOF |
|-------|-------------|-----------|-----------|---------------|---------------|-----------|
| Phase 0 | Cadrage + RACI + Plan audit ISO 19011 | 5 | 3 | 750 000 | 350 000 | 4 800 000 |
| Phase 1 | Carto actifs ISO 27005 + EBIOS RM + Registre IA Art.49 | 10 | 8 | 750 000 | 350 000 | 10 300 000 |
| Phase 2 | Audit tech PTES/WSTG/LLM Top10 + SAST/SCA | 15 | 10 | 850 000 | 400 000 | 16 750 000 |
| Phase 3 | Gap Analysis + Matrice conformite 27001/42001/NIS2/PCI/BCEAO | 10 | 5 | 750 000 | 350 000 | 9 250 000 |
| Phase 4 | Redaction PSSI/SoA/Registres/DPIA/Politique IA A.2 | 12 | 8 | 750 000 | 350 000 | 11 800 000 |
| Phase 5 | Forensic readiness + Timeline | 3 | 2 | 800 000 | 400 000 | 3 200 000 |
| Phase 6 | Restitution + Plan action + Schema Dir 3 ans | 5 | 2 | 750 000 | 350 000 | 4 450 000 |
| **TOTAL HT** | | **60** | **38** | | | **60 550 000** |
| TVA UEMOA 18% | | | | | | 10 899 000 |
| **TOTAL TTC** | | | | | | **71 449 000 XOF** |

Delai: 50 jours ouvres. Validite offre: 90 jours. Modalites: 30% commande, 40% mi-parcours, 30% livraison finale.
"""

def generate_dao_content(client, cabinet, tdr_dict):
    return f"""
# DAO / CAHIER DES CHARGES - MISSION AUDIT CYBER-GRC-IA
**Pouvoir Adjudicateur: {client}**

Article 1 - Objet: Audit SMSI ISO 27001:2022 + SIA ISO 42001:2023 + Conformite NIS2/DORA/BCEAO
Article 2 - Perimetre: {tdr_dict.get('perimetre','SI complet')} + Cloud + IA generative + Prestataires
Article 3 - Normes exigibles: [ISO 27001:2022 Cl.4-10] [ISO 42001:2023 Cl.4-10 + Annexe A/B] [NIS2 Art.20-21] [DORA Art.11-13] [RGPD Art.32-35] [PCI DSS 4.0.1 Req 2,8,10] [BCEAO Instr. 007-09-2017 Art.34]
Article 4 - Livrables attendus: Voir Phase 6 - 10 documents Big Four
Article 5 - Profil prestataire: Certifications ISO 27001 LA + ISO 42001 LA + CISA/CISM/CISSP + EBIOS RM + Exp Afrique BCEAO/COBAC min 5 missions
Article 6 - Criteres evaluation: Technique 70% (Methodo 30%, Equipe 25%, References 15%), Financier 30%
Article 7 - Confidentialite + Chain of Custody SHA-256 [ISO 27037]
"""

def generate_audit_section(phase_key, client, cabinet, tdr_dict, kb_ctx):
    sections = {
        "A_CADRAGE": f"""
## PHASE A - CADRAGE & LANCEMENT [ISO 27001 Cl.5 + ISO 42001 Cl.5 + A.5.2 + NIS2 Art.20]
**Client: {client} | Cabinet: {cabinet}**

- **RACI Detaille:**
| Activite | R | A | C | I | Norme |
|----------|---|---|---|---|-------|
| Validation perimetre SMSI/SIA | RSSI {client} | DG | DPO, AI Officer | Metiers | ISO 27001 Cl.4.3 + ISO 42001 Cl.4.3 + AI Act Art.49 |
| Gouvernance IA | AI Officer | DG | DPO, RSSI | COMEX | ISO 42001 A.2.1 + A.5.2 |

- **Matrice Escalade:** Niveau 1: Chef projet {cabinet} -> RSSI {client} [24h] / Niveau 2: CISO {cabinet} -> DG {client} [48h] / Niveau 3: Associe {cabinet} -> CA {client}
- **Outils collecte:** ERL Evidence Request List 150 preuves [ISO 19011 Cl.6.3.2], Questionnaire 27001/42001/27002 300 questions, Template Registre IA B.3
- **Livrable A:** PV Kick-off + RACI signe + Planning Gantt Mermaid + ERL
""",
        "B_CARTO": f"""
## PHASE B - ETAT EXISTANT & CARTOGRAPHIE [ISO 27005 + EBIOS RM v1.5 + ISO 42001 B.3 + AI Act Art.49]

**Inventaire actifs:**
- Actifs SI: Serveurs, AD, FW, Cloud M365/AWS, OT si present [ISO 27001 A.5.9 + A.8.1]
- Actifs IA: Modeles LLM, RAG, Prompt templates, Donnees entrainement [ISO 42001 A.6.2.2 + B.3 + AI Act Art.49 + Annexe VIII]
- Shadow AI: Scan proxy logs -> detection API openai.com, anthropic, cohere, huggingface [ISO 42001 A.9.3 + A.10 + OWASP LLM10]
- Flux: DFD niveau 0/1 [OWASP ASVS 1.2]

**Maturite CMMI 0-5 + COBIT 2019:** Evalue sur 38 controles 27001 + 40 controles 42001

**KB interne exploite:** {len(kb_ctx)} chars

**Livrable B:** Registre Actifs + Registre Systemes IA (B.7.4) + DFD + Radar Maturite
""",
        "C_RISQUES": f"""
## PHASE C - ANALYSE RISQUES & AUDIT TECHNIQUE [ISO 27005:2022 + ISO 23894:2023 + EBIOS RM + MITRE ATLAS + PTES]

**EBIOS RM Workshop 1-5:**
- Socle securite, Sources risque, Biens supports, Evenements redoutes, Scenarios

**Scenarios techniques:**
- Attaque AD: Kerberoasting -> DCSync [MITRE ATT&CK T1558.003 + T1003.006] -> Impact Critique [CVSS 9.1] -> [ISO 27001 A.8.5 + NIS2 Art.21]
- Prompt Injection RAG: LLM01 OWASP -> Exfiltration donnees personnelles [RGPD Art.33 + AI Act Art.15 + ISO 42001 A.8.4]

**Pentest:**
- Interne/Externe PTES, OWASP WSTG 4.2, API Top10 2023, LLM Top10 2025
- SAST: SonarQube Quality Gate, Semgrep
- Secrets: TruffleHog, Gitleaks

**Audit RH:** Formation 27001 A7.2 + 42001 Cl.7.2/7.3, Phishing simulation

**Livrable C:** Registre Risques + Rapport Pentest + CVSS v4.0 + Chain ATT&CK
""",
        "D_GAP": f"""
## PHASE D - GAP ANALYSIS - MATRICE CROISEE FORMAT 2026 OBLIGATOIRE

Format: [ECART] -> ISO 27001:2022 [Clause] + ISO 42001:2023 [Clause] + [Autre Norme Art.]

Exemples audites pour {client}:
- MFA non generalise -> ISO 27001 A5.17 + A8.5 + ISO 42001 A.9.3 + NIS2 Art.20 + PCI DSS 8.4.3 + NIST PR.AC-1 + CIS 6.5 + BCEAO Art.34 => [Majeur]
- Usage ChatGPT non maitrise -> ISO 27001 A5.17 + ISO 42001 A.9.3 + EU AI Act Art.50 + OWASP LLM01 + ISO 42001 A.10 => [Critique] [PREUVE: logs proxy]
- Logs < 1 an -> ISO 27001 A8.15 + ISO 27018 12.4 + NIS2 Art.21 + PCI DSS 10.7 + DORA Art.12 => [Majeur]
- Absence Registre IA -> ISO 42001 B.3 + B.7.4 + AI Act Art.49 => [Critique] [Sanction AI Act 15M€ ou 3% CA]
- Pas de DPIA IA -> RGPD Art.35 + ISO 42001 B.7.2 + AI Act Art.27 => [Majeur]

Radar Charts: Conformite % par norme

Livrable D: Tableau ecarts [Conforme/Mineur/Majeur/Critique] + Radar
""",
        "E_REMEDIATION": f"""
## PHASE E - REMEDIATION & PLAN ACTION CHIFFRE XOF + LIVRABLES BIG FOUR

**10 Livrables:**
1. Executive Summary DG 1 page Risque Business + Risque IA [Cl.9.3]
2. Rapport RSSI/DPO 100+ pages source article par article
3. Reorg SI Tech/Metier/Humain/Strategie/Gouv IA [COBIT APO02]
4. PSSI + SoA + Politique IA A.2 + Procedure Cycle Vie IA A.6
5. Org cible + RACI incluant AI Officer, DPO, Data Steward [ISO 42001 A.5.2]
6. Plan traitement vuln Quick Wins/90j/12mois CVSS v4.0
7. Plan action chiffre XOF avec JH, delais, responsables
8. Estimation couts/priorites
9. Schema Directeur 3 ans SI/Cyber/IA Responsable chiffre
10. Tableau bord conformite % + Radar 27001+42001+NIS2+PCI + Attestation

**Gantt Mermaid:**
```mermaid
gantt
    title Plan Traitement {client}
    dateFormat YYYY-MM-DD
    section Quick Wins
    MFA partout :done, 2026-01-01, 15d
    Durcissement AD :active, 2026-01-16, 15d
    section 90j
    Registre IA Art49 :2026-02-01, 21d
    Politique IA A.2 :2026-02-22, 14d
```

**Preuve:** SHA-256 + Chain of Custody + Re-test [ISO 27043]
"""
    }
    return sections.get(phase_key, "Section non trouvee")

def generate_certification_roadmap(norme, client, cabinet):
    roadmaps = {
        "ISO 27001:2022": f"Gap ISO 27001:2022 Cl.4-10 + Annexe A 93 controles -> Mise en conformite -> PSSI + SoA + 30 politiques -> Implementation 3 mois -> Audit blanc ISO 19011 -> Revue direction Cl.9.3 -> Certification AFNOR/Bureau Veritas. Cout estime 45M XOF pour {client}.",
        "ISO 42001:2023": f"SIA ISO 42001:2023 Cl.4-10 + Annexe A + B -> Registre IA B.3/B.7.4 + Politique IA A.2 + Impact IA B.7.2 + Cycle vie A.6 -> Gestion risques 23894 -> Audit blanc -> Certification. {client} doit nommer AI Officer [A.5.2]. Cout 35M XOF.",
        "ISO 22301:2019": f"BIA + PCA/PRA DORA Art.11 + Tests annuels. Cout 25M XOF.",
        "PCI DSS 4.0.1": f"Scope CDE + Req 1-12 v4.0.1 + ASV + Pentest segmentation + QSA. Cout 60M XOF pour {client} si PSP UEMOA.",
        "SOC 2": f"TSC 2017 Securite Disponibilite Confidentialite -> SOC 2 Type I puis Type II 6 mois observation.",
        "NIS2": f"Directive 2022/2555 Art.20-21 -> Mesures Cyber Hygiene + Supply Chain + Reporting 24h/72h.",
        "DORA": f"Reglement 2022/2554 + RTS ICT Risk Management Art.9 + TLPT + Registre sous-traitants."
    }
    return roadmaps.get(norme, f"Roadmap certification {norme} pour {client} - workflow Gap -> Doc -> Implementation -> Audit blanc -> Accompagnement {cabinet}.")
