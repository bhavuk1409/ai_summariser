from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

from download_video import download_video
from extract_audio import extract_audio
from transcribe_audio import transcribe_audio
from summarize_transcription import summarize_transcription, save_output

app = FastAPI()

# Enable CORS (for frontend calls)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change to specific frontend URL if needed)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# File paths (Overwritten each time)
VIDEO_PATH = "video.mp4"
AUDIO_PATH = "audio.wav"
OUTPUT_TEXT_PATH = "output.txt"

# Request Body Model
class VideoRequest(BaseModel):
    url: str

@app.get("/")
async def root():
    return {"message": "✅ FastAPI Video Processing API is running! Use a POST request to /process_video"}

@app.post("/process_video")
async def process_video(request: VideoRequest):
    try:
        # Step 1: Download Video
        print("📥 Downloading video...")
        download_video(request.url, VIDEO_PATH)

        # Step 2: Extract Audio
        print("🎵 Extracting audio...")
        extract_audio(VIDEO_PATH, AUDIO_PATH) #/Users/bhavukagrawal/FastAPI_Tut/app.py

        # Step 3: Transcribe Audio
        print("📝 Transcribing audio...")
        transcript = transcribe_audio(AUDIO_PATH)
        if not transcript:
            raise HTTPException(status_code=400, detail="Transcription failed.")

        # Step 4: Summarize Transcription
        print("🔍 Summarizing transcription...")
        summary = summarize_transcription(transcript)
        if not summary:
            raise HTTPException(status_code=400, detail="Summarization failed.")

        # Step 5: Save Output
        save_output(transcript, summary, OUTPUT_TEXT_PATH)

        return {
            "message": "✅ Process completed successfully!",
            "transcript": transcript,
            "summary": summary
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Error: {str(e)}")
