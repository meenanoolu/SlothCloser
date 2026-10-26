# 🦥 SlothCloser

A calm local agent that closes the day for you.

> Hacktoberfest · Week 3: Slow and Steady

**Demo:** https://sloth-closer.onrender.com

---

## The idea

You dump whatever is still on your mind.  
It hands back a short summary, open loops, a soft bedtime reflection, one optional tiny thing for tomorrow, an ambient prompt — and can **speak** the reflection out loud.

Then:

> **Day closed.**  
> You can stop carrying it now.

---

## Why open-weight / local

Your evening thoughts stay on your machine. No account. Zero ongoing cost. Works offline after the model is pulled.

---

## Partner tech (wired into the product)

| Partner | Role |
|---------|------|
| **Gemma** | Default open-weight model |
| **Ollama** | Local inference |
| **Render** | Hosting + Blueprint |
| **ElevenLabs** | Premium bedtime voice when `ELEVENLABS_API_KEY` is set |
| **edge-tts** | Free neural voice so demos always speak without a key |
| **MongoDB Atlas** | Local history uses Atlas-ready documents |

---

## Run

```bash
ollama pull gemma2:2b   # optional but best
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### Optional: ElevenLabs quality voice

```bash
# .env
ELEVENLABS_API_KEY=your_key
```

Without a key the app still speaks using a free neural voice. Users never see key setup messages in the UI.

---

Take it slow.
