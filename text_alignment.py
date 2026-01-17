import difflib
import re
from dataclasses import dataclass
from typing import List, Optional
from datetime import timedelta

@dataclass
class Word:
    text: str
    start: float # seconds
    end: float   # seconds

    def to_srt_entry(self, index: int) -> str:
        """Converts word to a generic SRT entry (just for compatibility if needed)."""
        s = timedelta(seconds=self.start)
        e = timedelta(seconds=self.end)
        
        # Helper to format timedelta like SRT (00:00:00,000)
        def format_td(td):
            total_seconds = int(td.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            milliseconds = int(td.microseconds / 1000)
            return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

        return f"{index}\n{format_td(s)} --> {format_td(e)}\n{self.text}\n\n"

def tokenize(text: str) -> List[str]:
    """Splits text into words, preserving minimal necessary punctuation/structure logic."""
    # Simple whitespace split for now, stripping distinct punctuation if needed?
    # Actually, we want to preserve tokens as user typed them.
    return text.split()

def reconcile_alignments(original_words: List[Word], new_text: str) -> List[Word]:
    """
    Reconciles the original word timings with the new text.
    Uses difflib to match words and interpolates timestamps for changes.
    """
    new_tokens = tokenize(new_text)
    original_tokens = [w.text for w in original_words]
    
    # Matcher
    matcher = difflib.SequenceMatcher(None, original_tokens, new_tokens)
    
    final_words: List[Word] = []
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            # Copy original timestamps
            for k in range(j2 - j1):
                orig_idx = i1 + k
                new_token = new_tokens[j1 + k]
                orig_word = original_words[orig_idx]
                # We use the NEW text but ORIGINAL time
                final_words.append(Word(text=new_token, start=orig_word.start, end=orig_word.end))
                
        elif tag == 'replace':
            # Range [i1, i2) replaced by [j1, j2)
            # We take the time range covered by original words [i1, i2)
            # And distribute it over [j1, j2)
            
            if i2 > i1:
                start_t = original_words[i1].start
                end_t = original_words[i2-1].end
            else:
                # Should not happen for 'replace', but safety fallback
                # Use previous word end or next word start
                start_t = final_words[-1].end if final_words else 0.0
                # We don't have next word reference easily here without lookahead
                # Just assume small duration
                end_t = start_t + 0.1 

            duration = end_t - start_t
            num_new = j2 - j1
            step = duration / num_new
            
            for k in range(num_new):
                w_start = start_t + (k * step)
                w_end = w_start + step
                final_words.append(Word(text=new_tokens[j1+k], start=w_start, end=w_end))
                
        elif tag == 'insert':
            # Insertions at [j1, j2). Original range empty [i1, i1).
            # We need to find a time gap.
            
            # Start time: End of last finalized word OR Start of next original word
            if final_words:
                start_basis = final_words[-1].end
            elif i1 < len(original_words):
                start_basis = original_words[i1].start
            else:
                start_basis = 0.0 # Start of file
                
            # End time constraint: Start of next original word (if exists)
            if i1 < len(original_words):
                end_constraint = original_words[i1].start
            else:
                # End of file... just add some time
                end_constraint = start_basis + (0.5 * (j2 - j1)) # Estimate 0.5s per word
                
            available_duration = max(0.1, end_constraint - start_basis)
            
            # Determine if we really have "space" or if we need to squeeze.
            # Ideally we check the gap between words. 
            # If gap is tight, we might overlap or shift subsequent words (complex).
            # Simple approach: Linear interpolation in the 'gap' or just append time if end of file.
            
            num_new = j2 - j1
            
            # If we are inserting into a tight spot, we might overlap.
            # Let's just divide the available "gap" (or logical duration)
            
            # Heuristic: 
            # If gap is large (> 0.2s * num_new), allow full spread.
            # If gap is small/negative (adjacent words), we just assign minimal duration
            # and effectively "overlap" or push boundaries.
            # Note: Manim renderer handles time simply by waiting or moving on.
            # Slight overlap in timestamps might be okay if they strictly increase in start time.
            
            # Let's enforce strictly increasing start times?
            
            # To be safe, let's just use the start_basis and add arbitrary duration.
            # The next word (if equal) will reset current_time in Manim logic to its rigid start time.
            
            # Actually, careful: if we insert 10 words between two words spoken 0.1s apart.
            # We can't fit them. 
            # Ideally we should "steal" time from neighbours or just squash them.
            
            step = available_duration / num_new
            # Clamp step to be reasonable?
            # step = min(step, 0.5) 
            
            for k in range(num_new):
                w_start = start_basis + (k * step)
                w_end = w_start + step
                final_words.append(Word(text=new_tokens[j1+k], start=w_start, end=w_end))

        elif tag == 'delete':
            # Original words [i1, i2) removed.
            # We just don't add them. Timestamps effectively vanish.
            pass
            
    return final_words

if __name__ == "__main__":
    # Simple Test
    orig = [
        Word("hello", 1.0, 1.5),
        Word("world", 1.6, 2.0),
        Word("this", 2.1, 2.3),
        Word("is", 2.3, 2.5),
        Word("test", 2.6, 3.0)
    ]
    
    new_txt = "hello brave new world this test"
    # Expected: 
    # hello -> 1.0-1.5
    # brave, new -> inserted between 1.5 and 1.6 (tight gap!)
    # world -> 1.6-2.0
    # this -> 2.1-2.3
    # is -> deleted
    # test -> 2.6-3.0
    
    res = reconcile_alignments(orig, new_txt)
    for r in res:
        print(f"{r.text}: {r.start:.2f}-{r.end:.2f}")
