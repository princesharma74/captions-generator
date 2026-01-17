from manim import *
import os
from config import VideoConfig

# Function to configure Manim global settings
def setup_manim_config(cfg: VideoConfig):
    config.pixel_width = cfg.width
    config.pixel_height = cfg.height
    config.frame_rate = cfg.fps
    config.background_color = cfg.bg_color
    # Calculate frame height/width ratio
    config.frame_height = 16.0 # Manim default is 8.0 usually, but we want high adaptability
    config.frame_width = 16.0 * (cfg.width / cfg.height)

class SubtitleScene(Scene):
    def __init__(self, text: str, clip_duration: float, video_config: VideoConfig, **kwargs):
        self.subtitle_text = text
        self.clip_duration = clip_duration
        self.video_config = video_config
        super().__init__(**kwargs)

    def construct(self):
        # Create Text
        subtitle = Text(
            self.subtitle_text,
            font=self.video_config.font_name,
            font_size=self.video_config.font_size,
            color=self.video_config.text_color,
            line_spacing=1.2
        )
        
        # Constrain width to avoidance overflow (e.g. 80% of frame width)
        max_width = config.frame_width * 0.8
        if subtitle.width > max_width:
            subtitle.width = max_width
            
        # Position Text
        # Center in the middle (ORIGIN)
        subtitle.move_to(ORIGIN)
        
        # Create Background Strip
        # We want rounded corners.
        # SurroundingRectangle is good, or RoundedRectangle matching size.
        # RoundedRectangle is more flexible for corners.
        
        # Add padding
        bg_width = subtitle.width + self.video_config.padding * 2
        bg_height = subtitle.height + self.video_config.padding * 2
        
        background = RoundedRectangle(
            corner_radius=self.video_config.strip_corner_radius,
            width=bg_width,
            height=bg_height,
            color=self.video_config.strip_color,
            fill_opacity=self.video_config.strip_opacity,
            stroke_width=0
        )
        background.move_to(subtitle.get_center())
        
        # Group them
        group = VGroup(background, subtitle)
        
        # Animations
        fade_in_time = self.video_config.fade_in_time
        fade_out_time = self.video_config.fade_out_time
        
        # Calculate hold time (duration - fade in - fade out)
        # Ensure we don't have negative hold time
        total_anim_time = fade_in_time + fade_out_time
        if self.clip_duration < total_anim_time:
            # If clip is too short, scale timings proportionally
            ratio = self.clip_duration / total_anim_time
            fade_in_time *= ratio
            fade_out_time *= ratio
            hold_time = 0
        else:
            hold_time = self.clip_duration - total_anim_time
            
        self.play(FadeIn(group), run_time=fade_in_time)
        if hold_time > 0:
            self.wait(hold_time)
        self.play(FadeOut(group), run_time=fade_out_time)

def generate_scene(text: str, duration: float, output_file: str, video_config: VideoConfig):
    """
    Generates a video clip for a single subtitle segment.
    """
    # Important: Manim writes to a specific directory structure by default.
    # We need to control the output.
    # The Scene.render() method writes to config.media_dir
    
    # We can use 'manim.config' context manager to isolate settings if needed,
    # but since we are running potentially in a loop, we setup once.
    
    # Instantiate Scene
    # Note: Manim is tricky to run precisely from function calls without CLI overhead because
    # it relies heavily on global config state.
    # To output to a specific file, we might need to move the file after generation
    # or hook into the file writer.
    
    # Let's try to override the output file config for this run.
    # Actually, simpler approach: clean the media dir or use a temp dir, then move the file.
    
    scene = SubtitleScene(text, duration, video_config)
    scene.render()
    
    # The output location is usually media/videos/video_quality/SubtitleScene.mp4
    # But we want to rename it/move it to 'output_file'
    # Manim 0.18+ has improved config.
    
    # We will need to locate the generated file.
    # A robust way is to ask the scene's renderer where the file is.
    
    generated_path = scene.renderer.file_writer.movie_file_path
    
    if generated_path:
        os.rename(generated_path, output_file)
    else:
        raise Exception("Video generation failed, no output file.")

