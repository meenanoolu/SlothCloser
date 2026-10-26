"""
SlothCloser v1.5 – premium calm UI + ambient motion + real ElevenLabs voice
"""

import streamlit as st
from pathlib import Path

from agent import SlothAgent, list_available_models, save_closing, load_recent_closings
from config import (
    APP_TITLE,
    APP_SUBTITLE,
    APP_ICON,
    DEFAULT_MODEL,
    MOODS,
    CHALLENGE_TAG,
    APP_VERSION,
    ELEVENLABS_API_KEY,
)
from voice import is_voice_available, synthesize_bedtime

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Session
for k, v in {
    "notes": "",
    "last_result": None,
    "page": "home",
    "voice_bytes": None,
    "voice_error": None,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# -------------------------------------------------
# CSS – ambient motion background + premium calm UI
# -------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Inter:wght@400;500;600;700&display=swap');

:root {
    --bg: #070b10;
    --surface: #121820;
    --surface-2: #182028;
    --text: #ebe7e2;
    --text-muted: #8a8580;
    --accent: #9cbf9c;
    --accent-dim: #6f8f6f;
    --border: #242c38;
    --glow: rgba(156, 191, 156, 0.14);
    --warm: #d4b48a;
}

/* Full-viewport ambient motion layer */
.stApp {
    background: #070b10 !important;
}
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background:
        radial-gradient(ellipse 90% 70% at 15% 20%, rgba(40, 80, 55, 0.35) 0%, transparent 55%),
        radial-gradient(ellipse 80% 60% at 85% 75%, rgba(30, 55, 70, 0.28) 0%, transparent 50%),
        radial-gradient(ellipse 70% 50% at 50% 100%, rgba(25, 45, 35, 0.4) 0%, transparent 45%),
        radial-gradient(ellipse 100% 80% at 50% -20%, rgba(35, 70, 50, 0.22) 0%, transparent 50%),
        #070b10;
    animation: ambientShift 28s ease-in-out infinite alternate;
}
.stApp::after {
    content: "";
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background:
        radial-gradient(circle at 30% 40%, rgba(156, 191, 156, 0.06) 0%, transparent 25%),
        radial-gradient(circle at 70% 60%, rgba(100, 140, 160, 0.05) 0%, transparent 22%);
    animation: ambientFloat 18s ease-in-out infinite alternate;
    opacity: 0.9;
}

@keyframes ambientShift {
    0%   { filter: hue-rotate(0deg) brightness(1); transform: scale(1); }
    50%  { filter: hue-rotate(8deg) brightness(1.05); transform: scale(1.02); }
    100% { filter: hue-rotate(-6deg) brightness(0.98); transform: scale(1.01); }
}
@keyframes ambientFloat {
    0%   { opacity: 0.7; transform: translateY(0) scale(1); }
    100% { opacity: 1; transform: translateY(-12px) scale(1.04); }
}

html, body {
    color: var(--text);
    font-family: 'Inter', system-ui, sans-serif;
    background: transparent !important;
}

.block-container {
    max-width: 660px;
    padding-top: 1rem;
    padding-bottom: 3.5rem;
    position: relative;
    z-index: 1;
}

