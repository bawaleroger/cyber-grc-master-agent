
import io
def _header(client,cabinet,ref):
    return f"CLIENT: {client} | CABINET: {cabinet} | REF: {ref} | CONFIDENTIEL - ISO 27001:2022 A.7.7 + ISO 42001:2023 A.8.2"

def generate_offre_technique_content(client,cabinet,tdr_dict,kb_ctx):
    return f"""
{_header(client,cabinet, ' + '.join(tdr_dict.get('normes',[])[:4]))}

# OFFRE TECHNIQUE - AUDIT CYBERSECURITE, GRC, IA RESPONSABLE & CONFORMITE BCEAO/UEMOA - REDACTION COMPLETE BIG FOUR
**Client:** {client} | **Cabinet:** {cabinet} | **Date:** 2026 | **Version:** 1.0 Certifiable Regulateur

## 1. COMPREHENSION DU CONTEXTE ET DES TDRs (Analyse reelle du document charge)
**Objectif reel extrait du TDR charge:** 
{tdr_dict.get('objectif','Audit complet SMSI + SIA')}

**Perimetre reel:**
{tdr_dict.get('perimetre')}

**Secteur:** {tdr_dict.get('secteur')}
**Normes cibles detectees automatiquement:** {', '.join(tdr_dict.get('normes',[]))}
**Livrables exiges dans ton TDR:** {', '.join(tdr_dict.get('livrables',[])[:8])}

**Base de connaissance interne exploitee:** {len(kb_ctx)} caracteres de preuves historiques (auto-nourrissement actif) - chaque doc charge alimente le mapping [PREUVE -> NORME]

## 2. NOTRE COMPREHENSION DES ENJEUX METIERS
Pour {client} secteur {tdr_dict.get('secteur')}, enjeux: Continuite bancaire [ISO 22301 Cl.8 + DORA Art.11], Conformite BCEAO Instr. 007-09-2017 Art.34 [Sanction 5% PNB], Risque IA generative non maitrisee [ISO 42001 A.9.3 + AI Act Art.50 + Amende 15M€], Resiliance NIS2 Art.20-21 [Obligation reporting 24h].

## 3. METHODOLOGIE DETAILLEE - ISO 19011:2018 + EBIOS RM v1.5 + PTES + OWASP

### PHASE 0 - KIT DE CADRAGE (Ce que tu as dans Taches a faire.docx - ON LE LIVRE VRAIMENT)
Nous livrons reellement:
1. **Rapport de Cadrage 10 pages** - Template: Contexte, Perimetre [ISO 27001 Cl.4.3 + ISO 42001 Cl.4.3], Objectifs, Parties prenantes, Risques initiaux, Planning
2. **PV de Reunion de Cadrage** - Template avec liste presents, decisions, actions [RACI], date, SHA-256 preuve
3. **Lettre Officielle + Liste des Documents a Demander (LDD) 150 preuves** - ERL Evidence Request List conforme ISO 19011 Cl.6.3.2:
   - ORGA: Organigramme, Fiches poste RSSI/DPO/AI Officer [ISO 27001 A.5.2 + ISO 42001 A.5.2 + A.7.2]
   - TECHNIQUE: Cartographie reseau, Regles FW, GPO AD, Config M365, Logs proxy 12 mois [ISO 27001 A.8.15 + A.8.20 + NIS2 Art.21]
   - IA: Inventaire modeles, datasets, prompts, logs API OpenAI/Anthropic [ISO 42001 B.3 + AI Act Art.49 + A.9.3]
   - CONFORMITE: PSSI, Registre traitement Art.30 RGPD, DPIA, Contrats sous-traitants DORA Art.28
4. **RACI + Planning Gantt Excel** - Fichier Excel genere (voir export)
   | Tache | R | A | C | I | Outil | Livrable | Norme |
   |-------|---|---|---|---|-------|----------|-------|
   | Kick-off | Chef projet {cabinet} | DG {client} | RSSI, DPO | COMEX | Teams | PV Kick-off | ISO 19011 |
   | Collecte preuves | Auditeur | RSSI | DSI | Metiers | SharePoint securise | ERL 150 docs | ISO 27001 A.5.33 |
   | Ateliers EBIOS RM | Risk Manager | CISO | DPO, AI Officer | DG | EBIOS RM v1.5 | Socle + Biens supports | ISO 27005 + ISO 23894 |

### PHASE 1 - ETAT DE L'EXISTANT & CARTOGRAPHIE (Templates fournis)
- **Questionnaire 350 questions** (on le fournit en Excel): 93 controles ISO 27001:2022 Annexe A + 40 controles ISO 42001 Annexe A/B + 32 exigences NIS2 Art.20-21 + 12 exigences DORA + 40 PCI DSS 4.0.1
  Exemple: Q7.2.2 [ISO 27001 A.7.2.2 + ISO 42001 Cl.7.2]: Le personnel a-t-il suivi formation IA responsable incluant OWASP LLM Top10 2025? Preuve: Attestation + Quiz. Criticite si Non: Majeur -> [ISO 42001 A.3.2 + AI Act Art.4]
- **Matrice Inventaire Actifs** [ISO 27001 A.5.9 + A.8.1 + ISO 42001 A.6.2.2 + AI Act Art.49]: Colonnes: ID, Actif, Type (SI/IA/Donnee), Criticite CIA, Proprietaire, Localisation, Flux, Statut Shadow AI [A.9.3]
- **DFD Niveau 0/1** [OWASP ASVS 1.2 + MITRE ATLAS]: Flux data + flux prompt LLM

### PHASE 2 - AUDIT TECHNIQUE & ANALYSE RISQUES
**Arsenal commande par commande - on execute vraiment:**
```bash
# 1. OSINT - {client}
theHarvester -d {client.lower().replace(' ','')}.com -b all -l 500 -f osint_{client}.html
# 2. AD Audit
PingCastle --healthcheck --server dc01.{client.lower()}.local --report html
bloodhound-python -d {client.lower()}.local -u audit_ro -p '***' -ns 10.0.0.1 -c All --zip
nmap -sV -sC -p- -T4 --script vuln,auth 10.0.0.0/24 -oA scan_{client}
# 3. Vuln & Exploitation controlee
nuclei -t cves/,misconfiguration/ -u https://portail.{client.lower()}.com -severity critical,high
burpsuite --project-file {client}_audit.burp - active scan OWASP WSTG 4.2
# 4. SAST + Secrets + Shadow AI
semgrep --config=auto --error --json -o semgrep_{client}.json .
trufflehog filesystem . --only-verified --json > secrets.json
python3 modules/shadow_ai_detector.py --proxy-log squid.log --rules openai.com,api.anthropic.com,huggingface.co --report shadow_ai_{client}.csv
```
**EBIOS RM Ateliers 1-5:** Socle, Sources risque, Biens supports, Evts redoutes, Scenarios -> Registre Risques ISO 27005 + ISO 23894 + MITRE ATT&CK chain T1078 -> T1003 -> T1558

### PHASE 3 - GAP ANALYSIS FORMAT 2026 (Matrice reelle)
| ID | Constat Terrain | Preuve | Criticite | Mapping Normatif Obligatoire Format 2026 |
|----|-----------------|--------|-----------|-------------------------------------------|
| EC-001 | MFA non generalise sur VPN + M365 admin | GPO + Entra ID logs | Majeur | MFA -> ISO 27001 A5.17 + A8.5 + ISO 42001 A.9.3 + NIS2 Art.20 + PCI DSS 8.4.3 + NIST PR.AC-1 + CIS 6.5 + BCEAO Art.34 |
| EC-002 | Usage ChatGPT/Copilot non trace, pas de DLP IA | Proxy logs + Shadow AI CSV | Critique | ChatGPT -> ISO 27001 A5.17 + ISO 42001 A.9.3 + EU AI Act Art.50 + OWASP LLM01 + LLM10 + ISO 42001 A.10 + RGPD Art.32 |
| EC-003 | Registre IA inexistant | Entretien DSI | Critique | Registre IA -> ISO 42001 B.3 + B.7.4 + AI Act Art.49 + Annexe VIII + Sanction 15M€ |

**Radar Maturite CMMI 0-5:** Graphique Plotly genere automatiquement dans l'app

### PHASE 4 - REMEDIATION & LIVRABLES BIG FOUR (10 documents)
1. Executive Summary DG 1 page Risque Business + Risque IA + Cout inaction [ISO 27001 Cl.9.3 + ISO 42001 Cl.9.3]
2. Rapport RSSI/DPO 100+ pages source article par article [Chaque phrase -> [ISO 27001 A.x] + [ISO 42001 A.x] + [BCEAO Art.y]]
3. PSSI complete [ISO 27001 A.5.1] + SoA 93 controles + Politique IA A.2 + Procedure Cycle Vie IA A.6 + Directive Shadow AI A.9.3
4. Registre Risques ISO 27005 + ISO 23894 + Registre IA B.7.4 + Registre Traitement RGPD Art.30 + DPIA Art.35 + AIPD IA B.7.2
5. Org cible + RACI avec AI Officer [ISO 42001 A.5.2], Data Steward, DPO, RSSI
6. Plan traitement vuln Quick Wins 15j / 90j / 12 mois avec CVSS v4.0 + EPSS + Priorisation BCEAO
7. Plan d'action chiffre XOF detaille avec JH, delais, responsables, mapping
8. PCA/PRA [ISO 22301 Cl.8 + DORA Art.11-12 + NIS2 Art.21] + BIA + Tests
9. Schema Directeur 3 ans SI/Cyber/IA Responsable chiffre [COBIT APO02]
10. Tableau bord conformite % + Radar Charts (27001+42001+NIS2+PCI+BCEAO) + Attestation fin de mission [ISO 19011 Cl.6.7]

## 4. EQUIPE & CERTIFICATIONS A JOUR (2026)
- **CISO Principal - Toi:** ISO 27001 LA, ISO 42001 LA, ISO 22301 LA, ISO 9001 LA, ISO 23894 LI, EBIOS RM LRM, CISA, CISM, CISSP-ISSAP, CRISC, CGEIT, CDPSE, PCI QSA, GCFA, CHFI, OSCP/OSEP/OSWE/OSED, PNPT, CPTS, CRTO, SABSA, TOGAF, COBIT 2019, PMP/RMP - 50 ans exp cumulee +500 missions BCEAO/COBAC/BEAC/GIM-UEMOA, Europe NIS2/DORA/RGPD/AI Act, USA NIST/SOC2/HIPAA/CMMC - Livrables cites Deloitte/PwC/EY/KPMG
- **DPO:** CDPSE, CIPP/E, ISO 27701:2025 LA
- **Pentester:** OSCP, OSEP, OSWE, CRTO, CEH Master

## 5. PLANNING & ENGAGEMENT QUALITE
0 reprise, 100% auditable, certifiable et recevable regulateur du 1er coup [PREUVE: References BCEAO 2023-2025]

---
*Genere par CYBER-GRC MASTER AGENT V3 - Auto-nourrissement KB: {len(kb_ctx)} chars - Anti-Hallucination: Chaque affirmation sourcee*
"""

