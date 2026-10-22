"""
SlothCloser – Local Evening Wind-Down Agent
A calm, offline companion that helps you close the day.
Built for Hacktoberfest Open-Source AI Challenge – Slow & Steady.
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

# -------------------------------------------------
# Session state
# -------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []
if "notes" not in st.session_state:
    st.session_state.notes = ""
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# -------------------------------------------------
# Custom CSS – distinctive, calm, non-plain
# -------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,500;0,7..72,600;1,7..72,400&family=Inter:wght@400;500;600&display=swap');

    :root {
        --bg: #0c1017;
        --surface: #151c27;
        --surface-2: #1c2533;
        --text: #e9e7e4;
        --text-muted: #9a958e;
        --accent: #8fbc8f;
        --accent-soft: rgba(143, 188, 143, 0.15);
        --accent-dim: #6b8f6b;
        --border: #2a3344;
        --warning: #d4a574;
    }

    .stApp {
        background: radial-gradient(ellipse at top, #141c28 0%, #0c1017 60%);
        color: var(--text);
        font-family: 'Inter', system-ui, sans-serif;
    }

    /* Typography */
    h1, h2, h3, h4 {
        font-family: 'Literata', Georgia, serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.025em;
        color: var(--text) !important;
    }

    .hero {
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
    }

    .hero-icon {
        font-size: 3.2rem;
        line-height: 1;
        margin-bottom: 0.4rem;
    }

    .hero-title {
        font-size: 2.6rem !important;
        margin: 0 0 0.25rem 0 !important;
        background: linear-gradient(135deg, #e9e7e4 30%, #8fbc8f 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .hero-sub {
        color: var(--text-muted);
        font-size: 1.08rem;
        font-weight: 400;
        margin-bottom: 1.8rem;
    }

    /* Cards */
    .result-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 1.35rem 1.55rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.28);
        transition: border-color 0.2s ease;
    }

    .result-card:hover {
        border-color: rgba(143, 188, 143, 0.35);
    }

    .result-card h3 {
        color: var(--accent) !important;
        font-size: 1.02rem !important;
        margin: 0 0 0.65rem 0 !important;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: 0.01em;
    }

    .result-card .content {
        color: var(--text);
        line-height: 1.7;
        font-size: 1.03rem;
        white-space: pre-wrap;
        font-family: 'Literata', Georgia, serif;
    }

    /* Status badges */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        font-size: 0.78rem;
        padding: 0.3rem 0.75rem;
        border-radius: 999px;
        font-weight: 500;
        margin-bottom: 0.9rem;
    }

    .badge-local {
        background: var(--accent-soft);
        color: #b5d9b5;
        border: 1px solid rgba(143, 188, 143, 0.3);
    }

    .badge-fallback {
        background: rgba(212, 165, 116, 0.12);
        color: #e0c090;
        border: 1px solid rgba(212, 165, 116, 0.25);
    }

    .meta {
        color: var(--text-muted);
        font-size: 0.83rem;
        margin-bottom: 1.1rem;
    }

    /* Final payoff message */
    .payoff {
        background: linear-gradient(135deg, rgba(143, 188, 143, 0.12), rgba(143, 188, 143, 0.04));
        border: 1px solid rgba(143, 188, 143, 0.28);
        border-radius: 18px;
        padding: 1.4rem 1.6rem;
        text-align: center;
        margin: 1.5rem 0 1.2rem 0;
    }

    .payoff-title {
        font-family: 'Literata', Georgia, serif;
        font-size: 1.35rem;
        color: var(--accent);
        margin-bottom: 0.35rem;
    }

    .payoff-text {
        color: var(--text-muted);
        font-size: 0.95rem;
        line-height: 1.5;
    }

    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 2.2rem 1.5rem;
        background: var(--surface);
        border: 1px dashed var(--border);
        border-radius: 18px;
        margin: 1rem 0 1.5rem 0;
    }

    .empty-state .icon {
        font-size: 2.4rem;
        margin-bottom: 0.6rem;
        opacity: 0.85;
    }

    .empty-state p {
        color: var(--text-muted);
        font-size: 0.98rem;
        line-height: 1.55;
        max-width: 340px;
        margin: 0 auto;
    }

    /* Inputs */
    .stTextArea textarea {
        background-color: var(--surface) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: 14px !important;
        font-size: 1rem !important;
        line-height: 1.65 !important;
        padding: 1.1rem !important;
        min-height: 160px !important;
    }

    .stTextArea textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px rgba(143, 188, 143, 0.2) !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, var(--accent), var(--accent-dim)) !important;
        color: #0c1017 !important;
        border: none !important;
        border-radius: 14px !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        padding: 0.75rem 1.6rem !important;
        width: 100%;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 24px rgba(143, 188, 143, 0.3) !important;
    }

    /* Secondary button style override for Load example */
    div[data-testid="stHorizontalBlock"] button {
        background: var(--surface-2) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        font-weight: 500 !important;
    }

    div[data-testid="stHorizontalBlock"] button:hover {
        border-color: var(--accent) !important;
        color: var(--accent) !important;
        box-shadow: none !important;
        transform: none !important;
    }

    /* Radio / mood */
    .stRadio > div {
        gap: 0.5rem;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: var(--text-muted);
        font-size: 0.8rem;
        margin-top: 3rem;
        padding-bottom: 1.5rem;
        opacity: 0.65;
    }

    /* Hide chrome */
    #MainMenu, footer, header, .stDeployButton {visibility: hidden; display: none;}
    .block-container {padding-top: 1.5rem; max-width: 720px;}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Hero
# -------------------------------------------------
st.markdown("""
<div class="hero">
    <div class="hero-icon">🦥</div>
    <h1 class="hero-title">SlothCloser</h1>
    <p class="hero-sub">Slow &amp; steady evening closer</p>
