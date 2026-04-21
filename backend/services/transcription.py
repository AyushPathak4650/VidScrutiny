import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Point the OpenAI client to Groq's API
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def transcribe_audio(filepath: str) -> list:
    """
    Sends the audio file to Groq's Whisper API and returns the transcript segments.
    Each segment contains 'text', 'start', and 'end' keys.
    """
    try:
        with open(filepath, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-large-v3", # Groq's supported Whisper model
                file=audio_file,
                response_format="verbose_json"
            )
            
        # verbose_json returns an object with a 'segments' list.
        segments = transcript.segments
        
        # Clean up the output to only what we need
        # The SDK returns objects, so we use dot notation instead of dictionary brackets
        cleaned_segments = [
            {
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip()
            }
            for segment in segments
        ]
        
        return cleaned_segments
        
    except Exception as e:
        raise Exception(f"Transcription failed: {str(e)}")