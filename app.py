"""
SlothCloser – Local Evening Wind-Down Agent
A calm, offline companion that helps you close the day.
"""

import streamlit as st
from pathlib import Path
from agent import SlothAgent, list_available_models
from config import (
    APP_TITLE,
    APP_SUBTITLE,
    APP_ICON,
    DEFAULT_MODEL,
    MOODS,
    CHALLENGE_TAG,
    APP_VERSION,
)

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Session state
if "history" not in st.session_state:
    st.session_state.history = []
if "notes" not in st.session_state:
    st.session_state.notes = ""
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# -------------------------------------------------
# Beautiful calm CSS
# -------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Inter:wght@400;500;600&display=swap');

:root {
    --bg: #0b0f14;
    --surface: #141a22;
    --surface-2: #1a222d;
    --text: #e8e4df;
    --text-muted: #8b8680;
    --accent: #9cbf9c;
    --accent-dim: #6f8f6f;
    --border: #252d3a;
    --glow: rgba(156, 191, 156, 0.12);
    --glow-strong: rgba(156, 191, 156, 0.22);
}

html, body, .stApp {
    background: radial-gradient(ellipse 130% 90% at 50% -25%, #152018 0%, #0b0f14 60%) !important;
    color: var(--text);
    font-family: 'Inter', system-ui, sans-serif;
}

.block-container {
    max-width: 680px;
    padding-top: 1.4rem;
    padding-bottom: 3.5rem;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header, .stDeployButton {display: none !important; visibility: hidden;}

/* ---------- Motion keyframes ---------- */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(18px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
}
@keyframes softPulse {
    0%, 100% { opacity: 0.85; transform: scale(1); }
    50%      { opacity: 1; transform: scale(1.04); }
}
@keyframes gentleGlow {
    0%, 100% { box-shadow: 0 0 0 0 rgba(156, 191, 156, 0); }
    50%      { box-shadow: 0 0 28px 4px rgba(156, 191, 156, 0.18); }
}
@keyframes breathe {
    0%, 100% { filter: drop-shadow(0 4px 12px rgba(156, 191, 156, 0.22)); }
    50%      { filter: drop-shadow(0 6px 22px rgba(156, 191, 156, 0.38)); }
}
@keyframes cardReveal {
    from { opacity: 0; transform: translateY(22px) scale(0.97); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes payoffReveal {
    from { opacity: 0; transform: translateY(16px) scale(0.96); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes shimmer {
    0%   { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

/* ---------- Hero ---------- */
.hero {
    text-align: center;
    margin-bottom: 2rem;
    animation: fadeUp 0.7s ease-out both;
}
.hero-emoji {
    font-size: 3.4rem;
    line-height: 1;
    margin-bottom: 0.55rem;
    display: inline-block;
    animation: breathe 4.5s ease-in-out infinite;
}
.hero-title {
    font-family: 'Cormorant Garamond', Georgia, serif !important;
    font-size: 3rem !important;
    font-weight: 600 !important;
    letter-spacing: -0.03em;
    color: var(--text) !important;
    margin: 0 0 0.3rem 0 !important;
    animation: fadeUp 0.75s ease-out 0.08s both;
}
.hero-sub {
    font-family: 'Inter', sans-serif;
    font-size: 1.05rem;
    color: var(--text-muted);
    font-weight: 400;
    letter-spacing: 0.01em;
    max-width: 440px;
    margin: 0 auto;
    line-height: 1.55;
    animation: fadeUp 0.8s ease-out 0.16s both;
}

/* ---------- Section labels ---------- */
.section-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.74rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin: 1.55rem 0 0.6rem 0;
    animation: fadeIn 0.5s ease-out both;
}

/* ---------- Text area ---------- */
.stTextArea textarea {
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    font-size: 1.03rem !important;
    line-height: 1.7 !important;
    padding: 1.2rem 1.3rem !important;
    min-height: 160px !important;
    transition: border-color 0.25s ease, box-shadow 0.3s ease, background 0.25s ease !important;
}
.stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--glow), 0 8px 32px rgba(0,0,0,0.25) !important;
    background: var(--surface-2) !important;
}

/* ---------- Buttons ---------- */
.stButton > button {
    border-radius: 14px !important;
    font-weight: 600 !important;
    font-size: 1.02rem !important;
    padding: 0.8rem 1.5rem !important;
    border: none !important;
    transition: all 0.25s cubic-bezier(0.22, 1, 0.36, 1) !important;
    position: relative;
    overflow: hidden;
}
button[kind="primary"] {
    background: linear-gradient(135deg, #9cbf9c, #6f8f6f) !important;
    color: #0b0f14 !important;
    box-shadow: 0 4px 18px rgba(156, 191, 156, 0.25) !important;
}
button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 32px rgba(156, 191, 156, 0.4) !important;
}
button[kind="primary"]:active {
    transform: translateY(0) !important;
}
div[data-testid="stHorizontalBlock"] button {
    background: var(--surface) !important;
    color: var(--text-muted) !important;
    border: 1px solid var(--border) !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
}
div[data-testid="stHorizontalBlock"] button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    background: var(--surface-2) !important;
    transform: translateY(-1px);
}

/* ---------- Mood radio ---------- */
.stRadio > label {display: none;}
.stRadio div[role="radiogroup"] {
    gap: 0.55rem;
    flex-wrap: wrap;
}
.stRadio div[role="radiogroup"] label {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 999px !important;
    padding: 0.42rem 1rem !important;
    color: var(--text-muted) !important;
    font-size: 0.88rem !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
}
.stRadio div[role="radiogroup"] label:hover {
    border-color: var(--accent) !important;
    color: var(--text) !important;
    background: var(--surface-2) !important;
    transform: translateY(-1px);
}

/* ---------- Result cards ---------- */
.result-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1.4rem 1.55rem;
    margin-bottom: 0.95rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.22);
    animation: cardReveal 0.55s cubic-bezier(0.22, 1, 0.36, 1) both;
    transition: border-color 0.25s ease, box-shadow 0.3s ease, transform 0.25s ease;
}
.result-card:hover {
    border-color: rgba(156, 191, 156, 0.35);
    box-shadow: 0 8px 36px rgba(0,0,0,0.28);
    transform: translateY(-2px);
}
.result-card:nth-child(1) { animation-delay: 0.05s; }
.result-card:nth-child(2) { animation-delay: 0.12s; }
.result-card:nth-child(3) { animation-delay: 0.19s; }
.result-card:nth-child(4) { animation-delay: 0.26s; }
.result-card:nth-child(5) { animation-delay: 0.33s; }

.result-card .card-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.73rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 0.55rem;
}
.result-card .card-body {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 1.24rem;
    line-height: 1.65;
    color: var(--text);
    white-space: pre-wrap;
}

/* ---------- Payoff ---------- */
.payoff {
    background: linear-gradient(145deg, rgba(156, 191, 156, 0.13), rgba(156, 191, 156, 0.03));
    border: 1px solid rgba(156, 191, 156, 0.3);
    border-radius: 18px;
    padding: 1.85rem 1.6rem;
    text-align: center;
    margin: 1.8rem 0 1.4rem 0;
    animation: payoffReveal 0.7s cubic-bezier(0.22, 1, 0.36, 1) 0.4s both;
    transition: box-shadow 0.4s ease;
}
.payoff:hover {
    box-shadow: 0 0 40px rgba(156, 191, 156, 0.15);
}
.payoff-title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 1.75rem;
    color: var(--accent);
    margin-bottom: 0.4rem;
    letter-spacing: -0.01em;
}
.payoff-text {
    font-size: 0.98rem;
    color: var(--text-muted);
    line-height: 1.55;
}