#MainMenu, footer, header, .stDeployButton,
[data-testid="stToolbar"], [data-testid="stDecoration"] {
    display: none !important;
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes softPulse {
    0%, 100% { opacity: 0.85; transform: scale(1); }
    50%      { opacity: 1; transform: scale(1.05); }
}
@keyframes breathe {
    0%, 100% { filter: drop-shadow(0 4px 16px rgba(156, 191, 156, 0.25)); }
    50%      { filter: drop-shadow(0 8px 28px rgba(156, 191, 156, 0.45)); }
}
@keyframes cardReveal {
    from { opacity: 0; transform: translateY(18px) scale(0.97); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes payoffReveal {
    from { opacity: 0; transform: translateY(14px) scale(0.96); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

.hero {
    text-align: center;
    margin-bottom: 1.7rem;
    animation: fadeUp 0.7s ease-out both;
}
.hero-emoji {
    font-size: 3.3rem;
    line-height: 1;
    margin-bottom: 0.45rem;
    display: inline-block;
    animation: breathe 4.8s ease-in-out infinite;
}
.hero-title {
    font-family: 'Cormorant Garamond', Georgia, serif !important;
    font-size: 2.85rem !important;
    font-weight: 600 !important;
    letter-spacing: -0.03em;
    color: var(--text) !important;
    margin: 0 0 0.25rem 0 !important;
}
.hero-sub {
    font-size: 1.02rem;
    color: var(--text-muted);
    max-width: 420px;
    margin: 0 auto;
    line-height: 1.55;
}

.section-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin: 1.35rem 0 0.55rem 0;
}

.stTextArea textarea {
    background: rgba(18, 24, 32, 0.85) !important;
    backdrop-filter: blur(12px);
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 18px !important;
    font-size: 1.02rem !important;
    line-height: 1.7 !important;
    padding: 1.15rem 1.25rem !important;
    min-height: 150px !important;
    transition: border-color 0.25s ease, box-shadow 0.3s ease !important;
}
.stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--glow), 0 10px 36px rgba(0,0,0,0.35) !important;
    background: rgba(24, 32, 40, 0.92) !important;
}

.stButton > button {
    border-radius: 14px !important;
    font-weight: 600 !important;
    font-size: 0.98rem !important;
    padding: 0.75rem 1.35rem !important;
    border: none !important;
    transition: all 0.22s cubic-bezier(0.22, 1, 0.36, 1) !important;
}
button[kind="primary"] {
    background: linear-gradient(135deg, #9cbf9c, #6f8f6f) !important;
    color: #070b10 !important;
    box-shadow: 0 4px 18px rgba(156, 191, 156, 0.3) !important;
}
button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 32px rgba(156, 191, 156, 0.42) !important;
}
div[data-testid="stHorizontalBlock"] button {
    background: rgba(18, 24, 32, 0.8) !important;
    color: var(--text-muted) !important;
    border: 1px solid var(--border) !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
}
div[data-testid="stHorizontalBlock"] button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    background: rgba(24, 32, 40, 0.95) !important;
}

.stRadio > label { display: none; }
.stRadio div[role="radiogroup"] { gap: 0.5rem; flex-wrap: wrap; }
.stRadio div[role="radiogroup"] label {
    background: rgba(18, 24, 32, 0.75) !important;
    border: 1px solid var(--border) !important;
    border-radius: 999px !important;
    padding: 0.4rem 0.95rem !important;
    color: var(--text-muted) !important;
    font-size: 0.86rem !important;
    transition: all 0.2s ease !important;
}
.stRadio div[role="radiogroup"] label:hover {
    border-color: var(--accent) !important;
    color: var(--text) !important;
    background: rgba(24, 32, 40, 0.9) !important;
}

.result-card {
    background: rgba(18, 24, 32, 0.82);
    backdrop-filter: blur(14px);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1.3rem 1.45rem;
    margin-bottom: 0.85rem;
    box-shadow: 0 6px 28px rgba(0,0,0,0.25);
    animation: cardReveal 0.55s cubic-bezier(0.22, 1, 0.36, 1) both;
    transition: border-color 0.25s ease, transform 0.25s ease, box-shadow 0.3s ease;
}
.result-card:hover {
    border-color: rgba(156, 191, 156, 0.35);
    transform: translateY(-2px);
    box-shadow: 0 10px 36px rgba(0,0,0,0.3);
}
.result-card .card-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 0.5rem;
}
.result-card .card-body {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 1.22rem;
    line-height: 1.65;
    color: var(--text);
    white-space: pre-wrap;
}

