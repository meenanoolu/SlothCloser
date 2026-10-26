# 🦥 SlothCloser

A calm local agent that closes the day for you.

> Hacktoberfest · Week 3: Slow and Steady

**Stack:** FastAPI · custom frontend · Ollama/Gemma · edge-tts · Render

---

## Run locally

```bash
# optional local model
ollama pull gemma2:2b

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn server:app --reload --port 8000
```

Open http://localhost:8000

---

## What changed 

- real web app (FastAPI + HTML/CSS/JS)
- Ambient motion background, glass cards, polished interactions
- Free neural bedtime voice (edge-tts) — no API key
- Same single-call Gemma agent + local history

## Partner tech in use

| Partner | Role |
|---------|------|
| **Gemma** | Open-weight model |
| **Ollama** | Local inference |
| **Render** | Hosting ($50 credit available) |
| **edge-tts** | Free in-app voice |
| **MongoDB Atlas–ready** | Local history documents |


---

Take it slow.
