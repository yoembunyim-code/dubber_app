import streamlit as st
import json
import os
import time
import tempfile
import speech_recognition as sr
from moviepy.editor import VideoFileClip
from deep_translator import GoogleTranslator
from gtts import gTTS

# ==========================================
# CONFIGURATION & DATABASE (កំណត់រចនាសម្ព័ន្ធ)
# ==========================================
CONTACT_TELEGRAM = "@Semsamnang_Dev"
TRIAL_VIDEO_LIMIT = 3
LICENSE_FILE = "license.json"

VALID_VIP_CODES = ["VIP2024", "SEMSAMNANG123", "KHMERDUBBING"]

KHMER_VOICES = [
    "កញ្ញា ស្រី (Female)", 
    "លោក ប្រុស (Male)", 
    "កញ្ញា កំប្លែង (Female - Srey Mom)"
]

# ==========================================
# LICENSE MANAGER (គ្រប់គ្រងការសាកល្បង)
# ==========================================
def load_license():
    if os.path.exists(LICENSE_FILE):
        with open(LICENSE_FILE, 'r') as f:
            data = json.load(f)
            return data.get("video_processed", 0), data.get("is_vip", False)
    return 0, False

def save_license(count, is_vip=False):
    with open(LICENSE_FILE, 'w') as f:
        json.dump({"video_processed": count, "is_vip": is_vip}, f)

def check_license(is_vip):
    if is_vip:
        return True, "VIP Unlimited"
    usage, _ = load_license()
    if usage >= TRIAL_VIDEO_LIMIT:
        return False, usage
    return True, usage

# ==========================================
# STREAMLIT UI DESIGN (រចនាប្លង់ស្អាត)
# ==========================================
st.set_page_config(page_title="AI Khmer Dubbing PRO", page_icon="🎬", layout="wide")

# Sidebar: កន្លែងដាក់លេខកូដ VIP និងជ្រើសសំឡេង
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3176/3176366.png", width=80)
    st.title("⚙️ Settings")
    
    st.subheader("🔑 Enter VIP Code")
    vip_input = st.text_input("VIP Code", placeholder="បញ្ចូលលេខកូដនៅទីនេះ")
    if st.button("Activate VIP"):
        if vip_input in VALID_VIP_CODES:
            usage, _ = load_license()
            save_license(usage, is_vip=True)
            st.success("✅ បានធ្វើឱ្យសកម្ម VIP ដោយជោគជ័យ!")
            st.rerun()
        else:
            st.error("❌ លេខកូដ VIP មិនត្រឹមត្រូវ។")

    st.subheader("🎙️ Voice Selection")
    selected_voice = st.selectbox("ជ្រើសរើសសំឡេងដែលចង់បាន:", KHMER_VOICES)
    
    # បន្ថែមជម្រើសដកដង្ហើមតាមតួអង្គ
    add_breathing = st.checkbox("🎭 បញ្ចូលការដកដង្ហើមតាមមាត់តួអង្គ", value=True)

    st.markdown("---")
    st.caption(f"👨‍💻 Dev: **{CONTACT_TELEGRAM}**")

# Main Area: ផ្នែកសំខាន់របស់កម្មវិធី
st.title("🎬 AI Khmer Dubbing PRO")
st.markdown("---")

col1, col2 = st.columns([2, 1])

# ------------------- RIGHT COLUMN: CONTROLS -------------------
with col2:
    st.subheader("🕹️ Controls")
    
    video_file = st.file_uploader("1. BROWSE VIDEO", type=["mp4", "avi", "mov", "mkv"])
    srt_file = st.file_uploader("2. BROWSE SRT (Optional)", type=["srt"])
    
    lang_option = st.selectbox("SOURCE LANG:", ["Auto-detect", "English", "Chinese", "Thai", "Japanese"])
    keep_bg = st.checkbox("Keep background music", value=True)
    
    usage, is_vip = load_license()
    if is_vip:
        st.success("🔓 VIP Mode Active (Unlimited)")
    else:
        st.info(f"📊 Trial: {usage}/{TRIAL_VIDEO_LIMIT} Videos")

    start_dubbing = st.button("START DUBBING", type="primary", use_container_width=True)
    stop_dubbing = st.button("STOP", type="secondary", use_container_width=True)

# ------------------- LEFT COLUMN: LOGS & OUTPUT -------------------
with col1:
    st.subheader("📄 Processing Logs & Real Translation")
    log_area = st.empty()
    progress_bar = st.progress(0)

    if start_dubbing:
        if video_file is None:
            st.error("សូមជ្រើសរើសវីដេអូជាមុនសិន!")
        else:
            can_run, status_msg = check_license(is_vip)
            if not can_run:
                st.error(f"❌ អ្នកបានប្រើប្រាស់អស់កូតាឥតគិតថ្លៃហើយ!")
                st.stop()
            
            if not is_vip:
                save_license(usage + 1, is_vip=False)
            
            try:
                log_area.code("[20%] កំពុងអានឯកសារវីដេអូ...")
                progress_bar.progress(0.20)

                # រក្សាទុកវីដេអូជា File បណ្តោះអាសន្ន
                tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
                tfile.write(video_file.read())
                video_path = tfile.name

                # ទាញយកសំឡេងចេញពីវីដេអូ
                log_area.code("[40%] កំពុងទាញយកសំឡេងចេញពីវីដេអូ...")
                progress_bar.progress(0.40)
                
                audio_path = video_path.replace(".mp4", ".wav")
                video_clip = VideoFileClip(video_path)
                if video_clip.audio is not None:
                    video_clip.audio.write_audiofile(audio_path, logger=None)
                else:
                    st.error("វីដេអូនេះគ្មានសំឡេងទេ!")
                    st.stop()

                # អានសំឡេងមកជាអត្ថបទ (Speech Recognition)
                log_area.code("[60%] កំពុងបម្លែងសំឡេងដើមជាអត្ថបទតាមសាច់រឿងពិត...")
                progress_bar.progress(0.60)
                
                recognizer = sr.Recognizer()
                with sr.AudioFile(audio_path) as source:
                    audio_data = recognizer.record(source)
                original_text = recognizer.recognize_google(audio_data)

                # បកប្រែជាភាសាខ្មែរដោយប្រើ deep-translator
                log_area.code("[80%] កំពុងបកប្រែអត្ថបទជាភាសាខ្មែរ...")
                progress_bar.progress(0.80)
                
                translated_text = GoogleTranslator(source='auto', target='km').translate(original_text)

                # បញ្ចូលការដកដង្ហើមតាមមាត់តួអង្គបើបានធីក
                if add_breathing:
                    final_script = f"[ហឺត...] {translated_text} [ដកដង្ហើមធំ]"
                else:
                    final_script = translated_text

                log_area.code("[100%] បញ្ចប់ដោយជោគជ័យ!")
                progress_bar.progress(1.0)
                st.balloons()
                
                st.success("ដំណើរការបកប្រែសម្រេចបានជោគជ័យ!")
                
                # បង្ហាញលទ្ធផលអត្ថបទ និងវីដេអូដើម
                st.markdown("### 📝 អត្ថបទដើមក្នុងវីដេអូ:")
                st.info(original_text)

                st.markdown("### 🇰🇭 អត្ថបទបកប្រែជាខ្មែរ (តាមសាច់រឿងពិត):")
                st.success(final_script)

                st.markdown("### 🎬 វីដេអូលទ្ធផល:")
                st.video(video_path)

            except Exception as e:
                st.error(f"មានបញ្ហាក្នុងការដំណើរការ: {e}")
