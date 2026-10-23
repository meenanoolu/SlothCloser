"""
SlothCloser – Local Evening Wind-Down Agent
A calm, offline companion that helps you close the day.
"""

import streamlit as st
from pathlib import Path
from agent import SlothAgent, list_available_models
from config import APP_TITLE, APP_SUBTITLE, APP_ICON, DEFAULT_MODEL, MOODS

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
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header, .stDeployButton {display: none !important; visibility: hidden;}

/* Hero */
.hero {
    text-align: center;
    margin-bottom: 2.2rem;
}
.hero-emoji {
    font-size: 3.4rem;
    line-height: 1;
    margin-bottom: 0.6rem;
    filter: drop-shadow(0 4px 12px rgba(156, 191, 156, 0.25));
}
.hero-title {
    font-family: 'Cormorant Garamond', Georgia, serif !important;
    font-size: 3rem !important;
    font-weight: 600 !important;
    letter-spacing: -0.03em;
    color: var(--text) !important;
    margin: 0 0 0.3rem 0 !important;
}
.hero-sub {
    font-family: 'Inter', sans-serif;
    font-size: 1.05rem;
    color: var(--text-muted);
    font-weight: 400;
    letter-spacing: 0.01em;
}

/* Section labels */
.section-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin: 1.6rem 0 0.7rem 0;
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
    min-height: 150px !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}
.stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--glow) !important;
}

/* Primary button */
.stButton > button[kind="primary"],
div[data-testid="stVerticalBlock"] > div:has(button) button {
    border-radius: 14px !important;
    font-weight: 600 !important;
    font-size: 1.02rem !important;
    padding: 0.78rem 1.5rem !important;
    border: none !important;
    transition: all 0.2s ease !important;
}

/* Main close button */
button[data-testid="baseButton-secondary"] {
    background: linear-gradient(135deg, #9cbf9c, #6f8f6f) !important;
    color: #0b0f14 !important;
}
button[data-testid="baseButton-secondary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 28px rgba(156, 191, 156, 0.35) !important;
}

/* Secondary / load example */
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
    box-shadow: none !important;
    transform: none !important;
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
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 0.55rem;
}
.result-card .card-body {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 1.2rem;
    line-height: 1.65;
    color: var(--text);
    white-space: pre-wrap;
}

/* Payoff */
.payoff {
    background: linear-gradient(145deg, rgba(156, 191, 156, 0.1), rgba(156, 191, 156, 0.03));
    border: 1px solid rgba(156, 191, 156, 0.25);
    border-radius: 18px;
    padding: 1.6rem 1.5rem;
    text-align: center;
    margin: 1.6rem 0 1.2rem 0;
}
.payoff-title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 1.55rem;
    color: var(--accent);
    margin-bottom: 0.3rem;
}
.payoff-text {
    font-size: 0.95rem;
    color: var(--text-muted);
    line-height: 1.5;
}

/* Badge */
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
    padding: 2.5rem 1.5rem;
    background: var(--surface);
    border: 1px dashed var(--border);
    border-radius: 18px;
    margin: 1.2rem 0;
}
.empty-icon {
    font-size: 2.2rem;
    margin-bottom: 0.7rem;
    opacity: 0.9;
}
.empty p {
    color: var(--text-muted);
    font-size: 0.98rem;
    line-height: 1.6;
    max-width: 300px;
    margin: 0 auto;
}

/* Footer */
.footer {
    text-align: center;
    color: var(--text-muted);
    font-size: 0.78rem;
    margin-top: 3rem;
    opacity: 0.6;
}