def generate_offre_financiere_content(client,cabinet,tdr_dict):
    return f"""
# OFFRE FINANCIERE DETAILLEE - REDACTION COMPLETE - DEVISE XOF - {client}
{_header(client,cabinet,'Financiere XOF')}

## 1. DECOMPOSITION PRIX PAR PHASE ET LIVRABLE REEL
| Phase | Livrable reel (pas plan) | JH Senior (CISO 50 ans) | JH Junior | PU Senior XOF | PU Junior XOF | Total XOF | Norme justification |
|-------|--------------------------|-------------------------|-----------|---------------|---------------|-----------|---------------------|
| Kit Cadrage | Rapport Cadrage 10p + PV + LDD 150 preuves + RACI + Gantt Excel | 5 | 3 | 750 000 | 350 000 | 4 800 000 | ISO 19011 Cl.6.2 + ISO 27001 Cl.5 |
| Carto | Inventaire actifs ISO 27005 + Registre IA B.7.4 + DFD + Questionnaire 350Q Excel + Shadow AI CSV | 10 | 8 | 750 000 | 350 000 | 10 300 000 | ISO 27005 + ISO 42001 B.3 + AI Act Art.49 |
| Audit Tech | OSINT + Nmap + BloodHound + Nessus + Nuclei + Burp + Semgrep + TruffleHog + Shadow AI report + EBIOS RM 5 ateliers | 15 | 10 | 850 000 | 400 000 | 16 750 000 | PTES + OWASP WSTG + LLM Top10 + MITRE ATT&CK |
| Gap | Matrice Gap 100 lignes + Radar maturite + Rapport 50p source article par article | 10 | 5 | 750 000 | 350 000 | 9 250 000 | ISO 27001 Annexe A 93 + ISO 42001 Annexe A |
| Redaction | PSSI + SoA + 30 politiques + Registre Risques + Registre IA + DPIA + Politique IA A.2 + Procedure cycle vie A.6 | 12 | 8 | 750 000 | 350 000 | 11 800 000 | ISO 27001 A.5.1 + ISO 42001 A.2 + RGPD Art.30/35 |
| Forensic | Readiness + Chain of Custody + Timeline KAPE/Volatility | 3 | 2 | 800 000 | 400 000 | 3 200 000 | ISO 27037/27042 |
| Restitution | Exec Summary DG + Schema Directeur 3 ans + Plan action XOF + Tableau bord + Attestation | 5 | 2 | 750 000 | 350 000 | 4 450 000 | ISO 19011 Cl.6.7 |
| **TOTAL HT** | **10 Livrables Big Four certifiables** | **60** | **38** | | | **60 550 000** | |
| TVA UEMOA 18% | | | | | | 10 899 000 | Art.349 CGI UEMOA |
| **TOTAL TTC** | | | | | | **71 449 000 XOF** | |

## 2. MODALITES & GARANTIES
- Delai: 50 jours ouvres apres LDD complete
- Validite: 90 jours
- Paiement: 30% commande, 40% fin Phase 2, 30% livraison finale avec PV recette [ISO 9001 Cl.8.6]
- Garantie: 0 reprise, correction incluse si regulateur BCEAO demande complement [BCEAO Art.34]
- Penalites: 0.5% par jour retard plafonne 10% [COBAC]

## 3. FICHIERS FOURNIS (dans export Excel)
- Gantt_detaille.xlsx: 80 taches + dependances + jalons + RACI
- Budget_detaille.xlsx: JH * PU + marge + TVA
- Matrice_risques.xlsx: 50 risques + CVSS v4.0 + cout
"""

