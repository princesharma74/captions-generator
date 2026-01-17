import streamlit as st
import os
import shutil
import subprocess
from datetime import datetime
import sys
import srt
import difflib

# Import local modules
# Depending on how streamlit is run, we might need to adjust python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import transcriber
import video_processor
import text_alignment

# Page Config
st.set_page_config(
    page_title="Caption Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎬 Caption Generator")
st.markdown("Generate high-quality, karaoke-style highlighted subtitles for your videos.")
st.markdown("**Note:** You can edit the transcription text below. The system will automatically align your edits with the original audio timing.")

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    st.subheader("Model Settings")
    whisper_model = st.selectbox("Whisper Model", ["base", "tiny", "small", "medium", "large"], index=0)
    
    st.subheader("Visual Style")
    
    # Font Settings
    # Font Settings
    try:
        import manimpango
        available_fonts = sorted(manimpango.list_fonts())
    except ImportError:
        available_fonts = ["Arial", "Helvetica", "Times New Roman", "Courier New"]
    
    default_font_index = 0
    if "Arial Black" in available_fonts:
         default_font_index = available_fonts.index("Arial Black")
    
    font_name = st.selectbox("Font Family", available_fonts, index=default_font_index)
    font_size = st.slider("Font Size", min_value=20, max_value=120, value=70)
    
    # Colors
    col1, col2 = st.columns(2)
    with col1:
        text_color = st.color_picker("Text Color", "#FFFFFF")
        highlight_color = st.color_picker("Highlight Color", "#00FF00")
    with col2:
        strip_color = st.color_picker("Strip Color", "#000000")
        corner_radius = st.slider("Corner Radius", 0.0, 1.0, 0.2, step=0.1)

    strip_opacity = st.slider("Strip Opacity", 0.0, 1.0, 0.8, step=0.1)
    
    st.subheader("Layout")
    bottom_offset = st.slider("Vertical Offset", -5.0, 5.0, 0.0, step=0.5, help="0 is Center")


# Initialize Session State
if "original_words" not in st.session_state:
    st.session_state.original_words = [] # List of text_alignment.Word
if "plain_text" not in st.session_state:
    st.session_state.plain_text = ""
if "work_dir" not in st.session_state:
    st.session_state.work_dir = ""
if "audio_path" not in st.session_state:
    st.session_state.audio_path = ""
if "last_uploaded_file" not in st.session_state:
    st.session_state.last_uploaded_file = None

# Main Input
st.subheader("1. Upload Audio")
uploaded_file = st.file_uploader("Choose an audio file", type=["mp3", "wav", "m4a"])

