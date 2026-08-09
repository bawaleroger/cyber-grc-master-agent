
# 🛡️ CYBER-GRC MASTER AGENT V5

**Agent IA autonome - Prêt GitHub + Streamlit.io - Knowledge Base JSON persistante**

## CTO Architecture

### 1. Fonctionnalités Core
- **Dépôt auto-classifiant** : Rapports, Cours, TDRs, DAO, Offres Techniques/Financières, PSSI, Registres Risques → classés automatiquement via `core/classifier.py`
- **Dossiers auto-créés** : Si champ manquant, `ensure_folder_structure()` crée et classe seul (ex: si pas de PSSI, crée `data/documents/PSSI/`)
- **Documents toujours disponibles** : Stockage persistant `data/documents/<CLASSIFICATION>/` + index JSON `data/knowledge_base.json`
- **Knowledge Base JSON** : Toute doc → entrée JSON avec id, classification, path, summary, firm, client, timestamp. Searchable.
- **Multi-API** : Liaison illimitée d'APIs via sidebar → stockées dans KB `apis[]` → headers auto-générés
- **Prompt V5 intégré** : Sans normes ivoiriennes (RGSSI-CI désactivé), ISO 42001 intégré partout (7.2, 7.3, A.3.2, A.5.2, A.9.3, A.10)

### 2. Structure
```
cyber-grc-agent/
├── app.py -> Streamlit main (4 tabs)
├── core/
│   ├── agent.py -> Prompt V5 Master
│   ├── classifier.py -> Regex classification + auto-folder
│   ├── knowledge_base.py -> JSON CRUD persistant
│   └── api_manager.py -> Multi-API linking
├── data/
│   ├── knowledge_base.json -> Source de vérité
│   └── documents/
│       ├── TDR/
│       ├── DAO/
│       ├── OFFRE_TECHNIQUE/
│       ├── OFFRE_FINANCIERE/
│       ├── RAPPORT_AUDIT/
│       └── ...
├── requirements.txt
└── README.md
```

### 3. Déploiement
```bash
pip install -r requirements.txt
streamlit run app.py
```

**Streamlit Cloud** : push ce dossier sur GitHub, puis New App -> app.py. Ajoute OPENAI_API_KEY dans secrets pour activer LLM réel (actuellement réponse simulée Big Four).

### 4. Roadmap CTO V6
- ChromaDB Vector Store pour RAG sur tous les docs
- OpenAI Function Calling pour générer offres techniques/financières auto en XOF
- OCR + Pypdf pour extraction auto
- Webhook API pour lier Jira, Confluence, SharePoint

**Auteur CTO** : Cyber-GRC Master - Version sans CI + ISO 42001 partout