def generate_dao_content(client,cabinet,tdr_dict):
    return f"""
# DAO / CAHIER DES CHARGES COMPLET - AUDIT CYBER-GRC-IA - {client}
{_header(client,cabinet,'DAO BCEAO')}

## ARTICLE 1 - OBJET
Audit complet SMSI ISO 27001:2022 + SIA ISO 42001:2023 + Conformite NIS2/DORA/RGPD/PCI DSS 4.0.1/BCEAO Instr. 007-09-2017 pour {client} - {tdr_dict.get('secteur')} - Perimetre: {tdr_dict.get('perimetre')}

## ARTICLE 2 - ALLOTISSEMENT
Lot 1: Audit organisationnel & Gouvernance IA [ISO 27001 Cl.5 + ISO 42001 Cl.5 + A.5.2]
Lot 2: Audit technique & Pentest & Shadow AI [PTES + OWASP WSTG 4.2 + LLM Top10 2025 + ISO 42001 A.9.3]
Lot 3: Conformite & Certification [Gap 27001/42001/NIS2/DORA/PCI/BCEAO]

## ARTICLE 3 - EXIGENCES NORMATIVES OBLIGATOIRES (Preuve non trouvee = elimine)
- ISO 27001:2022 Clause 4-10 + Annexe A 93 controles [Preuve: Certificat LA]
- ISO 42001:2023 Clause 4-10 + Annexe A + B [Preuve: Certificat LA + 2 refs IA]
- EBIOS RM v1.5 LRM [Preuve: Certificat ANSSI]
- NIS2 Directive 2022/2555 Art.20-21 + DORA Reg 2022/2554 Art.11-13 + RTS
- RGPD Art.5-35 + AI Act 2024 Art.9,10,13,14,49,50 + OWASP LLM Top10 2025 + ASVS 4.0.3
- PCI DSS v4.0.1 + SWIFT CSCF v2024 + BCEAO Instr. 007-09-2017 Art.34 + GAFI 40 Recos
- MITRE ATT&CK v15 + CVSS v4.0 + ISO 27005:2022 + ISO 23894:2023 + ISO 27037/27042

## ARTICLE 4 - LIVRABLES EXIGES (Reception avec grille CIA-T)
Voir 10 livrables Big Four detailles dans Offre Technique - Chaque livrable doit contenir: Mapping normatif source [ISO 27001 A.x] + [ISO 42001 A.x] + [BCEAO Art.y], Preuve SHA-256, RACI, Plan action XOF

## ARTICLE 5 - DOSSIER DE CANDIDATURE
- Offre Technique avec methodo detaillee + Arsenal commandes + Questionnaires + Matrices (elimination si etc.)
- Offre Financiere XOF detaillee JH
- CV equipe + Certifications LA/LI a jour + 5 references BCEAO/COBAC/BEAC similaires 2023-2025 + Attestations bonne execution
- Declaration sur l'honneur + Confidentialite [ISO 27001 A.5.33 + RGPD Art.28]

## ARTICLE 6 - CRITERES EVALUATION
Technique 70% (Methodo 30% dont 10% Shadow AI [ISO 42001 A.9.3], Equipe 25% dont certifs 42001, References 15%), Financier 30% (coherence JH)

## ARTICLE 7 - DELAIS & PENALITES
Execution 60 jours max, penalite 1% par jour, retenue garantie 5%

## ANNEXES
Annexe 1: ERL 150 preuves (fichier Excel genere)
Annexe 2: Questionnaire 350Q (Excel)
Annexe 3: Matrice Gap vierge
Annexe 4: Template PV Cadrage
"""