/* Expander */
.streamlit-expanderHeader {
    background: var(--surface) !important;
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
    font-size: 0.9rem !important;
    color: var(--text-muted) !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Hero
# -------------------------------------------------
st.markdown("""
<div class="hero">
    <div class="hero-emoji">🦥</div>
    <h1 class="hero-title">SlothCloser</h1>
    <p class="hero-sub">Slow &amp; steady evening closer</p>
</div>
""", unsafe_allow_html=True)

with st.expander("How it works"):
    st.markdown("""
1. Dump whatever is on your mind (messy is fine)  
2. Optionally choose how the day felt  
3. Click **Close my day**  
4. Receive a summary, open loops, bedtime reflection, one tiny thing for tomorrow, and an ambient prompt  

Everything can run fully offline with an open-weight model.  
If no model is available, a calm fallback still works.
""")

# -------------------------------------------------
# Sidebar
# -------------------------------------------------
with st.sidebar:
    st.markdown("### Settings")
    available = list_available_models()
    if available:
        default_index = available.index(DEFAULT_MODEL) if DEFAULT_MODEL in available else 0
        model = st.selectbox("Local model", options=available, index=default_index)
    else:
        st.info("No local models detected → calm offline fallback will be used.")
        model = st.text_input("Model name (optional)", value=DEFAULT_MODEL)

    st.caption("Tip: `ollama pull gemma2:2b`")
    st.caption("Works fully offline once the model is downloaded.")

    if st.session_state.history:
        st.markdown("---")
        st.markdown("### Recent closings")
        for i, item in enumerate(reversed(st.session_state.history[-4:])):
            label = f"{item['timestamp']} · {item.get('mood', 'neutral')}"
            if st.button(label, key=f"hist_{i}"):
                st.session_state.notes = item.get("notes", "")
                st.session_state.last_result = None
                st.rerun()

# -------------------------------------------------
# Input
# -------------------------------------------------
st.markdown('<div class="section-label">What happened today</div>', unsafe_allow_html=True)

col_a, col_b = st.columns([1, 3])
with col_a:
    if st.button("Load example", use_container_width=True):
        example_path = Path(__file__).parent / "example-notes.md"
        if example_path.exists():
            st.session_state.notes = example_path.read_text(encoding="utf-8")
            st.session_state.last_result = None
            st.rerun()

notes = st.text_area(
    label="notes",
    value=st.session_state.notes,
    height=160,
    placeholder="Paste your daily notes or just dump whatever is on your mind...",
    label_visibility="collapsed",
    key="notes_input",
)
st.session_state.notes = notes

uploaded = st.file_uploader("Or load a markdown / text file", type=["md", "txt", "markdown"])
if uploaded is not None:
    notes = uploaded.read().decode("utf-8")
    st.session_state.notes = notes
    st.session_state.last_result = None
    st.success(f"Loaded `{uploaded.name}`")

st.markdown('<div class="section-label">How does the day feel</div>', unsafe_allow_html=True)
mood_keys = list(MOODS.keys())
mood_labels = list(MOODS.values())
mood_index = st.radio(
    "mood",
    options=range(len(mood_keys)),
    format_func=lambda i: mood_labels[i],
    horizontal=True,
    label_visibility="collapsed",
    index=0,
)
selected_mood = mood_keys[mood_index]

st.write("")
_, col_btn, _ = st.columns([0.8, 2, 0.8])
with col_btn:
    close_btn = st.button("🦥  Close my day", use_container_width=True, type="primary")

# -------------------------------------------------
# Process
# -------------------------------------------------
if close_btn:
    if not notes or not notes.strip():
        st.warning("Write a few lines about your day first.")
    else:
        with st.status("Taking it slow…", expanded=True) as status:
            status.write("Reading your notes…")
            agent = SlothAgent(model=model)
            result = agent.close_day(notes, mood=selected_mood)
            status.update(label="Day closed", state="complete", expanded=False)

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
        st.markdown(f'<div class="badge badge-local">Local open-weight model · {model}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="meta">{result["timestamp"]} · {MOODS.get(result.get("mood", selected_mood), selected_mood)}</div>', unsafe_allow_html=True)

    cards = [
        ("Day summary", result["summary"]),
        ("Still open", result["open_loops"]),
        ("Bedtime reflection", result["bedtime"]),
        ("One tiny thing for tomorrow", result["tomorrow"]),
        ("Ambient soundscape", result["ambient"]),
    ]

    for label, content in cards:
        st.markdown(f"""
        <div class="result-card">
            <div class="card-label">{label}</div>
            <div class="card-body">{content}</div>
        </div>
        """, unsafe_allow_html=True)

    # Payoff
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

st.markdown("""
<div class="footer">
    Built for Hacktoberfest · Runs offline with open-weight models · Take it slow
</div>
""", unsafe_allow_html=True)