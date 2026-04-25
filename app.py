import time
import re
import streamlit as st

# ======================================================
# Configuración general
# ======================================================
st.set_page_config(
    page_title="AI Security Demo – 4-3-3",
    layout="centered"
)

# ======================================================
# Modelos mentales
# ======================================================
AI_TYPES = ["Analítica", "Predictiva", "Generativa", "Agéntica"]

USE_CASES = [
    "Consumo (Workforce / GenAI)",
    "Desarrollo (RAG / App)",
    "Accionable (Agentes / Tools)"
]

USE_CASE_DESC = {
    USE_CASES[0]: "Usuarios consumen GenAI (Chat/Copilot-like). Riesgo: prompt injection + data leakage.",
    USE_CASES[1]: "Apps corporativas con RAG y datos internos. Riesgo: RAG poisoning + exposición de secretos.",
    USE_CASES[2]: "Agentes ejecutan acciones reales. Riesgo: abuso de herramientas y sobre-permisos."
}

# ======================================================
# Guardrail demo (prompt injection)
# ======================================================
PATTERNS = [
    r"ignore (all|previous) instructions",
    r"system prompt",
    r"developer message",
    r"reveal",
    r"bypass",
    r"jailbreak"
]

def is_attack(text):
    t = text.lower()
    return any(re.search(p, t) for p in PATTERNS)

# ======================================================
# Estado
# ======================================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "audit" not in st.session_state:
    st.session_state.audit = []

if "blocked" not in st.session_state:
    st.session_state.blocked = False

# ======================================================
# Render de flujo (simple y estable)
# ======================================================
def render_flow(use_case, highlight=None, blocked=False):
    ok = "palegreen"
    warn = "gold"
    bad = "lightcoral"
    neutral = "lightgrey"

    def node(name, label, color):
        if highlight == name:
            return f'{name} [label="{label}", style=filled, fillcolor=lightskyblue, penwidth=3]'
        return f'{name} [label="{label}", style=filled, fillcolor={color}]'

    guard_color = bad if blocked else ok
    style = "dashed" if blocked else "solid"

    if use_case == USE_CASES[0]:
        dot = f"""
        digraph {{
            rankdir=LR;
            {node("User","Usuario", ok)}
            {node("Gateway","Prompt Gateway", warn)}
            {node("Guard","Guardrails", guard_color)}
            {node("LLM","LLM Runtime", neutral)}
            {node("Resp","Respuesta", ok)}

            User -> Gateway -> Guard;
            Guard -> LLM [style={style}]
            LLM -> Resp [style={style}]
        }}
        """
    elif use_case == USE_CASES[1]:
        dot = f"""
        digraph {{
            rankdir=LR;
            {node("App","App / API", ok)}
            {node("Gateway","Prompt Gateway", warn)}
            {node("Guard","Guardrails", guard_color)}
            {node("KB","Knowledge Base", neutral)}
            {node("LLM","LLM Runtime", neutral)}
            {node("Resp","Respuesta", ok)}

            App -> Gateway -> Guard;
            Guard -> KB [style={style}]
            KB -> LLM [style={style}]
            LLM -> Resp [style={style}]
        }}
        """
    else:
        dot = f"""
        digraph {{
            rankdir=LR;
            {node("User","Usuario", ok)}
            {node("Agent","AI Agent", warn)}
            {node("Guard","Guardrails", guard_color)}
            {node("Tools","Tools / APIs", warn)}
            {node("Action","Acción", ok)}

            User -> Agent -> Guard;
            Guard -> Tools [style={style}]
            Tools -> Action [style={style}]
        }}
        """

    st.graphviz_chart(dot, width="stretch")

def animate(use_case, blocked, slot):
    sequence = [
        ["User", "Gateway", "Guard", "LLM", "Resp"],
        ["App", "Gateway", "Guard", "KB", "LLM", "Resp"],
        ["User", "Agent", "Guard", "Tools", "Action"]
    ][USE_CASES.index(use_case)]

    if blocked:
        sequence = sequence[:sequence.index("Guard")+1]

    for s in sequence:
        with slot:
            render_flow(use_case, highlight=s, blocked=blocked)
        time.sleep(0.35)

# ======================================================
# UI
# ======================================================
st.title("🧠🔐 AI Security Demo – 4‑3‑3")
st.caption("Riesgo visible | Flujos controlados | Decisión y enforcement")

with st.sidebar:
    animate_on = st.toggle("Animar flujo", True)
    uc = st.selectbox("Caso de uso", USE_CASES)
    st.caption(USE_CASE_DESC[uc])

case_num = USE_CASES.index(uc) + 1
st.subheader(f"Caso de uso {case_num}/3 — {uc}")
st.caption(USE_CASE_DESC[uc])

flow_slot = st.container()
render_flow(uc, blocked=st.session_state.blocked)

st.subheader("💬 Chat")
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

prompt = st.chat_input("Escribí un prompt (demo)")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    attack = is_attack(prompt)

    st.session_state.blocked = attack

    if animate_on:
        animate(uc, attack, flow_slot)

    if attack:
        msg = "🚫 **Bloqueado por Guardrails**\n\nEl flujo se detuvo en el punto de decisión."
    else:
        msg = "✅ **Prompt permitido**\n\nEl flujo completó su ejecución."

    st.session_state.messages.append({"role": "assistant", "content": msg})

    st.session_state.audit.append({
        "caso": uc,
        "prompt": prompt[:40],
        "decision": "blocked" if attack else "allowed"
    })

    st.rerun()

st.divider()
st.subheader("🧾 Audit log")
st.dataframe(st.session_state.audit, use_container_width=True)
