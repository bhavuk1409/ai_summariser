from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import whisper
from transformers import pipeline
import asyncio
import os
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global models
transcribe_model = None
summarize_model = None

# File paths
VIDEO_PATH = "video.mp4"
AUDIO_PATH = "audio.wav"
OUTPUT_TEXT_PATH = "output.txt"

# Request Body Model
class VideoRequest(BaseModel):
    url: str

async def load_models():
    """Load ML models in background"""
    global transcribe_model, summarize_model
    try:
        logger.info("Loading Whisper model...")
        transcribe_model = whisper.load_model("base")
        logger.info("Whisper model loaded")
        
        logger.info("Loading summarization model...")
        summarize_model = pipeline(
            "summarization", 
            model="facebook/bart-large-cnn",
            device=-1  # Force CPU usage
        )
        logger.info("Summarization model loaded")
    except Exception as e:
        logger.error(f"Model loading failed: {e}")

@app.on_event("startup")
async def startup_event():
    """Startup event to load models"""
    asyncio.create_task(load_models())

def download_video(url: str, save_path: str):
    """Download video from URL"""
    import requests
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)
        logger.info("Video downloaded successfully")
    except Exception as e:
        logger.error(f"Video download failed: {e}")
        raise

def extract_audio(video_path: str, audio_path: str):
    """Extract audio from video using ffmpeg"""
    try:
        cmd = f"ffmpeg -y -i {video_path} -vn -acodec pcm_s16le -ar 16000 -ac 1 {audio_path}"
        os.system(cmd)
        if not os.path.exists(audio_path):
            raise Exception("Audio file not created")
        logger.info("Audio extracted successfully")
    except Exception as e:
        logger.error(f"Audio extraction failed: {e}")
        raise

def cleanup_files(files: list):
    """Clean up temporary files"""
    for file in files:
        try:
            if os.path.exists(file):
                os.remove(file)
        except Exception as e:
            logger.warning(f"Could not remove {file}: {e}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"status": "running", "message": "Video Summarizer API"}

@app.get("/health")
async def health_check():
    """Health check endpoint for Render"""
    return {"status": "healthy"}

@app.post("/process_video")
async def process_video(request: VideoRequest, background_tasks: BackgroundTasks):
    """Process video endpoint with background task"""
    try:
        background_tasks.add_task(
            process_video_background,
            request.url,
            VIDEO_PATH,
            AUDIO_PATH,
            OUTPUT_TEXT_PATH
        )
        return JSONResponse(
            content={"message": "Processing started. Check back later for results."},
            status_code=202
        )
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_video_background(url: str, video_path: str, audio_path: str, output_path: str):
    """Background task for video processing"""
    try:
        # Wait for models to load
        while transcribe_model is None or summarize_model is None:
            await asyncio.sleep(1)
            logger.info("Waiting for models to load...")

        # Step 1: Download
        logger.info("Downloading video...")
        download_video(url, video_path)

        # Step 2: Extract audio
        logger.info("Extracting audio...")
        extract_audio(video_path, audio_path)

        # Step 3: Transcribe
        logger.info("Transcribing audio...")
        result = transcribe_model.transcribe(audio_path)
        transcript = result.get("text", "")
        if not transcript:
            raise Exception("Empty transcription")

        # Step 4: Summarize
        logger.info("Summarizing text...")
        summary = summarize_model(transcript, max_length=150, min_length=50)[0]["summary_text"]
        if not summary:
            raise Exception("Empty summary")

        # Step 5: Save output
        logger.info("Saving results...")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"Transcript:\n{transcript}\n\nSummary:\n{summary}")

        # Cleanup
        cleanup_files([video_path, audio_path])
        logger.info("Processing completed successfully")

    except Exception as e:
        logger.error(f"Background processing failed: {e}")
        cleanup_files([video_path, audio_path, output_path])
