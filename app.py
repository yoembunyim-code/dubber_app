import streamlit as st
import os
import asyncio
import tempfile
import subprocess
from datetime import datetime
from deep_translator import GoogleTranslator
import edge_tts

# Configuration Page
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

# Function សម្រាប់បញ្ជូល Audio ចូល Video ដោយប្រើ FFmpeg ផ្ទាល់ (សុវត្ថិភាព 100%)
def merge_video_audio(video_path, audio_path, output_path):
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",        # រក្សាគុណភាពវីដេអូដើម (ដើរលឿនខ្លាំង)
        "-c:a", "aac",         # Convert សំឡេងទៅ AAC
        "-map", "0:v:0",       # យក វីដេអូ ពី file ទី១
        "-map", "1:a:0",       # យក សំឡេង ពី file ទី២
        "-shortest",           # កាត់សំឡេង/វីដេអូ ឱ្យសមប្រវែងគ្នា
        output_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

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

# Content Input
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
        with st.spinner("🤖 កំពុងដំណើរការ... សូមរង់ចាំបន្តិច"):
            try:
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

                    # ៤. Merge Audio ចូល Video ដោយប្រើ FFmpeg
                    st.write("📌 កំពុងបញ្ចូលសំឡេងទៅក្នុងវីដេអូ...")
                    merge_video_audio(in_video_path, out_audio_path, out_video_path)

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