.payoff {
    background: linear-gradient(145deg, rgba(156, 191, 156, 0.14), rgba(156, 191, 156, 0.03));
    border: 1px solid rgba(156, 191, 156, 0.3);
    border-radius: 18px;
    padding: 1.7rem 1.5rem;
    text-align: center;
    margin: 1.5rem 0 1.2rem 0;
    animation: payoffReveal 0.65s cubic-bezier(0.22, 1, 0.36, 1) 0.35s both;
    box-shadow: 0 0 40px rgba(156, 191, 156, 0.08);
}
.payoff-title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 1.7rem;
    color: var(--accent);
    margin-bottom: 0.35rem;
}
.payoff-text {
    font-size: 0.96rem;
    color: var(--text-muted);
    line-height: 1.55;
}

.badge {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    font-size: 0.74rem;
    font-weight: 500;
    padding: 0.28rem 0.75rem;
    border-radius: 999px;
    margin-bottom: 0.7rem;
}
.badge-local {
    background: rgba(156, 191, 156, 0.14);
    color: #b5d4b5;
    border: 1px solid rgba(156, 191, 156, 0.28);
}
.badge-fallback {
    background: rgba(200, 160, 100, 0.12);
    color: #d4b48a;
    border: 1px solid rgba(200, 160, 100, 0.25);
}
.badge-voice {
    background: rgba(120, 160, 200, 0.14);
    color: #a8c4e0;
    border: 1px solid rgba(120, 160, 200, 0.3);
}

.empty {
    text-align: center;
    padding: 2.6rem 1.5rem;
    background: rgba(18, 24, 32, 0.7);
    border: 1px dashed var(--border);
    border-radius: 18px;
    margin: 1.2rem 0;
    animation: fadeUp 0.55s ease-out both;
}
.empty-icon {
    font-size: 2.3rem;
    margin-bottom: 0.6rem;
    display: inline-block;
    animation: softPulse 3.5s ease-in-out infinite;
}
.empty p {
    color: var(--text-muted);
    font-size: 0.96rem;
    line-height: 1.65;
    max-width: 300px;
    margin: 0 auto;
}

.history-item {
    background: rgba(18, 24, 32, 0.75);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 0.85rem 1.05rem;
    margin-bottom: 0.5rem;
    font-size: 0.88rem;
    color: var(--text-muted);
    transition: border-color 0.2s ease, transform 0.2s ease;
}
.history-item:hover {
    border-color: rgba(156, 191, 156, 0.32);
    transform: translateX(3px);
}
.history-item strong { color: var(--text); }

.footer {
    text-align: center;
    margin-top: 2.6rem;
    padding-top: 1.4rem;
    border-top: 1px solid var(--border);
    font-size: 0.75rem;
    color: var(--text-muted);
    line-height: 1.75;
    position: relative;
    z-index: 1;
}

.stSelectbox > div > div {
    background: rgba(18, 24, 32, 0.85) !important;
    border-radius: 12px !important;
    border-color: var(--border) !important;
}
div[data-testid="stSpinner"] > div {
    border-top-color: var(--accent) !important;
}

.page-title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 2rem;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 0.3rem;
    animation: fadeUp 0.5s ease-out both;
}
.page-sub {
    font-size: 0.95rem;
    color: var(--text-muted);
    margin-bottom: 1.5rem;
    line-height: 1.5;
}

.voice-box {
    background: rgba(18, 24, 32, 0.85);
    border: 1px solid rgba(120, 160, 200, 0.28);
    border-radius: 16px;
    padding: 1.1rem 1.25rem;
    margin: 0.9rem 0 1.1rem 0;
    animation: fadeUp 0.5s ease-out both;
}
.voice-box .voice-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #a8c4e0;
    margin-bottom: 0.55rem;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Top nav
# -------------------------------------------------
n1, n2, n3 = st.columns(3)
with n1:
    if st.button("Close the day", use_container_width=True, key="nav_home"):
        st.session_state.page = "home"
        st.rerun()
with n2:
    if st.button("History", use_container_width=True, key="nav_hist"):
        st.session_state.page = "history"
        st.rerun()
