import sys
import os
import argparse
import subprocess
import shutil
from datetime import timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import transcriber
import ass_generator
import video_processor
from config import VideoConfig
import templates

def get_audio_duration(audio_path):
    cmd = [
        "ffprobe", 
        "-v", "error", 
        "-show_entries", "format=duration", 
        "-of", "default=noprint_wrappers=1:nokey=1", 
        audio_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(result.stdout.strip())

from datetime import datetime

# ... imports ...

def get_timestamped_dir(base_path):
    # outputs/YYYYMMDD_HHMMSS
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_parent = os.path.join(os.path.dirname(base_path), "outputs")
    return os.path.join(output_parent, timestamp)

def step_one_subtitles(audio_path, output_dir, template_name="default"):
    print(f"--- [Step 1] Generating Subtitles for {audio_path} ---")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    
    # 1. Transcribe
    print("Transcribing...")
    # Transcriber saves to same dir as audio usually? 
    # Or we can check if we can control output.
    # We will let it run and move.
    
    raw_srt_generated = transcriber.transcribe_audio(audio_path)
    
    target_raw_srt = os.path.join(output_dir, f"{base_name}_raw.srt")
    if os.path.exists(raw_srt_generated):
        # If it was generated in source dir, move it.
        # But if source dir is output dir (unlikely), don't move.
        if os.path.abspath(raw_srt_generated) != os.path.abspath(target_raw_srt):
            shutil.move(raw_srt_generated, target_raw_srt)
            print(f"Moved Raw SRT to: {target_raw_srt}")
    else:
        # Maybe it was already there or something went wrong
        pass
        
    # Double check if target exists now
    if not os.path.exists(target_raw_srt):
        print(f"Error: Raw SRT not found at {target_raw_srt}")
        return

    # 2. Generate ASS
    print("Generating ASS...")
    target_ass = os.path.join(output_dir, f"{base_name}.ass")
    
    # Load template config
    sub_config = templates.get_template(template_name)
    print(f"    Using Template: {template_name}")
    
    ass_generator.generate_ass(target_raw_srt, target_ass, config=sub_config)
    
    print(f"--- Step 1 Complete ---")
    print(f"Work Directory: {output_dir}")
    print(f"Subtitles: {target_ass}")
    print(f"Please edit the subtitles if needed, then run Step 2:")
    print(f"  uv run python cli.py {audio_path} --step 2 --work_dir {output_dir}")

def step_two_video(audio_path, output_dir):
    print(f"--- [Step 2] Rendering Video for {audio_path} ---")
    
    if not os.path.exists(output_dir):
        print(f"Error: Work directory {output_dir} does not exist.")
        return

    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    
    ass_path = os.path.join(output_dir, f"{base_name}.ass")
    if not os.path.exists(ass_path):
        print(f"ERROR: Subtitle file not found at {ass_path}")
        print("Please ensure you have run Step 1 or provided the correct --work_dir")
        return

    output_video_path = os.path.join(output_dir, f"{base_name}_karaoke.mp4")
    temp_bg_path = os.path.join(output_dir, f"{base_name}_bg.mp4")
    
    duration = get_audio_duration(audio_path)
    config = VideoConfig()
    
    print(f"Generating background video ({duration}s)...")
    video_processor.generate_blank_clip(duration, temp_bg_path, config)
    
    print(f"Burning subtitles...")
    video_processor.merge_audio(
        video_path=temp_bg_path,
        audio_path=audio_path,
        output_path=output_video_path,
        subtitles_path=ass_path
    )
    
    # Cleanup
    if os.path.exists(temp_bg_path):
        os.remove(temp_bg_path)
        
    print(f"--- Step 2 Complete ---")
    print(f"Final Video: {output_video_path}")

def main():
    parser = argparse.ArgumentParser(description="Caption Generation CLI")
    parser.add_argument("audio_file", help="Path to input audio file")
    parser.add_argument("--step", type=int, choices=[1, 2], help="Specific step to run (1=Subtitles, 2=Video). If omitted, runs both.")
    parser.add_argument("--work_dir", help="Directory for input/output files. Required for Step 2 standalone. Defaults to new timestamped dir for Step 1/Both.")
    parser.add_argument("--template", "-t", default="default", help="Subtitle style template (default, karaoke, cinematic, shorts)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.audio_file):
        print(f"Error: File {args.audio_file} not found.")
        return

    # Determine Output Directory
    if args.work_dir:
        output_dir = args.work_dir
    else:
        # If no dir specified, create a new timestamped one
        output_dir = get_timestamped_dir(args.audio_file)
        
        # If running ONLY step 2 without a dir, that's a problem
        if args.step == 2:
            print("Error: --work_dir is required when running only Step 2.")
            return

    if args.step == 1:
        step_one_subtitles(args.audio_file, output_dir, args.template)
    elif args.step == 2:
        step_two_video(args.audio_file, output_dir)
    else:
        # Run both
        step_one_subtitles(args.audio_file, output_dir, args.template)
        step_two_video(args.audio_file, output_dir)

if __name__ == "__main__":
    main()
