import subprocess
import os
import shutil
from typing import List
from config import VideoConfig

def generate_blank_clip(duration: float, output_path: str, config: VideoConfig):
    """Generates a blank/solid color video clip of specific duration."""
    # Use lavfi to generate color source
    # color=c=COLOR:s=WxH:d=DURATION
    # We need to map config color hex to ffmpeg friendly or just use it.
    # FFmpeg takes hex like #RRGGBB.
    
    cmd = [
        "ffmpeg",
        "-y",
        "-f", "lavfi",
        "-i", f"color=c={config.bg_color}:s={config.width}x{config.height}:d={duration}:r={config.fps}",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        output_path
    ]
    
    # Run silently
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

def concat_videos(video_files: List[str], output_file: str):
    """Concatenates a list of video files using ffmpeg concat demuxer."""
    
    # Create a wrapper list file
    list_file = "concat_list.txt"
    with open(list_file, "w") as f:
        for vid in video_files:
            # Escape path for ffmpeg concat
            # Ideally use relative paths or absolute paths safely
            abs_path = os.path.abspath(vid)
            # FFmpeg concat file format requires 'file ' prefix and safe quoting
            f.write(f"file '{abs_path}'\n")
            
    try:
        cmd = [
            "ffmpeg",
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", list_file,
            "-c", "copy",
            output_file
        ]
        subprocess.run(cmd, check=True)
    finally:
        if os.path.exists(list_file):
            os.remove(list_file)

def replace_audio_track(video_path: str, audio_path: str, output_path: str):
    """Replaces the audio track of a video with a new audio file."""
    if not os.path.exists(audio_path):
        print(f"Warning: Audio file {audio_path} not found. Skipping audio replacement.")
        shutil.copy(video_path, output_path)
        return

    cmd = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy", # Fast copy video stream
        "-c:a", "aac",  # Encode audio to AAC
        "-map", "0:v:0", # Map first video stream from input 0
        "-map", "1:a:0", # Map first audio stream from input 1
        "-shortest",
        output_path
    ]
    
    subprocess.run(cmd, check=True)

def cleanup_temp_files(files: List[str]):
    for f in files:
        if os.path.exists(f):
            os.remove(f)