/* ---------- Badges ---------- */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    font-size: 0.75rem;
    font-weight: 500;
    padding: 0.3rem 0.8rem;
    border-radius: 999px;
    margin-bottom: 0.8rem;
    animation: fadeIn 0.5s ease-out both;
}
.badge-local {
    background: rgba(156, 191, 156, 0.12);
    color: #b5d4b5;
    border: 1px solid rgba(156, 191, 156, 0.25);
}
.badge-fallback {
    background: rgba(200, 160, 100, 0.1);
    color: #d4b48a;
    border: 1px solid rgba(200, 160, 100, 0.22);
}

.meta {
    font-size: 0.82rem;
    color: var(--text-muted);
    margin-bottom: 1.15rem;
    animation: fadeIn 0.5s ease-out 0.1s both;
}

/* ---------- Empty state ---------- */
.empty {
    text-align: center;
    padding: 2.6rem 1.6rem;
    background: var(--surface);
    border: 1px dashed var(--border);
    border-radius: 18px;
    margin: 1.3rem 0;
    animation: fadeUp 0.6s ease-out both;
}
.empty-icon {
    font-size: 2.4rem;
    margin-bottom: 0.7rem;
    opacity: 0.9;
    display: inline-block;
    animation: softPulse 3.5s ease-in-out infinite;
}
.empty p {
    color: var(--text-muted);
    font-size: 0.98rem;
    line-height: 1.65;
    max-width: 320px;
    margin: 0 auto;
}

