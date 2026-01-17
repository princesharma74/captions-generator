from dataclasses import dataclass, field
from typing import Tuple

@dataclass
class VideoConfig:
    """Configuration for the video generation."""
    
    # Video settings
    width: int = 1920
    height: int = 1080
    fps: int = 30
    
    # Visual settings
    font_size: int = 70 # Larger for landscape
    font_name: str = "Sans"
    text_color: str = "#FFFFFF"
    
    # Strip (background behind text) settings
    strip_color: str = "#000000"
    strip_opacity: float = 0.7
    strip_corner_radius: float = 0.2
    padding: float = 0.5
    
    # Main background
    bg_color: str = "#00FF00"
    
    # Animation timings
    fade_in_time: float = 0.2
    fade_out_time: float = 0.2
    
    # Positioning
    # Landscape: Center text.
    # We remove bottom margin percent concept or set to None/Center
    bottom_margin_percent: float = 0.0 # Not used if centered logic applied

@dataclass
class ManimConfig:
    """Configuration for Manim Captions."""
    font_name: str = "Arial Black"
    font_size: int = 72
    text_color: str = "#FFFFFF" # Hex for Manim
    highlight_color: str = "#FFA500" # Orange
    
    # Background Box
    bg_color: str = "#000000"
    bg_opacity: float = 0.8
    corner_radius: float = 0.4
    padding_h: float = 0.8 
    padding_v: float = 0.4
    
    # Layout (relative to center or edge)
    # Manim coordinates are different, but we can stick to simple "bottom center" assumption for now
    # or expose position offset.
    bottom_offset: float = 1.5 # Units from bottom edge
