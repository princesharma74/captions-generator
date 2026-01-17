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

## Streamlit Web App

For a visual interface with real-time editing and configuration, use the Streamlit app.

```bash
uv run streamlit run app.py
```

### Key Features

1.  **Interactive Editor**:
    - Upload audio files directly.
    - **Transcribe**: Uses Whisper to generate text.
    - **Edit Transcript**: Modify the text in a simple text area. The system automatically reconciles your edits with the original audio timestamps.

2.  **Visual Customization**:
    - **Font Selection**: Choose from any font installed on your system.
    - **Size & Colors**: Adjust font size, text color, highlight color, and background opacity.
    - **Layout**: Fine-tune the vertical position of the captions.

3.  **Smart Rendering**:
    - Prevents font shrinking on long lines with smart text chunking.
    - Generates high-quality 1080p, 60fps videos.
