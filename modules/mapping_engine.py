
MAPPING_TABLE={"MFA":"ISO 27001:2022 A.5.17 + A.8.5 + ISO 42001:2023 A.9.3 + NIS2 Art.20 + PCI DSS 4.0.1 Req 8.4.3 + NIST CSF PR.AC-1 + CIS 6.5 + BCEAO Art.34","Formation IA":"ISO 27001 A.7.2.2 + ISO 42001 Cl.7.2 + A.3.2 + AI Act Art.4","ChatGPT":"ISO 27001 A5.17 + ISO 42001 A.9.3 + EU AI Act Art.50 + OWASP LLM01"}
def auto_map(action):
    for k,v in MAPPING_TABLE.items():
        if k.lower() in action.lower():
            return f"{action} -> {v}"
    return f"{action} -> ISO 27001:2022 A.5.1 + ISO 42001:2023 A.2.1 + NIS2 Art.21 [MAPPING GENERIQUE]"
