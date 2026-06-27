# 🎤 SpeechFindr
> **AI-Powered Speech Recognition & Video Intelligence Web App**
> Final Year Project · Iqra University, Karachi · B.S. Information Technology

SpeechFindr turns a **YouTube link or an uploaded audio/video file** into a
searchable, timestamped transcript — then layers AI features on top:
summaries, topic tags, chapter markers, transcript Q&A, multi-language
translation, and spoken (text-to-speech) playback.

---

## 🏗 Architecture

Two independent tiers:

```
SpeechFindr/
├── backend/                 ← Python FastAPI API (port 8001)
│   ├── main.py              ← App entrypoint (wires routers + CORS)
│   ├── config.py            ← Settings, tier knobs, transcript cache
│   ├── routes/              ← HTTP layer (thin)
│   ├── services/            ← Core logic (transcription, translation, tts, …)
│   ├── models/              ← Pydantic request/response models
│   ├── utils/               ← Helpers (time formatting, etc.)
│   ├── requirements.txt
│   └── .env.example         ← Copy to .env and fill in your keys
│
└── frontend/                ← Vite + React 19 single-page app
    ├── src/pages/           ← Home, Contact, AppPage (+ appLogic.js)
    ├── src/components/       ← Navbar, Footer, CustomCursor
    ├── src/styles/          ← Per-page CSS
    └── .env.example         ← VITE_API_BASE → points at the backend
```

---

## ⚙️ How It Works

### Getting a transcript (cascading fallback)
For a **YouTube URL** the backend tries, in order:
1. **Native captions** in the chosen language
2. **Auto-generated captions** as fallback
3. **Groq Whisper** (`whisper-large-v3-turbo`) — downloads the audio with
   yt-dlp, extracts it with FFmpeg, and transcribes

For an **uploaded file**, FFmpeg converts to 16 kHz mono MP3, long media is
**sliced into chunks and transcribed in parallel**, and results are stitched
back with correct timestamps. Identical re-uploads are served from cache.

### AI features (Groq `llama-3.3-70b-versatile`)
- **Summary** — general or keyword-focused; short / medium / detailed; output in English, Urdu, or Arabic
- **Topics** — concise topic tags extracted from the transcript
- **Chapters** — timestamped chapter markers
- **Q&A** — ask questions about the video; a lightweight term-frequency retriever feeds the most relevant transcript segments to the model and returns an answer with a cited timestamp

### Translation & speech
- **Translation** — Google web endpoint first (free, no token budget), with Groq LLM as a fallback; output stays on a single engine for consistent style
- **Text-to-speech** — Microsoft Edge neural voices (`edge-tts`), falling back to gTTS

### Free / Paid tier toggle
A runtime switch (UI button → `POST /settings/tier`) scales concurrency and
token budgets. Free tier paces itself under Groq's free limits and prefers
Google translation; paid tier unlocks more parallelism. Setting
`GROQ_PAID_API_KEY` auto-selects paid mode on startup.

---

## 🚀 Running Locally

> **Prerequisites:** Python 3.10+, Node.js 18+, and **FFmpeg installed and on your PATH**.

### 1. Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows  (use: source venv/bin/activate on macOS/Linux)
pip install -r requirements.txt

# Create your local secrets file (this file is git-ignored):
copy .env.example .env         # Windows  (use: cp .env.example .env elsewhere)
# …then open backend/.env and paste in your Groq API key(s).

uvicorn main:app --reload --host 127.0.0.1 --port 8001
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev                    # served by Vite (default http://localhost:5173)
```
The frontend talks to the backend at `VITE_API_BASE` (defaults to
`http://127.0.0.1:8001`). To override, copy `frontend/.env.example` to
`frontend/.env` and edit the value.

---

## 🔌 API Endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET/POST` | `/youtube/transcript` | Transcript for a YouTube URL (captions → Whisper) |
| `POST` | `/file/transcript` | Transcript for an uploaded audio/video file |
| `POST` | `/summary` | General or keyword summary (EN/UR/AR) |
| `POST` | `/topics` | Topic tags |
| `POST` | `/chapters` | Timestamped chapter markers |
| `POST` | `/qa` | Question answering over the transcript |
| `POST` | `/translate` | Translate transcript segments |
| `POST` | `/tts` | Synthesize speech (returns MP3) |
| `GET` | `/settings` · `POST /settings/tier` | Read settings · flip free/paid tier |
| `GET` | `/progress/{job_id}` | Live progress + streaming partial segments |
| `GET` | `/health` | Health check |

---

## 🔐 Secrets & Configuration

API keys live in **`backend/.env`**, which is **git-ignored** — it is never
committed or pushed. New environments start from `backend/.env.example`.

Key environment variables (see `.env.example` for the full list):

| Variable | Purpose |
|---|---|
| `GROQ_API_KEY` | Whisper transcription (required) |
| `GROQ_SUMMARY_API_KEY` | Summaries |
| `GROQ_ANALYSIS_API_KEY` | Topics / chapters / Q&A |
| `GROQ_TRANSLATION_API_KEY_1/2` | Groq translation (alternated) |
| `GROQ_PAID_API_KEY` | Optional single paid key for all features |
| `GROQ_TIER` | `free` \| `paid` (auto-detected if empty) |
| `TTS_ENGINE` | `edge` (default) \| `gtts` |
| `YTDLP_COOKIES_FROM_BROWSER`, `YTDLP_PROXY` | Optional YouTube download helpers |

---

## 🛠 Tech Stack

**Backend:** FastAPI · Uvicorn · Groq (Whisper + LLaMA 3.3) · yt-dlp · FFmpeg ·
deep-translator (Google) · edge-tts / gTTS · Pydantic

**Frontend:** React 19 · React Router · Vite · vanilla CSS design system

---

## 👥 Team
| Name | Role |
|---|---|
| **Anas Tanveer** | Lead · Backend |
| Awaab Mubashar Siddique | Frontend · Integration |

---

## 🎓 Academic Info
- **University:** Iqra University, Karachi
- **Degree:** B.S. Information Technology

---

*Built with ❤️ — SpeechFindr Team, Iqra University Karachi*
