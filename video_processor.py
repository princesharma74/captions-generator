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

def merge_audio(video_path: str, audio_path: str, output_path: str, subtitles_path: str = None):
    """Merges video with audio, cutting audio to video length if needed. Optionally burns subtitles."""
    # Note: If video is generated from audio, they should match.
    # We use ffmpeg to mux.
    
    if not os.path.exists(audio_path):
        print(f"Warning: Audio file {audio_path} not found. Skipping merge.")
        shutil.copy(video_path, output_path)
        return

    cmd = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-i", audio_path
    ]
    
    # Video Codec Logic
    if subtitles_path and os.path.exists(subtitles_path):
        # We must re-encode to burn subtitles
        print(f"Burning subtitles from: {subtitles_path}")
        
        # FFmpeg filter path handling is tricky with special chars.
        # Ideally use absolute path.
        abs_sub_path = os.path.abspath(subtitles_path).replace("\\", "/") 
        # On Windows, drive letters might be an issue in filter strings. 
        # But this is Mac.
        
        # Determine filter type based on extension
        if abs_sub_path.endswith(".ass"):
            vf_filter = f"ass='{abs_sub_path}'"
        else:
            vf_filter = f"subtitles='{abs_sub_path}'"
            
        cmd.extend([
            "-vf", vf_filter,
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23" # Good quality
        ])
    else:
        # Fast copy if no subtitles
        cmd.extend(["-c:v", "copy"])

    cmd.extend([
        "-c:a", "aac",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest", # Ensure output stops when shortest stream ends
        output_path
    ])
    subprocess.run(cmd, check=True)

def cleanup_temp_files(files: List[str]):
    for f in files:
        if os.path.exists(f):
            os.remove(f)
