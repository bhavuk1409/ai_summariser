import whisper
import logging

def transcribe_audio(audio_path):
    model = whisper.load_model("tiny")  # Adjust model size as needed
    try:
        # Perform transcription
        result = model.transcribe(audio_path)
        transcript = result.get("text", "")
        
        # Print and return the transcript
        print("\n📝 Transcription Completed:")
        print(transcript)
        return transcript
    
    except Exception as e:
        # Log the error if transcription fails
        logging.error(f"❌ Transcription failed: {e}")
        return {"error": "Transcription failed", "message": str(e)}  # Return error response
