# Research Plan: Word-Level Highlighting for Subtitles

## Objective
Highlight each spoken word in the rendered video in sync with the audio, while maintaining readable subtitle chunks.

## Analysis of Current State
- **Input**: `transcriber.py` generates a "Raw SRT" file where each subtitle entry is a single word with precise start/end timestamps.
- **Optimization**: `srt_optimizer.py` groups these words into readable chunks (e.g., max 6 words) for standard SRT output.
- **Rendering**: `video_processor.py` currently merges video and audio but keeps subtitles separate (or doesn't burn them yet).

## Proposed Solution options

### Option 1: Frame-by-Frame Text Rendering (Python/MoviePy)
- **Concept**: Generate a text image for every single word change and overlay it on the video.
- **Pros**: Infinite customization (any animation, particle effects, etc.).
- **Cons**: Extremely slow to render. Complex to manage text layout consistency across frames.

### Option 2: Complex FFmpeg Drawtext Filters
- **Concept**: Construct a massive FFmpeg command with hundreds of `drawtext` filters, enabling them at specific times.
- **Pros**: No external files needed.
- **Cons**: Command line length limits. Hard to debug. Performance issues with many filters.

### Option 3: ASS/SSA Subtitles (Recommended)
- **Concept**: Use the Advanced Substation Alpha (ASS) subtitle format.
- **Mechanism**: ASS supports "Karaoke" tags (`{\k<duration>}`) which allow styling changes (fill color, highlight) to propagate through a line of text based on durations.
- **Workflow**:
    1.  Take the **Raw SRT** (Word-level timings).
    2.  Group words into lines (similar to `srt_optimizer`).
    3.  Instead of plain text, generate ASS dialogue lines with embedded tags.
        -   Example: `Dialogue: 0,0:00:01.50,0:00:03.00,Default,,0,0,0,,{\k20}Hello {\k30}world {\k40}this {\k60}is...`
    4.  Use FFmpeg to burn this ASS file into the video: `ffmpeg -i video.mp4 -vf "ass=subtitles.ass" output.mp4`.
- **Pros**: 
    -   Standard industry way to do this.
    -   Efficient rendering via FFmpeg `libass`.
    -   Supports rich styling (fonts, borders, shadows, alignment).
- **Cons**: Requires generating a specific file format (ASS) syntax.

## Implementation Strategy
1.  **New Module**: Create `ass_generator.py` (or extend `srt_optimizer.py`).
    -   Input: List of word objects (with start/end/text).
    -   Logic:
        -   Group words into lines (reusing logic from `srt_optimizer`).
        -   Calculate duration of each word in centiseconds.
        -   Format string with `{\k<centiseconds>}` tags.
    -   Output: `.ass` file.
2.  **Video Processor Update**: Update `video_processor.py` to accept a subtitle file path and use the `subtitles` (or `ass`) filter in FFmpeg to burn it in.

## Feasibility
- `transcriber.py` already provides the necessary word-level granularity.
- `ffmpeg` is already being used in the project.
- Python string manipulation is sufficient to generate the ASS file.

## Conclusion
We will proceed with **Option 3 (ASS/SSA Subtitles)** as it provides the best balance of performance, quality, and maintainability.
