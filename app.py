import json
import os
import time
import asyncio
import tempfile
import streamlit as st

# Safe Import for MoviePy
try:
    from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip
except Exception:
    from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip

import edge_tts
from deep_translator import GoogleTranslator

# ==============================================================================
# ⚙️ CONFIGURATION & VIP SYSTEM
# ==============================================================================
TELEGRAM_USERNAME = "bunyim"
VALID_VIP_CODES = [
    "VIP-SECRET-2026",
    "VIP-PASS-8888",
    "VIP-PRO-9999",
    "CAM-VIP-1234"
]

TRIAL_LIMIT = 3
LICENSE_FILE = "license.json"

clean_telegram = TELEGRAM_USERNAME.replace("@", "").strip()
TELEGRAM_LINK = f"https://t.me/{clean_telegram}"

def load_license():
    default = {"license_key": "", "activated": False, "expiry_date": "", "trial_used": 0}
    if not os.path.exists(LICENSE_FILE):
        return default
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
        save_license(data)
        return True, "🎉 បើកប្រើប្រាស់ VIP ជោគជ័យ!"
    return False, "⚠️ VIP Code មិនត្រឹមត្រូវទេ!"

def generate_tts_audio(text, voice_code, output_path):
    communicate = edge_tts.Communicate(text, voice_code)
    asyncio.run(communicate.save(output_path))

def process_simple_dubbing(video_bytes, voice_code):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as f_in:
        f_in.write(video_bytes)
        in_vdo_path = f_in.name

    out_vdo_path = in_vdo_path.replace(".mp4", "_out.mp4")

    try:
        video = VideoFileClip(in_vdo_path)
        
        # កាត់សំឡេងដើមចេញទាំងស្រុង យកតែវីដេអូស្អាត
        video_clean = video.without_audio()

        sample_text = "សូមស្វាគមន៍មកកាន់ប្រព័ន្ធបញ្ចូលសំឡេង AI ខ្មែរដោយស្វ័យប្រវត្តិ។ លុបសំឡេងរំខាន ១០០ភាគរយ។"
        
        seg_audio_path = in_vdo_path.replace(".mp4", "_ai.mp3")
        generate_tts_audio(sample_text, voice_code, seg_audio_path)

        # ប្រើ with_start ជំនួស set_start សម្រាប់ MoviePy ជំនាន់ថ្មី
        ai_audio = AudioFileClip(seg_audio_path).with_start(0)
        
        final_video = video_clean.with_audio(ai_audio)
        final_video.write_videofile(out_vdo_path, codec="libx264", audio_codec="aac", logger=None)

        with open(out_vdo_path, "rb") as f:
            result_bytes = f.read()

        video.close()
        final_video.close()

        return result_bytes, sample_text

    except Exception as e:
        st.error(f"⚠️ មានបញ្ហា៖ {e}")
        return None, ""

# ==============================================================================
# 🌐 UI INTERFACE
# ==============================================================================
st.set_page_config(page_title="Khmer AI Dubber", page_icon="🎙️", layout="centered")

if "lic" not in st.session_state:
    st.session_state.lic = load_license()
if "vdo" not in st.session_state:
    st.session_state.vdo = None
if "txt" not in st.session_state:
    st.session_state.txt = ""

lic = st.session_state.lic
is_vip = lic.get("activated", False)
rem_trials = max(0, TRIAL_LIMIT - lic.get("trial_used", 0))

st.title("🎙️ KHMER AI PURE DUBBER")
st.caption("ប្រព័ន្ធលុបសំឡេងរំខាន និងដាក់សំឡេង AI ខ្មែរសុទ្ធ ១០០%")

st.link_button("💬 ទាក់ទង Admin តាម Telegram", TELEGRAM_LINK, use_container_width=True)

with st.expander("🔑 បញ្ចូល VIP Code", expanded=not is_vip):
    col1, col2 = st.columns([3, 1])
    code_in = col1.text_input("VIP Code", placeholder="លេខកូដ...", label_visibility="collapsed")
    if col2.button("Activate", type="primary", use_container_width=True):
        ok, msg = activate_vip(code_in)
        if ok:
            st.session_state.lic = load_license()
            st.success(msg)
            time.sleep(1)
            st.rerun()
        else:
            st.error(msg)

uploaded_vdo = st.file_uploader("១. បញ្ចូលវីដេអូ (MP4)", type=["mp4", "mov"])
selected_voice = st.selectbox("២. ជ្រើសរើសសំឡេង៖", [("km-KH-PisethNeural", "🇰🇭 ពិសិដ្ឋ (ប្រុស)"), ("km-KH-SreymomNeural", "🇰🇭 ស្រីមុំ (ស្រី)")], format_func=lambda x: x[1])

can_run = is_vip or (rem_trials > 0)

if st.button("▶ ចាប់ផ្តើមលុបកំចាត់សំឡេង (Process Video)", disabled=not can_run, type="primary", use_container_width=True):
    if not uploaded_vdo:
        st.warning("សូមដាក់វីដេអូសិន!")
    else:
        with st.spinner("🤖 កំពុងកាត់សំឡេងរំខាន និងបញ្ចូលសំឡេង AI..."):
            res_video, script = process_simple_dubbing(uploaded_vdo.getvalue(), selected_voice[0])
            if res_video:
                st.session_state.vdo = res_video
                st.session_state.txt = script
                if not is_vip:
                    lic["trial_used"] += 1
                    save_license(lic)
                    st.session_state.lic = lic
                st.success("✅ រួចរាល់!")
                time.sleep(0.5)
                st.rerun()

if st.session_state.vdo:
    st.markdown("---")
    st.video(st.session_state.vdo)
    st.download_button("📥 ទាញយកវីដេអូ", data=st.session_state.vdo, file_name="dubbed.mp4", mime="video/mp4", use_container_width=True)
