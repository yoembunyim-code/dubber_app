import streamlit as st
import os
import time
import tempfile
from datetime import datetime
from googletrans import Translator
import asyncio
import edge_tts
from moviepy.editor import VideoFileClip, AudioFileClip

# =======================================================
# 1. ផ្នែក Config
# =======================================================
OWNER_TELEGRAM = "@YOUR_TELEGRM" 

LICENSE_DATABASE = {
    "VIP-2026-ABCD": {"uses": 100, "expiry": "2026-12-31"}, 
    "ADMIN-9999":    {"uses": 999, "expiry": "2030-01-01"}, 
}

# =======================================================
# 2. មុខងារជំនួយ AI (Helper Functions)
# =======================================================

# មុខងារបកប្រែអត្ថបទទៅជាភាសាខ្មែរ
def translate_to_khmer(text):
    try:
        translator = Translator()
        translated = translator.translate(text, dest='km')
        return translated.text
    except Exception as e:
        return text  # បើមាន error វានឹងប្រើអត្ថបទដើម

# មុខងារបង្កើតសំឡេងនិយាយខ្មែរ (Edge-TTS)
async def generate_khmer_audio_async(text, voice, output_filename):
    # km-KH-SreymomNeural (ស្រី) ឬ km-KH-PisethNeural (ប្រុស)
    voice_name = "km-KH-SreymomNeural" if "ស្រី" in voice else "km-KH-PisethNeural"
    communicate = edge_tts.Communicate(text, voice_name)
    await communicate.save(output_filename)

def generate_khmer_audio(text, voice, output_filename):
    asyncio.run(generate_khmer_audio_async(text, voice, output_filename))

# =======================================================
# 3. ផ្នែកកំណត់ទំព័រ & CSS
# =======================================================
st.set_page_config(page_title="AI Dubbing & Translate System", layout="wide", page_icon="🎬")

if 'is_activated' not in st.session_state:
    st.session_state.is_activated = False
if 'current_key' not in st.session_state:
    st.session_state.current_key = None
if 'translated_video_data' not in st.session_state:
    st.session_state.translated_video_data = None
