# 🦥 SlothCloser

**A calm, local evening wind-down agent** that closes the day for you - slowly, kindly, offline.

> Hacktoberfest Open-Source AI Challenge · Week 3: Slow and Steady

**Live demo:** [https://sloth-closer.onrender.com](https://sloth-closer.onrender.com)

---

## What it does

Dump whatever is still on your mind. You get:

1. Short human day summary  
2. Things still open  
3. Soft bedtime reflection (mood-aware)  
4. One optional tiny thing for tomorrow  
5. Ambient soundscape prompt  
6. **Spoken bedtime voice** via ElevenLabs (when API key is set)

Then:

> **Day closed.**  
> You can stop carrying it now.

---

## Why open-weight / local

Evening thoughts stay on your machine. No account. Zero ongoing cost. Works offline after the model is pulled. Swap Gemma / Llama / Qwen whenever you want.

---

## Partner tech (actually wired)

| Partner | In the product |
|---------|----------------|
| **Gemma** | Default open-weight model |
| **Ollama** | Local inference |
| **Render** | Hosting + Blueprint |
| **ElevenLabs** | Real in-app TTS for the bedtime reflection |
| **MongoDB Atlas** | Local history uses Atlas-ready document shape |

---

## Quick start

```bash
# Optional local model
ollama pull gemma2:2b

# App
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### Enable ElevenLabs voice (optional)

Create a `.env` in the project root:

```
ELEVENLABS_API_KEY=your_key_here
# optional:
# ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
```

Or in Streamlit Cloud / Render: set the same env var / secret.

Then after closing a day, click **Speak the reflection** — audio plays in the app. No pasting into another site.

---

## Speed

One structured model call (not five). Much faster on small models.

---

## UI

Ambient motion background, glass cards, staggered reveals, breathing hero, soft payoff animation. Built to feel like a focused evening app, not a dashboard.

---

Take it slow.