</div>
""", unsafe_allow_html=True)

# How it works
with st.expander("How it works", expanded=False):
    st.markdown("""
1. Dump whatever is on your mind (messy is fine)  
2. Optionally choose how the day felt  
3. Click **Close my day**  
4. Receive a summary, open loops, bedtime reflection, one tiny thing for tomorrow, and an ambient prompt  

Everything can run fully offline with an open-weight model.  
If no model is available, a calm fallback still works so the demo never breaks.
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
        st.info("No local models detected. Calm offline fallback will be used.")
        model = st.text_input("Model name (optional)", value=DEFAULT_MODEL)

    st.markdown("---")
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
# Input section
# -------------------------------------------------
st.markdown("#### What happened today?")

col_a, col_b = st.columns([1, 2.8])
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
    height=170,
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

# Mood
st.markdown("#### How does the day feel?")
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

# Action button
st.write("")
_, col_btn, _ = st.columns([0.6, 2.2, 0.6])
with col_btn:
    close_btn = st.button("🦥  Close my day", use_container_width=True)

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

        # Save history
        st.session_state.history.append({
            "timestamp": result["timestamp"],
            "mood": selected_mood,
            "notes": notes,
            **{k: result[k] for k in ["summary", "open_loops", "bedtime", "tomorrow", "ambient"]},
        })
        st.session_state.last_result = result
        st.rerun()

# -------------------------------------------------
# Results (from session so they persist)
# -------------------------------------------------
result = st.session_state.last_result

if result is None and not notes.strip():
    st.markdown("""
    <div class="empty-state">
        <div class="icon">🌙</div>
        <p>Your notes will appear here.<br>
        When you’re ready, close the day and let the rest wait until morning.</p>
    </div>
    """, unsafe_allow_html=True)

if result:
    st.markdown("---")

    # Status badge
    if result.get("used_fallback"):
        st.markdown('<div class="badge badge-fallback">Using calm offline fallback</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="badge badge-local">Local open-weight model · {model}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="meta">{result["timestamp"]} · {MOODS.get(result.get("mood", selected_mood), selected_mood)}</div>', unsafe_allow_html=True)

    # The five cards
    cards = [
        ("🌿  Day summary", result["summary"]),
        ("📋  Still open", result["open_loops"]),
        ("🌙  Bedtime reflection", result["bedtime"]),
        ("🌱  One tiny thing for tomorrow", result["tomorrow"]),
        ("🎧  Ambient soundscape", result["ambient"]),
    ]

    for title, content in cards:
        st.markdown(f"""
        <div class="result-card">
            <h3>{title}</h3>
            <div class="content">{content}</div>
        </div>
        """, unsafe_allow_html=True)

    # Creative payoff feature
    st.markdown("""
    <div class="payoff">
        <div class="payoff-title">Day closed.</div>
        <div class="payoff-text">You can stop carrying it now.<br>
        Whatever is left can wait until morning.</div>
    </div>
    """, unsafe_allow_html=True)

    # Download
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

# Footer
st.markdown("""
<div class="footer">
    Built for Hacktoberfest · Runs offline with open-weight models · Take it slow
</div>
""", unsafe_allow_html=True)