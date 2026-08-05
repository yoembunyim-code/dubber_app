import json
import os
import time
import asyncio
import tempfile
from datetime import datetime, timedelta
import streamlit as st

# 🛡️ Safe MoviePy Import (ការពារ Version Error)
try:
    from moviepy.editor import VideoFileClip, AudioFileClip
except Exception:
    from moviepy import VideoFileClip, AudioFileClip

import edge_tts
from deep_translator import GoogleTranslator

# ==============================================================================
# ⚙️ DEVELOPER CONFIGURATIONS
# ==============================================================================
TELEGRAM_USERNAME = "@YOUR_TELEGRAM"  # ✍️ ផ្លាស់ប្តូរឈ្មោះ Telegram របស់អ្នក
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
# 🎙️ REAL AI DUBBING FUNCTION
# ==============================================================================
def dub_video(video_bytes, voice_code, voice_speed, input_text):
    """មុខងារបង្កើតសំឡេង AI និងកាត់បញ្ចូលក្នុងវីដេអូ"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as f_in:
        f_in.write(video_bytes)
        in_vdo_path = f_in.name

    audio_path = in_vdo_path.replace(".mp4", "_audio.mp3")
    out_vdo_path = in_vdo_path.replace(".mp4", "_out.mp4")

    try:
        # ១. បកប្រែអត្ថបទជាភាសាខ្មែរ
        translated_text = input_text
        if input_text and input_text.strip():
            try:
                translated_text = GoogleTranslator(source='auto', target='km').translate(input_text.strip())
            except Exception:
                translated_text = input_text.strip()
        
        if not translated_text:
            translated_text = "សួស្តី"

        # ២. បង្កើតសំឡេង AI ខ្មែរ (Edge TTS)
        rate_str = f"{int((voice_speed - 1.0) * 100):+d}%"
        communicate = edge_tts.Communicate(translated_text, voice_code, rate=rate_str)
        asyncio.run(communicate.save(audio_path))

        # ៣. កាត់បញ្ចូលសំឡេងទៅក្នុងវីដេអូ
        video = VideoFileClip(in_vdo_path)
        audio = AudioFileClip(audio_path)
        
        final_video = video.set_audio(audio)
        final_video.write_videofile(out_vdo_path, codec="libx264", audio_codec="aac", logger=None)

        with open(out_vdo_path, "rb") as f:
            result_bytes = f.read()

        video.close()
        audio.close()
        
        # លុបឯកសារបណ្តោះអាសន្ន
        for p in [in_vdo_path, audio_path, out_vdo_path]:
            if os.path.exists(p):
                try: os.remove(p)
                except Exception: pass

        return result_bytes, translated_text
    except Exception as e:
        st.error(f"កំហុសក្នុងការបកប្រែ៖ {e}")
        for p in [in_vdo_path, audio_path, out_vdo_path]:
            if os.path.exists(p):
                try: os.remove(p)
                except Exception: pass
        return None, ""


# ==============================================================================
# 🛡️ LICENSE SYSTEM
# ==============================================================================
def load_license():
    default = {"license_key": "", "activated": False, "expiry_date": "", "trial_used": 0}
    if not os.path.exists(LICENSE_FILE): return default
    try:
        with open(LICENSE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def save_license(data):
    try:
        with open(LICENSE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception:
        pass

def activate_vip(code):
    if code.strip() in VALID_VIP_CODES:
        data = load_license()
        data["license_key"] = code
        data["activated"] = True
        data["expiry_date"] = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
        save_license(data)
        return True, "🎉 Activate VIP ជោគជ័យ!"
    return False, "Code មិនត្រឹមត្រូវទេ!"


# ==============================================================================
# 🌐 STREAMLIT GUI INTERFACE
# ==============================================================================
st.set_page_config(page_title="Khmer Dubber Studio", page_icon="🎙️", layout="centered")

if "lic" not in st.session_state: st.session_state.lic = load_license()
if "vdo" not in st.session_state: st.session_state.vdo = None
if "txt" not in st.session_state: st.session_state.txt = ""

lic = st.session_state.lic
is_vip = lic.get("activated", False)
rem_trials = max(0, TRIAL_LIMIT - lic.get("trial_used", 0))

st.title("🎙️ KHMER VIDEO DUBBER STUDIO")

# 🔑 VIP Activation Panel
with st.expander("🔑 VIP Activation Panel", expanded=not is_vip):
    col1, col2 = st.columns([3, 1])
    code_in = col1.text_input("VIP Code", placeholder="បញ្ចូលលេខកូដ VIP...", label_visibility="collapsed")
    if col2.button("Activate", type="primary", use_container_width=True):
        ok, msg = activate_vip(code_in)
        if ok:
            st.session_state.lic = load_license()
            st.success(msg)
            time.sleep(1)
            st.rerun()
        else:
            st.error(msg)

# Status Badge
if is_vip:
    st.success("ស្ថានភាព៖ VIP Activated ✅ (ប្រើបានគ្មានដែនកំណត់)")
elif rem_trials > 0:
    st.warning(f"ស្ថានភាព៖ Trial Version ⏳ (នៅសល់ {rem_trials}/{TRIAL_LIMIT} វីដេអូ)")
else:
    st.error(f"ស្ថានភាព៖ Trial Expired 🚫 (សូមទាក់ទង {TELEGRAM_USERNAME})")

st.markdown("---")

# Input Settings
uploaded_vdo = st.file_uploader("១. បញ្ចូលវីដេអូ (MP4/MOV)", type=["mp4", "mov", "mkv", "avi"])
input_script = st.text_area("២. បញ្ចូលអត្ថបទដែលត្រូវបកប្រែ និងនិយាយជាខ្មែរ៖", value="សួស្តី! នេះគឺជាវីដេអូដែលបានបញ្ចូលសំឡេងបកប្រែជាភាសាខ្មែរ។")

col_a, col_b = st.columns(2)
with col_a:
    selected_voice_tuple = st.selectbox(
        "សំឡេង AI:",
        options=[
            ("km-KH-PisethNeural", "🇰🇭 សំឡេងប្រុស (ពិសិដ្ឋ)"),
            ("km-KH-SreymomNeural", "🇰🇭 សំឡេងស្រី (ស្រីមុំ)")
        ],
        format_func=lambda x: x[1]
    )
    voice_code = selected_voice_tuple[0]

with col_b:
    voice_speed = st.slider("ល្បឿននិយាយ:", 0.8, 1.3, 1.0, 0.1)

st.markdown("---")

# Dubbing Action Button
can_run = is_vip or (rem_trials > 0)
if st.button("▶ ចាប់ផ្តើមបកប្រែ និងបញ្ចូលសំឡេង", disabled=not can_run, type="primary", use_container_width=True):
    if not uploaded_vdo:
        st.warning("សូម Upload វីដេអូជាមុនសិន!")
    else:
        with st.spinner("🤖 កំពុងដំណើរការបកប្រែ និងបញ្ចូលសំឡេង AI..."):
            res, txt = dub_video(
                video_bytes=uploaded_vdo.getvalue(),
                voice_code=voice_code,
                voice_speed=voice_speed,
                input_text=input_script
            )
            if res:
                st.session_state.vdo = res
                st.session_state.txt = txt
                if not is_vip:
                    lic["trial_used"] += 1
                    save_license(lic)
                    st.session_state.lic = lic
                st.success("✅ រួចរាល់ 100%!")
                time.sleep(0.5)
                st.rerun()

# Output Display & Download
if st.session_state.vdo:
    st.markdown("---")
    st.subheader("🎉 លទ្ធផលវីដេអូដែលធ្វើរួច៖")
    if st.session_state.txt:
        st.info(f"📝 **អត្ថបទបកប្រែខ្មែរ៖** {st.session_state.txt}")
    
    st.video(st.session_state.vdo)
    st.download_button(
        label="📥 ទាញយកវីដេអូទុក (Download Video)",
        data=st.session_state.vdo,
        file_name="dubbed_video.mp4",
        mime="video/mp4",
        use_container_width=True
    )
