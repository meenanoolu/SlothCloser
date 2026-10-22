# 🦥 SlothCloser

**A calm, local evening wind-down agent** that helps you close the day - slowly, kindly, and completely offline.

> Built for the **Hacktoberfest Open-Source AI Challenge: Week 3 – Slow and Steady**

Live demo (after deploy): will appear here once Render Blueprint is live.

---

## The Problem

Most of us end the day with mental clutter still open.  
Unfinished thoughts keep looping. It becomes hard to properly rest.

## The Solution

SlothCloser reads whatever you dump and gently gives you:

1. A short, human **day summary**
2. The few things **still open**
3. A soft **bedtime reflection** (shaped by mood)
4. **One tiny thing for tomorrow** (so the morning feels lighter)
5. An **ambient soundscape prompt** you can imagine or paste into any free generator

It rewards laziness: the AI does the closing work so you don’t have to.

---

## Why Open-Source AI Matters

| Benefit | Why it matters |
|---------|----------------|
| Fully local | Your private evening thoughts never leave your machine |
| Works offline | No internet required after the model is downloaded |
| Zero ongoing cost | Set it up once, use it forever |
| Swappable models | Gemma, Llama, Qwen, Phi… whatever you prefer |
| No surveillance | A closed API could never offer the same privacy |

---

## Features

- Local open-weight models via Ollama (Gemma recommended)
- Optional mood that gently shapes the reflection
- One tiny thing for tomorrow
- Ambient soundscape prompt
- Clear “Day closed — you can stop carrying it” payoff
- Graceful offline fallback (public demo never breaks)
- Session history + example loader
- Download the closing as markdown
- Distinctive calm dark UI
- Deployable as Render Blueprint (same style as firststep)

---

## Quick Start (Local)

```bash
# 1. Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull gemma2:2b

# 2. App
git clone https://github.com/meenanoolu/SlothCloser.git
cd SlothCloser
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

---

## Deploy on Render (Blueprint – same as firststep)

This repo contains `render.yaml` + `Dockerfile`.

1. Go to [Render Dashboard](https://dashboard.render.com)
2. **New** → **Blueprint**
3. Connect the `meenanoolu/SlothCloser` repository
4. Render will read `render.yaml` and create the service automatically
5. After the first deploy you get a public URL

Every push to `main` will auto-deploy.

---

## Tech Stack

- Streamlit (custom calm theme)
- Ollama + open-weight models
- Python
- Docker + Render Blueprint

---

Take it slow.  
The day will still be there tomorrow.