if 'is_processing' not in st.session_state:
    st.session_state.is_processing = False

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); font-family: 'Segoe UI', sans-serif; }
    section[data-testid="stSidebar"] { background-color: #1e293b; color: #ffffff; }
    section[data-testid="stSidebar"] .stMarkdown { color: #cbd5e1; }
    
    .stButton > button { border-radius: 12px; font-weight: 700; border: none; transition: all 0.3s ease; width: 100%; height: 3.2em; color: white; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
    .stButton > button:hover { transform: translateY(-3px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2); }
    
    .stButton.green-btn > button { background: linear-gradient(90deg, #10b981, #059669); font-size: 20px; height: 4em; }
    .stButton.blue-btn > button { background: linear-gradient(90deg, #3b82f6, #2563eb); }
    
    div[data-testid="stFileUploader"] button { background: linear-gradient(90deg, #3b82f6, #2563eb) !important; color: white !important; border-radius: 12px; width: 100%; height: 3.2em; font-weight: bold; border: none; }
    .stTextInput > div > div > input { border-radius: 12px; border: 2px solid #e2e8f0; padding: 12px; font-size: 16px; background-color: white; }
    .stVideo { border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.15); margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

# =======================================================
# 4. Sidebar
# =======================================================
with st.sidebar:
    st.markdown("## ℹ️ ព័ត៌មានអាជ្ញាប័ណ្ណ")
    st.markdown("---")
    
    status_text = "✅ សកម្ម" if st.session_state.is_activated else "⛔ មិនទាន់បើក"
    st.markdown(f"**ស្ថានភាពប្រើប្រាស់:** `{status_text}`")
    if st.session_state.is_activated:
        st.caption(f"លេខកូដ៖ `{st.session_state.current_key}`")
    
    st.markdown("---")
    st.markdown("#### 📞 ត្រូវការជំនួយ?")
    st.markdown(f"[![Telegram](https://img.shields.io/badge/Telegram-{OWNER_TELEGRAM}-blue?style=for-the-badge&logo=telegram)](https://t.me/{OWNER_TELEGRAM.replace('@', '')})")
    
    st.markdown("---")
    if st.button("🔄 កំណត់ឡើងវិញ", use_container_width=True):
        st.session_state.is_activated = False
        st.session_state.translated_video_data = None
        st.success("បានកំណត់ឡើងវិញ!")

# =======================================================
# 5. Main Interface
# =======================================================
st.markdown("<h1 style='text-align: center;'>🎬 ប្រព័ន្ធឌឹប និងបកប្រែវីដេអូ AI</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>ផ្ទុកវីដេអូឡើង រួចបកប្រែ និងឌឹបជាភាសាខ្មែរដោយស្វ័យប្រវត្តិ</p>", unsafe_allow_html=True)
st.markdown("---")

col1, col2 = st.columns([3, 1])
with col1:
    uploaded_video = st.file_uploader("ផ្ទុកវីដេអូរបស់អ្នកនៅទីនេះ", type=['mp4', 'avi', 'mov', 'mkv'], label_visibility="collapsed")
    if uploaded_video is not None:
        st.caption(f"✅ បានផ្ទុកដោយជោគជ័យ៖ `{uploaded_video.name}`")
with col2:
    uploaded_srt = st.file_uploader("📄 ផ្ទុក SRT (ជម្រើស)", type=['srt'], label_visibility="collapsed")

st.markdown("<br>", unsafe_allow_html=True)
voice_option = st.selectbox("🎤 ជ្រើសរើសសម្លេងសម្រាប់ភាសាខ្មែរ", ["ស្រី (Female)", "ប្រុស (Male)"])
st.markdown("<br>", unsafe_allow_html=True)

# =======================================================
# 6. ផ្នែក START និងដំណើរការ AI ពិតប្រាកដ
# =======================================================
st.markdown("### 🚀 ចាប់ផ្ដើមឌឹប និងបកប្រែ")
st.markdown('<div class="green-btn">', unsafe_allow_html=True)

if st.button("🚀 START ឌឹបវីដេអូ", use_container_width=True):
    if not st.session_state.is_activated:
        st.warning("សូម Activate VIP ជាមុនសិន ទើបអាចប្រើ START បាន!")
    elif uploaded_video is None:
        st.warning("សូមផ្ទុកវីដេអូជាមុនសិន!")
    else:
        st.session_state.is_processing = True
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.is_processing:
    st.markdown("---")
    with st.status("🤖 កំពុងដំណើរការឌឹប និងបកប្រែដោយ AI... (សូមរង់ចាំ)", expanded=True) as status:
        try:
            # រៀបចំ Folder បណ្ដោះអាសន្ន
            with tempfile.TemporaryDirectory() as temp_dir:
                input_video_path = os.path.join(temp_dir, "input_video.mp4")
                output_audio_path = os.path.join(temp_dir, "khmer_audio.mp3")
                final_output_path = os.path.join(temp_dir, "final_dubbed.mp4")

                # រក្សាទុកវីដេអូដែលអាប់ឡូតទៅក្នុង File បណ្ដោះអាសន្ន
                with open(input_video_path, "wb") as f:
                    f.write(uploaded_video.read())

                # ជំហានទី 1 & 2: ទទួលបានអត្ថបទបកប្រែ
                st.write("📌 1. កំពុងអាន និងបកប្រែអត្ថបទទៅជាភាសាខ្មែរ...")
                if uploaded_srt is not None:
                    raw_text = uploaded_srt.read().decode("utf-8")
                else:
                    # ប្រសិនបើគ្មាន SRT អាចប្រើអត្ថបទគំរូ ឬភ្ជាប់ជាមួយ Whisper API
                    raw_text = "Welcome to our video dubbing system. Enjoy the automation."
                
                khmer_text = translate_to_khmer(raw_text)

                # ជំហានទី 3: សំយោគសំឡេងខ្មែរ (TTS)
                st.write(f"📌 2. កំពុងសំយោគសំឡេងខ្មែរ ({voice_option})...")
                generate_khmer_audio(khmer_text, voice_option, output_audio_path)

                # ជំហានទី 4: បញ្ចូលសំឡេងថ្មីទៅក្នុងវីដេអូ (Video-Audio Muxing)
                st.write("📌 3. កំពុងផ្សំសំឡេងខ្មែរចូលទៅក្នុងវីដេអូដើម...")
                video_clip = VideoFileClip(input_video_path)
                audio_clip = AudioFileClip(output_audio_path)

                # កំណត់សំឡេងថ្មីទៅឱ្យវីដេអូ
                final_clip = video_clip.set_audio(audio_clip)
                final_clip.write_videofile(final_output_path, codec="libx264", audio_codec="aac", logger=None)

                # អានទិន្នន័យវីដេអូចុងក្រោយទុកក្នុង Session
                with open(final_output_path, "rb") as f:
                    st.session_state.translated_video_data = f.read()

                # បិទ Clip ដើម្បីកុំឱ្យស្ទះ Memory
                video_clip.close()
                audio_clip.close()

            status.update(label="✅ ដំណើរការឌឹប និងបកប្រែបានបញ្ចប់ដោយជោគជ័យ!", state="complete", expanded=False)
            st.session_state.is_processing = False
            st.rerun()

        except Exception as e:
            st.error(f"❌ មានបញ្ហាក្នុងពេលដំណើរការ៖ {str(e)}")
            st.session_state.is_processing = False

# =======================================================
# 7. បង្ហាញ និងទាញយកលទ្ធផល
# =======================================================
if st.session_state.translated_video_data is not None:
    st.markdown("---")
    st.markdown("### 🎬 លទ្ធផលវីដេអូដែលបានឌឹបជាខ្មែរ")
    st.success("ឌឹបដោយជោគជ័យ! អ្នកអាចមើលវីដេអូ ឬទាញយកបានខាងក្រោម៖")
    
    st.video(st.session_state.translated_video_data)
    
    st.download_button(
        label="📥 ទាញយកវីដេអូដែលបានបកប្រែ",
        data=st.session_state.translated_video_data,
        file_name="dubbed_khmer_video.mp4",
        mime="video/mp4"
    )

# =======================================================
# 8. ផ្នែក Activate VIP
# =======================================================
st.markdown("---")
st.markdown("### 🔑 បើកសិទ្ធិប្រើប្រាស់ VIP")
if st.session_state.is_activated:
    st.info("💡 អ្នកបាន Activate VIP រួចហើយ! សូមចុច START ខាងលើដើម្បីចាប់ផ្ដើមដំណើរការ។")
else:
    c_input, c_btn = st.columns([4, 1])
    with c_input:
        act_code_input = st.text_input("បញ្ចូលលេខកូដ VIP នៅទីនេះ", placeholder="ឧ. VIP-2026-ABCD", label_visibility="collapsed")
    with c_btn:
        if st.button("✅ Activate VIP", type="primary", use_container_width=True):
            if not act_code_input or act_code_input.strip() == "":
                st.error("❌ សូមបញ្ចូលលេខកូដ។")
            else:
                if act_code_input in LICENSE_DATABASE:
                    details = LICENSE_DATABASE[act_code_input]
                    try:
                        today = datetime.now().date()
                        expiry_date = datetime.strptime(details['expiry'], "%Y-%m-%d").date()
                        if today > expiry_date:
                            st.error("❌ កូដនេះផុតកំណត់ហើយ!")
                        elif details['uses'] <= 0:
                            st.error("❌ កូដនេះអស់ការប្រើប្រាស់ហើយ!")
                        else:
                            st.session_state.is_activated = True
                            st.session_state.current_key = act_code_input
                            LICENSE_DATABASE[act_code_input]['uses'] -= 1
                            st.success("🎉 Activate ជោគជ័យ! សូមរីករាយប្រើប្រាស់។")
                            st.rerun()
                    except ValueError:
                        st.error("❌ កំហុសទិន្នន័យកូដ។")
                else:
                    st.error("❌ លេខកូដមិនត្រឹមត្រូវ! ទាក់ទង Telegram ដើម្បីទិញ License។")
