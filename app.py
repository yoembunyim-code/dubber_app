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
# STABLE EDGE-TTS FUNCTION (SUPPORT MULTI-SPEAKER)
# ==========================================
async def generate_edge_audio(text, output_file, voice="km-KH-SreymomNeural"):
    clean_text = text.strip() if text else ""
    if not clean_text:
        return False
    try:
        communicate = edge_tts.Communicate(clean_text, voice)
        await communicate.save(output_file)
        return os.path.exists(output_file) and os.path.getsize(output_file) > 0
    except Exception:
        return False

def text_to_speech_edge(text, output_file, voice="km-KH-SreymomNeural"):
    return asyncio.run(generate_edge_audio(text, output_file, voice))


# ==========================================
# UI INTERFACE
# ==========================================
st.title("🎬 AI Khmer Auto Dubber Pro")
st.caption("កម្មវិធីស្វ័យប្រវត្តិបកប្រែ និងបញ្ចូលសំឡេងវីដេអូជាភាសាខ្មែរ (មានសំឡេងប្រុស-ស្រីឆ្លើយឆ្លង & 3D Background)")

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

# បន្ថែមជម្រើសសំឡេងប្រុស-ស្រីមកវិញ
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

                    # ១. Whisper Transcription with Segments
                    st.info("🎙️ កំពុងទាញយកឃ្លាប្រយោគពីវីដេអូ...")
                    model = whisper.load_model(whisper_model_type)
                    result = model.transcribe(input_video_path)
                    segments = result.get("segments", [])
                    full_text = result.get("text", "").strip()

                    if not full_text:
                        st.error("⚠️ រកមិនឃើញសំឡេងនិយាយក្នុងវីដេអូនេះទេ។")
                    else:
                        st.write("**អត្ថបទដើមដែលទាញបាន៖**", full_text)

                        # ២. Translation
                        st.info("🌐 កំពុងបកប្រែជាភាសាខ្មែរ...")
                        translator = GoogleTranslator(source='auto', target='km')
                        
                        # បែងចែកប្រយោគ ឬកាត់ជាកំណាត់ៗដើម្បីធ្វើការឆ្លើយឆ្លងប្រុស-ស្រីបានល្អ
                        translated_sentences = []
                        if segments and len(segments) > 1:
                            for idx, seg in enumerate(segments):
                                seg_text = seg.get("text", "").strip()
                                if seg_text:
                                    try:
                                        tr_seg = translator.translate(seg_text)
                                        time.sleep(0.2)
                                    except Exception:
                                        tr_seg = seg_text
                                    
                                    # កំណត់សំឡេងប្រុស (Piseth) ឬ ស្រី (Sreymom) ឆ្លើយឆ្លងគ្នាដូរវេន
                                    if "ប្រុសស្រីឆ្លើយឆ្លង" in dub_mode:
                                        v_choice = "km-KH-SreymomNeural" if idx % 2 == 0 else "km-KH-PisethNeural"
                                    elif "ប្រុសសុទ្ធ" in dub_mode:
                                        v_choice = "km-KH-PisethNeural"
                                    else:
                                        v_choice = "km-KH-SreymomNeural"
                                    
                                    translated_sentences.append((tr_seg, v_choice))
                        else:
                            # ករណីវីដេអូខ្លី ឬអត់មាន Segment ច្បាស់
                            try:
                                tr_full = translator.translate(full_text)
                            except Exception:
                                tr_full = full_text
                            
                            v_choice = "km-KH-PisethNeural" if "ប្រុសសុទ្ធ" in dub_mode else "km-KH-SreymomNeural"
                            translated_sentences.append((tr_full, v_choice))

                        # បង្ហាញអត្ថបទបកប្រែ
                        all_translated_text = " ".join([item[0] for item in translated_sentences])
                        st.write("**អត្ថបទបកប្រែជាភាសាខ្មែរ៖**", all_translated_text)

                        # ៣. ដំណើរការបង្កើតសំឡេង (TTS) តាមប្រយោគនីមួយៗ
                        output_audio_path = os.path.join(temp_dir, "khmer_audio.mp3")
                        st.info(f"🔊 កំពុងបង្កើតសំឡេងនិយាយ ({dub_mode})...")

                        part_files = []
                        for idx, (sentence, voice_type) in enumerate(translated_sentences):
                            part_file = os.path.join(temp_dir, f"part_{idx}.mp3")
                            success = text_to_speech_edge(sentence, part_file, voice=voice_type)
                            if success:
                                part_files.append(part_file)

                        # បញ្ចូលဖាំយសំឡេងទាំងអស់ចូលគ្នា
                        if part_files:
                            with open(output_audio_path, 'wb') as outfile:
                                for f_path in part_files:
                                    with open(f_path, 'rb') as infile:
                                        outfile.write(infile.read())

                            if os.path.exists(output_audio_path) and os.path.getsize(output_audio_path) > 0:
                                st.audio(output_audio_path)
                                st.success("✅ បង្កើតសំឡេងប្រុស-ស្រីឆ្លើយឆ្លងគ្នារួចរាល់ជាជោគជ័យ!")

                                if not license_data.get("is_vip"):
                                    license_data["usage_count"] = license_data.get("usage_count", 0) + 1
                                    save_license(license_data)
                            else:
                                st.error("⚠️ មិនអាចបញ្ចូលឯកសារសំឡេងបានទេ។")
                        else:
                            st.error("⚠️ មិនអាចបង្កើតសំឡេងបានទេ។ សូមព្យាយាមម្តងទៀត។ា")
