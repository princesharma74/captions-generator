import srt
from typing import List
from datetime import timedelta
import re

def optimize_srt(input_srt_path: str, max_words: int = 6, min_words: int = 2) -> str:
    """
    Optimizes a raw SRT (word-level) by grouping words into chunks.
    """
    with open(input_srt_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # We assume the input is the "Raw SRT" from our transcriber, which has 1 distinct word per subtitle entry.
    words = list(srt.parse(content))
    
    if not words:
        return input_srt_path

    optimized_subs = []
    current_chunk = []
    index = 1
    
    def flush_chunk():
        nonlocal index, current_chunk
        if not current_chunk:
            return
            
        # Calculate timing
        # Start of first word, end of last word
        start = current_chunk[0].start
        end = current_chunk[-1].end
        
        # Join text
        text = " ".join(sub.content.strip() for sub in current_chunk)
        
        optimized_subs.append(srt.Subtitle(index=index, start=start, end=end, content=text))
        index += 1
        current_chunk = []

    # Regex for sentence ending punctuation
    sentence_end_pattern = re.compile(r'[.!?]+$')
    # Regex for clause ending punctuation (comma, semicolon)
    clause_end_pattern = re.compile(r'[,;]+$')

    for word_sub in words:
        clean_text = word_sub.content.strip()
        
        # If adding this word exceeds max, flush first
        if len(current_chunk) >= max_words:
            flush_chunk()
        
        current_chunk.append(word_sub)
        
        # Check natural breaks
        # 1. Punctuation
        if sentence_end_pattern.search(clean_text) or clause_end_pattern.search(clean_text):
            # If we have enough words to form a valid chunk, flush.
            # OR if it's a hard break (period), we almost always flush unless it's too short, 
            # but usually subtitles respect sentence boundaries.
            
            # Use min_words rule.
            # If current chunk is less than min_words, we might try to keep adding?
            # But if it's the end of a sentence, we must flush to avoid bridging sentences.
            
            is_sentence_end = bool(sentence_end_pattern.search(clean_text))
            
            if is_sentence_end:
                 flush_chunk()
            elif len(current_chunk) >= min_words:
                 # Comma break, flush if we have enough words
                 flush_chunk()
    
    # Final flush
    if current_chunk:
        flush_chunk()
        
    # Generate Output Path
    base_name = input_srt_path.replace("_raw.srt", "").replace(".srt", "")
    output_path = f"{base_name}_optimized.srt"
    
    srt_output = srt.compose(optimized_subs)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(srt_output)
        
    print(f"Optimized SRT saved to: {output_path}")
    return output_path
