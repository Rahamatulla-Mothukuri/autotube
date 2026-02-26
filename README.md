# 🎬 AutoTube AI Agent

Turn any topic into a YouTube video — fully automated, 100% free.

**Stack:** React (GitHub Pages) + FastAPI (Render) + Groq LLaMA 3 + Edge-TTS + Pexels + MoviePy

---

## 🧩 How It Works

```
Topic → Research (DuckDuckGo) → Script (Groq LLaMA 3) → Voice (Edge-TTS)
     → Video (Pexels + MoviePy) → Preview → Upload (YouTube API)
```

---

## 🔑 Free API Keys Needed

| Service | For | Get It |
|---------|-----|--------|
| Groq | Script AI (LLaMA 3) | https://console.groq.com |
| Pexels | Stock footage | https://www.pexels.com/api/ |
| YouTube Data API v3 | Upload | https://console.cloud.google.com |

---

## 🚀 Full Setup Guide

See detailed instructions below for each step.

### Step 1 — Clone Repo
```bash
git clone https://github.com/YOUR_USERNAME/autotube.git
cd autotube
```

### Step 2 — Get API Keys

**Groq:** https://console.groq.com → API Keys → Create Key

**Pexels:** https://www.pexels.com/api/ → Sign up → copy API key

**YouTube:**
1. https://console.cloud.google.com → Create project
2. Enable "YouTube Data API v3"
3. Credentials → OAuth 2.0 Client ID → Desktop App → Download JSON
4. Rename to `youtube_credentials.json` → place in `backend/`

### Step 3 — Deploy Backend on Render (Free)
1. https://render.com → New Web Service → Connect GitHub repo
2. Root Dir: `backend` | Build: `pip install -r requirements.txt` | Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. Add env vars: `GROQ_API_KEY`, `PEXELS_API_KEY`
4. Copy your Render URL

### Step 4 — YouTube Auth (One-time)
```bash
cd backend && pip install -r requirements.txt
python3 -c "from agents.youtube_agent import _get_credentials; _get_credentials()"
```
Browser opens → sign in → saves `youtube_token.json`. Upload this file to Render dashboard.

### Step 5 — Deploy Frontend on GitHub Pages
1. Edit `frontend/package.json`: set `"homepage": "https://YOUR_USERNAME.github.io/autotube"`
2. GitHub repo → Settings → Secrets → Add `REACT_APP_API_URL` = your Render URL
3. Settings → Pages → Source: `gh-pages` branch
4. Push to main — auto-deploys!

---

## 💻 Local Dev
```bash
# Backend
cd backend && pip install -r requirements.txt
cp .env.example .env  # fill in keys
uvicorn main:app --reload

# Frontend
cd frontend && npm install
echo "REACT_APP_API_URL=http://localhost:8000" > .env.local
npm start
```

---

## 📁 Structure
```
autotube/
├── backend/
│   ├── main.py              # FastAPI + job pipeline
│   ├── requirements.txt
│   └── agents/
│       ├── research_agent.py   # DuckDuckGo research
│       ├── script_agent.py     # Groq LLaMA 3
│       ├── voice_agent.py      # Edge-TTS (free)
│       ├── video_agent.py      # Pexels + MoviePy
│       └── youtube_agent.py    # YouTube upload
└── frontend/
    └── src/App.js           # Full React UI
```

---

## ⚠️ Free Tier Limits

- Render: sleeps after 15min idle (30s cold start)
- Groq: 30 req/min, 14,400/day
- Pexels: 200 req/hr, 20,000/month  
- YouTube: ~6 uploads/day free

## 📄 License: MIT
