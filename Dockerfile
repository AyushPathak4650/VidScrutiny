FROM python:3.11-slim

# Install ffmpeg for yt-dlp audio processing
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy the application code
COPY backend ./backend/
COPY frontend ./frontend/

# Expose the port
EXPOSE 8000

# Run the FastAPI server
WORKDIR /app/backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
