# 🎬 AutoTube AI Agent

> From idea to YouTube — fully automated. **100% Free forever.**

Enter any topic → AI researches it → writes script → generates voiceover → finds stock footage → creates video → uploads to YouTube.

---

## 🏗️ Architecture

```
Frontend (React)          Backend (FastAPI + Python)
GitHub Pages     ←──────→ Render.com (free tier)
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
              Groq LLaMA3    Edge TTS      Pexels API
             (script AI)    (voiceover)  (stock footage)
                                                  │
                                          YouTube API v3
                                           (upload)
```

---

## 🚀 Step-by-Step Deployment Guide

### STEP 1: Get Your Free API Keys

#### A) Groq API Key (for AI script generation)
1. Go to https://console.groq.com
2. Sign up free → Go to "API Keys"
3. Click "Create API Key"
4. Copy key starting with `gsk_...`

#### B) Pexels API Key (for stock footage)
1. Go to https://www.pexels.com/api/
2. Sign up free → "Your API Key"
3. Copy the key

#### C) YouTube OAuth Credentials (for uploading)
1. Go to https://console.cloud.google.com
2. Create a new project: "AutoTube"
3. Go to "APIs & Services" → "Library"
4. Search "YouTube Data API v3" → Enable it
5. Go to "APIs & Services" → "Credentials"
6. Click "Create Credentials" → "OAuth 2.0 Client IDs"
7. Application type: **Web application**
8. Name: AutoTube
9. Authorized redirect URIs: `https://YOUR-BACKEND.onrender.com/api/youtube/auth/callback`
10. Save Client ID and Client Secret

---

### STEP 2: Push to GitHub

```bash
# Create a new GitHub repo at github.com/new
# Name it: autotube

git init
git add .
git commit -m "Initial AutoTube AI Agent"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/autotube.git
git push -u origin main
```

---

### STEP 3: Deploy Backend to Render (Free)

1. Go to https://render.com → Sign up with GitHub
2. Click "New +" → "Web Service"
3. Connect your `autotube` GitHub repo
4. Configure:
   - **Name**: `autotube-backend`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variables:
   - `GROQ_API_KEY` = your Groq key
   - `PEXELS_API_KEY` = your Pexels key
   - `BACKEND_URL` = `https://autotube-backend.onrender.com` (your Render URL)
6. Click "Create Web Service"
7. Wait for deploy (~3 min). Note your URL: `https://autotube-backend.onrender.com`

> ⚠️ Free Render tier sleeps after 15 min. First request takes ~30s to wake up.

---

### STEP 4: Deploy Frontend to GitHub Pages

#### A) Add Backend URL as GitHub Secret
1. Go to your GitHub repo → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `VITE_API_URL`
4. Value: `https://autotube-backend.onrender.com`
5. Save

#### B) Enable GitHub Pages
1. Go to Settings → Pages
2. Source: "GitHub Actions"
3. Save

#### C) Update vite.config.js
Edit `frontend/vite.config.js`:
```js
base: '/autotube/',  // Replace 'autotube' with your actual repo name
```

#### D) Push to trigger deploy
```bash
git add .
git commit -m "Configure for deployment"
git push
```

5. GitHub Actions will auto-build and deploy
6. Your frontend will be live at: `https://YOUR_USERNAME.github.io/autotube/`

---

### STEP 5: Test Your App

1. Open `https://YOUR_USERNAME.github.io/autotube/`
2. Enter a topic like "The History of the Internet"
3. Follow the steps: Research → Script → Voice → Video → Upload
4. First time using YouTube upload: click "Enter OAuth Credentials" and follow the Google auth flow

---

## 🔧 Local Development

### Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # Fill in your keys
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env  # Set VITE_API_URL=http://localhost:8000
npm run dev
```

---

## 📁 Project Structure

```
autotube/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── requirements.txt
│   ├── .env.example
│   ├── routes/
│   │   ├── research.py      # Research endpoint
│   │   ├── script.py        # Script generation
│   │   ├── voice.py         # Voice synthesis
│   │   ├── video.py         # Video creation
│   │   └── youtube.py       # YouTube upload
│   └── agents/
│       ├── researcher.py    # DuckDuckGo + scraping + Groq
│       ├── script_writer.py # Groq LLaMA3 script writer
│       ├── voice_generator.py # Edge TTS voice generation
│       ├── video_creator.py # Pexels + MoviePy video creation
│       └── youtube_uploader.py # YouTube OAuth + upload
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main app with step flow
│   │   ├── App.css          # Dark cinematic theme
│   │   └── components/
│   │       ├── StepIndicator.jsx
│   │       ├── TopicInput.jsx
│   │       ├── ResearchPanel.jsx
│   │       ├── ScriptEditor.jsx
│   │       ├── VoiceSelector.jsx
│   │       ├── VideoPreview.jsx
│   │       └── UploadPanel.jsx
│   ├── package.json
│   └── vite.config.js
├── .github/workflows/deploy.yml  # Auto-deploy to GitHub Pages
├── render.yaml                    # Render deployment config
└── README.md
```

---

## 💡 Free Tier Limits

| Service | Free Limit | Notes |
|---------|-----------|-------|
| Groq LLaMA3 | 30 req/min, 6000 tokens/min | More than enough |
| Edge TTS | Unlimited | Microsoft's service, no key needed |
| Pexels | 200 req/hour, 20,000/month | Very generous |
| YouTube API | 10,000 units/day | ~6 uploads/day |
| Render | 750 hours/month | Free web service |
| GitHub Pages | Unlimited | Static hosting |

---

## 🔮 Future Enhancements

- [ ] Background music from Free Music Archive API
- [ ] Subtitle/caption generation with Whisper
- [ ] Thumbnail generation with DALL-E / Stable Diffusion
- [ ] Scheduled posting
- [ ] Multi-language support
- [ ] Channel analytics dashboard

---

## 📝 License

MIT — Use it, build on it, make money with it.
