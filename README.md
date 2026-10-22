# 🦥 SlothCloser

**A calm, local evening wind-down agent** that helps you close the day - slowly, kindly, and completely offline.

> Built for the **Hacktoberfest Open-Source AI Challenge: Week 3 - Slow and Steady**

---

## The Problem

Most of us end the day with mental clutter still open.  
Unfinished thoughts keep looping. Tasks float in the background. It becomes hard to properly rest.

## The Solution

SlothCloser reads whatever you dump (messy notes, journal entries, random thoughts) and gently gives you:

1. **A short, human day summary**
2. **The few things still open** (so your brain can stop looping)
3. **A soft bedtime reflection** so you can actually put the day down

It rewards laziness: the AI does the emotional + organizational closing work for you.

---

## Why Open-Source AI Matters Here

| Benefit | Why it matters |
|---------|----------------|
| **Fully local** | Your private evening thoughts never leave your machine |
| **Works offline** | No internet required after the model is downloaded |
| **Zero ongoing cost** | Set it up once, use it forever |
| **Swappable models** | Use Gemma, Llama, Qwen, Phi… whatever you prefer |
| **No surveillance** | A closed API could never offer the same privacy |

This is the kind of tool that only makes sense with open-weight models.

---

## Features

- 100% offline once the model is downloaded
- Works with any Ollama model (Gemma recommended)
- Beautiful calm dark UI
- Paste notes or upload a `.md` / `.txt` file
- One-click “Close my day”
- Graceful offline fallback (so public demos never break)
- Download the closing as markdown
- Zero telemetry

---

## Quick Start

### 1. Install Ollama
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Pull a model
```bash
ollama pull gemma2:2b
# or llama3.2:3b / qwen2.5:3b etc.
```

### 3. Run SlothCloser
```bash
git clone https://github.com/YOUR_USERNAME/sloth-closer.git
cd sloth-closer

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

Open the URL shown (usually http://localhost:8501).

---

## Tech Stack

- **Frontend**: Streamlit (calm custom dark theme)
- **AI**: Ollama + open-weight models (Gemma by default)
- **Language**: Python
- **Deployment**: Works on Render (with graceful fallback)

---

## Project Structure

```
sloth-closer/
├── app.py            # Streamlit UI
├── agent.py          # Ollama agent + offline fallback
├── prompts.py        # All prompts (easy to edit tone)
├── config.py         # Settings
├── Procfile          # For Render deployment
├── requirements.txt
└── README.md
```

---

## Deploy on Render

1. Push this repo to GitHub
2. Create a new **Web Service** on [Render](https://render.com)
3. Use these settings:

| Setting         | Value                                                                 |
|-----------------|-----------------------------------------------------------------------|
| Build Command   | `pip install -r requirements.txt`                                     |
| Start Command   | `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`   |

The public demo will automatically use the calm offline fallback if Ollama is not available on the server.

---

## License

MIT

---

Take it slow.  
The day will still be there tomorrow.
