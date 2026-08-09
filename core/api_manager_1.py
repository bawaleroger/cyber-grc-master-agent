
import json
from pathlib import Path
from core.knowledge_base import load_kb, save_kb

def add_api(name: str, base_url: str, api_key: str = "", description: str = ""):
    kb = load_kb()
    api = {"name": name, "base_url": base_url, "api_key": api_key, "description": description}
    kb["apis"].append(api)
    save_kb(kb)
    return api

def list_apis():
    return load_kb().get("apis", [])

def get_api_headers(api_name: str):
    kb = load_kb()
    for api in kb.get("apis", []):
        if api["name"] == api_name:
            if api.get("api_key"):
                return {"Authorization": f"Bearer {api['api_key']}"}
    return {}