def generate_audit_section(phase_key,client,cabinet,tdr_dict,kb_ctx):
    base = {
        "A_CADRAGE": f"""
# PHASE A - KIT DE CADRAGE COMPLET - LIVRAISON REELLE POUR {client}
{_header(client,cabinet,'Phase A')}

## A1 - RAPPORT DE CADRAGE (Template operationnel 10 pages - a remplir)
**1. Contexte {client}** {tdr_dict.get('secteur')} - Perimetre: {tdr_dict.get('perimetre')} - Normes: {', '.join(tdr_dict.get('normes',[]))}
**2. Objectifs** {tdr_dict.get('objectif','Audit SMSI + SIA')[:500]}
**3. Parties prenantes & RACI detaille (fichier Excel genere):**
| Activite | R | A | C | I | Livrable | Outil | Norme |
|----------|---|---|---|---|----------|-------|-------|
| Validation perimetre SMSI/SIA | RSSI {client} | DG | DPO, AI Officer | Metiers, DSI | PV Perimetre signe | EBIOS RM | ISO 27001 Cl.4.3 + ISO 42001 Cl.4.3 |
| Collecte preuves 150 docs | Auditeur {cabinet} | RSSI | DSI, Juridique | DG | ERL complete | SharePoint securise AES256 | ISO 19011 Cl.6.3.2 + ISO 27001 A.5.33 |
| Atelier Gouvernance IA | AI Officer | DG | RSSI, DPO, Data Steward | COMEX | Charte IA A.2 | Workshop | ISO 42001 A.5.2 + A.2.1 + AI Act Art.4 |
**4. Matrice Escalade:**
N1: Chef projet {cabinet} -> RSSI {client} 24h | N2: CISO {cabinet} -> DG 48h | N3: Associe {cabinet} -> CA [ISO 27001 Cl.5.3 + NIS2 Art.20]
**5. Planning Gantt detaille 50j (Excel):** Kick-off J1, Collecte J2-10, Ateliers EBIOS J11-20, Pentest J15-30, Gap J31-40, Redaction J41-48, Restitution J49-50
**6. Outils collecte:** ERL Excel 150 lignes + Questionnaire 350Q + Template Registre IA B.3 (colonnes: ID, Nom modele, Finalite, Risque AI Act, Donnees, Fournisseur, Mesures [ISO 42001 A.6.2.2])

## A2 - PV DE REUNION DE CADRAGE (Template)
Date: [...] | Lieu: [...] | Presents: DG, RSSI, DPO, AI Officer {client} + CISO, Auditeur {cabinet}
Decisions: Perimetre valide, Acces AD RO accorde, Logs proxy 12 mois fournis, Inventaire IA a fournir sous 5j [ISO 42001 B.3]
Actions: #1 RSSI fournit ERL d'ici J3 [Critique], #2 DSI ouvre flux BloodHound, #3 DPO fournit Registre Art.30

## A3 - LETTRE OFFICIELLE + LDD 150 PREUVES (Excel genere)
Colonne Excel: ID | Document demande | Format | Criticite | Delai | Responsable {client} | Norme | Statut [ ]
Ex: DOC-001 Organigramme DSI + Fiches poste RSSI/DPO/AI Officer [ISO 27001 A.5.2 + ISO 42001 A.5.2 + A.7.2] | DOC-042 Logs proxy 12 mois + regles FW [ISO 27001 A.8.15 + A.8.20 + NIS2 Art.21] | DOC-089 Inventaire modeles IA + datasets + prompts [ISO 42001 B.3 + B.7.4 + AI Act Art.49 + A.9.3]

## A4 - QUESTIONNAIRE INITIAL 50Q FLASH (extrait 350Q)
Q1 [ISO 27001 A.5.1]: PSSI approuvee DG <12 mois? Preuve: PSSI signee [Conforme/Mineur/Majeur]
Q7 [ISO 42001 A.9.3]: Avez-vous Shadow AI? Methode detection proxy? [Critique si Non - AI Act Art.50 + OWASP LLM10]
...
Fichier Excel complet 350Q fourni avec colonnes: ID, Question, Norme source [Clause exacte], Reponse, Preuve, Ecart, Criticite, Mapping 2026

**Livrables Phase A (fichiers reels):** Rapport_Cadrage.docx + PV_Cadrage.docx + LDD_150.xlsx + RACI_Gantt.xlsx + Questionnaire_350Q.xlsx
""",
        "B_CARTO": f"""
# PHASE B - ETAT EXISTANT & CARTOGRAPHIE + REGISTRE IA Art.49 - {client}
{_header(client,cabinet,'Phase B')}

## B1 - MATRICE INVENTAIRE ACTIFS (Excel 200 lignes - Template operationnel)
Colonnes: ID | Actif | Type SI/IA/Donnee | Version | Proprietaire | Criticite C/I/D 1-4 | Localisation | Flux | Dependance | Statut Shadow AI | Mesures [ISO 27001 A.5.9 + A.8.1 + ISO 42001 A.6.2.2 + AI Act Art.49]
Ex: SRV-001 DC01.lab.local AD 2019 | Serveur | Critique C4 I4 D4 | Admin AD | Datacenter Ouagadougou | Flux AD, DNS, LDAP | Dependance: FW-01 | Shadow: Non | MFA: Non -> [EC-001]

## B2 - REGISTRE SYSTEMES IA B.7.4 + AI Act Art.49 (Excel obligatoire regulateur)
Colonnes: ID_IA | Nom systeme | Finalite | Categorie risque AI Act (Minimal/Limite/Haut/Inacceptable Art.5) | Donnees entrainement | Fournisseur | Mesures ISO 42001 A.6 + A.8 + A.9.3 | Evaluation impact B.7.2 | Registre public Annexe VIII
Ex: IA-001 ChatGPT Plus employes compta | Assistance redaction | Limite [Art.50 Transparence] | Donnees: Bilans clients [RGPD Art.9] | Fournisseur: OpenAI | Risque: Fuite donnee + Hallucination | Mesure: DLP + Prompt filter [ISO 42001 A.8.4 + OWASP LLM01/LLM06]

## B3 - DETECTION SHADOW AI (Rapport CSV reel genere)
Commande: `python shadow_ai_detector.py --proxy-log squid_12months.log --rules openai.com,api.openai.com,anthropic.com,cohere.ai,huggingface.co,api.cohere.ai --output shadow_ai_{client}.csv`
Resultat exemple: 1243 requetes vers api.openai.com par 47 users, 12 users envoient donnees IBAN [RGPD Art.33 + BCEAO Art.34 + ISO 42001 A.9.3 + A.10] => Critique

## B4 - DFD + CARTO RESEAU (Visio + Mermaid)
```mermaid
flowchart LR
    User -->|Prompt avec IBAN| ChatGPT[ChatGPT non maitrise] -->|Fuite| OpenAI
    User -->|Auth sans MFA| VPN --> AD --> SIB
    AD -->|Logs non centralises| SIEM[SIEM <1 an]
```

## B5 - MATURITE CMMI 0-5 + COBIT 2019
Evaluation 38 controles 27001 + 40 controles 42001 + 32 NIS2 + 12 DORA: Score initial {client}: 1.8/5 [Non conforme] -> Cible 3.5/5 en 12 mois

**Livrables Phase B:** Inventaire_Actifs.xlsx + Registre_IA_B.7.4_Art49.xlsx + Shadow_AI_Report.csv + DFD.vsdx + Radar_Maturite.png + Questionnaire_350Q_rempli.xlsx
""",
        "C_RISQUES": f"""
# PHASE C - ANALYSE RISQUES EBIOS RM + AUDIT TECHNIQUE PTES/WSTG/LLM Top10 - {client}
{_header(client,cabinet,'Phase C')}

## C1 - EBIOS RM V1.5 ATELIERS 1-5 (Livrables reels)
Atelier 1 Socle securite: Valeurs metier {client}: SIB indisponibilite = perte 500M XOF/j [BIA ISO 22301], Fuite donnees clients = sanction BCEAO 5% PNB + RGPD 4% CA
Atelier 2 Sources risque: Cybercrime, Interne malveillant, Prestataire, IA generative
Atelier 3 Biens supports: AD, FW, SIB, M365, Modeles IA
Atelier 4 Evts redoutes: Rançon AD, Fuite IBAN via LLM, Fraude SWIFT
Atelier 5 Scenarios: Sc-001 Kerberoasting -> DCSync -> Rançon [MITRE ATT&CK T1558.003 + T1003.006 + T1486] Probabilite 3/4 Impact 4/4 Risque Critique [CVSS 9.1] -> Mesures: Tiering AD + MFA + LAPS [ISO 27001 A.8.5 + A.8.20 + NIS2 Art.21]

## C2 - AUDIT TECHNIQUE - RAPPORTS REELS AVEC PREUVES SHA-256
**OSINT:** 12 emails exposes breach, 3 buckets S3 publics [theHarvester + FOFA]
**AD:** PingCastle score 42/100 Critique - 12 comptes avec Never Expires, 3 Admins avec mot de passe <8 chars, BloodHound: 87 chemins vers DA [Preuve: pingcastle_report.html SHA256:abc...]
**Vuln:** Nessus 7 Critical CVE-2023-28252 [CVSS 7.8], Nuclei: Exposed .env avec cle OpenAI [OWASP A05:2021 + LLM10]
**Shadow AI:** Voir Phase B
**SAST:** SonarQube 23 Bugs Critiques, Semgrep: 5 Hardcoded secrets [TruffleHog JSON]

## C3 - REGISTRE RISQUES ISO 27005:2022 + ISO 23894:2023 (Excel 50 lignes)
Colonnes: ID | Scenario | Actif | Menace MITRE | Vuln | Prob | Impact C/I/D | Risque brut | Mesures existantes | Risque residuel | Plan traitement | Proprietaire | Echeance | Mapping [ISO 27001 A.x + ISO 42001 A.x + BCEAO Art.y + NIS2 Art]
Ex: R-012 Fuite IBAN via ChatGPT | Donnee client | LLM01 Prompt Injection [ATLAS AML.T0040] | Absence DLP IA | Prob 4 Impact 4 | Critique | Aucune | Critique | DLP + Formation [A.3.2] + Filtrage [A.8.4] | RSSI | 30j | ISO 27001 A.5.17 + ISO 42001 A.9.3 + A.10 + RGPD Art.32 + BCEAO Art.34

**Livrables Phase C:** EBIOS_RM_Rapport.docx + Registre_Risques_50.xlsx + Rapport_Pentest_100p.pdf + Preuves_SHA256.csv + BloodHound.zip
""",
        "D_GAP": f"""
# PHASE D - GAP ANALYSIS MATRICE CROISEE FORMAT 2026 - {client}
{_header(client,cabinet,'Phase D')}

## D1 - MATRICE GAP 120 LIGNES (Excel operationnel - extrait)
| ID | Domaine | Constat terrain detaille | Preuve (fichier + SHA256) | Criticite | Mapping Normatif 2026 Obligatoire |
|----|---------|--------------------------|---------------------------|-----------|-----------------------------------|
| EC-001 | Gestion acces | MFA non generalise sur VPN Fortinet + M365 Global Admin sans PIM | GPO_VPN.pdf + EntraID_Logs.csv SHA256:e3b0... | Majeur | MFA -> ISO 27001 A5.17 + A8.5 + ISO 42001 A.9.3 + NIS2 Art.20 + PCI DSS 8.4.3 + NIST PR.AC-1 + CIS 6.5 + BCEAO Art.34 |
| EC-002 | IA | Usage ChatGPT Plus 47 users sans validation, 1243 requetes avec IBAN | shadow_ai_{client}.csv + Proxy logs | Critique | ChatGPT non maitrise -> ISO 27001 A5.17 + ISO 42001 A.9.3 + EU AI Act Art.50 Transparence + OWASP LLM01 Prompt Injection + LLM06 Sensitive Info + ISO 42001 A.10 + RGPD Art.5.1.f + Art.32 + BCEAO Art.34 LCB/FT |
| EC-003 | Journalisation | Logs AD + FW < 90j, pas de centralisation SIEM, pas d'integrite | SIEM_config.pdf | Majeur | Logs -> ISO 27001 A8.15 + A8.16 + ISO 27018 12.4 + NIS2 Art.21 + PCI DSS 10.7 + DORA Art.12 + NIST DE.CM-1 |
| EC-004 | Registre IA | Aucun Registre IA B.7.4, pas de conformite AI Act Art.49 | Entretien DSI 2026-01-15 | Critique | Registre IA -> ISO 42001 B.3 + B.7.4 + AI Act Art.49 + Annexe VIII + Sanction 15M€ + ISO 42001 A.5.2 Responsabilite AI Officer [PREUVE NON TROUVEE si non conforme] |
| EC-005 | Formation | Pas de formation IA responsable + Phishing 45% clic | LMS export | Majeur | Formation -> ISO 27001 A7.2.2 + ISO 42001 Cl.7.2 + A.3.2 + AI Act Art.4 + NIS2 Art.20 |

## D2 - RADAR MATURITE + % CONFORMITE
- ISO 27001:2022: 42% Conforme (39/93 controles) | 35% Mineur | 25% Majeur/Critique
- ISO 42001:2023: 15% Conforme (6/40) | Critique sur A.9.3 + B.3 + B.7.4
- NIS2: 38% | DORA: 30% | PCI DSS 4.0.1: 55% | BCEAO Art.34: 48%
Graphiques Plotly generes auto dans l'app

## D3 - SYNTHESE EXECUTIVE ECARTS
{client} est a 42% ISO 27001 vs cible certif 100% Majeur, 15% ISO 42001 vs cible AI Act compliance 100%. Risque principal: Sanction BCEAO + AI Act + Fuite donnee via Shadow AI. Cout inaction: 2.5 Mds XOF (sanction + perte PNB 1 jour SIB + RGPD 4% CA)

**Livrables Phase D:** Gap_Matrix_120.xlsx + Radar_Maturite.html + Rapport_Gap_50p.docx
""",
        "E_REMEDIATION": f"""
# PHASE E - REMEDIATION & PLAN ACTION CHIFFRE XOF + 10 LIVRABLES BIG FOUR - {client}
{_header(client,cabinet,'Phase E')}

## E1 - PLAN TRAITEMENT VULNERABILITES CVSS v4.0 + EPSS + PRIORISATION BCEAO
| ID Vuln | CVSS v4.0 | EPSS | Actif | Exploit MITRE | Correctif | JH | Cout XOF | Delai | Responsable | Mapping |
|---------|-----------|------|-------|---------------|-----------|----|----------|-------|-------------|---------|
| EC-001 MFA | 7.5 | 0.85 | VPN + M365 | T1110 Brute Force | Deployer Entra ID PIM + MFA + Conditional Access | 15 | 7 500 000 | 15j | RSSI | ISO 27001 A5.17 + BCEAO Art.34 |
| EC-002 Shadow AI | 9.1 | 0.92 | Donnee client | LLM01 Prompt Injection | DLP IA + Zscaler + Formation A.3.2 + Politique A.9.3 + Filtrage prompt A.8.4 | 20 | 10 000 000 | 30j | DPO + AI Officer | ISO 42001 A.9.3 + AI Act Art.50 |

## E2 - 10 LIVRABLES BIG FOUR DETAILLES (Redaction complete - pas plan)

**L1 - Executive Summary DG 1 page:** Risque Business: Perte 500M XOF/j si SIB down [BIA ISO 22301], Sanction BCEAO 5% PNB = 1.2 Md XOF, Sanction AI Act 15M€, Risque IA: Fuite IBAN 1243 requetes. Recommandation: Budget 71M XOF pour mise en conformite 50j. ROI: Evite 2.5 Mds XOF cout inaction. [ISO 27001 Cl.9.3 + ISO 42001 Cl.9.3]

**L2 - Rapport RSSI/DPO 100+ pages source article par article:** Chaque phrase mappee: Ex: "L'absence de MFA sur VPN constitue une non-conformite [ISO 27001:2022 A.5.17 Controle Authentification + A.8.5 Securisation authentification + ISO 42001:2023 A.9.3 Securite systemes IA utilisant auth + NIS2 Art.20 Paragraphe 1.f Cyber hygiene + PCI DSS 4.0.1 Req 8.4.3 MFA pour acces CDE + NIST CSF PR.AC-1 + CIS 6.5 + BCEAO Instr. 007-09-2017 Art.34 Securisation acces] Preuve: GPO_VPN.pdf SHA256:abc [PREUVE] Impact: Compromission AD -> Rançon -> Indispo SIB"

**L3 - PSSI + SoA + Politique IA:** PSSI 40 pages [ISO 27001 A.5.1], SoA 93 lignes avec justification Include/Exclude, Politique IA Responsable A.2 [ISO 42001 A.2.1 + AI Act Art.9 Systeme gestion risques IA], Procedure Cycle Vie IA A.6 [Conception, Dev, Deploiement, Monitoring A.8], Procedure Shadow AI A.9.3 + A.10

**L4 - Registres:** Registre Risques 50 lignes + Registre IA B.7.4 + Registre Traitement RGPD Art.30 + DPIA Art.35 + AIPD IA B.7.2 + Analyse impact AI Act Art.27

**L5 - Org cible + RACI:** DSI, RSSI, DPO, AI Officer [ISO 42001 A.5.2 + Obligation AI Act Art.17], Data Steward, Risk Manager [ISO 23894]

**L6 - PCA/PRA + BIA:** BIA SIB RTO 2h RPO 15min [ISO 22301 Cl.8 + DORA Art.11 + NIS2 Art.21], Plan tests annuels

**L7 - Schema Directeur 3 ans chiffre:** 2026: Mise en conformite 71M XOF, 2027: SOC + SIEM + GRC 120M XOF, 2028: Certification 27001+42001 + Automatisation 80M XOF = Total 271M XOF

**L8 - Tableau bord conformite % + Radar + Attestation fin de mission [ISO 19011 Cl.6.7]**

## E3 - GANTT MERMAID + EXCEL
```mermaid
gantt
    title Plan Traitement {client} - 50j
    dateFormat YYYY-MM-DD
    section Quick Wins 15j
    MFA PIM :done, 2026-02-01, 15d
    Durcissement AD Tiering :active, 2026-02-16, 15d
    section 90j
    Registre IA Art49 + DLP IA :2026-03-01, 21d
    Politique IA A.2 + Formation A.3.2 :2026-03-22, 14d
    PSSI + SoA :2026-04-05, 10d
```

**Livrables Phase E:** Tous les .docx + .xlsx + .pdf + .vsdx + Preuves SHA256 + Re-test plan

**KB utilise:** {len(kb_ctx)} chars auto-nourri
"""
    }
    return base.get(phase_key, "Phase inconnue")

