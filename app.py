import streamlit as st
import os
import json
import asyncio
import tempfile
import time
import whisper
from deep_translator import GoogleTranslator
from deep_translator.exceptions import TooManyRequests
import edge_tts
import subprocess

# ==========================================
# PAGE CONFIG & 3D ANIMATED BACKGROUND CSS
# ==========================================
st.set_page_config(page_title="AI Khmer Auto Dubber Pro", page_icon="🎬", layout="wide")

custom_bg_html = """
<style>
.stApp {
    background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #1a1c29);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
}

@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.area {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: -1;
    overflow: hidden;
    pointer-events: none;
}

.circles {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    margin: 0;
    padding: 0;
}

.circles li {
    position: absolute;
    display: block;
    list-style: none;
    width: 20px;
    height: 20px;
    background: rgba(255, 255, 255, 0.15);
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    backdrop-filter: blur(4px);
    border: 1px solid rgba(255, 255, 255, 0.18);
    animation: animate 25s linear infinite;
    bottom: -150px;
    border-radius: 50%;
}

.circles li:nth-child(1) { left: 25%; width: 80px; height: 80px; animation-delay: 0s; }
.circles li:nth-child(2) { left: 10%; width: 30px; height: 30px; animation-delay: 2s; animation-duration: 12s; }
.circles li:nth-child(3) { left: 70%; width: 40px; height: 40px; animation-delay: 4s; }
.circles li:nth-child(4) { left: 40%; width: 60px; height: 60px; animation-delay: 0s; animation-duration: 18s; }
.circles li:nth-child(5) { left: 65%; width: 20px; height: 20px; animation-delay: 0s; }
.circles li:nth-child(6) { left: 75%; width: 110px; height: 110px; animation-delay: 3s; }
.circles li:nth-child(7) { left: 35%; width: 150px; height: 150px; animation-delay: 7s; }
.circles li:nth-child(8) { left: 50%; width: 25px; height: 25px; animation-delay: 15s; animation-duration: 45s; }
.circles li:nth-child(9) { left: 20%; width: 15px; height: 15px; animation-delay: 2s; animation-duration: 35s; }
.circles li:nth-child(10) { left: 85%; width: 150px; height: 150px; animation-delay: 0s; animation-duration: 11s; }

@keyframes animate {
    0% { transform: translateY(0) rotate(0deg) scale(1); opacity: 1; border-radius: 50%; }
    50% { transform: translateY(-500px) rotate(360deg) scale(1.2); opacity: 0.6; border-radius: 40%; }
    100% { transform: translateY(-1000px) rotate(720deg) scale(0.8); opacity: 0; border-radius: 50%; }
}
</style>

<div class="area">
    <ul class="circles">
        <li></li><li></li><li></li><li></li><li></li>
        <li></li><li></li><li></li><li></li><li></li>
    </ul>
</div>
"""
st.markdown(custom_bg_html, unsafe_allow_html=True)


# ==========================================
# CONFIGURATION & VIP SYSTEM
# ==========================================
CONTACT_TELEGRAM = "@yoem bunyim"
TELEGRAM_LINK = "https://t.me/bunyimyoem"
TRIAL_VIDEO_LIMIT = 3
LICENSE_FILE = "license.json"

DEFAULT_VIP_CODES = ["VIP2026", "KHMER_DUB_VIP", "BUNYIM_PRO", "VIP8888"]

try:
    VALID_VIP_CODES = st.secrets.get("VIP_CODES", DEFAULT_VIP_CODES)
except Exception:
    VALID_VIP_CODES = DEFAULT_VIP_CODES


def load_license():
    if os.path.exists(LICENSE_FILE):
        try:
            with open(LICENSE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"usage_count": 0, "is_vip": False, "vip_code": ""}

