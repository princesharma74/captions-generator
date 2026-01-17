import whisper
import srt
import os
from typing import List, Optional
from datetime import timedelta
import torch

def transcribe_audio(audio_path: str, model_name: str = "base") -> str:
    """
    Transcribes audio using Whisper and returns the path to the generated SRT file.
    The SRT file is saved in the same directory as the audio file.
    """
    print(f"Loading Whisper model '{model_name}'...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    # Mac M1/M2/M3 support MPS? Whisper might default to CPU if MPS is not fully supported or stable.
    # We will stick to auto-detect or CPU for safety unless user specific.
    # Actually, whisper handles device logic internally usually, but explicit is better.
    # On Mac, 'mps' is the accelerator. But whisper's support might vary.
    # We'll let whisper load default or cpu to avoid errors.
    
    model = whisper.load_model(model_name)
    
    print(f"Transcribing '{audio_path}'...")
    # Iterate verbose=False to just get result
    result = model.transcribe(audio_path, word_timestamps=True)
    
    srt_content = []
    
    # We can perform the "Raw" conversion here.
    # Whisper result contains 'segments' which are phrases.
    # We want word-level precision available for optimization phase?
    # Actually, the user asked for:
    # "Output: Raw SRT file with accurate timestamps"
    # "STAGE 2 ... Recalculate timing for new chunks"
    
    # So we should save a raw SRT first.
    # Whisper's default segments are decent, but might be too long.
    # We will save the default segments as the 'Raw SRT'.
    
    for i, segment in enumerate(result["segments"]):
        start = timedelta(seconds=segment["start"])
        end = timedelta(seconds=segment["end"])
        text = segment["text"].strip()
        
        # Save word-level timestamps in the text or metadata if possible?
        # Standard SRT doesn't hold word level metadata easily without custom format.
        # BUT, the optimizer needs word timestamps to re-chunk accurately.
        # If we only save standard SRT, we lose word timing.
        
        # STRATEGY: We will dump the standard SRT for the "Output: Raw SRT" requirement.
        # However, for the python pipeline, we might want to return the full result object or a richer structure.
        # But to strictly follow the "Stage 1 -> Output SRT -> Stage 2 -> Input SRT" pattern:
        # We need to save the word timestamps.
        
        # One way is to create a very granular SRT where every word is a subtitle? 
        # Or just rely on Whisper's segments and then for Stage 2, re-transcribe or assume linear interpolation?
        # NO, "Generate initial SRT file with word-level timestamps" says the prompt.
        # This usually implies specialized SRTs or just standard SRTs that are reasonably chunked.
        
        # Actually, let's look at "SRT Optimization" inputs: "Input: Raw SRT file".
        # If we save a normal SRT, we lose the word timings.
        # UNLESS we make every word its own subtitle in the raw file?
        # That would be a valid "Raw SRT with word-level timestamps".
        # Let's do that? It allows perfect re-chunking later.
        
        # Wait, usually "SRT with word level timestamps" might mean a proprietary format or just standard SRT.
        # Let's try to output a standard SRT with Whisper's segments, BUT also maybe a separate JSON or
        # maybe just trust the optimizer to interpolate if we don't save words?
        # Re-reading: "Recalculate timing for new chunks while maintaining sync".
        # If we don't have word timings, we can't do this accurately.
        
        # Decision: The raw SRT will have granular word-level entries if 'words' are available.
        # Whisper produces 'words' in the segment if word_timestamps=True.
        
        if "words" in segment:
            for word in segment["words"]:
                 # We can store words, but that makes a Huge SRT.
                 # Let's stick to the segment level for the "Raw SRT" file to be human readable?
                 # OR, better: The prompt asks for "Raw SRT file with accurate timestamps".
                 # If we return a list of words, it's NOT a standard subtitle file people usually use.
                 
                 # Alternative: Just use the segments. We can run the optimizer on the segments.
                 # But if we want to split a segment, we lose precision without word timings.
                 
                 # Let's save a "raw_words.srt" where every line is a word? 
                 # Or better, let's save the full JSON for the optimizer to use, but also export an SRT.
                 # BUT the pipeline prompt implies SRT file passing.
                 # "Input: Raw SRT file from Stage 1".
                 
                 # Let's make the "Raw SRT" effectively use the segments Whisper gave, 
                 # BUT, maybe we can hack it? No.
                 
                 # Let's assume the user means "SRT generated by Whisper".
                 # Note: Whisper segments are usually split by pauses.
                 # Optimization stage wants to: "Re-chunk text ... Max 6 words".
                 # If a whisper segment is 20 words, we need to split it. We need word timings.
                 
                 # REVISED STRATEGY: 
                 # Stage 1 output will be an SRT where EACH WORD is a separate subtitle entry.
                 # This guarantees "word-level timestamps" and allows perfect re-grouping in Stage 2.
                 pass

    # Actually, making an SRT with 1 word per line is valid SRT.
    subtitles = []
    index = 1
    
    # Flatten all words
    all_words = []
    for segment in result["segments"]:
        if "words" in segment:
            for w in segment["words"]:
                all_words.append(w)
        else:
            # Fallback if no word timestamps (some models/languages might fail)
            # Create a pseudo word entry for the whole segment
            all_words.append({
                "word": segment["text"],
                "start": segment["start"],
                "end": segment["end"]
            })

    for w in all_words:
        start = timedelta(seconds=w["start"])
        end = timedelta(seconds=w["end"])
        text = w["word"].strip()
        if not text: continue
        
        subtitles.append(srt.Subtitle(index=index, start=start, end=end, content=text))
        index += 1
        
    srt_output = srt.compose(subtitles)
    
    base_name = os.path.splitext(audio_path)[0]
    raw_srt_path = f"{base_name}_raw.srt"
    
    with open(raw_srt_path, "w", encoding="utf-8") as f:
        f.write(srt_output)
        
    print(f"Raw SRT saved to: {raw_srt_path}")
    return raw_srt_path

if __name__ == "__main__":
    # Test
    import sys
    if len(sys.argv) > 1:
        transcribe_audio(sys.argv[1])
