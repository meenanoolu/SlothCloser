# 🦥 SlothCloser

**A calm, local evening wind-down agent** that helps you close the day - slowly, kindly, and completely offline.

Built for the **Hacktoberfest Open-Source AI Challenge: Week 3 - Slow and Steady**.

---

## Why this exists

Most of us end the day with mental clutter still open.  
SlothCloser reads whatever you dump (notes, journal, messy thoughts) and gently gives you:

1. A short, human day summary  
2. The few things still open  
3. A soft bedtime reflection  

Everything runs **locally** with open-weight models. Your private thoughts never leave your machine.

---

## Features

- 100% offline once the model is downloaded
- Works with any Ollama model (Gemma, Llama 3.2, Qwen, Phi, etc.)
- Beautiful calm dark UI
- Paste notes or upload a `.md` / `.txt` file
- One-click “Close my day”
- Download the closing as markdown
- Zero telemetry, zero cost after setup

---

## Quick Start

### 1. Install Ollama
```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh

# or download from https://ollama.com
```

### 2. Pull a model (pick one)
```bash
ollama pull gemma2:2b          # fast & good
# or
ollama pull llama3.2:3b
# or
ollama pull qwen2.5:3b
```

### 3. Run SlothCloser
```bash
# clone or download this folder
cd sloth-closer

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt

streamlit run app.py
```

Open the URL that appears (usually http://localhost:8501).

---

## How to use

1. Write or paste today’s notes (messy is fine)
2. (Optional) choose a different local model in the sidebar
3. Click **Close my day**
4. Read the three gentle cards
5. Download the closing if you want to keep it

That’s it. No accounts, no internet, no pressure.

---

## Project structure

```
sloth-closer/
├── app.py            # Streamlit UI
├── agent.py          # Ollama agent logic
├── prompts.py        # All prompts (easy to edit)
├── config.py         # Settings
├── requirements.txt
└── README.md
```

---

## Why open-source AI matters here

- Your journal stays on your laptop
- Works on a plane or in the countryside
- You can swap models, change the tone, or fine-tune later
- Costs nothing after the first download
- No one is training on your private evening thoughts

A closed API could never offer the same privacy or permanence.

---

## Customization

- Change the default model in `config.py`
- Edit the tone and length of responses in `prompts.py`
- Add more tools later (auto-archive daily notes, calendar export, etc.)

---

Take it slow.  
The day will still be there tomorrow.
