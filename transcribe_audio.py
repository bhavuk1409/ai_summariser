import whisper
import os

def transcribe_audio(audio_path):
    print(f"🔍 Transcribing file at: {audio_path}")
    
    if not os.path.exists(audio_path):
        print("❌ File not found.")
        return ""

    try:
        model = whisper.load_model("base")  # You can use "small", "medium", or "large" too
        result = model.transcribe(audio_path)
        transcript = result.get("text", "")
        print("\n📝 Transcription Completed:")
        print(transcript)
        return transcript
    except Exception as e:
        print(f"❌ Transcription failed: {e}")
        return ""
