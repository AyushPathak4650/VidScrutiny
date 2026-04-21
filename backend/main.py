from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Literal
import os
import json

# Import our new services
from services.security import is_safe_url
from services.ingestion import download_audio, cleanup_file
from services.transcription import transcribe_audio
from services.analysis import analyze_transcript
from services.cache import get_cached_analysis, save_analysis

app = FastAPI(title="VidScrutiny API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/api/ws/analyze")
async def analyze_video_ws(websocket: WebSocket):
    await websocket.accept()
    
    # Track filepath so we can clean it up in the generic exception handler if needed
    video_filepath = None
    
    try:
        # Wait for the client to send the URL
        data = await websocket.receive_text()
        json_data = json.loads(data)
        url = json_data.get("url")
        target_language = json_data.get("language", "Auto")
        
        if not url:
            await websocket.send_text(json.dumps({"error": "Video URL is required"}))
            await websocket.close()
            return
            
        if not is_safe_url(url):
            await websocket.send_text(json.dumps({"error": "Invalid or unsafe URL provided"}))
            await websocket.close()
            return

        # Create a unique cache key based on URL and requested translation language
        cache_key = f"{url}_{target_language}"

        # --- 1. Check SQLite Cache ---
        await websocket.send_text(json.dumps({"status": "Checking database cache..."}))
        cached_result = get_cached_analysis(cache_key)
        if cached_result:
            await websocket.send_text(json.dumps({"status": "Cache hit! Loading instantly..."}))
            await websocket.send_text(json.dumps({
                "type": "result",
                "status": "success",
                "video_url": url,
                "stream_url": cached_result["stream_url"],
                "fact_checks": cached_result["fact_checks"]
            }))
            await websocket.close()
            return

        # --- 2. Ingestion ---
        await websocket.send_text(json.dumps({"status": "Downloading high-speed video stream..."}))
        # Offload synchronous yt-dlp call to thread
        import asyncio
        video_filepath = await asyncio.to_thread(download_audio, url)

        # --- 3. Transcription ---
        await websocket.send_text(json.dumps({"status": "Transcribing audio with Whisper-V3..."}))
        segments = await asyncio.to_thread(transcribe_audio, video_filepath)
        
        # --- 4. RAG & Analysis ---
        # analysis.py will send its own WS updates for Web Search and LLM Generation
        fact_checks = await asyncio.to_thread(analyze_transcript, segments, websocket, target_language)
        
        # Create a local stream URL
        filename = os.path.basename(video_filepath)
        local_stream_url = f"/temp_files/{filename}"
        
        # Save to SQLite Cache
        await asyncio.to_thread(save_analysis, cache_key, fact_checks, local_stream_url)
        
        # Send final payload
        await websocket.send_text(json.dumps({
            "type": "result",
            "status": "success",
            "video_url": url,
            "stream_url": local_stream_url,
            "fact_checks": fact_checks
        }))
        
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WS Error analyzing video: {e}")
        try:
            await websocket.send_text(json.dumps({"error": str(e)}))
            await websocket.close()
        except:
            pass
        # Clean up ONLY on error so we don't break the local stream
        if video_filepath:
            cleanup_file(video_filepath)

# Mount temp_files so the frontend can stream the downloaded video
temp_dir = os.path.join(os.path.dirname(__file__), "temp_files")
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)
app.mount("/temp_files", StaticFiles(directory=temp_dir), name="temp_files")

# Serve the frontend
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
