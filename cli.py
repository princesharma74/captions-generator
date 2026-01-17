import sys
import os
import argparse
import subprocess
import shutil
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import transcriber
import video_processor

def get_timestamped_dir(base_path):
    # outputs/YYYYMMDD_HHMMSS
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_parent = os.path.join(os.path.dirname(base_path), "outputs")
    return os.path.join(output_parent, timestamp)

def generate_captions(audio_path, output_dir):
    print(f"--- Generating Captions for {audio_path} ---")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    
    # 1. Transcribe
    print("[1/3] Transcribing Audio...")
    raw_srt_generated = transcriber.transcribe_audio(audio_path)
    
    target_raw_srt = os.path.join(output_dir, f"{base_name}_raw.srt")
    
    # Move SRT to output dir logic
    if os.path.exists(raw_srt_generated):
        if os.path.abspath(raw_srt_generated) != os.path.abspath(target_raw_srt):
            shutil.move(raw_srt_generated, target_raw_srt)
            print(f"    Moved Raw SRT to: {target_raw_srt}")
    
    if not os.path.exists(target_raw_srt):
        print(f"Error: Raw SRT not found at {target_raw_srt}")
        return

    # 2. Render with Manim
    print("[2/3] Rendering Video with Manim...")
    
    # Set Environment Variables
    env = os.environ.copy()
    env["MANIM_AUDIO_PATH"] = os.path.abspath(audio_path)
    env["MANIM_SRT_PATH"] = os.path.abspath(target_raw_srt)
    
    # Command
    cmd = [
        "manim", 
        "-r", "1920,1080",
        "--fps", "30",
        "--disable_caching", 
        "--media_dir", output_dir,
        "manim_renderer.py", 
        "CaptionScene"
    ]
    
    manim_temp_out = os.path.join(output_dir, "videos", "manim_renderer", "1080p30", "CaptionScene.mp4")
    
    try:
        subprocess.run(cmd, env=env, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Manim: {e}")
        return

    if not os.path.exists(manim_temp_out):
        print(f"Error: Manim output not found at {manim_temp_out}")
        return
        
    # 3. Final Audio Merge/Replace (Verification Step)
    print("[3/3] Finalizing Audio...")
    final_output = os.path.join(output_dir, f"{base_name}_final.mp4")
    
    # We replace audio track to ensure original high quality audio and perfect length sync (though Manim is usually good)
    video_processor.replace_audio_track(manim_temp_out, audio_path, final_output)
    
    print(f"--- Process Complete ---")
    print(f"Output Video: {final_output}")
    print(f"Work Directory: {output_dir}")

def main():
    parser = argparse.ArgumentParser(description="Caption Generation CLI (Manim)")
    parser.add_argument("audio_file", help="Path to input audio file")
    parser.add_argument("--work_dir", help="Optional work directory for outputs.")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.audio_file):
        print(f"Error: File {args.audio_file} not found.")
        return

    # Determine Output Directory
    if args.work_dir:
        output_dir = args.work_dir
    else:
        output_dir = get_timestamped_dir(args.audio_file)

    generate_captions(args.audio_file, output_dir)

if __name__ == "__main__":
    main()