if uploaded_file:
    # Reset state if new file uploaded
    if st.session_state.last_uploaded_file != uploaded_file.name:
        st.session_state.original_words = []
        st.session_state.plain_text = ""
        st.session_state.work_dir = ""
        st.session_state.audio_path = ""
        st.session_state.last_uploaded_file = uploaded_file.name
    
    # Prepare Workspace (if not already set)
    if not st.session_state.work_dir:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.work_dir = os.path.join("outputs", "streamlit_files", timestamp)
        os.makedirs(st.session_state.work_dir, exist_ok=True)
        
        # Save Audio
        file_path = os.path.join(st.session_state.work_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state.audio_path = os.path.abspath(file_path)

    st.audio(st.session_state.audio_path)
    
    # Step 2: Transcribe
    st.subheader("2. Transcribe & Edit")
    
    if st.button("📝 Transcribe Audio"):
        with st.spinner("Transcribing..."):
            try:
                raw_srt_path = transcriber.transcribe_audio(st.session_state.audio_path, model_name=whisper_model)
                
                # Parse SRT into original_words
                with open(raw_srt_path, "r", encoding="utf-8") as f:
                    srt_generator = srt.parse(f.read())
                    original_words = []
                    texts = []
                    for subtitle in srt_generator:
                         # Assume 1 word per subtitle line as per previous transcriber logic?
                         # Even if multiple words, we treat the subtitle content as the text.
                         # Actually, our text_alignment logic expects split words.
                         # If transcriber produces phrases, we might need to handle that.
                         # But current transcriber.py we built earlier produces 1 word per line.
                         # Let's double check.
                         # Yes, lines 122-129 in transcriber.py (from Step 10) appends words individually.
                         
                         w = text_alignment.Word(
                             text=subtitle.content,
                             start=subtitle.start.total_seconds(),
                             end=subtitle.end.total_seconds()
                         )
                         original_words.append(w)
                         texts.append(subtitle.content)
                    
                    st.session_state.original_words = original_words
                    st.session_state.plain_text = " ".join(texts)
                    
                st.success("Transcription Complete! You can edit the text below.")
                st.rerun()
            except Exception as e:
                st.error(f"Transcription failed: {str(e)}")
                st.exception(e)

    # Show Editor if text exists
    if st.session_state.plain_text:
        edited_text = st.text_area("Edit Transcript", st.session_state.plain_text, height=300)
        
        # Step 3: Render
        st.subheader("3. Generate Video")
        if st.button("🚀 Render Video"):
            status_area = st.empty()
            progress_bar = st.progress(0)
            
            try:
                work_dir = st.session_state.work_dir
                audio_path_abs = st.session_state.audio_path
                
                # Reconcile Timestamps
                status_area.text("⏳ Aligning edits with timestamps...")
                final_words = text_alignment.reconcile_alignments(st.session_state.original_words, edited_text)
                
                # Generate new SRT
                srt_entries = []
                for idx, w in enumerate(final_words):
                    srt_entries.append(w.to_srt_entry(idx+1))
                
                final_srt_content = "".join(srt_entries)
                srt_path = os.path.join(work_dir, "captions.srt")
                with open(srt_path, "w", encoding="utf-8") as f:
                    f.write(final_srt_content)
                
                progress_bar.progress(20)

                # Render Manim
                status_area.text("⏳ Rendering Animation...")
                
                env = os.environ.copy()
                env["MANIM_AUDIO_PATH"] = audio_path_abs
                env["MANIM_SRT_PATH"] = os.path.abspath(srt_path)
                
                # Inject Configs
                env["CFG_FONT_NAME"] = font_name
                env["CFG_FONT_SIZE"] = str(font_size)
                env["CFG_TEXT_COLOR"] = text_color
                env["CFG_HIGHLIGHT_COLOR"] = highlight_color
                env["CFG_BG_COLOR"] = strip_color
                env["CFG_BG_OPACITY"] = str(strip_opacity)
                env["CFG_CORNER_RADIUS"] = str(corner_radius)
                env["CFG_BOTTOM_OFFSET"] = str(bottom_offset)
                
                cmd = [
                    "manim", 
                    "-r", "1920,1080",
                    "--fps", "30",
                    "--disable_caching", 
                    "--media_dir", work_dir,
                    "manim_renderer.py", 
                    "CaptionScene"
                ]
                
                process = subprocess.run(cmd, env=env, capture_output=True, text=True)
                
                if process.returncode != 0:
                    st.error("Manim Rendering Failed!")
                    with st.expander("Show detailed error"):
                        st.code(process.stderr)
                        st.code(process.stdout)
                    st.stop()
                    
                progress_bar.progress(70)
                
                # Finalize
                status_area.text("⏳ Finalizing Audio Sync...")
                
                manim_video_path = os.path.join(work_dir, "videos", "manim_renderer", "1080p30", "CaptionScene.mp4")
                final_output_path = os.path.join(work_dir, f"final_output.mp4")
                
                if not os.path.exists(manim_video_path):
                     st.error(f"Could not find Manim output at: {manim_video_path}")
                     st.stop()

                video_processor.replace_audio_track(manim_video_path, audio_path_abs, final_output_path)
                
                progress_bar.progress(100)
                status_area.empty()
                st.success("✅ Generation Complete!")
                
                st.video(final_output_path)
                
                with open(final_output_path, "rb") as f:
                    st.download_button(
                        label="Download Video",
                        data=f,
                        file_name=f"captioned_video.mp4",
                        mime="video/mp4"
                    )
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.exception(e)
