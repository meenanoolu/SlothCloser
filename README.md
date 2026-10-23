# 🦥 SlothCloser

**A calm, local evening wind-down agent** that helps you close the day - slowly, kindly, and completely offline.

> Built for the **Hacktoberfest Open-Source AI Challenge: Week 3 – Slow and Steady**

**Live demo:** [https://sloth-closer.onrender.com](https://sloth-closer.onrender.com)

---

## Why I built this

I kept ending days with a messy head.  
Notes half-written, tasks still floating, a vague feeling that something was unfinished. I would close the laptop and still feel the day following me.

I wanted something that would do the closing work for me — not another productivity system, just a quiet ritual that says “you can stop carrying this now.”

SlothCloser is that ritual.

---

## What it does

You dump whatever is on your mind (messy is fine).  
It gives you back:

1. **A short, human day summary**
2. **The few things still open** (so your brain can stop looping)
3. **A soft bedtime reflection** shaped by how the day actually felt
4. **One tiny thing for tomorrow** — optional, light, never a to-do list
5. **An ambient soundscape prompt** you can imagine or paste into any free generator

Then it shows a clear payoff:

> **Day closed.**  
> You can stop carrying it now.

That last line is the whole point.

---

## Why open-source AI matters here

| Benefit | Why it matters |
|---------|----------------|
| **Fully local** | Your private evening thoughts never leave your machine |
| **Works offline** | No internet required after the model is downloaded |
| **Zero ongoing cost** | Set it up once, use it forever |
| **Swappable models** | Gemma, Llama, Qwen, Phi… whatever you prefer |
| **No surveillance** | A closed API could never offer the same privacy or permanence |

This is the kind of tool that only makes sense with open-weight models. A hosted chatbot would feel wrong for something this personal.

---

## Features

- Local open-weight models via Ollama (Gemma recommended)
- Optional mood that gently shapes the reflection
- One tiny thing for tomorrow
- Ambient soundscape prompt
- Clear “Day closed” mental-payoff message
- Graceful offline fallback (public demo never breaks)
- Session history of recent closings
- Load example + file upload
- Download the closing as markdown
- Distinctive calm dark UI
- Deployable as Render Blueprint

---

## Quick Start (Local)

```bash
# 1. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama pull gemma2:2b

# 2. Run the app
git clone https://github.com/meenanoolu/SlothCloser.git
cd SlothCloser
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Open the URL shown (usually http://localhost:8501).

---

## Deploy on Render (Blueprint)

This repo contains `render.yaml` + `Dockerfile`.

1. Go to [Render Dashboard](https://dashboard.render.com)
2. **New** → **Blueprint**
3. Connect the `meenanoolu/SlothCloser` repository
4. Render reads `render.yaml` and creates the service
5. Every push to `main` auto-deploys

Live instance: [https://sloth-closer.onrender.com](https://sloth-closer.onrender.com)

---

## Tech Stack

- **UI**: Streamlit (custom calm dark theme)
- **AI**: Ollama + open-weight models (Gemma by default)
- **Language**: Python
- **Deploy**: Docker + Render Blueprint

---

## Project Structure

```
sloth-closer/
├── app.py            # Streamlit UI + mood + history + payoff
├── agent.py          # Ollama agent + offline fallback
├── prompts.py        # All prompts (easy to edit tone)
├── config.py         # Settings & mood definitions
├── Dockerfile
├── render.yaml
├── example-notes.md
├── requirements.txt
└── README.md
```

---

Take it slow.  
The day will still be there tomorrow.
