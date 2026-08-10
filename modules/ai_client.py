
import os
import streamlit as st
class AIClient:
    def __init__(self):
        self.mode="local"
        try:
            if st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY"):
                self.mode="groq"
            elif st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY"):
                self.mode="openai"
        except: pass
    def generate(self, user_prompt, kb_context="", tdr_context=""):
        try:
            core=open("modules/prompt_core.py",encoding="utf-8").read()[:8000]
        except: core="CYBER-GRC MASTER"
        full=f"{core}\nKB:{kb_context[:6000]}\nTDR:{tdr_context[:4000]}\nDEMANDE:{user_prompt}"
        # Groq
        try:
            if self.mode=="groq":
                from groq import Groq
                key=st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
                client=Groq(api_key=key)
                r=client.chat.completions.create(model="llama-3.3-70b-versatile",messages=[{"role":"system","content":"Tu es CYBER-GRC MASTER Big Four"},{"role":"user","content":full}],temperature=0.15,max_tokens=8000)
                return r.choices[0].message.content
        except Exception as e:
            st.warning(f"Groq fail {e}")
        try:
            from openai import OpenAI
            key=st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
            if key:
                client=OpenAI(api_key=key)
                r=client.chat.completions.create(model="gpt-4o",messages=[{"role":"system","content":"CYBER-GRC MASTER"},{"role":"user","content":full}],temperature=0.2,max_tokens=8000)
                return r.choices[0].message.content
        except Exception as e:
            st.warning(f"OpenAI fail {e}")
        from modules.report_generator import local_fallback
        return local_fallback(user_prompt, kb_context, tdr_context)
ai=AIClient()
