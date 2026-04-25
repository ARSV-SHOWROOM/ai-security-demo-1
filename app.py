import time
import re
import streamlit as st

# ======================================================
# CONFIG GENERAL
# ======================================================
USE_REAL_LLM = False  # <- NO cambiar por ahora (demo simulada)

# ======================================================
# GUARDRAIL SIMPLE (PROMPT INJECTION - DEMO)
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
    text = text.lower()
    return any(re.search(p, text) for p in INJECTION_PATTERNS)

# ======================================================
# AUDIT LOG (EVIDENCIA)
# ======================================================
def add_audit(event, decision, reason=""):
    st.session_state.audit_log.append({
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "event": event,
        "decision": decision,
