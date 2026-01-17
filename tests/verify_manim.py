import os
import subprocess
import sys

def verify():
    # Setup paths
    work_dir = os.path.abspath("tests/output")
    os.makedirs(work_dir, exist_ok=True)
    
    audio_path = os.path.abspath("sample.mp3") # Assuming exists in root
    srt_path = os.path.abspath("tests/sample.srt")
    
    env = os.environ.copy()
    env["MANIM_AUDIO_PATH"] = audio_path
    env["MANIM_SRT_PATH"] = srt_path
    
    # Configs to mimic App
    env["CFG_FONT_NAME"] = "Arial"
    env["CFG_FONT_SIZE"] = "60"
    env["CFG_TEXT_COLOR"] = "#FFFFFF"
    env["CFG_HIGHLIGHT_COLOR"] = "#00FF00"
    env["CFG_BG_COLOR"] = "#000000"
    env["CFG_BG_OPACITY"] = "0.8"
    env["CFG_CORNER_RADIUS"] = "0.2"
    env["CFG_BOTTOM_OFFSET"] = "0"

    print(f"Running Manim in {work_dir}...")
    
    cmd = [
        "manim", 
        "-ql",  # Low quality for speed
        "--disable_caching", 
        "--media_dir", work_dir,
        "manim_renderer.py", 
        "CaptionScene"
    ]
    
    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Manim Failed!")
        print("STDERR:", result.stderr)
        print("STDOUT:", result.stdout)
    else:
        print("Manim Success!")
        print(f"Output should be in {work_dir}/videos/manim_renderer/480p15/CaptionScene.mp4")

if __name__ == "__main__":
    verify()
