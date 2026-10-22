"""
SlothCloser – Local Evening Wind-Down Agent
A calm, offline companion that helps you close the day.
"""

import streamlit as st
from pathlib import Path
from agent import SlothAgent, list_available_models
from config import APP_TITLE, APP_SUBTITLE, APP_ICON, DEFAULT_MODEL

# -------------------------------------------------
# Page config
# -------------------------------------------------
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="centered",
    initial_sidebar_state="collapsed",
)

# -------------------------------------------------
# Custom CSS – soft, slow, calming aesthetic
# -------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Literata:ital,opsz,wght@0,7..72,400;0,7..72,600;1,7..72,400&family=Inter:wght@400;500;600&display=swap');

    :root {
        --bg: #0f1419;
        --surface: #1a222d;
        --surface-2: #232d3b;
        --text: #e8e6e3;
        --text-muted: #a8a29e;
        --accent: #7c9a82;          /* soft sage */
        --accent-dim: #5a7260;
        --border: #2d3748;
        --success: #8fbc8f;
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
        font-size: 2.6rem !important;
        color: var(--text) !important;
        margin-bottom: 0.2rem !important;
    }

    .subtitle {
        color: var(--text-muted);
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 400;
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

    .stTextArea textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px rgba(124, 154, 130, 0.25) !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, var(--accent), var(--accent-dim)) !important;
        color: #0f1419 !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        padding: 0.7rem 1.8rem !important;
        transition: all 0.25s ease !important;
        width: 100%;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(124, 154, 130, 0.35) !important;
    }

    .stSelectbox > div > div {
        background-color: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        color: var(--text) !important;
    }

    .result-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1.5rem 1.75rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 4px 24px rgba(0,0,0,0.25);
    }

    .result-card h3 {
        color: var(--accent) !important;
        font-size: 1.15rem !important;
        margin-bottom: 0.75rem !important;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .result-card p, .result-card div {
        color: var(--text);
        line-height: 1.65;
        font-size: 1.02rem;
        white-space: pre-wrap;
    }

    .footer {
        text-align: center;
        color: var(--text-muted);
        font-size: 0.85rem;
        margin-top: 3rem;
        opacity: 0.7;
    }

    /* Hide Streamlit chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Header
# -------------------------------------------------
st.markdown(f'<h1 class="main-title">{APP_ICON} {APP_TITLE}</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="subtitle">{APP_SUBTITLE}</p>', unsafe_allow_html=True)

# -------------------------------------------------
# Sidebar / Model selection (collapsed by default)
# -------------------------------------------------
with st.sidebar:
    st.markdown("### Settings")
    available = list_available_models()
    if available:
        model = st.selectbox(
            "Local model",
            options=available,
            index=0 if DEFAULT_MODEL not in available else available.index(DEFAULT_MODEL),
            help="Models currently available in your Ollama instance"
        )
    else:
        st.warning("No models found. Make sure Ollama is running.")
        model = st.text_input("Model name", value=DEFAULT_MODEL)
    st.markdown("---")
    st.markdown("**Tip:** Run `ollama pull gemma2:2b` or any open model you like.")

# -------------------------------------------------
# Main input area
# -------------------------------------------------
st.markdown("#### What happened today?")
notes = st.text_area(
    label="notes",
    height=220,
    placeholder="Paste your daily notes, journal entry, or just dump whatever is on your mind...\n\nExample:\n- Finished the API design\n- Still need to reply to Sarah\n- Felt a bit drained after the meeting\n- Bought groceries",
    label_visibility="collapsed",
)

# Optional file upload
uploaded = st.file_uploader("Or load a markdown / text file", type=["md", "txt", "markdown"])
if uploaded is not None:
    notes = uploaded.read().decode("utf-8")
    st.success(f"Loaded {uploaded.name}")

# -------------------------------------------------
# Action button
# -------------------------------------------------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    close_btn = st.button("🦥 Close my day", use_container_width=True)

# -------------------------------------------------
# Process
# -------------------------------------------------
if close_btn:
    if not notes or not notes.strip():
        st.warning("Write a few lines about your day first.")
    else:
        with st.spinner("Taking it slow… thinking…"):
            agent = SlothAgent(model=model)
            result = agent.close_day(notes)

        st.markdown("---")
        st.markdown("### Your day, closed")

        # Summary card
        st.markdown(f"""
        <div class="result-card">
            <h3>🌿 Day summary</h3>
            <div>{result["summary"]}</div>
        </div>
        """, unsafe_allow_html=True)

        # Open loops card
        st.markdown(f"""
        <div class="result-card">
            <h3>📋 Still open</h3>
            <div>{result["open_loops"]}</div>
        </div>
        """, unsafe_allow_html=True)

        # Bedtime card
        st.markdown(f"""
        <div class="result-card">
            <h3>🌙 Bedtime reflection</h3>
            <div>{result["bedtime"]}</div>
        </div>
        """, unsafe_allow_html=True)

        # Download buttons
        full_text = f"""# Day Closed – {Path.cwd().name}

## Summary
{result["summary"]}

## Still open
{result["open_loops"]}

## Bedtime reflection
{result["bedtime"]}
"""
        st.download_button(
            label="💾 Save this closing",
            data=full_text,
            file_name="day-closed.md",
            mime="text/markdown",
            use_container_width=True,
        )

# -------------------------------------------------
# Footer
# -------------------------------------------------
st.markdown("""
<div class="footer">
    Built for Hacktoberfest · Runs 100% offline with open-weight models · Take it slow
</div>
""", unsafe_allow_html=True)