/* ---------- History ---------- */
.history-item {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0.75rem 1.05rem;
    margin-bottom: 0.55rem;
    font-size: 0.88rem;
    color: var(--text-muted);
    transition: border-color 0.2s ease, transform 0.2s ease;
}
.history-item:hover {
    border-color: rgba(156, 191, 156, 0.3);
    transform: translateX(3px);
}
.history-item strong {
    color: var(--text);
}

/* ---------- Footer ---------- */
.footer {
    text-align: center;
    margin-top: 3rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--border);
    font-size: 0.78rem;
    color: var(--text-muted);
    line-height: 1.75;
    animation: fadeIn 0.8s ease-out 0.3s both;
}

/* ---------- Selectbox ---------- */
.stSelectbox > div > div {
    background: var(--surface) !important;
    border-radius: 12px !important;
    border-color: var(--border) !important;
    transition: border-color 0.2s ease !important;
}

/* Smooth spinner feel */
div[data-testid="stSpinner"] > div {
    border-top-color: var(--accent) !important;
}
</style>

""", unsafe_allow_html=True)

# -------------------------------------------------
# Hero
# -------------------------------------------------
st.markdown(f"""
<div class="hero">
    <div class="hero-emoji">{APP_ICON}</div>
    <h1 class="hero-title">{APP_TITLE}</h1>
    <p class="hero-sub">{APP_SUBTITLE}</p>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Model status + selection
# -------------------------------------------------
available = list_available_models()
model = DEFAULT_MODEL
if available:
    # Prefer any Gemma if present
    gemma = [m for m in available if "gemma" in m.lower()]
    if gemma:
        model = gemma[0]
    else:
        model = available[0]

col_status, col_model = st.columns([2, 1])
with col_status:
    if available:
        st.markdown(
            f'<div class="badge badge-local">Local open-weight ready · {model}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="badge badge-fallback">No local model detected — calm offline fallback active</div>',
            unsafe_allow_html=True,
        )
with col_model:
    if available and len(available) > 1:
        model = st.selectbox("Model", available, index=available.index(model) if model in available else 0, label_visibility="collapsed")

# -------------------------------------------------
# Notes input
# -------------------------------------------------
st.markdown('<div class="section-label">What is still on your mind?</div>', unsafe_allow_html=True)

notes = st.text_area(
    "notes",
    value=st.session_state.notes,
    height=160,
    placeholder="Dump anything. Messy is fine. No structure required.\n\nFinished the design notes…\nStill need to reply to Maya…\nFeeling a little tired but content…",
    label_visibility="collapsed",
)
st.session_state.notes = notes

# Mood
st.markdown('<div class="section-label">How does the day feel?</div>', unsafe_allow_html=True)
mood_keys = list(MOODS.keys())
mood_labels = list(MOODS.values())
selected_idx = st.radio(
    "mood",
    options=range(len(mood_keys)),
    format_func=lambda i: mood_labels[i],
    horizontal=True,
    label_visibility="collapsed",
    index=0,
)
selected_mood = mood_keys[selected_idx]

# Action row
c1, c2, c3 = st.columns([2, 1, 1])
with c1:
    close_clicked = st.button("Close the day", type="primary", use_container_width=True)
