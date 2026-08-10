
def local_fallback(user_prompt, kb_context, tdr_context):
    return f"# CYBER-GRC MASTER LOCAL\nDemande:{user_prompt}\nKB:{len(kb_context)} chars\nTDR:{tdr_context[:500]}"

def _h(c, cab, ref): return f"CLIENT:{c} | CABINET:{cab} | REF:{ref}"

def generate_offre_technique_content(client,cabinet,tdr_dict,kb_ctx):
    return f"""
{_h(client,cabinet,'+'.join(tdr_dict.get('normes',[])[:4]))}
# OFFRE TECHNIQUE COMPLETE BIG FOUR - {client}
## 1. COMPREHENSION TDR
Objectif reel: {tdr_dict.get('objectif','')[:800]}
Perimetre: {tdr_dict.get('perimetre')}
Normes: {', '.join(tdr_dict.get('normes',[]))}
Livrables TDR: {', '.join(tdr_dict.get('livrables',[])[:6])}
KB: {len(kb_ctx)} chars auto-nourris

## 2. KIT DE CADRAGE LIVRE REELLEMENT
- Rapport Cadrage 10p + PV + LDD 150 preuves [ISO 19011 Cl.6.3.2 + ISO 27001 A.5.33]
- RACI + Gantt Excel
- Questionnaire 350Q [ISO 27001 A 93 + ISO 42001 A 40 + NIS2 32 + DORA 12]
- Matrice Actifs ISO 27005 + Registre IA B.7.4 Art49

## 3. ARSENAL
```bash
theHarvester -d {client.lower().replace(' ','')}.com -b all
nmap -sV -sC -p- --script vuln 10.0.0.0/24
bloodhound-python -d lab.local -u audit -p *** -ns 10.0.0.1
trufflehog filesystem . --only-verified
python shadow_ai_detector.py --proxy-log squid.log --rules openai.com,anthropic.com
```

## 4. EQUIPE
CISO Principal: ISO 27001 LA, 42001 LA, 22301 LA, CISA, CISM, CISSP-ISSAP, EBIOS LRM, OSCP/OSEP, SABSA - 50 ans +500 missions BCEAO

## 5. 10 LIVRABLES
1. Exec Summary DG 2. Rapport RSSI 100p 3. PSSI+SoA+Politique IA A.2 4. Registres 5. Org cible + RACI AI Officer A.5.2 6. Plan vuln CVSS v4.0 7. Plan action XOF 8. PCA/PRA DORA Art11 9. Schema Dir 3 ans 10. Tableau bord + Radar + Attestation
"""

def generate_offre_financiere_content(client,cabinet,tdr_dict):
    return f"""
# OFFRE FINANCIERE XOF - {client}
| Phase | Livrable | JH Senior | JH Junior | PU Senior | PU Junior | Total XOF |
|---|---|---|---|---|---|---|
| Kit Cadrage | Rapport+PV+LDD150+RACI+Gantt | 5 | 3 | 750k | 350k | 4 800 000 |
| Carto | Inventaire+Registre IA Art49+DFD+350Q+Shadow AI | 10 | 8 | 750k | 350k | 10 300 000 |
| Audit Tech | OSINT+Nmap+BloodHound+Nessus+Nuclei+Burp+SAST | 15 | 10 | 850k | 400k | 16 750 000 |
| Gap | Matrice 120 lignes + Radar | 10 | 5 | 750k | 350k | 9 250 000 |
| Redaction | PSSI+SoA+30 politiques+Registres | 12 | 8 | 750k | 350k | 11 800 000 |
| Forensic | Chain Custody | 3 | 2 | 800k | 400k | 3 200 000 |
| Restit | Exec Summary+SD 3 ans | 5 | 2 | 750k | 350k | 4 450 000 |
| TOTAL HT | | 60 | 38 | | | 60 550 000 |
| TVA 18% | | | | | | 10 899 000 |
| TOTAL TTC | | | | | | 71 449 000 XOF |
"""

def generate_dao_content(client,cabinet,tdr_dict):
    return f"""
# DAO COMPLET BCEAO/UEMOA - {client}
Article1 Objet: Audit SMSI 27001:2022 + SIA 42001:2023 + NIS2/DORA/BCEAO Art34 Perimetre:{tdr_dict.get('perimetre')}
Article3 Normes: [ISO 27001 Cl4-10 + Annexe A 93][ISO 42001 Cl4-10 + Annexe A/B][NIS2 Art20-21][DORA Art11-13][RGPD Art32-35][PCI DSS 4.0.1][BCEAO 007-09-2017 Art34][MITRE ATT&CK v15][CVSS v4.0]
Article4 Livrables: 10 livrables Big Four
Article6 Criteres: Tech 70% (Methodo 30% dont Shadow AI A.9.3 10%, Equipe 25% dont 42001, Ref 15%) Financier 30%
"""

def generate_audit_section(key,client,cabinet,tdr_dict,kb_ctx):
    base_dict={
        "A_CADRAGE": f"# PHASE A KIT CADRAGE COMPLET {client}\nRACI detaille, ERL 150 preuves, PV, Gantt 50j, Questionnaire 50Q flash, KB:{len(kb_ctx)} chars",
        "B_CARTO": f"# PHASE B CARTO + REGISTRE IA Art49 {client}\nInventaire 200 lignes + Registre IA B.7.4 + Shadow AI CSV 1243 req + DFD Mermaid + Maturite CMMI 1.8/5",
        "C_RISQUES": f"# PHASE C EBIOS RM + PENTEST {client}\nEBIOS 5 ateliers, Scenarios MITRE T1558.003->T1003.006->T1486 CVSS 9.1, PingCastle 42/100, Nuclei .env, TruffleHog secrets",
        "D_GAP": f"# PHASE D GAP 120 lignes {client}\nMFA->ISO 27001 A5.17+A8.5+ISO 42001 A.9.3+NIS2 Art20+PCI 8.4.3+BCEAO Art34 [Majeur], ChatGPT->ISO 27001 A5.17+ISO 42001 A.9.3+AI Act Art50+LLM01 [Critique]",
        "E_REMEDIATION": f"# PHASE E 10 LIVRABLES + PLAN XOF {client}\nExec Summary 1p, Rapport 100p source article par article, PSSI+SoA+Politique IA A.2, Registres, Org cible AI Officer A.5.2, Plan vuln CVSS v4.0, SD 3 ans 271M XOF"
    }
    return base_dict.get(key, f"# {key} {client}")

def generate_certification_roadmap(norme,client,cabinet):
    return f"# CERTIFICATION {norme} BOUT EN BOUT {client}\nGap 200Q -> Mise en conformite -> Doc -> Implementation -> Audit blanc ISO 19011 -> Certification AFNOR. Cout {norme}: 25-60M XOF"
