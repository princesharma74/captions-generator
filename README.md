# Caption Generator

A Python tool to generate high-quality, karaoke-style highlighted subtitles for video content using **Manim**.

## Features

- **Unified Background Strip**: Pixel-perfect rounded rectangle backdrop for better readability.
- **Precision Highlighting**: Word-level synchronization with custom animations.
- **High-Quality Rendering**: Uses Manim engine for sharp 1080p output.
- **Automated Workflow**: Transcribes, renders, and merges audio in one command.

## Requirements

- Python 3.10+
- FFmpeg (for audio processing)
- Manim (`uv pip install manim`)
- OpenAI Whisper (`uv pip install openai-whisper`)
- SRT (`uv pip install srt`)

## Installation

1.  Clone the repository.
2.  Install dependencies:
    ```bash
    uv pip install manim openai-whisper srt
    ```

## Usage

Generate a caption video from an audio file:

```bash
uv run python cli.py your_audio.mp3
```

This will run the entire pipeline:
1.  **Transcribe**: Generates `_raw.srt` using Whisper.
2.  **Render**: Uses Manim to generate `_karaoke.mp4` with high-quality styling.
3.  **Finalize**: Merges the original audio for high fidelity into `_final.mp4`.

Output location: `outputs/{timestamp}/your_audio_final.mp4`

## Configuration

Visual styles (font, colors, background) can be adjusted in `config.py` and `templates.py`. The system uses the default style by default.
