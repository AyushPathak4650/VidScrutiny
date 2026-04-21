<div align="center">
  
# 🕵️‍♂️ VidScrutiny: AI Fact-Checker

**Real-Time "Community Notes" for YouTube Shorts & TikToks**

[![Live Demo](https://img.shields.io/badge/🔴_Live_Demo-vid--scrutiny.vercel.app-blue?style=for-the-badge)](https://vid-scrutiny.vercel.app/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)]()
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)]()

*Text fact-checking is a solved problem. Video is the final frontier.*

</div>

<br/>

VidScrutiny acts as an automated, real-time "Community Notes" overlay for short-form video content. It digests video streams in seconds, transcribes the spoken audio, cross-references claims with the live internet, and projects beautiful, broadcast-quality fact-check overlays directly onto the video exactly when the claims are spoken.

## ✨ The "Wow" Factor Features

* ⚡ **Zero-Latency Feel:** Combines **Whisper-v3** and **Llama-3.3-70b** on specialized Groq hardware to process entire Shorts/Reels in seconds.
* 🌐 **Live Web Search (RAG):** AI hallucinations are neutralized. The system actively queries DuckDuckGo behind the scenes to find real, live URLs to back up or debunk every claim.
* 🇮🇳 **Multilingual AI:** Natively supports translating English videos into Hindi fact-checks (and vice-versa) via a single UI toggle.
* 🚀 **Real-Time WebSockets:** No fake loading bars. The Python backend streams its exact processing state to the frontend via WebSockets.
* 💾 **Smart SQLite Caching:** Analyzed a viral video once? It's cached in the database. The next user who pastes that link gets the result instantly.

---

## 🏗️ Architecture Pipeline

1. **Ingestion (`yt-dlp`):** Securely bypasses bot-blockers to extract raw `.mp4` and `.m4a` streams.
2. **Transcription (Whisper API):** Generates a highly accurate, timestamped transcript array.
3. **Contextual Search (DuckDuckGo):** The LLM isolates the main topic and silently searches the internet for real-time context.
4. **Analysis (Llama 3):** Rates each claim as `True`, `False`, or `Context` and formats it into strict JSON.
5. **Presentation (HTML5/Tailwind):** A custom video player triggers sleek, Fitts's Law-compliant UI cards to slide in exactly when the speaker makes the claim.

---

## 💻 Run it Locally (Docker)

The absolute best way to run VidScrutiny is via Docker, as it automatically handles complex `ffmpeg` dependencies required for video manipulation.

### Prerequisites
* Docker Desktop
* A free [Groq API Key](https://console.groq.com/keys)

### 1-Minute Setup
1. Clone the repository to your machine.
2. Create a `.env` file inside the `backend/` directory:
   ```env
   GROQ_API_KEY=gsk_your_groq_api_key_here
   ```
3. Boot the pipeline:
   ```bash
   docker-compose up --build
   ```
4. Open `http://localhost:8000` in your browser.

---

## 🌍 Production Deployment Architecture

Because this platform relies on **WebSockets** and **FFmpeg**, it uses an industry-standard split deployment:

* **The Frontend (Vercel):** The `frontend/` directory is deployed as a lightning-fast static site on Vercel.
* **The Backend (Render):** The `backend/` directory and `Dockerfile` are deployed as a persistent Web Service on Render to keep the WebSocket connections alive and execute the heavy video processing.
