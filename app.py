import json
import os
import time
import asyncio
import tempfile
from datetime import datetime, timedelta
import streamlit as st

# 🛡️ Protección MoviePy Version Import
try:
    from moviepy.editor import VideoFileClip, AudioFileClip
except (ModuleNotFoundError, ImportError):
    from moviepy import VideoFileClip, AudioFileClip

import edge_tts
from deep_translator import GoogleTranslator
import speech_recognition as sr

# ==============================================================================
# ⚙️ កន្លែងកំណត់ទិន្នន័យ (DEVELOPER CONFIGURATIONS)
# ==============================================================================
TELEGRAM_USERNAME = "@YOUR_TELEGRAM"  # ✍️ ផ្លាស់ប្តូរឈ្មោះ Telegram របស់អ្នកនៅទីនេះ
TELEGRAM_LINK = f"https://t.me/{TELEGRAM_USERNAME.replace('@', '')}"

VALID_VIP_CODES = [
    "VIP-SECRET-2026",
    "VIP-PASS-8888",
    "VIP-PRO-9999",
    "CAM-VIP-1234"
]

TRIAL_LIMIT = 3
LICENSE_FILE = "license.json"


# ==============================================================================
# 🎙️ AUTO SPEECH RECOGNITION & TRANSLATION ENGINE
# ==============================================================================
def extract_and_translate_audio(video_path):
    """ស្តាប់សំឡេងដើមក្នុងវីដេអូ រួចបកប្រែជាភាសាខ្មែរ"""
    try:
        temp_wav = video_path.replace(".mp4", "_temp.wav")
        video = VideoFileClip(video_path)
        
        if video.audio is None:
            video.close()
            return "ជម្រាបសួរ! វីដេអូនេះគ្មានសំឡេងដើមទេ។"

        # ទាញយកសំឡេងជា WAV
        video.audio.write_audiofile(temp_wav, codec='pcm_s16le', fps=16000, logger=None)
        video.close()

        # ស្គាល់សំឡេងនិយាយ (Speech to Text)
        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_wav) as source:
            audio_data = recognizer.record(source)
            try:
                original_text = recognizer.recognize_google(audio_data)
            except Exception:
                original_text = ""

        if os.path.exists(temp_wav):
            os.remove(temp_wav)

        if original_text:
            # បកប្រែអត្ថបទទៅជាភាសាខ្មែរ
            translator = GoogleTranslator(source='auto', target='km')
            translated_khmer = translator.translate(original_text)
            return translated_khmer
        else:
            return "ជម្រាបសួរ! នេះគឺជាវីដេអូដែលបានបញ្ចូលសំឡេងបកប្រែជាភាសាខ្មែរ។"
    except Exception:
        return "ជម្រាបសួរ! នេះគឺជាវីដេអូដែលបានបញ្ចូលសំឡេងបកប្រែជាភាសាខ្មែរ។"

async def generate_khmer_audio(text, voice_code, output_audio_path, rate=1.0):
    """បង្កើតសំឡេង AI ខ្មែរ"""
    rate_str = f"{int((rate - 1.0) * 100):+d}%"
    communicate = edge_tts.Communicate(text, voice_code, rate=rate_str)
    await communicate.save(output_audio_path)

def process_video_dubbing(video_bytes, voice_model_key, voice_speed, custom_text=""):
    """ដំណើរការបកប្រែ និងបញ្ចូលសំឡេងក្នុងវីដេអូ"""
    voice_map = {
        "kh_male": "km-KH-PisethNeural",     # សំឡេងប្រុស (ពិសិដ្ឋ)
        "kh_female": "km-KH-SreymomNeural",  # សំឡេងស្រី (ស្រីមុំ)
        "en_male": "en-US-ChristopherNeural",
        "en_female": "en-US-AvaNeural"
    }
    selected_voice = voice_map.get(voice_model_key, "km-KH-PisethNeural")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_in_video:
        temp_in_video.write(video_bytes)
        input_video_path = temp_in_video.name

    output_audio_path = input_video_path.replace(".mp4", "_khmer.mp3")
    output_video_path = input_video_path.replace(".mp4", "_dubbed.mp4")

    try:
        # ១. ប្រសិនបើមិនបានវាយអក្សរផ្ទាល់ខ្លួនទេ កម្មវិធីនឹងស្តាប់សំឡេងក្នុងវីដេអូដើម្បីបកប្រែស្វ័យប្រវត្តិ
        if custom_text and custom_text.strip():
            text_to_dub = custom_text.strip()
        else:
            text_to_dub = extract_and_translate_audio(input_video_path)

        # ២. បង្កើតសំឡេង AI
        asyncio.run(generate_khmer_audio(text_to_dub, selected_voice, output_audio_path, rate=voice_speed))

        # ៣. កាត់បញ្ចូលសំឡេងថ្មីទៅក្នុងវីដេអូ
        video_clip = VideoFileClip(input_video_path)
        new_audio = AudioFileClip(output_audio_path)

        final_video = video_clip.set_audio(new_audio)
        final_video.write_videofile(output_video_path, codec="libx264", audio_codec="aac", logger=None)

        with open(output_video_path, "rb") as f:
            dubbed_bytes = f.read()

        video_clip.close()
        new_audio.close()
        if os.path.exists(input_video_path): os.remove(input_video_path)
        if os.path.exists(output_audio_path): os.remove(output_audio_path)
        if os.path.exists(output_video_path): os.remove(output_video_path)

        return dubbed_bytes, text_to_dub
    except Exception as e:
        st.error(f"មានបញ្ហាក្នុងការបកប្រែវីដេអូ៖ {e}")
        return None, ""