def save_license(data):
    try:
        with open(LICENSE_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        st.error(f"មិនអាចរក្សាទុកព័ត៌មានអាជ្ញាបណ្ណបានទេ: {e}")

license_data = load_license()


# ==========================================
# TEXT-TO-SPEECH (EDGE TTS)
# ==========================================
async def generate_khmer_audio(text, output_file, voice="km-KH-SreymomNeural"):
    clean_text = text.strip() if text else ""
    if not clean_text:
        return False

    try:
        communicate = edge_tts.Communicate(clean_text, voice)
        await communicate.save(output_file)
        return True
    except Exception as e:
        return False

def text_to_speech_khmer(text, output_file, voice="km-KH-SreymomNeural"):
    return asyncio.run(generate_khmer_audio(text, output_file, voice))


# ==========================================
# UI INTERFACE
# ==========================================
st.title("🎬 AI Khmer Auto Dubber Pro")
st.caption("កម្មវិធីស្វ័យប្រវត្តិបកប្រែ និងបញ្ចូលសំឡេងវីដេអូជាភាសាខ្មែរ (សំឡេងប្រុស-ស្រីឆ្លើយឆ្លង & 3D Background)")

# --- SIDEBAR ---
st.sidebar.header("🔑 ប្រព័ន្ធអាជ្ញាបណ្ណ & VIP")
vip_input = st.sidebar.text_input("បញ្ចូលលេខកូដ VIP៖", value=license_data.get("vip_code", ""))
if st.sidebar.button("ផ្ទៀងផ្ទាត់ VIP"):
    if vip_input.strip() in VALID_VIP_CODES:
        license_data["is_vip"] = True
        license_data["vip_code"] = vip_input.strip()
        save_license(license_data)
        st.sidebar.success("🎉 បើកដំណើរការ VIP ជោគជ័យ!")
    else:
        st.sidebar.error("❌ លេខកូដ VIP មិនត្រឹមត្រូវទេ!")

if license_data.get("is_vip"):
    st.sidebar.info("🌟 ស្ថានភាព៖ **VIP Account**")
else:
    remaining = max(0, TRIAL_VIDEO_LIMIT - license_data.get("usage_count", 0))
    st.sidebar.warning(f"⏳ ស្ថានភាព៖ **Free Trial** (សល់ {remaining}/{TRIAL_VIDEO_LIMIT})")
    st.sidebar.markdown(f"📩 ទាក់ទងទិញកូដ VIP: [{CONTACT_TELEGRAM}]({TELEGRAM_LINK})")

st.sidebar.markdown("---")
st.sidebar.header("⚙️ ការកំណត់សំឡេង និង Model")
whisper_model_type = st.sidebar.selectbox("ជ្រើសរើស Whisper Model:", ["tiny", "base", "small", "medium"], index=1)

dub_mode = st.sidebar.selectbox(
    "ជម្រើសរបៀបបញ្ចូលសំឡេង:",
    [
        "សំឡេងស្រីសុទ្ធ (Sreymom)", 
        "សំឡេងប្រុសសុទ្ធ (Piseth)", 
        "ប្រុសស្រីឆ្លើយឆ្លងគ្នាស្វ័យប្រវត្តិ (Multi-Speaker)"
    ]
)


# ==========================================
# PROCESSING
# ==========================================
uploaded_file = st.file_uploader("បញ្ចូលវីដេអូរបស់អ្នក (.mp4, .mov, .avi):", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    if not license_data.get("is_vip" ) and license_data.get("usage_count", 0) >= TRIAL_VIDEO_LIMIT:
        st.error("⚠️ អស់ចំនួនដងសាកល្បង Free Trial ហើយ! សូមបញ្ចូលលេខកូដ VIP។")
    else:
        st.video(uploaded_file)
        
        if st.button("🚀 ចាប់ផ្តើមបញ្ចូលសំឡេងខ្មែរ (ឆ្លើយឆ្លងតួអង្គ)"):
            with st.spinner("កំពុងដំណើរការវិភាគ និងបកប្រែសំឡេងតួអង្គ..."):
                with tempfile.TemporaryDirectory() as temp_dir:
                    input_video_path = os.path.join(temp_dir, "input_video.mp4")
                    with open(input_video_path, "wb") as f:
                        f.write(uploaded_file.read())

                    # ១. Whisper Transcription with Segments
                    st.info("🎙️ កំពុងទាញយកកាលបរិច្ឆេទ និងឃ្លាប្រយោគពីវីដេអូ...")
                    model = whisper.load_model(whisper_model_type)
                    result = model.transcribe(input_video_path, word_timestamps=False)
                    segments = result.get("segments", [])

                    if not segments:
                        st.error("⚠️ រកមិនឃើញឃ្លាប្រយោគនិយាយក្នុងវីដេអូនេះទេ។")
                    else:
                        translator = GoogleTranslator(source='auto', target='km')
                        audio_segments = []
                        
                        st.info("🔄 កំពុងបកប្រែ និងបែងចែកសំឡេងប្រុសស្រីតាមប្រយោគ...")
                        
                        for i, seg in enumerate(segments):
                            original_text = seg.get("text", "").strip()
                            if not original_text:
                                continue
                            
                            try:
                                translated = translator.translate(original_text)
                                time.sleep(0.3) # ကာለការពារ TooManyRequests
                            except Exception:
                                translated = original_text

                            # កំណត់សំឡេងប្រុស ឬ ស្រី តាមការជ្រើសរើស ឬឆ្លើយឆ្លងគ្នាតាមលំដាប់ (Segment គូ/សេស)
                            if "ប្រុសស្រីឆ្លើយឆ្លង" in dub_mode:
                                chosen_voice = "km-KH-SreymomNeural" if i % 2 == 0 else "km-KH-PisethNeural"
                            elif "ប្រុសសុទ្ធ" in dub_mode:
                                chosen_voice = "km-KH-PisethNeural"
                            else:
                                chosen_voice = "km-KH-SreymomNeural"

                            seg_audio_path = os.path.join(temp_dir, f"seg_{i}.mp3")
                            success = text_to_speech_khmer(translated, seg_audio_path, voice=chosen_voice)
                            
                            if success and os.path.exists(seg_audio_path):
                                audio_segments.append((seg_audio_path, seg.get("start", 0)))

                        if audio_segments:
                            # បង្កើតឯកសារລាយបញ្ជីសម្រាប់ FFmpeg Concatenation & Mixing
                            list_file_path = os.path.join(temp_dir, "playlist.txt")
                            
                            # វិធីសាស្ត្របញ្ចូលសំឡេងសរុบ ឬលាយចូលគ្នា
                            combined_audio_path = os.path.join(temp_dir, "final_khmer_dub.mp3")
                            
                            # ប្រើប្រាស់ FFmpeg ដើម្បី Mix សំឡេងបញ្ចូលគ្នាតាមពេលវេលា (Timestamps)
                            # បង្កើត Audio Track ពេញលេញ
                            inputs = []
                            filter_complex_parts = []
                            
                            for idx, (aud_path, start_time) in enumerate(audio_segments):
                                inputs.extend(["-i", aud_path])
                                delay_ms = int(start_time * 1000)
                                filter_complex_parts.append(f"[{idx}:a]adelay={delay_ms}|{delay_ms}[a{idx}]")
                            
                            mix_inputs = "".join([f"[a{i}]" for i in range(len(audio_segments))])
                            filter_complex = ";".join(filter_complex_parts) + f";{mix_inputs}amix=inputs={len(audio_segments)}:duration=longest[outa]"
                            
                            ffmpeg_cmd = ["ffmpeg"] + inputs + ["-filter_complex", filter_complex, "-map", "[outa]", combined_audio_path, "-y"]
                            
                            try:
                                subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                
                                if os.path.exists(combined_audio_path):
                                    st.audio(combined_audio_path)
                                    st.success("✨ បង្កើតសំឡេងប្រុសស្រីឆ្លើយឆ្លងគ្នារួចរាល់ជាជោគជ័យ!")

                                    if not license_data.get("is_vip"):
                                        license_data["usage_count"] = license_data.get("usage_count", 0) + 1
                                        save_license(license_data)
                                else:
                                    st.error("⚠️ កំហុសក្នុងការកែច្នៃសំឡេងតាម FFmpeg។")
                            except Exception as ffmpeg_err:
                                st.error(f"⚠️ រកមិនឃើញ FFmpeg ឬមានបញ្ហាពេលបញ្ចូលសំឡេង៖ {ffmpeg_err}")
                        else:
                            st.error("⚠️ មិនអាចបង្កើតសំឡេងសម្រាប់វីដេអូនេះបានទេ។")
