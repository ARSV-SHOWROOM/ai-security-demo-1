import time
import re
from typing import Optional, List, Dict
import streamlit as st

# ======================================================
# CONFIG GENERAL
# ======================================================
USE_REAL_LLM = False  # Demo simulada (sin API Key)

# ======================================================
# 4-3-3 (mental model)
# ======================================================
AI_TYPES = ["Analítica", "Predictiva", "Generativa", "Agéntica"]

AI_USE_CASES: Dict[str, str] = {
    "Consumo (Workforce / GenAI)": "Usuarios consumen GenAI (Chat/Copilot-like). Riesgo: prompt injection + data leakage.",
    "Desarrollo (RAG / App)": "Equipos construyen apps con GenAI + RAG sobre docs. Riesgo: RAG poisoning + secretos.",
    "Accionable (Agentes / Tools)": "Agentes ejecutan acciones (tickets/infra/etc.). Riesgo: tool abuse + over-permission.",
}
USE_CASE_ORDER = list(AI_USE_CASES.keys())

# ======================================================
# Guardrail simple (Prompt Injection - demo)
# ======================================================
INJECTION_PATTERNS = [
    r"ignore (all|previous) instructions",
    r"system prompt",
    r"developer message",
    r"reveal.*instructions",
    r"bypass",
    r"jailbreak",
    r"internal policy",
]

def looks_like_prompt_injection(text: str) -> bool:
    t = text.lower()
    return any(re.search(p, t) for p in INJECTION_PATTERNS)

# ======================================================
