
MAPPING_TABLE={"MFA":"ISO 27001 A5.17 + A8.5 + ISO 42001 A.9.3 + NIS2 Art.20 + PCI DSS 8.4.3 + BCEAO Art.34","ChatGPT":"ISO 27001 A5.17 + ISO 42001 A.9.3 + AI Act Art.50 + OWASP LLM01"}
def auto_map(a):
    for k,v in MAPPING_TABLE.items():
        if k.lower() in a.lower(): return f"{a} -> {v}"
    return f"{a} -> ISO 27001 A.5.1 + ISO 42001 A.2.1 + NIS2 Art.21"
