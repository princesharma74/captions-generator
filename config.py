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
class SubtitleConfig:
    """Configuration for ASS Subtitles."""
    # Colors are in ASS Hex format: &HAABBGGRR
    # Primary color (Fill) - White
    primary_color: str = "&H00FFFFFF"
    # Secondary color (Karaoke highlight) - Yellow (BGR: 00FFFF)
    secondary_color: str = "&H0000FFFF" 
    
    font_name: str = "Arial"
    font_size: int = 60
    # Alignment: 2 = Bottom Center, 5 = Top Center, 10 = Center of Screen (if using ASS numpad alignment)
    # Standard ASS alignment: 1=Left, 2=Center, 3=Right (Subtitles)
    # 5=Top Left? No, ASS numpad: 7 8 9, 4 5 6, 1 2 3.
    # So 2 is Bottom Center.
    # Alignment: 2 = Bottom Center, 5 = Top Center?
    # ASS alignment (numpad): 
    # 1=Bottom Left, 2=Bottom Center, 3=Bottom Right
    # 4=Mid Left, 5=Mid Center, 6=Mid Right
    # 7=Top Left, 8=Top Center, 9=Top Right
    # User asked for "subtitles in the center".
    alignment: int = 5 
    margin_v: int = 50
    outline_color: str = "&H00000000"
    outline_width: int = 2
    shadow_depth: int = 1
    
    # Premium styling options
    bold: bool = False
    border_style: int = 1 # 1=Outline, 3=Opaque Box
    back_color: str = "&H80000000" # Background box color (if border_style=3)
    margin_l: int = 10
    margin_r: int = 10
