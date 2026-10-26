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
}

html, body, .stApp {
    background: radial-gradient(ellipse 120% 80% at 50% -20%, #152018 0%, #0b0f14 55%) !important;
    color: var(--text);
    font-family: 'Inter', system-ui, sans-serif;
}

.block-container {
    max-width: 680px;
    padding-top: 1.6rem;
    padding-bottom: 3rem;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header, .stDeployButton {display: none !important; visibility: hidden;}

/* Hero */
.hero {
    text-align: center;
    margin-bottom: 1.8rem;
}
.hero-emoji {
    font-size: 3.2rem;
    line-height: 1;
    margin-bottom: 0.5rem;
    filter: drop-shadow(0 4px 14px rgba(156, 191, 156, 0.28));
}
.hero-title {
    font-family: 'Cormorant Garamond', Georgia, serif !important;
    font-size: 2.9rem !important;
    font-weight: 600 !important;
    letter-spacing: -0.03em;
    color: var(--text) !important;
    margin: 0 0 0.25rem 0 !important;
}
.hero-sub {
    font-family: 'Inter', sans-serif;
    font-size: 1.02rem;
    color: var(--text-muted);
    font-weight: 400;
    letter-spacing: 0.01em;
    max-width: 420px;
    margin: 0 auto;
    line-height: 1.5;
}

/* Section labels */
.section-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.76rem;
    font-weight: 600;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin: 1.4rem 0 0.55rem 0;
}

/* Text area */
.stTextArea textarea {
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 16px !important;
    font-size: 1.02rem !important;
    line-height: 1.7 !important;
    padding: 1.15rem 1.25rem !important;
    min-height: 155px !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}
.stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--glow) !important;
}

/* Buttons */
.stButton > button {
    border-radius: 14px !important;
    font-weight: 600 !important;
    font-size: 1.02rem !important;
    padding: 0.78rem 1.5rem !important;
    border: none !important;
    transition: all 0.2s ease !important;
}

/* Primary close button */
button[kind="primary"] {
    background: linear-gradient(135deg, #9cbf9c, #6f8f6f) !important;
    color: #0b0f14 !important;
}
button[kind="primary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 28px rgba(156, 191, 156, 0.35) !important;
}

/* Secondary buttons */
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
}

/* Radio mood */
.stRadio > label {display: none;}
.stRadio div[role="radiogroup"] {
    gap: 0.5rem;
    flex-wrap: wrap;
}
.stRadio div[role="radiogroup"] label {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 999px !important;
    padding: 0.4rem 0.95rem !important;
    color: var(--text-muted) !important;
    font-size: 0.88rem !important;
    transition: all 0.15s ease !important;
}
.stRadio div[role="radiogroup"] label:hover {
    border-color: var(--accent) !important;
    color: var(--text) !important;
}

/* Result cards */
.result-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1.35rem 1.5rem;
    margin-bottom: 0.9rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.2);
}
.result-card .card-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.74rem;
    font-weight: 600;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 0.55rem;
}
.result-card .card-body {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 1.22rem;
    line-height: 1.65;
    color: var(--text);
    white-space: pre-wrap;
}

/* Payoff */
.payoff {
    background: linear-gradient(145deg, rgba(156, 191, 156, 0.11), rgba(156, 191, 156, 0.03));
    border: 1px solid rgba(156, 191, 156, 0.28);
    border-radius: 18px;
    padding: 1.7rem 1.5rem;
    text-align: center;
    margin: 1.7rem 0 1.3rem 0;
}
.payoff-title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 1.65rem;
    color: var(--accent);
    margin-bottom: 0.35rem;
}
.payoff-text {
    font-size: 0.97rem;
    color: var(--text-muted);
    line-height: 1.55;
}

/* Badges */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    font-size: 0.75rem;
    font-weight: 500;
    padding: 0.28rem 0.75rem;
    border-radius: 999px;
    margin-bottom: 0.75rem;
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
    margin-bottom: 1.1rem;
}

/* Empty state */
.empty {
    text-align: center;
    padding: 2.4rem 1.5rem;
    background: var(--surface);
    border: 1px dashed var(--border);
    border-radius: 18px;
    margin: 1.2rem 0;
}
.empty-icon {
    font-size: 2.2rem;
    margin-bottom: 0.65rem;
    opacity: 0.9;
}
.empty p {
    color: var(--text-muted);
    font-size: 0.98rem;
    line-height: 1.6;
    max-width: 310px;
    margin: 0 auto;
}

/* Footer */
.footer {
    text-align: center;
    margin-top: 2.8rem;
    padding-top: 1.4rem;
    border-top: 1px solid var(--border);
    font-size: 0.78rem;
    color: var(--text-muted);
    line-height: 1.7;
}

/* History chips */
.history-item {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0.7rem 1rem;
    margin-bottom: 0.5rem;
    font-size: 0.88rem;
    color: var(--text-muted);
}
.history-item strong {
    color: var(--text);
}

/* Select / other Streamlit widgets */
.stSelectbox > div > div {
    background: var(--surface) !important;
    border-radius: 12px !important;
    border-color: var(--border) !important;
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

    for label, content in cards:
        safe = (
            content.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        st.markdown(f"""
        <div class="result-card">
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