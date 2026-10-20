import streamlit as st
import os
import json
import asyncio
import tempfile
import time
import whisper
from deep_translator import GoogleTranslator
import edge_tts

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
# STABLE TEXT-TO-SPEECH (EDGE TTS) FUNCTION
# ==========================================
async def generate_khmer_audio_stable(text, output_file, voice="km-KH-SreymomNeural"):
    clean_text = text.strip() if text else ""
    if not clean_text:
        return False

    try:
        # កាត់អត្ថបទវែងៗជាកំណាត់ៗ (Max 300 characters per chunk) ដើម្បីការពារ Edge TTS Error
        chunk_size = 300
        chunks = [clean_text[i:i+chunk_size] for i in range(0, len(clean_text), chunk_size)]
        
        temp_files = []
        for idx, chunk in enumerate(chunks):
            if not chunk.strip():
                continue
            part_file = f"{output_file}_part_{idx}.mp3"
            communicate = edge_tts.Communicate(chunk, voice)
            await communicate.save(part_file)
            temp_files.append(part_file)

        # បញ្ចូលဖាំយសំឡេងតូចៗទាំងនោះបញ្ចូលគ្នាជាឯកសារចុងក្រោយ
        with open(output_file, 'wb') as outfile:
            for f_name in temp_files:
                if os.path.exists(f_name):
                    with open(f_name, 'rb') as infile:
                        outfile.write(infile.read())
                    os.remove(f_name)

        return os.path.exists(output_file) and os.path.getsize(output_file) > 0
    except Exception as e:
        st.error(f"កំហុស TTS: {e}")
        return False

def text_to_speech_khmer(text, output_file, voice="km-KH-SreymomNeural"):
    return asyncio.run(generate_khmer_audio_stable(text, output_file, voice))


# ==========================================
# UI INTERFACE
# ==========================================
st.title("🎬 AI Khmer Auto Dubber Pro")
st.caption("កម្មវិធីស្វ័យប្រវត្តិបកប្រែ និងបញ្ចូលសំឡេងវីដេអូជាភាសាខ្មែរ (មានសំឡេងប្រុស-ស្រី & 3D Background)")

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
    if not license_data.get("is_vip") and license_data.get("usage_count", 0) >= TRIAL_VIDEO_LIMIT:
        st.error("⚠️ អស់ចំនួនដងសាកល្បង Free Trial ហើយ! សូមបញ្ចូលលេខកូដ VIP។")
    else:
        st.video(uploaded_file)
        
        if st.button("🚀 ចាប់ផ្តើមបញ្ចូលសំឡេងខ្មែរ"):
            with st.spinner("កំពុងដំណើរការវិភាគ បកប្រែ និងបង្កើតសំឡេង (សូមរង់ចាំបន្តិច)..."):
                with tempfile.TemporaryDirectory() as temp_dir:
                    input_video_path = os.path.join(temp_dir, "input_video.mp4")
                    with open(input_video_path, "wb") as f:
                        f.write(uploaded_file.read())

                    # ១. Whisper Transcription
                    st.info("🎙️ កំពុងទាញយកអត្ថបទនិយាយចេញពីវីដេអូ...")
                    model = whisper.load_model(whisper_model_type)
                    result = model.transcribe(input_video_path)
                    full_text = result.get("text", "").strip()

                    if not full_text:
                        st.error("⚠️ រកមិនឃើញសំឡេងនិយាយក្នុងវីដេអូនេះទេ។")
                    else:
                        st.write("**អត្ថបទដើមដែលទាញបាន៖**", full_text)

                        # ២. Translation
                        st.info("🌐 កំពុងបកប្រែជាភាសាខ្មែរ...")
                        translated_text = ""
                        try:
                            translator = GoogleTranslator(source='auto', target='km')
                            if len(full_text) > 300:
                                chunks = [full_text[i:i+300] for i in range(0, len(full_text), 300)]
                                translated_chunks = []
                                for chunk in chunks:
                                    translated_chunks.append(translator.translate(chunk))
                                    time.sleep(0.3)
                                translated_text = " ".join(translated_chunks)
                            else:
                                translated_text = translator.translate(full_text)
                        except Exception:
                            translated_text = full_text

                        if translated_text:
                            st.write("**អត្ថបទបកប្រែជាភាសាខ្មែរ៖**", translated_text)

                            # ៣. Stable Text-to-Speech Generation
                            output_audio_path = os.path.join(temp_dir, "khmer_audio.mp3")
                            
                            if "ប្រុសស្រីឆ្លើយឆ្លង" in dub_mode:
                                chosen_voice = "km-KH-SreymomNeural"
                            elif "ប្រុសសុទ្ធ" in dub_mode:
                                chosen_voice = "km-KH-PisethNeural"
                            else:
                                chosen_voice = "km-KH-SreymomNeural"

                            st.info(f"🔊 កំពុងបង្កើតសំឡេងនិយាយ ({dub_mode})...")
                            
                            tts_success = text_to_speech_khmer(translated_text, output_audio_path, voice=chosen_voice)

                            if tts_success and os.path.exists(output_audio_path):
                                st.audio(output_audio_path)
                                st.success("✅ បង្កើតសំឡេងបញ្ចូលជាភាសាខ្មែរបានជោគជ័យ!")

                                if not license_data.get("is_vip"):
                                    license_data["usage_count"] = license_data.get("usage_count", 0) + 1
                                    save_license(license_data)
                            else:
                                st.error("⚠️ មិនអាចបង្កើតសំឡេងបានទេ។ សូមព្យាយាមម្តងទៀតជាមួយវីដេអូខ្លីជាងមុន។")
                        else:
                            st.error("⚠️ ការបកប្រែបរាជ័យ។")