# ==============================================================================
# 🛡️ LICENSE MANAGEMENT FUNCTIONS
# ==============================================================================
def load_license():
    default_data = {"license_key": "", "activated": False, "activation_date": "", "expiry_date": "", "trial_used": 0}
    if not os.path.exists(LICENSE_FILE):
        return default_data
    try:
        with open(LICENSE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            data.setdefault("trial_used", 0)
            return data
    except Exception:
        return default_data

def save_license(data):
    try:
        with open(LICENSE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception:
        return False

def activate_vip(code):
    code = code.strip()
    if not code:
        return False, "សូមបញ្ចូល Activation Code!"
    if code in VALID_VIP_CODES:
        data = load_license()
        now = datetime.now()
        data["license_key"] = code
        data["activated"] = True
        data["activation_date"] = now.strftime("%Y-%m-%d")
        data["expiry_date"] = (now + timedelta(days=365)).strftime("%Y-%m-%d")
        save_license(data)
        return True, "🎉 Activation ជោគជ័យ! កម្មវិធីរបស់អ្នកត្រូវបានដោះសោ VIP រួចរាល់។"
    else:
        return False, "Activation Code មិនត្រឹមត្រូវទេ (Invalid Code)!"


# ==============================================================================
# 🌐 STREAMLIT GUI INTERFACE
# ==============================================================================
st.set_page_config(page_title="Khmer Dubber - VIP System", page_icon="🎙️", layout="centered")

if "license_data" not in st.session_state:
    st.session_state.license_data = load_license()
if "processed_video" not in st.session_state:
    st.session_state.processed_video = None
if "processed_file_name" not in st.session_state:
    st.session_state.processed_file_name = ""
if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""

lic_data = st.session_state.license_data
is_vip = lic_data.get("activated", False)
used_trials = lic_data.get("trial_used", 0)
remaining_trials = max(0, TRIAL_LIMIT - used_trials)

st.markdown("<h1 style='text-align: center;'>🎙️ KHMER VIDEO DUBBER STUDIO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>ប្រព័ន្ធបកប្រែ និងបញ្ចូលសំឡេងខ្មែរស្វ័យប្រវត្តិ</p>", unsafe_allow_html=True)

# 🔑 VIP Activation Panel
st.subheader("🔑 VIP Activation Panel")
col_input, col_btn = st.columns([3, 1])
with col_input:
    user_code = st.text_input("Activation Code:", placeholder="បញ្ចូលលេខកូដ VIP...", key="vip_code_input", label_visibility="collapsed")
with col_btn:
    if st.button("Activate VIP 🚀", type="primary", use_container_width=True):
        success, msg = activate_vip(user_code)
        if success:
            st.session_state.license_data = load_license()
            st.success(msg)
            time.sleep(1)
            st.rerun()
        else:
            st.error(msg)

c1, c2, c3 = st.columns([2, 1.5, 1.5])
with c1:
    if is_vip:
        st.success("ស្ថានភាព៖ VIP Activated ✅")
    elif remaining_trials > 0:
        st.warning("ស្ថានភាព៖ Trial Version ⏳")
    else:
        st.error("ស្ថានភាព៖ Trial Expired 🚫")
with c2:
    if st.button("📋 Check License", use_container_width=True):
        if is_vip:
            st.info(f"**Key:** `{lic_data.get('license_key')}` | **Expires:** {lic_data.get('expiry_date')}")
        else:
            st.warning(f"ប្រើប្រាស់៖ {used_trials}/{TRIAL_LIMIT} វីដេអូ")
with c3:
    st.link_button("🛒 ទិញ VIP Code", TELEGRAM_LINK, use_container_width=True)

st.markdown("---")

# 🎙️ Voice & Video Settings
st.subheader("🎙️ ការកំណត់សំឡេង និងវីដេអូ")
uploaded_file = st.file_uploader("១. បញ្ចូលវីដេអូរបស់អ្នក (MP4, MOV)", type=["mp4", "mov", "mkv"])

custom_text = st.text_area(
    "២. (ជម្រើសបន្ថែម) បញ្ចូលអក្សរផ្ទាល់ខ្លួន ប្រសិនបើមិនចង់ឱ្យ AI បកប្រែសំឡេងដើមដោយស្វ័យប្រវត្តិ៖",
    placeholder="ទុកកន្លែងនេះឱ្យទំនេរ ប្រសិនបើចង់ឱ្យ AI ស្តាប់សំឡេងដើមក្នុងវីដេអូ រួចបកប្រែជាខ្មែរដោយស្វ័យប្រវត្តិ..."
)

col_v1, col_v2 = st.columns(2)
with col_v1:
    voice_choice = st.selectbox(
        "ជ្រើសរើសសំឡេង AI (Voice):",
        options=[
            ("kh_male", "🇰🇭 សំឡេងខ្មែរ (ប្រុស) - ពិសិដ្ឋ"),
            ("kh_female", "🇰🇭 សំឡេងខ្មែរ (ស្រី) - ស្រីមុំ"),
            ("en_male", "🇺🇸 English Male"),
            ("en_female", "🇺🇸 English Female")
        ],
        format_func=lambda x: x[1]
    )
with col_v2:
    voice_speed = st.slider("ល្បឿននិយាយ (Speed):", 0.7, 1.5, 1.0, 0.1)

st.markdown("---")

# ▶ Dubbing Process
st.subheader("▶ ដំណើរការបកប្រែ & បញ្ចូលសំឡេង")

if is_vip:
    st.success("🎉 អ្នកកំពុងប្រើប្រាស់ VIP Mode (Unlimited)")
elif remaining_trials > 0:
    st.info(f"⚠️ កំពុងប្រើ Trial Version (នៅសល់៖ {remaining_trials}/{TRIAL_LIMIT} វីដេអូ)")
else:
    st.error(f"🚫 អស់សិទ្ធិសាកល្បង! សូមទាក់ទង Telegram៖ {TELEGRAM_USERNAME}")

start_disabled = (not is_vip) and (remaining_trials <= 0)

if st.button("▶ ចាប់ផ្តើមបកប្រែ និងបញ្ចូលសំឡេង (Start Dubbing)", disabled=start_disabled, type="primary", use_container_width=True):
    if not uploaded_file:
        st.warning("សូមបញ្ចូលវីដេអូ (Upload) ជាមុនសិន!")
    else:
        with st.spinner("🤖 កំពុងស្តាប់សំឡេងដើម បកប្រែជាខ្មែរ និងកាត់បញ្ចូលសំឡេង AI ទៅក្នុងវីដេអូ..."):
            result_bytes, translated_text = process_video_dubbing(
                uploaded_file.getvalue(),
                voice_choice[0],
                voice_speed,
                custom_text
            )
            
            if result_bytes:
                st.session_state.processed_video = result_bytes
                st.session_state.processed_file_name = f"khmer_dubbed_{uploaded_file.name}"
                st.session_state.translated_text = translated_text
                
                if not is_vip:
                    lic_data["trial_used"] += 1
                    save_license(lic_data)
                    st.session_state.license_data = lic_data

                st.success("✅ បកប្រែ និងបញ្ចូលសំឡេងខ្មែរក្នុងវីដេអូរួចរាល់ 100%!")
                time.sleep(0.5)
                st.rerun()

# 📺 Result Display
if st.session_state.processed_video is not None:
    st.markdown("---")
    st.subheader("🎉 លទ្ធផលវីដេអូដែលបានបញ្ចូលសំឡេងខ្មែររួច៖")
    if st.session_state.translated_text:
        st.info(f"📝 **អត្ថបទដែលបានបកប្រែជាខ្មែរ៖** {st.session_state.translated_text}")
        
    st.video(st.session_state.processed_video)
    
    st.download_button(
        label="📥 ទាញយកវីដេអូដែលបកប្រែរួច (Download Dubbed Video)",
        data=st.session_state.processed_video,
        file_name=st.session_state.processed_file_name,
        mime="video/mp4",
        use_container_width=True
    )
