import srt
import os
from datetime import timedelta
from typing import List, Optional
from config import SubtitleConfig
import re

def generate_ass(input_srt_path: str, output_path: str, config: SubtitleConfig = SubtitleConfig()):
    """
    Generates an ASS subtitle file with karaoke highlighting from a word-level SRT.
    """
    
    with open(input_srt_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Parse word-level SRT
    words = list(srt.parse(content))
    
    if not words:
        print("No words found in SRT.")
        return
        
    # Standard header for ASS file
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{config.font_name},{config.font_size},{config.primary_color},{config.secondary_color},{config.outline_color},{config.back_color},{'-1' if config.bold else '0'},0,0,0,100,100,0,0,{config.border_style},{config.outline_width},{config.shadow_depth},{config.alignment},{config.margin_l},{config.margin_r},{config.margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    events = []
    
    # Reuse simple grouping logic (max 6 words)
    # Ideally should share logic with srt_optimizer but to keep it self-contained:
    max_words = 6
    min_words = 2
    
    current_chunk = []
    
    def format_time(td):
        # Format timedelta to h:mm:ss.cc
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        # Centiseconds
        centiseconds = int((td.microseconds / 10000))
        return f"{hours}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"

    def flush_chunk():
        nonlocal current_chunk
        if not current_chunk:
            return
            
        start_time = current_chunk[0].start
        # End time should be end of last word
        # BUT, standard ASS karaoke often fills the gap to the next line or audio duration.
        # For now, let's strictly use the last word's end time.
        end_time = current_chunk[-1].end
        
        ass_start = format_time(start_time)
        ass_end = format_time(end_time)
        
        # Build text string with karaoke tags
        # {\kXX} where XX is duration in centiseconds
        
        # Note: 'SecondaryColour' is the "active" color in some players? 
        # Actually in standard karaoke:
        # Before \k: Primary Colour (Wait)
        # After \k: Secondary Colour (Played) -> NO.
        # Standard: Text is Primary. \k fills it with Secondary. 
        # Actually, \k is "fill up to this point".
        # \kf or \K is fill.
        # Use \k (block highlight) or \kf (continuous fill).
        # We'll use \k for word-by-word instant change.
        
        # Color behavior:
        # PrimaryColour is the "Filled" color (Already sung).
        # SecondaryColour is the "Unfilled" color (Not yet sung).
        # Wait, usually it's the reverse? 
        # Let's check ASS specs.
        # "SecondaryColour: This is the color that the text changes to when it is sung in karaoke mode."
        # OK. So Primary = Normal/Unsung. Secondary = Sung/Highlighted.
        
        line_text = ""
        current_line_time = start_time
        
        for w in current_chunk:
            # We need duration relative to the previous word/start of line.
            # \k takes duration in centiseconds.
            
            # Problem: Gap between words.
            # strict duration = w.end - w.start
            # but if there is a gap between word 1 and word 2, we need to account for it.
            # Usually we assign the gap to the previous word or next word.
            # Let's assign gap to previous word? 
            # Or just let it be silent?
            # \k tags are sequential. 
            # {\k20}Word1 {\k30}Word2
            # Time 0: All Primary.
            # Time +0.20: Word1 turns Secondary.
            # Time +0.50: Word2 turns Secondary.
            
            # We need to map exact timestamps to these durations.
            # total_duration of line = end_time - start_time
            
            # Let's recalculate durations to be contiguous for the line
            pass
        
        # To make it smooth, we fill gaps.
        # word1: 0.0 - 0.5
        # word2: 0.6 - 1.0 (gap 0.1)
        # render: \k50 Word1 \k10(space) \k40 Word2
        
        chunk_text_parts = []
        last_end = start_time
        
        for i, w in enumerate(current_chunk):
            # Gap before this word?
            gap = w.start - last_end
            if gap.total_seconds() > 0:
                # Add gap duration to the previous word or as a space?
                # If we add to space, we need a space in text.
                gap_cs = int(gap.total_seconds() * 100)
                if gap_cs > 0:
                     chunk_text_parts.append(f"{{\\k{gap_cs}}} ") 
            
            # Word duration
            dur = w.end - w.start
            dur_cs = int(dur.total_seconds() * 100)
            
            # Sanity check: Ensure at least 1 cs
            if dur_cs < 1: dur_cs = 1
            
            word_content = w.content.strip()
            # Add a space after the word.
            # Note: For the last word in a line, a trailing space is usually fine/invisible, 
            # but we can check if it's the last word in chunk.
            # Ideally, we only add space if it's NOT the last word, OR if we want to ensure separation from next line?
            # Actually, in subtitles, lines are separate. So last word space doesn't matter much.
            # But inside the line, we definitely need it.
            
            chunk_text_parts.append(f"{{\\k{dur_cs}}}{word_content} ")
            
            last_end = w.end
            
        final_text = "".join(chunk_text_parts).strip() # Strip trailing space of the line
        
        # Escape any existing braces in text? Unlikely in subtitles but good practice.
        # final_text = final_text.replace("{", "\{").replace("}", "\}")
        
        # Dialogue: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
        dialogue = f"Dialogue: 0,{ass_start},{ass_end},Default,,0,0,0,,{final_text}"
        events.append(dialogue)
        
        current_chunk = []

    # Logic to populate chunks (same as optimizer)
    sentence_end_pattern = re.compile(r'[.!?]+$')
    clause_end_pattern = re.compile(r'[,;]+$')

    for word_sub in words:
        clean_text = word_sub.content.strip()
        if len(current_chunk) >= max_words:
            flush_chunk()
        
        current_chunk.append(word_sub)
        
        if sentence_end_pattern.search(clean_text):
            flush_chunk()
        elif clause_end_pattern.search(clean_text) and len(current_chunk) >= min_words:
            flush_chunk()
            
    if current_chunk:
        flush_chunk()
        
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(header)
        f.write("\n".join(events))
        
    print(f"ASS file saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 2:
        generate_ass(sys.argv[1], sys.argv[2])
    elif len(sys.argv) > 1:
        # deduce output
        inp = sys.argv[1]
        outp = inp.replace(".srt", ".ass")
        generate_ass(inp, outp)
