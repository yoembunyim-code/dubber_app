import streamlit as st
import os
import asyncio
import tempfile
from datetime import datetime
from deep_translator import GoogleTranslator
import edge_tts
from moviepy.editor import VideoFileClip, AudioFileClip

# Page Configuration
st.set_page_config(page_title="AI Dubbing System", layout="wide", page_icon="🎬")

OWNER_TELEGRAM = "@YOUR_TELEGRAM"
LICENSE_DATABASE = {
    "VIP-2026-ABCD": {"uses": 100, "expiry": "2026-12-31"},
    "ADMIN-9999": {"uses": 999, "expiry": "2030-01-01"},
}

# Session State Setup
if 'is_activated' not in st.session_state:
    st.session_state.is_activated = False
if 'current_key' not in st.session_state:
    st.session_state.current_key = None

# Async function for Edge TTS
async def generate_voice(text, voice_name, output_path):
    communicate = edge_tts.Communicate(text, voice_name)
    await communicate.save(output_path)

# UI Styles
st.markdown("<h1 style='text-align: center;'>🎬 ប្រព័ន្ធឌឹប និងបកប្រែវីដេអូ AI</h1>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## ℹ️ ព័ត៌មានអាជ្ញាប័ណ្ណ")
    status_text = "✅ សកម្ម" if st.session_state.is_activated else "⛔ មិនទាន់បើក"
    st.markdown(f"**ស្ថានភាព:** `{status_text}`")
    if st.session_state.is_activated:
        st.caption(f"កូដ៖ `{st.session_state.current_key}`")

# Main Inputs
uploaded_video = st.file_uploader("ផ្ទុកវីដេអូ (MP4)", type=['mp4'])
script_text = st.text_area("បញ្ចូលអត្ថបទដើម ឬអត្ថបទដែលត្រូវឌឹប (ភាសាអង់គ្លេស ឬខ្មែរ):", height=100)
voice_gender = st.selectbox("🎤 ជ្រើសរើសសំឡេងខ្មែរ", ["ស្រី (Sreymom)", "ប្រុស (Piseth)"])

if st.button("🚀 ចាប់ផ្ដើមឌឹបវីដេអូ", type="primary", use_container_width=True):
    if not st.session_state.is_activated:
        st.error("❌ សូម Activate VIP នៅខាងក្រោមជាមុនសិន!")
    elif uploaded_video is None:
        st.warning("⚠️ សូមផ្ទុកវីដេអូជាមុនសិន!")
    elif not script_text.strip():
        st.warning("⚠️ សូមបញ្ចូលអត្ថបទសម្រាប់និយាយ!")
    else:
        with st.spinner("🤖 កំពុងដំណើរការ... សូមរង់ចាំបន្តិច"):
            try:
                # បង្កើត Temporary Directory សុវត្ថិភាព
                with tempfile.TemporaryDirectory() as temp_dir:
                    in_video_path = os.path.join(temp_dir, "input.mp4")
                    out_audio_path = os.path.join(temp_dir, "speech.mp3")
                    out_video_path = os.path.join(temp_dir, "output.mp4")

                    # ១. រក្សាទុកវីដេអូ
                    with open(in_video_path, "wb") as f:
                        f.write(uploaded_video.read())

                    # ២. បកប្រែអត្ថបទទៅខ្មែរ
                    translated_text = GoogleTranslator(source='auto', target='km').translate(script_text)
                    st.info(f"📝 អត្ថបទបកប្រែខ្មែរ៖ {translated_text}")

                    # ៣. បង្កើតសំឡេងនិយាយខ្មែរ (Edge-TTS)
                    selected_voice = "km-KH-SreymomNeural" if "ស្រី" in voice_gender else "km-KH-PisethNeural"
                    asyncio.run(generate_voice(translated_text, selected_voice, out_audio_path))

                    # ៤. បញ្ចូលសំឡេងទៅក្នុងវីដេអូដោយសុវត្ថិភាព
                    video_clip = VideoFileClip(in_video_path)
                    audio_clip = AudioFileClip(out_audio_path)
                    
                    # សម្រួលប្រវែង Audio មិនឱ្យលើស Video
                    if audio_clip.duration > video_clip.duration:
                        audio_clip = audio_clip.subclip(0, video_clip.duration)

                    final_clip = video_clip.set_audio(audio_clip)
                    final_clip.write_videofile(
                        out_video_path, 
                        codec="libx264", 
                        audio_codec="aac", 
                        preset="ultrafast", # ការពារ RAM Crash លើ Cloud
                        logger=None
                    )

                    # បិទ Resource
                    video_clip.close()
                    audio_clip.close()

                    # ៥. បង្ហាញលទ្ធផល
                    st.success("✅ ឌឹបរួចរាល់!")
                    with open(out_video_path, "rb") as vf:
                        video_bytes = vf.read()
                        st.video(video_bytes)
                        st.download_button("📥 ទាញយកវីដេអូ", video_bytes, file_name="dubbed_video.mp4", mime="video/mp4")

            except Exception as e:
                st.error(f"❌ កំហុសបច្ចេកទេស៖ {str(e)}")

# VIP Activation Section
st.markdown("---")
st.subheader("🔑 បើកសិទ្ធិ VIP")
act_code = st.text_input("បញ្ចូលកូដ VIP")
if st.button("Activate"):
    if act_code in LICENSE_DATABASE:
        st.session_state.is_activated = True
        st.session_state.current_key = act_code
        st.success("🎉 បើកសិទ្ធិជោគជ័យ!")
        st.rerun()
    else:
        st.error("កូដមិនត្រឹមត្រូវ!")
