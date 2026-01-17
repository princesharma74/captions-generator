import os
from config import ManimConfig

def get_config() -> ManimConfig:
    """Returns the standard Manim configuration, with optional overrides from environment variables."""
    return ManimConfig(
        font_name=os.environ.get("CFG_FONT_NAME", "Arial Black"),
        font_size=int(os.environ.get("CFG_FONT_SIZE", 56)),
        text_color=os.environ.get("CFG_TEXT_COLOR", "#FFFFFF"),
        highlight_color=os.environ.get("CFG_HIGHLIGHT_COLOR", "#00FF00"),
        bg_color=os.environ.get("CFG_BG_COLOR", "#000000"),
        bg_opacity=float(os.environ.get("CFG_BG_OPACITY", 0.8)),
        corner_radius=float(os.environ.get("CFG_CORNER_RADIUS", 0.2)),
        padding_h=float(os.environ.get("CFG_PADDING_H", 0.5)),
        padding_v=float(os.environ.get("CFG_PADDING_V", 0.2)),
        bottom_offset=float(os.environ.get("CFG_BOTTOM_OFFSET", 0))
    )
