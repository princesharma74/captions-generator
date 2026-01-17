import argparse
import os
import shutil
import tempfile
import time
from datetime import datetime
from config import VideoConfig
from parser import parse_srt
from scene_generator import generate_scene, setup_manim_config
from video_processor import generate_blank_clip, concat_videos, cleanup_temp_files, merge_audio
from transcriber import transcribe_audio
from srt_optimizer import optimize_srt

def get_timestamped_dir(base_output_dir="outputs"):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(base_output_dir, ts)
    os.makedirs(path, exist_ok=True)
    return path

def do_transcribe(args):
    print(f"Starting Transcription for: {args.audio}")
    output_dir = get_timestamped_dir()
    print(f"Output Directory: {output_dir}")
    
    # 1. Transcribe
    raw_srt = transcribe_audio(args.audio, model_name=args.model)
    
    # Move raw SRT to output folder
    raw_filename = os.path.basename(raw_srt)
    dest_raw = os.path.join(output_dir, raw_filename)
    shutil.move(raw_srt, dest_raw)
    
    # 2. Optimize
    print("Optimizing subtitles...")
    optimized_srt = optimize_srt(dest_raw)
    
    # Optimize_srt saves as _optimized in same dir (which is now output_dir)
    print(f"DONE. Files saved in: {output_dir}")
    print(f"Optimized SRT: {optimized_srt}")
    print("You can now edit the SRT file if needed.")
    print(f"To render, run: uv run python subtitle_video_generator.py render {optimized_srt} --audio {args.audio} --output {output_dir}/final_video.mp4")

def do_render(args):
    print(f"Starting Render for: {args.srt}")
    
    if not os.path.exists(args.srt):
        print(f"Error: SRT file '{args.srt}' not found.")
        return

    # Initialize Config
    # TODO: Load config from args or a file if we want persistence
    config = VideoConfig(
        font_size=args.font_size,
        text_color=args.text_color,
        bg_color=args.bg_color,
        strip_color=args.strip_color,
        strip_opacity=args.strip_opacity,
        width=1920,
        height=1080, # Driven by Defaults in config.py now
        fps=30
    )

    print("Parsing SRT...")
    segments = parse_srt(args.srt)
    if not segments:
        print("No valid subtitles found.")
        return

    print(f"Found {len(segments)} subtitle segments.")

    temp_dir = tempfile.mkdtemp(prefix="manim_subs_")
    print(f"Working in temporary directory: {temp_dir}")

    timeline_clips = []
    current_time = 0.0
    
    try:
        setup_manim_config(config)

        for i, segment in enumerate(segments):
            # Handle Gap
            if segment.start_time > current_time:
                gap_duration = segment.start_time - current_time
                if gap_duration > 0.01:
                    gap_file = os.path.join(temp_dir, f"gap_{i}.mp4")
                    print(f"Generating gap: {gap_duration:.2f}s")
                    generate_blank_clip(gap_duration, gap_file, config)
                    timeline_clips.append(gap_file)
                current_time = segment.start_time
            
            # Generate Subtitle
            clip_file = os.path.join(temp_dir, f"seg_{i}.mp4")
            print(f"Generating segment {i+1}/{len(segments)}: '{segment.text}' ({segment.duration:.2f}s)")
            generate_scene(segment.text, segment.duration, clip_file, config)
            timeline_clips.append(clip_file)
            current_time += segment.duration
            
        print("Concatenating clips...")
        # Intermediate video without audio logic
        temp_video_output = os.path.join(temp_dir, "temp_concatenated.mp4")
        concat_videos(timeline_clips, temp_video_output)
        
        # Audio Merge
        if args.audio:
            print("Merging Audio...")
            merge_audio(temp_video_output, args.audio, args.output)
        else:
            print("No audio provided, moving video to output...")
            shutil.move(temp_video_output, args.output)
            
        print(f"Done! Video saved to: {args.output}")

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Cleaning up temporary files...")
        shutil.rmtree(temp_dir)

def main():
    parser = argparse.ArgumentParser(description="Subtitle Video Generator")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Transcribe Command
    parser_transcribe = subparsers.add_parser("transcribe", help="Transcribe audio to SRT")
    parser_transcribe.add_argument("audio", help="Input audio file")
    parser_transcribe.add_argument("--model", default="base", help="Whisper model")
    
    # Render Command
    parser_render = subparsers.add_parser("render", help="Render video from SRT")
    parser_render.add_argument("srt", help="Input SRT file")
    parser_render.add_argument("--output", required=True, help="Output MP4 file path")
    parser_render.add_argument("--audio", help="Audio file to merge (optional)")
    
    # visual args for render
    parser_render.add_argument("--font-size", type=int, default=70, help="Font size (default: 70)")
    parser_render.add_argument("--text-color", type=str, default="#FFFFFF", help="Text color")
    parser_render.add_argument("--bg-color", type=str, default="#00FF00", help="Background color")
    parser_render.add_argument("--strip-color", type=str, default="#000000", help="Strip color")
    parser_render.add_argument("--strip-opacity", type=float, default=0.7, help="Strip opacity")

    args = parser.parse_args()
    
    if args.command == "transcribe":
        do_transcribe(args)
    elif args.command == "render":
        do_render(args)

if __name__ == "__main__":
    main()