with n3:
    if st.button("About", use_container_width=True, key="nav_about"):
        st.session_state.page = "about"
        st.rerun()

# -------------------------------------------------
# HOME
# -------------------------------------------------
if st.session_state.page == "home":
    st.markdown(f"""
    <div class="hero">
        <div class="hero-emoji">{APP_ICON}</div>
        <h1 class="hero-title">{APP_TITLE}</h1>
        <p class="hero-sub">{APP_SUBTITLE}</p>
    </div>
    """, unsafe_allow_html=True)

    available = list_available_models()
    model = DEFAULT_MODEL
    if available:
        gemma = [m for m in available if "gemma" in m.lower()]
        model = gemma[0] if gemma else available[0]

    cs, cm = st.columns([2.4, 1])
    with cs:
        if available:
            st.markdown(f'<div class="badge badge-local">● Local open-weight · {model}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="badge badge-fallback">○ Offline fallback active</div>', unsafe_allow_html=True)
        if is_voice_available():
            st.markdown('<div class="badge badge-voice">🎙️ ElevenLabs voice ready</div>', unsafe_allow_html=True)
    with cm:
        if available and len(available) > 1:
            model = st.selectbox("Model", available, index=available.index(model) if model in available else 0, label_visibility="collapsed")

    st.markdown('<div class="section-label">What is still on your mind?</div>', unsafe_allow_html=True)
    notes = st.text_area(
        "notes",
        value=st.session_state.notes,
        height=150,
        placeholder="Dump anything. Messy is fine.\n\nFinished the design notes…\nStill need to reply to Maya…\nFeeling a little tired but content…",
        label_visibility="collapsed",
    )
    st.session_state.notes = notes

    st.markdown('<div class="section-label">How does the day feel?</div>', unsafe_allow_html=True)
    mood_keys = list(MOODS.keys())
    selected_idx = st.radio(
        "mood",
        options=range(len(mood_keys)),
        format_func=lambda i: list(MOODS.values())[i],
        horizontal=True,
        label_visibility="collapsed",
        index=0,
        key="mood_radio",
    )
    selected_mood = mood_keys[selected_idx]

    c1, c2, c3 = st.columns([2.2, 1, 1])
    with c1:
        close_clicked = st.button("Close the day", type="primary", use_container_width=True)
    with c2:
        if st.button("Example", use_container_width=True):
            p = Path(__file__).parent / "example-notes.md"
            if p.exists():
                st.session_state.notes = p.read_text(encoding="utf-8")
                st.rerun()
    with c3:
        if st.button("Clear", use_container_width=True):
            st.session_state.notes = ""
            st.session_state.last_result = None
            st.session_state.voice_bytes = None
            st.rerun()

    if close_clicked:
        if not (notes or "").strip():
            st.warning("Write a few notes first — even one line is enough.")
        else:
            with st.spinner("Closing the day…"):
                agent = SlothAgent(model=model)
                result = agent.close_day(notes, mood=selected_mood)
                result["mood"] = selected_mood
                try:
                    save_closing(result, notes)
                except Exception:
                    pass
                st.session_state.last_result = result
                st.session_state.voice_bytes = None
                st.session_state.voice_error = None
                st.rerun()

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
            st.markdown('<div class="badge badge-fallback">Calm offline fallback</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="badge badge-local">Local open-weight · {model}</div>', unsafe_allow_html=True)

        cards = [
            ("Day summary", result["summary"]),
            ("Still open", result["open_loops"]),
            ("Bedtime reflection", result["bedtime"]),
            ("One tiny thing for tomorrow", result["tomorrow"]),
            ("Ambient soundscape", result["ambient"]),
        ]
        for i, (label, content) in enumerate(cards):
            safe = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            delay = 0.05 + i * 0.07
            st.markdown(f"""
            <div class="result-card" style="animation-delay: {delay}s">
                <div class="card-label">{label}</div>
                <div class="card-body">{safe}</div>
            </div>
            """, unsafe_allow_html=True)

        # ElevenLabs voice – real in-app playback
        st.markdown("""
        <div class="voice-box">
            <div class="voice-label">Bedtime voice</div>
        </div>
        """, unsafe_allow_html=True)

        if is_voice_available():
            if st.session_state.voice_bytes is None and st.session_state.voice_error is None:
                if st.button("🎙️ Speak the reflection", use_container_width=True, key="gen_voice"):
                    with st.spinner("Generating calm voice…"):
                        audio = synthesize_bedtime(result["bedtime"])
                        if audio:
                            st.session_state.voice_bytes = audio
                            st.session_state.voice_error = None
                        else:
                            st.session_state.voice_error = "Could not generate voice. Check your API key or try again."
                        st.rerun()
            if st.session_state.voice_bytes:
                st.audio(st.session_state.voice_bytes, format="audio/mp3")
                st.caption("Generated with ElevenLabs — play while the lights go down.")
            elif st.session_state.voice_error:
                st.caption(st.session_state.voice_error)
        else:
            st.caption(
                "Add `ELEVENLABS_API_KEY` to a `.env` file (or Streamlit secrets) to hear the reflection spoken in-app. "
                "Free tier works for demos."
            )

        st.markdown("""
        <div class="payoff">
            <div class="payoff-title">Day closed.</div>
            <div class="payoff-text">You can stop carrying it now.<br>
            Whatever is left can wait until morning.</div>
        </div>
        """, unsafe_allow_html=True)

        full_md = f"""# Day Closed — {result["timestamp"]}
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
            "💾 Save this closing",
            data=full_md,
            file_name=f"day-closed-{result['timestamp'].replace(' ', '-').replace(':', '')}.md",
            mime="text/markdown",
            use_container_width=True,
        )

# -------------------------------------------------
# HISTORY
# -------------------------------------------------
elif st.session_state.page == "history":
    st.markdown('<div class="page-title">Recent closings</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-sub">Saved locally on this machine. Documents are shaped for MongoDB Atlas if you want them across devices later.</p>',
        unsafe_allow_html=True,
    )
    closings = load_recent_closings(15)
    if not closings:
        st.markdown("""
        <div class="empty">
            <div class="empty-icon">📭</div>
            <p>No closings yet.<br>When you close a day it will appear here.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for h in closings:
            summary = h.get("summary", "")[:155]
            if len(h.get("summary", "")) > 155:
                summary += "…"
            mood_label = MOODS.get(h.get("mood", "neutral"), h.get("mood", ""))
            st.markdown(f"""
            <div class="history-item">
                <strong>{h.get('timestamp', '')}</strong> · {mood_label}<br>
                {summary}
            </div>
            """, unsafe_allow_html=True)

# -------------------------------------------------
# ABOUT
# -------------------------------------------------
elif st.session_state.page == "about":
    st.markdown('<div class="page-title">Why this exists</div>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-sub">A quiet ritual for the end of the day — not another productivity system.</p>',
        unsafe_allow_html=True,
    )
    st.markdown("""
You dump whatever is still on your mind.  
SlothCloser gives you a short summary, the open loops, a soft bedtime reflection,  
one optional tiny thing for tomorrow, and an ambient prompt —  
then a clear **Day closed.** so you can stop carrying it.

**Why open-weight / local?**  
Evening thoughts stay on your machine. No account required. Zero ongoing cost.  
Swap models whenever you want. Works offline after the first pull.

**What’s under the hood**
- **Gemma** — default open-weight model  
- **Ollama** — local inference  
- **Render** — live demo + Blueprint  
- **ElevenLabs** — real in-app voice for the bedtime reflection (optional API key)  
- **MongoDB Atlas–ready** local history documents  
""")

st.markdown(f"""
<div class="footer">
    {CHALLENGE_TAG}<br>
    Open-weight · Local-first · Zero ongoing cost · v{APP_VERSION}<br>
    Take it slow.
</div>
""", unsafe_allow_html=True)
