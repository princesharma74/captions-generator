# Project: Subtitle Video Generator

## Overview
This project generates landscape (1920x1080) videos with centered subtitle animations from Audio or SRT inputs. It features a split workflow allowing users to edit subtitles before rendering.

## Workflow
1.  **Transcribe**: Audio -> Optimized SRT (saved in timestamped output folder).
2.  **Edit**: User edits SRT if needed.
3.  **Render**: SRT + Audio -> Video (merged).

## Key Components

### 1. `config.py`
- Defines default resolution **1920x1080** (Landscape).
- Defines text positioning (Centered).

### 2. `subtitle_video_generator.py`
- **Command `transcribe`**:
    - Wrapper for `transcribe_audio` + `optimize_srt`.
    - Manages output directories.
- **Command `render`**:
    - Wrapper for Phase 1/2 rendering logic + Audio Merge.

### 3. `transcriber.py` & `srt_optimizer.py`
- Handles Whisper transcription and smart re-chunking.

### 4. `scene_generator.py`
- Generates Manim scenes with centered text and rounded background strips.

### 5. `video_processor.py`
- Concatenates clips and merges audio using FFmpeg (`-shortest` flag).

## Dependencies
- **Python:** `manim`, `srt`, `openai-whisper`, `torch`
- **System:** `ffmpeg`

## Usage
```bash
# 1. Transcribe
uv run python subtitle_video_generator.py transcribe input.mp3

# 2. Render
uv run python subtitle_video_generator.py render outputs/TIMESTAMP/file.srt --audio input.mp3 --output final.mp4
```
