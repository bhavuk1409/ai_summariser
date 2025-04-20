from download_video import download_video
from extract_audio import extract_audio
from transcribe_audio import transcribe_audio
from summarize_transcription import summarize_transcription, save_output

# Define paths
video_url = ""
video_path = "video.mp4"
audio_path = "audio.wav"
output_text_path = "output.txt"

# Execute steps in order
download_video(video_url, video_path)
extract_audio(video_path, audio_path)
transcript = transcribe_audio(audio_path)
summary = summarize_transcription(transcript)
save_output(transcript, summary, output_text_path)

print("✅ Process completed successfully!")
