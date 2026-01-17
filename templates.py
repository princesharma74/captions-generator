from config import SubtitleConfig

TEMPLATES = {
    "default": SubtitleConfig(
        font_name="Arial",
        font_size=60,
        primary_color="&H00FFFFFF",  # White
        secondary_color="&H0000FFFF", # Yellow
        outline_color="&H00000000",   # Black
        outline_width=2,
        shadow_depth=1,
        alignment=5, # Center
        margin_v=50
    ),
    "karaoke": SubtitleConfig(
        font_name="Romance Fatal Serif Std", # Or a more "Karaoke" font if available, fallback to Serif
        font_size=50,
        primary_color="&H00FFFFFF",  # White
        secondary_color="&H00FFFF00", # Cyan/Blueish for fill
        outline_color="&H00000000",
        outline_width=3,
        shadow_depth=2,
        alignment=2, # Bottom Center
        margin_v=30
    ),
    "cinematic": SubtitleConfig(
        font_name="Helvetica",
        font_size=40,
        primary_color="&H00E0E0E0",  # Light Gray
        secondary_color="&H00FFFFFF", # White for highlight
        outline_color="&H80000000",   # Semi-transparent black
        outline_width=1,
        shadow_depth=0,
        alignment=2, # Bottom Center
        margin_v=80
    ),
    "shorts": SubtitleConfig(
        font_name="Impac", # Impact is common for shorts, spelling check? Usually "Impact". Let's use "Verdana" safe or "Arial Black"
        font_size=80,
        primary_color="&H0000FFFF",   # Yellow text
        secondary_color="&H000000FF", # Red highlight
        outline_color="&H00000000",   # Black outline
        outline_width=4,
        shadow_depth=0,
        alignment=5, # Center Screen
        margin_v=20
    ),
    "classic": SubtitleConfig(
        font_name="Helvetica",        # Classic minimal font
        font_size=64,
        primary_color="&H00FFFFFF",   # White text (unhighlighted)
        secondary_color="&H0000FFFF", # Yellow highlight (word-by-word)
        outline_color="&H00000000",   # Black (not used since outline_width=0)
        outline_width=0,              # NO OUTLINE - clean minimal look
        shadow_depth=2,               # Subtle shadow for readability
        alignment=2,                  # Bottom Center
        margin_v=60
    ),
    "premium": SubtitleConfig(
        font_name="Arial Black",      # Bold sans-serif
        font_size=72,
        bold=True,
        primary_color="&H00FFFFFF",   # White (unhighlighted)
        secondary_color="&H0000A5FF", # Orange highlight
        outline_color="&H00000000",   # Not used
        outline_width=0,              # No outline
        shadow_depth=0,               # No shadow (background provides contrast)
        border_style=3,               # Opaque background box
        back_color="&HCC000000",      # Dark background, 80% opacity
        alignment=2,                  # Bottom center
        margin_v=60,
        margin_l=40,                  # Horizontal padding
        margin_r=40
    )
}

def get_template(name: str) -> SubtitleConfig:
    """Returns the requested template or the default if not found."""
    return TEMPLATES.get(name.lower(), TEMPLATES["default"])
