from manim import *
import srt
import os
import templates

class CaptionScene(Scene):
    def construct(self):
        # 1. Configuration & Setup
        audio_path = os.environ.get("MANIM_AUDIO_PATH")
        srt_path = os.environ.get("MANIM_SRT_PATH")
        
        if not audio_path or not srt_path:
            raise ValueError("Environment variables MANIM_AUDIO_PATH and MANIM_SRT_PATH must be set.")
            
        # Add audio
        self.add_sound(audio_path)
        
        # Parse SRT
        with open(srt_path, "r", encoding="utf-8") as f:
            words = list(srt.parse(f.read()))

        # Design Config
        cfg = templates.get_config()
        
        FONT_NAME = cfg.font_name
        FONT_SIZE = cfg.font_size
        TEXT_COLOR = cfg.text_color
        HIGHLIGHT_COLOR = cfg.highlight_color
        BG_COLOR = cfg.bg_color
        BG_OPACITY = cfg.bg_opacity
        CORNER_RADIUS = cfg.corner_radius
        PADDING_H = cfg.padding_h
        PADDING_V = cfg.padding_v
        BOTTOM_OFFSET = cfg.bottom_offset
        
        # 2. Group into chunks (lines)
        chunks = []
        current_chunk = []
        current_char_count = 0
        MAX_CHARS = 30 # optimized for 1080p width to prevent font scaling
        
        for w in words:
            # content might have spaces, but we care about visual length
            word_len = len(w.content.strip())
            
            # If adding this word exceeds limit (and we already have words), break chunk
            if current_chunk and (current_char_count + word_len > MAX_CHARS):
                chunks.append(current_chunk)
                current_chunk = []
                current_char_count = 0
            
            current_chunk.append(w)
            # Add length of word plus a rough space
            current_char_count += word_len + 1
            
        if current_chunk:
            chunks.append(current_chunk)
            
        # 3. Animation Loop
        
        # Track where we are in global time
        # We start at 0.0
        # self.renderer.time is the reliable clock in Manim
        
        # Wait until first subtitle
        if chunks:
             first_start = chunks[0][0].start.total_seconds()
             if first_start > 0:
                 self.wait(first_start)

        for chunk_idx, chunk in enumerate(chunks):
            if not chunk: continue
            
            # A. Create Single Text Object for the line
            # This ensures perfect baseline alignment
            chunk_text_str = " ".join([w.content.strip() for w in chunk])
            
            # Manim Text object
            # We use a try-catch block or fallback for fonts? No, assume font exists as per config.
            line_mobject = Text(chunk_text_str, font=FONT_NAME, font_size=FONT_SIZE, color=TEXT_COLOR)
            
            # B. Map Words to Sub-Mobjects
            # Manim Text strips spaces from submobjects list.
            # "Hello World" -> [H,e,l,l,o,W,o,r,l,d]
            word_boxes = [] # Will verify against word timings
            
            char_pointer = 0
            for w in chunk:
                clean_content = w.content.strip().replace(" ", "").replace("\t", "").replace("\n", "")
                num_chars = len(clean_content)
                
                if num_chars > 0 and char_pointer + num_chars <= len(line_mobject):
                    # Get the sub-mobjects for this word
                    # It's a VGroup of characters
                    word_group = line_mobject[char_pointer : char_pointer + num_chars]
                    
                    # Calculate bounding box for this word
                    # We can use a SurroundingRectangle or just get center/dims
                    # We'll compute the rect needed for the highlight
                    word_boxes.append(word_group)
                    
                    char_pointer += num_chars
                else:
                    # Skip or handle empty (shouldn't happen with valid words)
                    word_boxes.append(None)

            # C. Position the Line
            max_width = config.frame_width - (PADDING_H * 2) - 1.0
            if line_mobject.width > max_width:
                line_mobject.scale(max_width / line_mobject.width)
            
            if BOTTOM_OFFSET != 0:
                 line_mobject.to_edge(DOWN * BOTTOM_OFFSET)
            else:
                 line_mobject.move_to(ORIGIN)

            # D. Background Strip
            line_bg = RoundedRectangle(
                corner_radius=CORNER_RADIUS,
                height=line_mobject.height + PADDING_V,
                width=line_mobject.width + PADDING_H,
                fill_color=BG_COLOR,
                fill_opacity=BG_OPACITY,
                stroke_width=0
            )
            line_bg.move_to(line_mobject.get_center())
            
            # E. Highlight Box (Active Word)
            # Initialize off-screen or invisible
            active_word_bg = RoundedRectangle(
                corner_radius=CORNER_RADIUS/2,
                height=0, width=0, 
                fill_color=HIGHLIGHT_COLOR,
                fill_opacity=0,
                stroke_width=0
            )

            # Group for entry
            scene_group = VGroup(line_bg, active_word_bg, line_mobject)
            
            # F. Entry Animation
            # Fade in quickly. Ideally we time this just before the first word starts.
            # But the loop structure waits for first word start effectively.
            # We might be slightly late if we don't anticipate.
            # However, the previous chunk loop 'wait' logic should put us exactly at start_time of this chunk?
            # Actually, we rely on 'wait' calls.
            
            # Let's check time
            start_time = chunk[0].start.total_seconds()
            curr_time = self.renderer.time
            
            # If we are early (common), wait.
            if start_time > curr_time:
                self.wait(start_time - curr_time)
            
            # Now we are at 'start_time'. 
            # Show the line.
            self.play(FadeIn(scene_group), run_time=0.1)
            
            # Note: FadeIn takes 0.1s. So now we are at start_time + 0.1s.
            # This eats into the first word's time!
            # Fix: We should ideally have faded in *before* start_time.
            # But simplicity first: We'll accept 0.1s latency on first word or compensate.
            # Better: Make FadeIn super fast or simultaneous with first highlight?
            # Let's assume 0.1s is acceptable or we subtract it from first wait.
            
            # G. Word Loop (Karaoke)
            for i, w in enumerate(chunk):
                w_start = w.start.total_seconds()
                w_end = w.end.total_seconds()
                
                # Check current time
                now = self.renderer.time
                
                # Gap handling?
                # If w_start > now, it means there is silence between words in this chunk.
                if w_start > now:
                    self.wait(w_start - now)
                
                # Now we expect to be at w_start.
                # If we drifted past w_start (due to lag), we just proceed immediately.
                
                # Highlight Animation
                target_word_mobj = word_boxes[i]
                if target_word_mobj:
                    # New Geometry
                    new_height = target_word_mobj.height + PADDING_V/2
                    new_width = target_word_mobj.width + PADDING_H/2
                    new_center = target_word_mobj.get_center()
                    
                    # We want the highlight to appear/move instantly or quickly?
                    # "Karaoke" usually implies the highlight is present for the duration of the word.
                    # So we move it *to* the word at the START, then hold.
                    
                    # If this is the first word, just appear.
                    # If subsequent, animate from previous.
                    
                    # Compute duration for move. Fast!
                    anim_dur = 0.05
                    
                    # Check if word is shorter than anim_dur
                    word_duration = w_end - w_start
                    run_dur = min(anim_dur, word_duration)
                    
                    self.play(
                        active_word_bg.animate.become(
                            RoundedRectangle(
                                corner_radius=CORNER_RADIUS/2,
                                height=new_height,
                                width=new_width,
                                fill_color=HIGHLIGHT_COLOR,
                                fill_opacity=0.8,
                                stroke_width=0
                            ).move_to(new_center)
                        ),
                        run_time=run_dur
                    )
                    
                    # Wait for remainder of word
                    # We rely on absolute end time
                    post_anim_now = self.renderer.time
                    remainder = w_end - post_anim_now
                    if remainder > 0:
                        self.wait(remainder)
                else:
                    # No visual for this word (e.g. valid silence or mapping error)
                    # Just wait out the duration
                    end_wait = w_end - self.renderer.time
                    if end_wait > 0:
                        self.wait(end_wait)

            # H. Exit Animation
            self.play(FadeOut(scene_group), run_time=0.1)