with c2:
    if st.button("Load example", use_container_width=True):
        example_path = Path(__file__).parent / "example-notes.md"
        if example_path.exists():
            st.session_state.notes = example_path.read_text(encoding="utf-8")
            st.rerun()
with c3:
    if st.button("Clear", use_container_width=True):
        st.session_state.notes = ""
        st.session_state.last_result = None
        st.rerun()

# -------------------------------------------------
# Run the agent
# -------------------------------------------------
if close_clicked:
    if not (notes or "").strip():
        st.warning("Write a few notes first — even one line is enough.")
    else:
        with st.spinner("Closing the day… slowly…"):
            agent = SlothAgent(model=model)
            result = agent.close_day(notes, mood=selected_mood)
            result["mood"] = selected_mood
            st.session_state.history.append({
                "timestamp": result["timestamp"],
                "mood": selected_mood,
                "notes": notes,
                **{k: result[k] for k in ["summary", "open_loops", "bedtime", "tomorrow", "ambient"]},
            })
            st.session_state.last_result = result
            st.rerun()

# -------------------------------------------------
# Results
# -------------------------------------------------
result = st.session_state.last_result

if result is None and not (notes or "").strip():
    st.markdown("""
    <div class="empty">
        <div class="empty-icon">🌙</div>
        <p>Your notes will appear here.<br>
        When you’re ready, close the day<br>and let the rest wait until morning.</p>
    </div>
    """, unsafe_allow_html=True)

if result:
    st.markdown("---")

    if result.get("used_fallback"):
        st.markdown('<div class="badge badge-fallback">Using calm offline fallback</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="badge badge-local">Local open-weight · {model}</div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="meta">{result["timestamp"]} · {MOODS.get(result.get("mood", selected_mood), selected_mood)}</div>',
        unsafe_allow_html=True,
    )

    cards = [
        ("Day summary", result["summary"]),
        ("Still open", result["open_loops"]),
        ("Bedtime reflection", result["bedtime"]),
        ("One tiny thing for tomorrow", result["tomorrow"]),
        ("Ambient soundscape", result["ambient"]),
    ]

    for i, (label, content) in enumerate(cards):
        safe = (
            content.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        delay = 0.06 + i * 0.08
        st.markdown(f"""
        <div class="result-card" style="animation-delay: {delay}s">
            <div class="card-label">{label}</div>
            <div class="card-body">{safe}</div>
        </div>
        """, unsafe_allow_html=True)

    # The emotional payoff — the whole point of the tool
    st.markdown("""
    <div class="payoff">
        <div class="payoff-title">Day closed.</div>
        <div class="payoff-text">You can stop carrying it now.<br>
        Whatever is left can wait until morning.</div>
    </div>
    """, unsafe_allow_html=True)

    full_text = f"""# Day Closed — {result["timestamp"]}
**Mood:** {MOODS.get(result.get("mood", "neutral"), "neutral")}

## Summary
{result["summary"]}

## Still open
{result["open_loops"]}

## Bedtime reflection
{result["bedtime"]}

## One tiny thing for tomorrow
{result["tomorrow"]}

## Ambient soundscape
{result["ambient"]}
"""
    st.download_button(
        label="💾  Save this closing",
        data=full_text,
        file_name=f"day-closed-{result['timestamp'].replace(' ', '-').replace(':', '')}.md",
        mime="text/markdown",
        use_container_width=True,
    )

# -------------------------------------------------
# Recent closings (lightweight personal memory)
# -------------------------------------------------
if st.session_state.history:
    with st.expander(f"Recent closings ({len(st.session_state.history)})", expanded=False):
        for h in reversed(st.session_state.history[-5:]):
            st.markdown(f"""
            <div class="history-item">
                <strong>{h['timestamp']}</strong> · {MOODS.get(h.get('mood', 'neutral'), h.get('mood', ''))}<br>
                {h.get('summary', '')[:140]}{'…' if len(h.get('summary', '')) > 140 else ''}
            </div>
            """, unsafe_allow_html=True)

st.markdown(f"""
<div class="footer">
    {CHALLENGE_TAG}<br>
    Open-weight models · Local-first · Zero ongoing cost · v{APP_VERSION}<br>
    Take it slow.
</div>
""", unsafe_allow_html=True)