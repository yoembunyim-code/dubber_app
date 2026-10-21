import streamlit as st
import os
import json
import asyncio
import tempfile
import time
import whisper
from deep_translator import GoogleTranslator
import edge_tts
from gtts import gTTS
import subprocess

# ==========================================
# PAGE CONFIG & 3D ANIMATED BACKGROUND CSS
# ==========================================
st.set_page_config(page_title="AI Khmer Auto Dubber Pro", page_icon="🎬", layout="wide")

custom_bg_html = """
<style>
.stApp {
    background: linear-gradient(-45deg, #050515, #1a0b2e, #0f1c3f, #071330);
    background-size: 400% 400%;
    animation: gradientBG 12s ease infinite;
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
    width: 30px;
    height: 30px;
    background: rgba(255, 255, 255, 0.2);
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5), inset 0 0 15px rgba(255, 255, 255, 0.4);
    backdrop-filter: blur(6px);
    border: 1.5px solid rgba(255, 255, 255, 0.3);
    animation: animate 20s linear infinite;
    bottom: -200px;
    border-radius: 50%;
}

.circles li:nth-child(1) { left: 10%; width: 100px; height: 100px; animation-delay: 0s; animation-duration: 15s; }
.circles li:nth-child(2) { left: 20%; width: 50px; height: 50px; animation-delay: 2s; animation-duration: 10s; }
.circles li:nth-child(3) { left: 35%; width: 90px; height: 90px; animation-delay: 4s; animation-duration: 18s; }
.circles li:nth-child(4) { left: 50%; width: 120px; height: 120px; animation-delay: 0s; animation-duration: 22s; }
.circles li:nth-child(5) { left: 65%; width: 40px; height: 40px; animation-delay: 3s; animation-duration: 12s; }
.circles li:nth-child(6) { left: 75%; width: 140px; height: 140px; animation-delay: 2s; animation-duration: 25s; }
.circles li:nth-child(7) { left: 85%; width: 70px; height: 70px; animation-delay: 5s; animation-duration: 14s; }
.circles li:nth-child(8) { left: 90%; width: 110px; height: 110px; animation-delay: 1s; animation-duration: 20s; }

@keyframes animate {
    0% { transform: translateY(0) rotate(0deg) scale(1); opacity: 0.9; }
    50% { transform: translateY(-700px) rotate(360deg) scale(1.3); opacity: 0.6; }
    100% { transform: translateY(-1300px) rotate(720deg) scale(0.7); opacity: 0; }
}
</style>

<div class="area">
    <ul class="circles">
        <li></li><li></li><li></li><li></li>
        <li></li><li></li><li></li><li></li>
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
        st.error(f"មិនអាចរក្សាទុកព័ត៌មានអាជ្ញាបណ្ណได้ទេ: {e}")

license_data = load_license()


# ==========================================
# STABLE SAFE TTS FUNCTION
# ==========================================
async def generate_edge_audio_safe(text, output_file, voice="km-KH-SreymomNeural"):
    clean_text = text.strip() if text else ""
    if not clean_text:
        return False
    try:
        communicate = edge_tts.Communicate(clean_text, voice)
        await communicate.save(output_file)
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            return True
    except Exception:
        pass
    
    try:
        tts = gTTS(text=clean_text, lang='km', slow=False)
        tts.save(output_file)
        return os.path.exists(output_file) and os.path.getsize(output_file) > 0
    except Exception:
        return False

def text_to_speech_safe(text, output_file, voice="km-KH-SreymomNeural"):
    return asyncio.run(generate_edge_audio_safe(text, output_file, voice))


# ==========================================
# UI INTERFACE
# ==========================================
st.title("🎬 AI Khmer Auto Dubber Pro")
st.caption("ប្រព័ន្ធស្វ័យប្រវត្តិបកប្រែវីដេអូជាសំឡេងខ្មែរ (ប្រុស-ស្រីឆ្លើយឆ្លង និង 3D Background)")

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
whisper_model_type = st.sidebar.selectbox("ជ្រើសរើស Whisper Model:", ["base", "small"], index=0)

dub_mode = st.sidebar.selectbox(
    "ជម្រើសរបៀបបញ្ចូលសំឡេង៖",
    [
        "ប្រុសស្រីឆ្លើយឆ្លងគ្នាស្វ័យប្រវត្តិ (Multi-Speaker)",
        "សំឡេងស្រីសុទ្ធ (Sreymom)", 
        "សំឡេងប្រុសសុទ្ធ (Piseth)"
    ]
)


# ==========================================
# PROCESSING & REMUXING VIDEO
# ==========================================
uploaded_file = st.file_uploader("បញ្ចូលវីដេអូរបស់អ្នក (.mp4, .mov, .avi):", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    if not license_data.get("is_vip") and license_data.get("usage_count", 0) >= TRIAL_VIDEO_LIMIT:
        st.error("⚠️ អស់ចំនួនដងសាកល្បង Free Trial ហើយ! សូមបញ្ចូលលេខកូដ VIP។")
    else:
        st.video(uploaded_file)
        
        if st.button("🚀 បកប្រែ និងបញ្ចូលសំឡេងខ្មែរចូលវីដេអូ"):
            with st.spinner("កំពុងវិភាគវីដេអូ បកប្រែជាខ្មែរ និងបញ្ចូលសំឡេងប្រុស-ស្រី..."):
                with tempfile.TemporaryDirectory() as temp_dir:
                    input_video_path = os.path.join(temp_dir, "input_video.mp4")
                    with open(input_video_path, "wb") as f:
                        f.write(uploaded_file.read())

                    # ១. Whisper Transcription ຢ່າງត្រឹមត្រូវ
                    st.info("🎙️ កំពុងទាញយកឃ្លាប្រយោគពីវីដេអូដើម...")
                    try:
                        model = whisper.load_model(whisper_model_type)
                        result = model.transcribe(input_video_path)
                        full_text = result.get("text", "").strip()
                    except Exception as e:
                        st.error(whisper model error: {e})
                        full_text = ""

                    if not full_text:
                        st.error("⚠️ រកមិនឃើញសំឡេងនិយាយក្នុងវីដេអូនេះទេ។ សូមពិនិត្យមើលវីដេអូរបស់អ្នក។")
                    else:
                        st.write("**អត្ថបទដើមដែលចាប់បាន៖**", full_text)

                        # ២. Translation to Khmer
                        st.info("🌐 កំពុងបកប្រែជាភាសាខ្មែរ...")
                        translator = GoogleTranslator(source='auto', target='km')
                        try:
                            if len(full_text) > 400:
                                chunks = [full_text[i:i+400] for i in range(0, len(full_text), 400)]
                                translated_chunks = []
                                for chunk in chunks:
                                    translated_chunks.append(translator.translate(chunk))
                                    time.sleep(0.1)
                                translated_text = " ".join(translated_chunks)
                            else:
                                translated_text = translator.translate(full_text)
                        except Exception:
                            translated_text = full_text

                        if translated_text:
                            st.write("**អត្ថបទបកប្រែជាភាសាខ្មែរ៖**", translated_text)

                            # ៣. Multi-Speaker Generation
                            output_audio_path = os.path.join(temp_dir, "khmer_audio.mp3")
                            st.info(f"🔊 កំពុងបង្កើតសំឡេងនិយាយ ({dub_mode})...")

                            sentences = [s.strip() for s in translated_text.replace("。", ".").split(".") if s.strip()]
                            if not sentences:
                                sentences = [translated_text]

                            part_files = []
                            for idx, sentence in enumerate(sentences):
                                part_file = os.path.join(temp_dir, f"part_{idx}.mp3")
                                
                                if "ប្រុសស្រីឆ្លើយឆ្លង" in dub_mode:
                                    v_choice = "km-KH-SreymomNeural" if idx % 2 == 0 else "km-KH-PisethNeural"
                                elif "ប្រុសសុទ្ធ" in dub_mode:
                                    v_choice = "km-KH-PisethNeural"
                                else:
                                    v_choice = "km-KH-SreymomNeural"

                                success = text_to_speech_safe(sentence, part_file, voice=v_choice)
                                if success:
                                    part_files.append(part_file)

                            if part_files:
                                with open(output_audio_path, 'wb') as outfile:
                                    for f_path in part_files:
                                        with open(f_path, 'rb') as infile:
                                            outfile.write(infile.read())

                                # ៤. Remux Video with FFmpeg (រក្សាប្រវែងវីដេអូដើមដោយមិនកាត់តម្រឹមខុស)
                                output_video_path = os.path.join(temp_dir, "final_output_video.mp4")
                                st.info("🎬 កំពុងផ្គុំសំឡេងខ្មែរចូលទៅក្នុងវីដេអូដោយប្រើប្រាស់ FFmpeg...")
                                
                                ffmpeg_cmd = [
                                    "ffmpeg", "-y",
                                    "-i", input_video_path,
                                    "-i", output_audio_path,
                                    "-c:v", "copy",
                                    "-map", "0:v:0",
                                    "-map", "1:a:0",
                                    "-c:a", "aac",
                                    output_video_path
                                ]

                                try:
                                    subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                    
                                    if os.path.exists(output_video_path) and os.path.getsize(output_video_path) > 0:
                                        st.success("✅ បង្កើតវីដេអូបញ្ចូលសំឡេងខ្មែរ (ប្រុស-ស្រី) បានជោគជ័យពេញលេញ!")
                                        
                                        with open(output_video_path, "rb") as vid_file:
                                            video_bytes = vid_file.read()
                                            st.video(video_bytes)
                                            st.download_button(
                                                label="📥 ទាញយកវីដេអូអភិវឌ្ឍន៍ថ្មី (.mp4)",
                                                data=video_bytes,
                                                file_name="khmer_dubbed_video.mp4",
                                                mime="video/mp4"
                                            )

                                        if not license_data.get("is_vip"):
                                            license_data["usage_count"] = license_data.get("usage_count", 0) + 1
                                            save_license(license_data)
                                    else:
                                        st.error("⚠️ កំហុសក្នុងការផ្គុំវីដេអូជាមួយ FFmpeg។")
                                except Exception as ffmpeg_err:
                                    st.error(f"⚠️ រកមិនឃើញ FFmpeg ឬមានបញ្ហាក្នុងការដំណើរការ៖ {ffmpeg_err}")
                            else:
                                st.error("⚠️ មិនអាចបង្កើតសំឡេងបានទេ។ សូមព្យាយាមម្តងទៀត។")
                        else:
                            st.error("⚠️ ការបកប្រែបរាជ័យ។")
