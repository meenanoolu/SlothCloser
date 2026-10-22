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

# Session state
if "history" not in st.session_state:
    st.session_state.history = []
if "notes" not in st.session_state:
    st.session_state.notes = ""

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,600;1,7..72,400&family=Inter:wght@400;500;600&display=swap');

    :root {
        --bg: #0f1419;
        --surface: #1a222d;
        --text: #e8e6e3;
        --text-muted: #a8a29e;
        --accent: #7c9a82;
        --accent-dim: #5a7260;
        --border: #2d3748;
    }

    .stApp {
        background: linear-gradient(160deg, #0f1419 0%, #141c24 50%, #0f1419 100%);
        color: var(--text);
        font-family: 'Inter', system-ui, sans-serif;
    }

    h1, h2, h3 {
        font-family: 'Literata', Georgia, serif !important;
        font-weight: 600 !important;
        letter-spacing: -0.02em;
    }

    .main-title {
        font-size: 2.45rem !important;
        color: var(--text) !important;
        margin-bottom: 0.1rem !important;
    }

    .subtitle {
        color: var(--text-muted);
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }

    .stTextArea textarea {
        background-color: var(--surface) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        font-size: 1rem !important;
        line-height: 1.6 !important;
        padding: 1rem !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, var(--accent), var(--accent-dim)) !important;
        color: #0f1419 !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        padding: 0.7rem 1.8rem !important;
        width: 100%;
    }

    .result-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1.3rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 24px rgba(0,0,0,0.25);
    }

    .result-card h3 {
        color: var(--accent) !important;
        font-size: 1.05rem !important;
        margin-bottom: 0.6rem !important;
    }

    .result-card div {
        color: var(--text);
        line-height: 1.65;
        font-size: 1.01rem;
        white-space: pre-wrap;
    }

    .status-badge {
        display: inline-block;
        font-size: 0.78rem;
        padding: 0.22rem 0.65rem;
        border-radius: 999px;
        margin-bottom: 0.8rem;
        font-weight: 500;
    }

    .status-local {
        background: rgba(124, 154, 130, 0.18);
        color: #a8d5b0;
        border: 1px solid rgba(124, 154, 130, 0.35);
    }

    .status-fallback {
        background: rgba(180, 140, 80, 0.15);
        color: #e0c080;
        border: 1px solid rgba(180, 140, 80, 0.3);
    }

    .meta-line {
        color: var(--text-muted);
        font-size: 0.82rem;
        margin-bottom: 0.9rem;
    }

    .footer {
        text-align: center;
        color: var(--text-muted);
        font-size: 0.82rem;
        margin-top: 2.5rem;
        opacity: 0.7;
    }

    #MainMenu, footer, header, .stDeployButton {visibility: hidden; display: none;}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown(f'<h1 class="main-title">{APP_ICON} {APP_TITLE}</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="subtitle">{APP_SUBTITLE}</p>', unsafe_allow_html=True)

with st.expander("How it works", expanded=False):
    st.markdown("""
1. Dump whatever is on your mind (messy is fine)  
2. Optionally choose how the day felt  
3. Click **Close my day**  
4. Receive a summary, open loops, bedtime reflection, one tiny thing for tomorrow, and an ambient prompt  

Everything can run fully offline with an open-weight model.  
If no model is available, a calm fallback still works.
""")

# Sidebar
with st.sidebar:
    st.markdown("### Settings")
    available = list_available_models()
    if available:
        default_index = available.index(DEFAULT_MODEL) if DEFAULT_MODEL in available else 0
        model = st.selectbox("Local model", options=available, index=default_index)
    else:
        st.info("No local models detected → calm offline fallback will be used.")
        model = st.text_input("Model name (optional)", value=DEFAULT_MODEL)

    st.markdown("---")
    st.markdown("**Tip:** `ollama pull gemma2:2b`")
    st.caption("Works fully offline once the model is downloaded.")

    if st.session_state.history:
        st.markdown("---")
        st.markdown("### Recent closings")
        for i, item in enumerate(reversed(st.session_state.history[-4:])):
            label = f"{item['timestamp']} · {item.get('mood', 'neutral')}"
            if st.button(label, key=f"hist_{i}"):
                st.session_state.notes = item.get("notes", "")
                st.rerun()