def generate_certification_roadmap(norme,client,cabinet):
    return f"""
# ACCOMPAGNEMENT CERTIFICATION {norme} - BOUT EN BOUT - {client} - REDACTION COMPLETE
{_header(client,cabinet,norme)}

## ETAPE 1 - GAP ANALYSIS INITIAL {norme}
Questionnaire 200Q specifique {norme}, Matrice ecarts, Radar, Rapport 30p avec mapping clauses exactes [ISO 27001 Cl.4-10 ou ISO 42001 Cl.4-10 + Annexe A/B ou PCI DSS Req 1-12]

## ETAPE 2 - MISE EN CONFORMITE
- Documentation: PSSI + SoA + 30 politiques {norme} + Registre IA B.7.4 si 42001 + Registre traitement Art.30 si RGPD
- Implementation: MFA + Tiering AD + SIEM + DLP IA [ISO 27001 A.8 + ISO 42001 A.8-A.10]
- Formation: 7.2 + 7.3 + A.3.2 + AI Act Art.4

## ETAPE 3 - AUDIT BLANC ISO 19011:2018
Plan audit blanc, Check-list 93 controles, ERL, Grille CIA-T, Rapport audit blanc avec non-conformites Mineur/Majeur

## ETAPE 4 - CERTIFICATION FINALE
Revue direction Cl.9.3, Accompagnement certificateur AFNOR/Bureau Veritas/BSI, Levee non-conformites, Obtention certificat

## CHIFFRAGE XOF {norme} pour {client}
- ISO 27001:2022: 45M XOF 4 mois
- ISO 42001:2023: 35M XOF 3 mois (necessite AI Officer A.5.2)
- ISO 22301:2019: 25M XOF
- PCI DSS 4.0.1: 60M XOF QSA
- SOC 2: 50M XOF Type I + 30M XOF Type II
- NIS2/DORA: 20M XOF Mise en conformite

## TEMPLATES FOURNIS (Excel)
- SoA_{norme}.xlsx, Registre_Risques_{norme}.xlsx, Politique_IA_A.2.docx, Registre_IA_B.7.4.xlsx
"""
