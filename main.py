from download_video import download_video
from extract_audio import extract_audio
from transcribe_audio import transcribe_audio
from summarize_transcription import summarize_transcription, save_output

# Define paths
video_url = "https://ohio.stream-io-cdn.com/1366698/video/recordings/default_00ce3429-8031-41eb-9337-ed138d758a53/rec_default_00ce3429-8031-41eb-9337-ed138d758a53_720p_1745088076291.mp4?Expires=1746302539&Signature=hQLniNKRcIszpjAL3mxccUSDeA9XRT25SIa9lynFO7RZpVa1Yl5479xdUcL2Lc9lqXXKQ3C~5w-EQgziKu7Eo4Oh8UMZV9AZhdjL2k9FoD~VAWkpU5mnNyiRK3X3q7qI70NjrfBQ47psVxbKY4LRYZSPmE8qqSUbMSmfGII4WaCzagi1l~D91GU0V0zhFxY6VxQJMChYxQUqMAKDgB-7NLVblNSLRHPW3M-8zISn968qG7XqB9ZVyTK8-otula6ffOqZeaH8~rcAyJ~yhEPr62oLn8PpoyMaiaRJrY0JsGb76Co7VXdPY4QhnNoiKTRLTqeMB2gjRe1lfN6OEQgUSQ__&Key-Pair-Id=APKAIHG36VEWPDULE23Q"
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