# Main input
st.markdown("#### What happened today?")

col_a, col_b = st.columns([1, 3])
with col_a:
    if st.button("Load example", use_container_width=True):
        example_path = Path(__file__).parent / "example-notes.md"
        if example_path.exists():
            st.session_state.notes = example_path.read_text(encoding="utf-8")
            st.rerun()

notes = st.text_area(
    label="notes",
    value=st.session_state.notes,
    height=190,
    placeholder="Paste your daily notes or just dump whatever is on your mind...",
    label_visibility="collapsed",
    key="notes_input",
)
st.session_state.notes = notes

uploaded = st.file_uploader("Or load a markdown / text file", type=["md", "txt", "markdown"])
if uploaded is not None:
    notes = uploaded.read().decode("utf-8")
    st.session_state.notes = notes
    st.success(f"Loaded `{uploaded.name}`")

# Mood
st.markdown("#### How does the day feel? *(optional)*")
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

# Action
st.write("")
col1, col2, col3 = st.columns([1, 2.2, 1])
with col2:
    close_btn = st.button("🦥 Close my day", use_container_width=True)

# Process with progressive status (feels faster)
if close_btn:
    if not notes or not notes.strip():
        st.warning("Write a few lines about your day first.")
    else:
        status = st.status("Taking it slow…", expanded=True)
        agent = SlothAgent(model=model)

        status.write("Reading your notes…")
        result = agent.close_day(notes, mood=selected_mood)
        status.update(label="Day closed", state="complete", expanded=False)

        # History
        st.session_state.history.append({
            "timestamp": result["timestamp"],
            "mood": selected_mood,
            "notes": notes,
            "summary": result["summary"],
            "open_loops": result["open_loops"],
            "bedtime": result["bedtime"],
            "tomorrow": result["tomorrow"],
            "ambient": result["ambient"],
        })

        st.markdown("---")
        st.markdown("### Your day, closed")

        if result.get("used_fallback"):
            st.markdown('<div class="status-badge status-fallback">Using calm offline fallback</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="status-badge status-local">Powered by local open-weight model · {model}</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="meta-line">{result["timestamp"]} · Mood: {MOODS.get(selected_mood, selected_mood)}</div>', unsafe_allow_html=True)

        # Cards
        cards = [
            ("🌿 Day summary", result["summary"]),
            ("📋 Still open", result["open_loops"]),
            ("🌙 Bedtime reflection", result["bedtime"]),
            ("🌱 One tiny thing for tomorrow", result["tomorrow"]),
            ("🎧 Ambient soundscape prompt", result["ambient"]),
        ]
        for title, content in cards:
            st.markdown(f"""
            <div class="result-card">
                <h3>{title}</h3>
                <div>{content}</div>
            </div>
            """, unsafe_allow_html=True)

        # Download
        full_text = f"""# Day Closed — {result["timestamp"]}
**Mood:** {MOODS.get(selected_mood, selected_mood)}

## Summary
{result["summary"]}

## Still open
{result["open_loops"]}

## Bedtime reflection
{result["bedtime"]}

## One tiny thing for tomorrow
{result["tomorrow"]}

## Ambient soundscape prompt
{result["ambient"]}
"""
        st.download_button(
            label="💾 Save this closing",
            data=full_text,
            file_name=f"day-closed-{result['timestamp'].replace(' ', '-').replace(':', '')}.md",
            mime="text/markdown",
            use_container_width=True,
        )

st.markdown('<div class="footer">Built for Hacktoberfest · Runs offline with open-weight models · Take it slow</div>', unsafe_allow_html=True)