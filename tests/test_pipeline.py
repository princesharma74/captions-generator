import sys
import os
import subprocess
from datetime import timedelta

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import transcriber
import ass_generator
import video_processor
from config import VideoConfig

def get_audio_duration(audio_path):
    # Use ffmpeg/ffprobe to get duration
    cmd = [
        "ffprobe", 
        "-v", "error", 
        "-show_entries", "format=duration", 
        "-of", "default=noprint_wrappers=1:nokey=1", 
        audio_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(result.stdout.strip())

def run_pipeline(audio_path):
    print(f"--- Starting Pipeline for {audio_path} ---")
    
    # 1. Transcribe
    print("[1] Transcribing...")
    # transcribe_audio returns the raw srt path
    raw_srt_path = transcriber.transcribe_audio(audio_path)
    output_base = os.path.splitext(audio_path)[0]
    if not os.path.exists(raw_srt_path):
        # Fallback if transcriber behavior changed, check likely path
        raw_srt_path = output_base + "_raw.srt"
        
    print(f"    Raw SRT: {raw_srt_path}")
    
    # 2. Generate ASS
    print("[2] Generating ASS Subtitles...")
    ass_path = output_base + ".ass"
    ass_generator.generate_ass(raw_srt_path, ass_path)
    print(f"    ASS File: {ass_path}")
    
    # 3. Process Video
    print("[3] Rendering Video...")
    # We need a dummy video background
    duration = get_audio_duration(audio_path)
    temp_video_bg = output_base + "_bg.mp4"
    final_output = output_base + "_karaoke.mp4"
    
    config = VideoConfig()
    # Create black background
    config.bg_color = "black" 
    
    print(f"    Generating background video ({duration}s)...")
    video_processor.generate_blank_clip(duration, temp_video_bg, config)
    
    print(f"    Burning subtitles and merging audio...")
    video_processor.merge_audio(
        video_path=temp_video_bg,
        audio_path=audio_path,
        output_path=final_output,
        subtitles_path=ass_path
    )
    
    # Cleanup
    if os.path.exists(temp_video_bg):
        os.remove(temp_video_bg)
        
    print(f"--- Pipeline Complete ---")
    print(f"Output Video: {final_output}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_pipeline(sys.argv[1])
    else:
        print("Usage: python test_pipeline.py <audio_file>")
