# 🕵️‍♂️ VidScrutiny

**An automated information nutrition label and timeline fact-checker for short-form video content.**

Text fact-checking is a solved problem; video is the frontier. VidScrutiny acts as a real-time "Community Notes" overlay for YouTube, TikToks, and Reels, neutralizing misinformation at the exact second it is spoken.

## ✨ Features

- **Real-Time Fact Checking:** Leverages Whisper-v3 for blazing-fast audio transcription and Llama-3.3-70b for factual analysis.
- **Live Web Search (RAG):** AI hallucinations are mitigated by actively searching DuckDuckGo for live internet context to verify claims.
- **WebSocket Streaming:** The frontend communicates with the backend via WebSockets to provide a live, step-by-step progress scanner as the AI digests the video.
- **Fitts's Law UI:** Broadcast-quality overlay cards, F-pattern visual hierarchy, and strictly accessible touch-target timeline markers.
- **Local SQLite Caching:** Videos analyzed once are instantly retrieved for future users, cutting processing time to zero.

---

## 🚀 Running Locally (Recommended)

The easiest way to run the full application (which requires `ffmpeg` for audio/video extraction) is via Docker.

### Prerequisites
- Docker & Docker Compose
- A free [Groq API Key](https://console.groq.com/keys) (Used for free, ultra-fast LLM inference)

### Setup
1. Clone the repository.
2. Navigate to the `backend/` directory and create a `.env` file:
   ```bash
   GROQ_API_KEY=gsk_your_groq_api_key_here
   ```
3. From the root of the project, run:
   ```bash
   docker-compose up --build
   ```
4. Open your browser and go to `http://localhost:8000`.

---

## 🌍 Deployment Guide

Because this application relies on **WebSockets** (for real-time UI loading states) and **FFmpeg** (to download and extract video files securely), a standard Vercel Serverless deployment for the backend won't work perfectly (Vercel Serverless restricts WebSockets and limits executions to 10 seconds).

The industry standard for an app like this is a **Split Deployment**:

### 1. Deploy the Frontend (Vercel)
Vercel is perfect for hosting the sleek frontend UI.
1. Push your code to GitHub.
2. Go to [Vercel](https://vercel.com/new) and import your repository.
3. In the project settings, set the **Root Directory** to `frontend`.
4. Click **Deploy**.

*(Note: Before deploying, update `app.js` line 13 to point to your live backend URL instead of `localhost:8000`)*.

### 2. Deploy the Backend (Railway or Render)
Railway and Render perfectly support Dockerfiles and WebSockets.
1. Go to [Railway.app](https://railway.app/) or [Render.com](https://render.com/).
2. Create a new project from your GitHub repository.
3. Set the **Root Directory** to `backend`.
4. The platform will automatically detect the `Dockerfile` and build it.
5. Add your `GROQ_API_KEY` to the Environment Variables.
6. Deploy!

---

## 🛠 Tech Stack
- **Frontend:** HTML5, Modern JavaScript, Tailwind CSS (Zero dependencies)
- **Backend:** Python, FastAPI, WebSockets
- **Ingestion:** `yt-dlp` (Video extraction)
- **AI Pipeline:** OpenAI SDK, Groq (Whisper-large-v3, Llama-3.3-70b-versatile)
- **RAG:** `duckduckgo-search`
- **Database:** SQLite3
