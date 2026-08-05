import streamlit as st
import os
import asyncio
import tempfile
from datetime import datetime

# Import External Packages ជាមួយ Safety Check
try:
    from deep_translator import GoogleTranslator
    import edge_tts
    from moviepy.editor import VideoFileClip, AudioFileClip
except Exception as e:
    st.error(f"⚠️ Error Importing Libraries: {e}")

# Config Page
st.set_page_config(page_title="AI Dubbing System", layout="wide", page_icon="🎬")

OWNER_TELEGRAM = "@YOUR_TELEGRAM"
LICENSE_DATABASE = {
    "VIP-2026-ABCD": {"uses": 100, "expiry": "2026-12-31"},
    "ADMIN-9999": {"uses": 999, "expiry": "2030-01-01"},
}

# Session States
if 'is_activated' not in st.session_state:
    st.session_state.is_activated = False
if 'current_key' not in st.session_state:
    st.session_state.current_key = None

# Function សម្រាប់បង្កើតសំឡេង
async def generate_voice_async(text, voice_name, output_path):
    communicate = edge_tts.Communicate(text, voice_name)
    await communicate.save(output_path)

def generate_voice(text, voice_name, output_path):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(generate_voice_async(text, voice_name, output_path))
    loop.close()

# ----------------- UI -----------------
st.title("🎬 ប្រព័ន្ធឌឹប និងបកប្រែវីដេអូ AI")
st.caption("ប្រព័ន្ធបកប្រែ និងបញ្បញ្ចូលសំឡេងខ្មែរស្វ័យប្រវត្តិ")

# Sidebar
with st.sidebar:
    st.header("ℹ️ ព័ត៌មានអាជ្ញាប័ណ្ណ")
    status_text = "✅ VIP សកម្ម" if st.session_state.is_activated else "⛔ មិនទាន់បើក"
    st.subheader(f"ស្ថានភាព: {status_text}")
    if st.session_state.is_activated:
        st.info(f"Code: {st.session_state.current_key}")

# Content
uploaded_video = st.file_uploader("១. ផ្ទុកវីដេអូ (MP4)", type=['mp4', 'mov'])
script_text = st.text_area("២. បញ្ចូលអត្ថបទដើម ឬអត្ថបទបកប្រែ:", height=100, placeholder="ឧទាហរណ៍: Hello, welcome to my channel.")
voice_gender = st.selectbox("៣. ជ្រើសរើសសំឡេងខ្មែរ", ["ស្រី (Sreymom)", "ប្រុស (Piseth)"])

st.markdown("<br>", unsafe_allow_html=True)

if st.button("🚀 ចាប់ផ្ដើមឌឹបវីដេអូ", type="primary", use_container_width=True):
    if not st.session_state.is_activated:
        st.error("❌ សូម Activate VIP នៅខាងក្រោមជាមុនសិន!")
    elif uploaded_video is None:
        st.warning("⚠️ សូមផ្ទុកវីដេអូជាមុនសិន!")
    elif not script_text.strip():
        st.warning("⚠️ សូមបញ្ចូលអត្ថបទសម្រាប់និយាយ!")
    else:
        with st.spinner("🤖 កំពុងដំណើរការ... សូមរង់ចាំ (អាចចំណាយពេល ១-២ នាទី)"):
            try:
                # បង្កើត Temp Folder
                with tempfile.TemporaryDirectory() as temp_dir:
                    in_video_path = os.path.join(temp_dir, "input.mp4")
                    out_audio_path = os.path.join(temp_dir, "speech.mp3")
                    out_video_path = os.path.join(temp_dir, "output.mp4")

                    # ១. រក្សាទុក Uploaded Video
                    with open(in_video_path, "wb") as f:
                        f.write(uploaded_video.read())

                    # ២. បកប្រែអត្ថបទ
                    st.write("📌 កំពុងបកប្រែអត្ថបទទៅជាភាសាខ្មែរ...")
                    translated_text = GoogleTranslator(source='auto', target='km').translate(script_text)
                    st.success(f"📝 អត្ថបទខ្មែរ: {translated_text}")

                    # ៣. បង្កើតសំឡេងនិយាយ
                    st.write("📌 កំពុងបង្កើតសំឡេងនិយាយខ្មែរ...")
                    selected_voice = "km-KH-SreymomNeural" if "ស្រី" in voice_gender else "km-KH-PisethNeural"
                    generate_voice(translated_text, selected_voice, out_audio_path)

                    # ៤. Merge Audio ចូល Video
                    st.write("📌 កំពុងបញ្ចូលសំឡេងទៅក្នុងវីដេអូ...")
                    video_clip = VideoFileClip(in_video_path)
                    audio_clip = AudioFileClip(out_audio_path)

                    if audio_clip.duration > video_clip.duration:
                        audio_clip = audio_clip.subclip(0, video_clip.duration)

                    final_clip = video_clip.set_audio(audio_clip)
                    final_clip.write_videofile(
                        out_video_path,
                        codec="libx264",
                        audio_codec="aac",
                        temp_audiofile=os.path.join(temp_dir, "temp-audio.m4a"),
                        remove_temp=True,
                        logger=None
                    )

                    video_clip.close()
                    audio_clip.close()

                    # ៥. បង្ហាញលទ្ធផល
                    st.balloons()
                    st.success("🎉 ឌឹបរួចរាល់!")
                    
                    with open(out_video_path, "rb") as vf:
                        video_bytes = vf.read()
                        st.video(video_bytes)
                        st.download_button("📥 ទាញយកវីដេអូ", video_bytes, file_name="dubbed_khmer.mp4", mime="video/mp4")

            except Exception as e:
                st.error(f"❌ បញ្ហាបច្ចេកទេសក្នុងពេល Render: {str(e)}")

# VIP Section
st.markdown("---")
st.subheader("🔑 បើកសិទ្ធិ VIP")
act_code = st.text_input("បញ្ចូលកូដ VIP (ឧទាហរណ៍: VIP-2026-ABCD)")
if st.button("Activate VIP"):
    if act_code in LICENSE_DATABASE:
        st.session_state.is_activated = True
        st.session_state.current_key = act_code
        st.success("🎉 បើកសិទ្ធិជោគជ័យ!")
        st.rerun()
    else:
        st.error("❌ កូដមិនត្រឹមត្រូវ!")
