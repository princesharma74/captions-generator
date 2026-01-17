# Karaoke Caption Generator

A Python tool to generate karaoke-style word-level highlighted subtitles for audio files and render them onto a video.

## Available Templates

You can choose from several pre-configured subtitle styles:

- `default` - Standard white text with yellow highlights and black outline
- `karaoke` - Serif font with cyan highlights and heavy outline
- `cinematic` - Light gray text with minimal outline, top-aligned
- `shorts` - Bold yellow text with red highlights for social media
- `classic` - Minimal Helvetica font with NO outlines, clean professional look with word-by-word yellow highlighting
- `premium` - **NEW!** Bold Arial Black font with dark rounded background box (per-line), orange highlights, and no outlines

Use the `--template` or `-t` flag to select a template:

```bash
uv run python cli.py sample.mp3 --template classic
```

## Features
- **Word-Level Precision**: Uses OpenAI Whisper for accurate word-level timestamps.
- **Karaoke Highlighting**: Generates ASS subtitles with `{\k}` karaoke tags.
- **2-Step Workflow**: Allows you to edit subtitles before burning them into the video.
- **Customizable**: Configurable fonts, colors, and backgrounds via `config.py`.

## Prerequisites

- Python 3.10+
- FFmpeg (installed and accessible in PATH)
- `uv` (recommended for dependency management)

## Installation

1.  Clone the repository.
2.  Install dependencies:
    ```bash
    uv pip install -r requirements.txt
    ```
    *(If provided, otherwise install `openai-whisper`, `srt`)*

## Usage

The main entry point is `cli.py`.

### 1. Simple Usage (One-Click)
Generate subtitles and video in one go:
```bash
uv run python cli.py your_audio.mp3
```
This will create a timestamped folder in `outputs/` with the final video.

### 2. Advanced Usage (2-Step Process)

**Step 1: Generate Subtitles**
```bash
uv run python cli.py your_audio.mp3 --step 1
```
Output:
- Creates `outputs/YYYYMMDD_HHMMSS/`
- Contains `your_audio_raw.srt` (Editable timestamps)
- Contains `your_audio.ass` (Generated karaoke styles)

**Step 2: Render Video**
After editing the subtitles if needed, run step 2, pointing to the work directory from step 1:
```bash
uv run python cli.py your_audio.mp3 --step 2 --work_dir outputs/2026xxxx_xxxxxx/
```
Output:
- `your_audio_karaoke.mp4` inside the work directory.

## Configuration

Edit `config.py` to change:
- `VideoConfig`: Background color, font size, resolution.
- `SubtitleConfig`: Primary/Secondary colors, font, alignment.
