
def local_fallback(user_prompt, kb_context, tdr_context):
    return f"""
# CYBER-GRC MASTER - MODE LOCAL AUTONOME
**CLIENT:** CLIENT | **MODE:** Local Big Four | **KB:** {len(kb_context)} chars

## MENU PHASE 0
- B1: OFFRE TECHNIQUE
- B2: OFFRE FINANCIERE XOF
- B3: DAO
- B4: PLAN AUDIT COMPLET
- B5: CERTIFICATION

## DEMANDE: {user_prompt}

### GAP ANALYSIS FORMAT 2026 OBLIGATOIRE
| Action | Mapping Normatif Complet |
|--------|--------------------------|
| MFA + Formation IA | ISO 27001 A5.17 + A7.2.2 + ISO 42001 A.3.2 + NIS2 Art.20 + PCI DSS 8.4.3 + NIST PR.AC-1 + CIS 6.5 + BCEAO Art.34 |
| Usage ChatGPT non maitrise | ISO 27001 A5.17 + ISO 42001 A.9.3 + EU AI Act Art.50 + OWASP LLM01 |
| Journalisation | ISO 27001 A.8.15 + NIS2 Art.21 + PCI DSS 10.7 + NIST DE.CM-1 |

### PLAN D'ACTION XOF
| Action | JH | Cout XOF | Mapping |
|--------|----|----------|---------|
| MFA + PAM | 15 | 7 500 000 | ISO 27001 A5.17 + BCEAO Art34 |
| Politique IA + Registre IA AI Act Art49 | 10 | 5 000 000 | ISO 42001 A.2 + A.9.3 + AI Act Art49 |
| PCA/PRA | 12 | 6 000 000 | ISO 22301 Cl8 + DORA Art11 |

> Configure GROQ_API_KEY pour generation Big Four 100+ pages avec API Llama 3.3 70B.
"""
